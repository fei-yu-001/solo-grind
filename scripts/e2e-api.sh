#!/usr/bin/env bash
# 智考刷题系统 · 接口验收脚本
# 用法: bash scripts/e2e-api.sh [base_url]
# 只造自己的临时数据，跑完删干净；只对本地 8080 跑，不要指向线上。
set -uo pipefail

BASE="${1:-http://127.0.0.1:8080}"
CURL=(curl -sS --max-time 25)
PASS=0
FAIL=0
TOKEN=""
ADMIN_TOKEN=""

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

# 中文查询参数必须编码，否则 Windows 版 curl 直接报 URL rejected
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

echo "== 0. 未带令牌"
check "GET /api/banks 无 token" "$(status GET /api/banks)" "401"

echo "== 1. 登录与身份"
R=$(login admin admin123)
TOKEN=$(printf '%s' "$R" | py "d['data']['token']")
ADMIN_TOKEN="$TOKEN"
[ -n "$TOKEN" ] && [ "${TOKEN:0:3}" != "ERR" ] && ok "管理员登录取到 token" || bad "管理员登录失败: $R"
check "密码错误 401" "$("${CURL[@]}" -o /dev/null -w '%{http_code}' -X POST "$BASE/api/auth/login" -H 'content-type: application/json' -d '{"username":"admin","password":"bad"}')" "401"
check "当前用户是 admin" "$(api GET /api/auth/me | py "d['data']['username']")" "admin"
check "管理员角色" "$(api GET /api/auth/me | py "d['data']['role']")" "ADMIN"
STU=$(login student01 student123 | py "d['data']['token']")
Q_BASE=$(api GET '/api/questions?page=1&size=1' | py "d['data']['total']")
B_BASE=$(api GET '/api/banks?page=1&size=1' | py "d['data']['total']")
echo "  基线：题库 $B_BASE 个，题目 $Q_BASE 道"

echo "== 2. 题库：分页、条件、增改删"
check "题库分页 size=1 返回 1 条" "$(api GET '/api/banks?page=1&size=1' | py "len(d['data']['records'])")" "1"
check "题库 total 等于基线" "$(api GET '/api/banks?page=1&size=1' | py "d['data']['total']")" "$B_BASE"
GROUP=$(ue 本科组)
check "按组别过滤" "$(api GET "/api/banks?groupName=$GROUP&page=1&size=10" | py "d['data']['total']")" "1"
check "题库带题目数" "$(api GET "/api/banks?groupName=$GROUP&page=1&size=10" | py "d['data']['records'][0]['questionCount']")" "40"
api GET /api/banks/all >/dev/null
BNAME="E2E-BANK-$RANDOM"
TMPBODY="$(mktemp)"
printf '%s' "{\"name\":\"$BNAME\",\"groupName\":\"本科组\",\"description\":\"created by e2e\",\"status\":\"ENABLED\"}" > "$TMPBODY"
BANK_ID=$("${CURL[@]}" -X POST "$BASE/api/banks" -H 'content-type: application/json; charset=utf-8'   -H "Authorization: Bearer $TOKEN" --data-binary "@$(cygpath -w "$TMPBODY")" | py "d['data']['id']")
rm -f "$TMPBODY"
[ -n "$BANK_ID" ] && [ "${BANK_ID:0:3}" != "ERR" ] && ok "新增题库 id=$BANK_ID" || bad "新增题库失败"
BNAME_UE=$(ue "$BNAME")
check "按关键字查到自己" "$(api GET "/api/banks?keyword=$BNAME_UE&page=1&size=10" | py "d['data']['total']")" "1"
TMPBODY="$(mktemp)"
printf '%s' "{\"name\":\"$BNAME-B\",\"groupName\":\"专科组\",\"description\":\"updated by e2e\",\"status\":\"ENABLED\"}" > "$TMPBODY"
NEW_NAME=$("${CURL[@]}" -X PUT "$BASE/api/banks/$BANK_ID" -H 'content-type: application/json; charset=utf-8'   -H "Authorization: Bearer $TOKEN" --data-binary "@$(cygpath -w "$TMPBODY")" | py "d['data']['name']")
rm -f "$TMPBODY"
check "改题库名" "$NEW_NAME" "$BNAME-B"

