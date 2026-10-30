#!/usr/bin/env bash
# 架构师补充审计：缓存失效、判分细则、批量操作、全端权限
# 用法: bash scripts/e2e-extra.sh [base_url]
# 只造临时数据，跑完删干净。只对本地 8080 跑。
set -uo pipefail

BASE="${1:-http://127.0.0.1:8080}"
CURL=(curl -sS --max-time 25)
PASS=0
FAIL=0
TOKEN=""

py() {
  python -c "
import json,sys
d=json.load(sys.stdin)
try:
    print(eval(sys.argv[1]))
except Exception as e:
    print('ERR:'+str(e))
" "$1"
}
ue() { python -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1"; }
ok() { echo "  [ok]   $1"; PASS=$((PASS + 1)); }
bad() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }
check() { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1（期望 $3，实际 $2）"; fi; }

api() {
  local method="$1" path="$2" body="${3:-}" tok="${4:-$TOKEN}"
  if [ -n "$body" ]; then
    "${CURL[@]}" -X "$method" "$BASE$path" -H 'content-type: application/json' \
      ${tok:+-H "Authorization: Bearer $tok"} -d "$body"
  else
    "${CURL[@]}" -X "$method" "$BASE$path" ${tok:+-H "Authorization: Bearer $tok"}
  fi
}
status() {
  local method="$1" path="$2" body="${3:-}" tok="${4:-$TOKEN}"
  if [ -n "$body" ]; then
    "${CURL[@]}" -o /dev/null -w '%{http_code}' -X "$method" "$BASE$path" \
      -H 'content-type: application/json' ${tok:+-H "Authorization: Bearer $tok"} -d "$body"
  else
    "${CURL[@]}" -o /dev/null -w '%{http_code}' -X "$method" "$BASE$path" ${tok:+-H "Authorization: Bearer $tok"}
  fi
}
login() {
  "${CURL[@]}" -X POST "$BASE/api/auth/login" -H 'content-type: application/json' \
    -d "{\"username\":\"$1\",\"password\":\"$2\"}"
}

TOKEN=$(login admin admin123 | py "d['data']['token']")
STU=$(login student02 student123 | py "d['data']['token']")

echo "== 0. 清理上一次中断留下的探针数据"
PAPERS=$(api GET '/api/papers?page=1&size=100' | py "' '.join(str(x['id']) for x in d['data']['records'] if x['title'].startswith(('E2E-','GRADE-PROBE','DBG-')))")
for pid in $PAPERS; do
  api POST "/api/papers/$pid/close" >/dev/null 2>&1
  api DELETE "/api/papers/$pid" >/dev/null 2>&1
done
BANKS=$(api GET '/api/banks?page=1&size=100' | py "' '.join(str(x['id']) for x in d['data']['records'] if x['name'].startswith(('E2E-','BATCH-','CACHE-PROBE')))")
for bid in $BANKS; do api DELETE "/api/banks/$bid" >/dev/null 2>&1; done
echo "  清掉试卷 $PAPERS | 题库 $BANKS"

echo "== 1. 判断题答案格式（契约要求 A/B 字符串，不带引号）"
JUDGE_TMP="$(mktemp)"
printf '%s' "$(api GET "/api/questions?type=judge&page=1&size=1")" > "$JUDGE_TMP"
JUDGE_WIN="$(cygpath -w "$JUDGE_TMP")"
trap 'rm -f "$JUDGE_TMP"' EXIT
check "判断题 answer 是 A 或 B" "$(python -c "
import json
d=json.load(open(r'$JUDGE_WIN',encoding='utf-8'))['data']['records'][0]
a=d['answer']
print('OK' if isinstance(a,str) and a in ('A','B') else 'BAD:'+repr(a))
")" "OK"
check "判断题有两个选项" "$(python -c "
import json
d=json.load(open(r'$JUDGE_WIN',encoding='utf-8'))['data']['records'][0]
o=d['options']
print('OK' if isinstance(o,list) and len(o)==2 and o[0]['key']=='A' else 'BAD:'+repr(o)[:60])
")" "OK"

echo "== 2. 题库字典缓存：命中 -> 增题库后失效"
api GET /api/banks/all >/dev/null
if command -v redis-cli >/dev/null 2>&1; then
  check "字典先落缓存" "$(redis-cli exists dict:banks | tr -d '\r')" "1"
  TMPBODY=$(mktemp)
  printf '%s' '{"name":"CACHE-PROBE","groupName":"本科组","description":"cache probe","status":"ENABLED"}' > "$TMPBODY"
  NB=$("${CURL[@]}" -X POST "$BASE/api/banks" -H 'content-type: application/json; charset=utf-8' \
    -H "Authorization: Bearer $TOKEN" --data-binary "@$(cygpath -w "$TMPBODY")" | py "d['data']['id']")
  rm -f "$TMPBODY"
  check "新增题库后字典缓存被清" "$(redis-cli exists dict:banks | tr -d '\r')" "0"
  api GET /api/banks/all >/dev/null
  check "再次查询重新落缓存" "$(redis-cli exists dict:banks | tr -d '\r')" "1"
  api DELETE "/api/banks/$NB" >/dev/null
  check "删题库后字典缓存也被清" "$(redis-cli exists dict:banks | tr -d '\r')" "0"
else
  bad "没有 redis-cli，跳过缓存失效检查"
fi

echo "== 3. 判分细则（判断全对/多选少选半分的边界）"
PID=$(api POST /api/papers '{"title":"GRADE-PROBE","bankId":1,"judgeCount":1,"singleCount":0,"multiCount":1,"judgeScore":4,"singleScore":1,"multiScore":6,"durationSec":600}' | py "d['data']['id']")
api POST "/api/papers/$PID/publish" >/dev/null
DET=$(api GET "/api/papers/$PID")
JQ=$(printf '%s' "$DET" | py "d['data']['questions'][0]['id']")
JA=$(printf '%s' "$DET" | py "d['data']['questions'][0]['answer']")
MQ=$(printf '%s' "$DET" | py "d['data']['questions'][1]['id']")
MA=$(printf '%s' "$DET" | py "d['data']['questions'][1]['answer']")
MA_FIRST=$(printf '%s' "$DET" | py "d['data']['questions'][1]['answer'][0]")
if [ "$JA" = "A" ]; then JW="B"; else JW="A"; fi

# 判断题答对 4 分 + 多选只选一个（少选）应得 3 分
SC=$(api POST /api/answers/submit "{\"paperId\":$PID,\"answers\":[{\"questionId\":$JQ,\"chosen\":\"$JA\"},{\"questionId\":$MQ,\"chosen\":[\"$MA_FIRST\"]}]}" "$STU")
check "判断全对 4 分" "$(printf '%s' "$SC" | py "d['data']['totalScore']")" "7"
check "多选少选得一半 3 分" "$(printf '%s' "$SC" | py "d['data']['totalScore'] - 4")" "3"
api DELETE "/api/scores/$PID/3" >/dev/null

# 判断题答错 0 分 + 多选多选（超出标准答案）0 分
SC2=$(api POST /api/answers/submit "{\"paperId\":$PID,\"answers\":[{\"questionId\":$JQ,\"chosen\":\"$JW\"},{\"questionId\":$MQ,\"chosen\":[\"A\",\"B\",\"C\",\"D\"]}]}" "$STU")
check "判断答错 + 多选乱选 = 0 分" "$(printf '%s' "$SC2" | py "d['data']['totalScore']")" "0"
check "答错数 2" "$(printf '%s' "$SC2" | py "d['data']['wrongCount']")" "2"
api DELETE "/api/scores/$PID/3" >/dev/null
api POST "/api/papers/$PID/close" >/dev/null
api DELETE "/api/papers/$PID" >/dev/null

echo "== 4. 批量移动题目"
TMPBODY=$(mktemp)
printf '%s' '{"name":"BATCH-A","groupName":"本科组","status":"ENABLED"}' > "$TMPBODY"
A=$("${CURL[@]}" -X POST "$BASE/api/banks" -H 'content-type: application/json; charset=utf-8' -H "Authorization: Bearer $TOKEN" --data-binary "@$(cygpath -w "$TMPBODY")" | py "d['data']['id']")
printf '%s' '{"name":"BATCH-B","groupName":"本科组","status":"ENABLED"}' > "$TMPBODY"
B=$("${CURL[@]}" -X POST "$BASE/api/banks" -H 'content-type: application/json; charset=utf-8' -H "Authorization: Bearer $TOKEN" --data-binary "@$(cygpath -w "$TMPBODY")" | py "d['data']['id']")
rm -f "$TMPBODY"
Q=$(api POST /api/questions "{\"bankId\":$A,\"type\":\"single\",\"stem\":\"batch probe\",\"options\":[{\"key\":\"A\",\"text\":\"x\"}],\"answer\":\"A\",\"difficulty\":1,\"sortNo\":1}" | py "d['data']['id']")
check "批量移动返回 updated=1" "$(api PATCH /api/questions/batch "{\"ids\":[$Q],\"bankId\":$B}" | py "d['data']['updated']")" "1"
check "移动后归属题库变了" "$(api GET "/api/questions/$Q" | py "d['data']['bankId']")" "$B"
api DELETE "/api/questions/$Q" >/dev/null
api DELETE "/api/banks/$A" >/dev/null
api DELETE "/api/banks/$B" >/dev/null

echo "== 5. 全线权限：考生做管理操作一律 403"
# 权限测试要送合法请求体，否则会先被参数校验拦成 400
TMPBODY=$(mktemp)
printf '%s' '{"name":"NO-PERM","groupName":"本科组","status":"ENABLED"}' > "$TMPBODY"
STU_CREATE=$("${CURL[@]}" -o /dev/null -w '%{http_code}' -X POST "$BASE/api/banks"   -H 'content-type: application/json; charset=utf-8' -H "Authorization: Bearer $STU" --data-binary "@$(cygpath -w "$TMPBODY")")
printf '%s' '{"name":"NO-PERM2","groupName":"本科组","status":"ENABLED"}' > "$TMPBODY"
STU_UPDATE=$("${CURL[@]}" -o /dev/null -w '%{http_code}' -X PUT "$BASE/api/banks/1"   -H 'content-type: application/json; charset=utf-8' -H "Authorization: Bearer $STU" --data-binary "@$(cygpath -w "$TMPBODY")")
rm -f "$TMPBODY"
check "考生建题库 403" "$STU_CREATE" "403"
check "考生改题库 403" "$STU_UPDATE" "403"
check "考生删题库 403" "$(status DELETE /api/banks/1 '' "$STU")" "403"
check "考生建题目 403" "$(status POST /api/questions '{"bankId":1,"type":"single","stem":"x","options":[],"answer":"A","difficulty":1}' "$STU")" "403"
check "考生组卷 403" "$(status POST /api/papers '{"title":"x","bankId":1,"judgeCount":1,"singleCount":0,"multiCount":0,"judgeScore":1,"singleScore":1,"multiScore":1,"durationSec":60}' "$STU")" "403"
check "考生查题库列表 200（只读允许）" "$(status GET /api/banks '' "$STU")" "200"

echo
echo "结果: $PASS 通过, $FAIL 失败"
[ "$FAIL" -eq 0 ]