echo "== 3. 题目：分页、条件、标签、增改删、批量移动"
check "题目总数等于基线" "$(api GET '/api/questions?page=1&size=1' | py "d['data']['total']")" "$Q_BASE"
check "size=10 正好 10 条" "$(api GET '/api/questions?page=1&size=10' | py "len(d['data']['records'])")" "10"
check "按题型过滤（判断题 16）" "$(api GET '/api/questions?type=judge&page=1&size=10' | py "d['data']['total']")" "16"
check "按题库过滤（题库1 40）" "$(api GET '/api/questions?bankId=1&page=1&size=10' | py "d['data']['total']")" "40"
check "按标签过滤不报错" "$(api GET '/api/questions?tagId=1&page=1&size=10' | py "'yes' if 'total' in d['data'] else 'no'")" "yes"
TAG_ID=$(api GET /api/tags | py "d['data'][0]['id']")
QID=$(api POST /api/questions "{\"bankId\":$BANK_ID,\"type\":\"single\",\"stem\":\"E2E question stem\",\"options\":[{\"key\":\"A\",\"text\":\"A-text\"},{\"key\":\"B\",\"text\":\"B-text\"}],\"answer\":\"A\",\"analysis\":\"because A\",\"difficulty\":2,\"sortNo\":1,\"tagIds\":[$TAG_ID]}" | py "d['data']['id']")
[ -n "$QID" ] && [ "${QID:0:3}" != "ERR" ] && ok "新增题目 id=$QID" || bad "新增题目失败"
check "详情带题库名" "$(api GET "/api/questions/$QID" | py "d['data']['bankName']")" "$BNAME-B"
check "详情带标签（多对多）" "$(api GET "/api/questions/$QID" | py "len(d['data']['tags'])")" "1"
check "题干可改" "$(api PUT "/api/questions/$QID" "{\"bankId\":$BANK_ID,\"type\":\"multi\",\"stem\":\"E2E question stem updated\",\"options\":[{\"key\":\"A\",\"text\":\"A-text\"},{\"key\":\"B\",\"text\":\"B-text\"},{\"key\":\"C\",\"text\":\"C-text\"}],\"answer\":[\"A\",\"B\"],\"difficulty\":3,\"sortNo\":1,\"tagIds\":[$TAG_ID]}" | py "d['data']['stem']")" "E2E question stem updated"
check "题型改成功" "$(api GET "/api/questions/$QID" | py "d['data']['type']")" "multi"

echo "== 4. 试卷：组卷（事务）、明细、状态流转"
PID=$(api POST /api/papers "{\"title\":\"E2E-PAPER-$RANDOM\",\"bankId\":1,\"judgeCount\":2,\"singleCount\":3,\"multiCount\":1,\"judgeScore\":1,\"singleScore\":1,\"multiScore\":2,\"durationSec\":600}" | py "d['data']['id']")
[ -n "$PID" ] && [ "${PID:0:3}" != "ERR" ] && ok "组卷成功 id=$PID" || bad "组卷失败"
check "组卷总分 2*1+3*1+1*2=7" "$(api GET "/api/papers/$PID" | py "d['data']['totalScore']")" "7"
check "组卷题目数 6" "$(api GET "/api/papers/$PID" | py "len(d['data']['questions'])")" "6"
check "题序从 1 开始" "$(api GET "/api/papers/$PID" | py "d['data']['questions'][0]['seq']")" "1"
check "题量超出题库 409" "$(status POST /api/papers '{"title":"E2E-TOO-MANY","bankId":1,"judgeCount":999,"singleCount":0,"multiCount":0,"judgeScore":1,"singleScore":1,"multiScore":2,"durationSec":600}')" "409"
check "发布试卷" "$(api POST "/api/papers/$PID/publish" | py "d['data']['status']")" "PUBLISHED"
check "已发布不能改组卷 409" "$(status PUT "/api/papers/$PID" "{\"title\":\"E2E-PAPER-EDIT\",\"bankId\":1,\"judgeCount\":2,\"singleCount\":3,\"multiCount\":1,\"judgeScore\":1,\"singleScore\":1,\"multiScore\":2,\"durationSec\":600}")" "409"

echo "== 5. 交卷判分"
Q1=$(api GET "/api/papers/$PID" | py "d['data']['questions'][0]['id']")
Q2=$(api GET "/api/papers/$PID" | py "d['data']['questions'][1]['id']")
A1=$(api GET "/api/papers/$PID" | py "d['data']['questions'][0]['answer']")
A2=$(api GET "/api/papers/$PID" | py "d['data']['questions'][1]['answer']")
if [ "$(api GET "/api/papers/$PID" | py "isinstance(d['data']['questions'][1]['answer'], list)")" = "True" ]; then
  A2="[\"$(printf '%s' "$A2" | tr -d '[]" ' | cut -c1)\"]"
else
  A2="\"$A2\""
fi
BODY="{\"paperId\":$PID,\"answers\":[{\"questionId\":$Q1,\"chosen\":\"$A1\"},{\"questionId\":$Q2,\"chosen\":$A2}]}"
SC=$(api POST /api/answers/submit "$BODY" "$STU")
check "考生交卷成功" "$(printf '%s' "$SC" | py "'yes' if d['data']['totalScore'] >= 0 else 'no'")" "yes"
check "得分等于答对题分（前两题都对）" "$(printf '%s' "$SC" | py "d['data']['totalScore']")" "2"
check "答对题数 2" "$(printf '%s' "$SC" | py "d['data']['correctCount']")" "2"
check "未答计入 blankCount" "$(printf '%s' "$SC" | py "d['data']['blankCount']")" "4"
check "同一考生同卷再交 409" "$(status POST /api/answers/submit "$BODY" "$STU")" "409"
check "成绩列表能查到" "$(api GET "/api/scores?paperId=$PID&page=1&size=10" | py "d['data']['total']")" "1"
check "成绩明细有逐题" "$(api GET "/api/scores/$PID/2" | py "len(d['data']['items'])")" "6"
check "排行榜可用" "$(api GET "/api/scores/ranking?paperId=$PID" | py "'yes' if isinstance(d['data'], list) else 'no'")" "yes"
# 此时已多出一张临时卷子和一道临时题目，所以只校验不小于基线
check "统计题目数不小于基线" "$(api GET /api/scores/stats | py "'yes' if d['data']['questionCount'] >= $Q_BASE else 'no'")" "yes"

echo "== 6. 权限与引用校验"
# 中文请求体走文件，避免 Windows 版 curl 按 GBK 编码命令行参数
TMPBODY="$(mktemp)"
printf '%s' '{"name":"E2E-STUDENT-BANK","groupName":"本科组","status":"ENABLED"}' > "$TMPBODY"
STU_STATUS=$("${CURL[@]}" -o /dev/null -w '%{http_code}' -X POST "$BASE/api/banks"   -H 'content-type: application/json; charset=utf-8' -H "Authorization: Bearer $STU"   --data-binary "@$(cygpath -w "$TMPBODY")")
rm -f "$TMPBODY"
check "考生调管理接口 403" "$STU_STATUS" "403"
check "题库下有题不能删 409" "$(status DELETE /api/banks/1)" "409"
USED_Q=$(api GET "/api/papers/$PID" | py "d['data']['questions'][0]['id']")
check "题目被试卷引用不能删 409" "$(status DELETE "/api/questions/$USED_Q")" "409"

echo "== 7. Redis"
if command -v redis-cli >/dev/null 2>&1; then
  TTL=$(redis-cli ttl "login:token:$TOKEN" 2>/dev/null | tr -d '\r')
  [ -n "$TTL" ] && [ "$TTL" -gt 0 ] 2>/dev/null && ok "令牌 TTL=${TTL}s" || bad "令牌没进 Redis（ttl=$TTL）"
  api GET /api/banks/all >/dev/null
  check "题库字典进缓存" "$(redis-cli exists dict:banks 2>/dev/null | tr -d '\r')" "1"
  api GET "/api/scores/ranking?paperId=$PID" >/dev/null
  check "排行榜进缓存" "$(redis-cli exists "cache:ranking:$PID" 2>/dev/null | tr -d '\r')" "1"
else
  bad "没有 redis-cli，跳过缓存检查"
fi

echo "== 8. 清理"
check "撤销成绩" "$(status DELETE "/api/scores/$PID/2")" "200"
check "结束试卷" "$(status POST "/api/papers/$PID/close")" "200"
check "删除试卷" "$(status DELETE "/api/papers/$PID")" "200"
check "删除题目" "$(status DELETE "/api/questions/$QID")" "200"
check "删除题库" "$(status DELETE "/api/banks/$BANK_ID")" "200"
check "登出" "$(status POST /api/auth/logout)" "200"
check "登出后旧 token 401" "$(status GET /api/banks)" "401"

echo
echo "结果: $PASS 通过, $FAIL 失败"
[ "$FAIL" -eq 0 ]
