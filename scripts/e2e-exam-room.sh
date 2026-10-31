#!/usr/bin/env bash
# 考生在线答题流程验收：取卷 -> 确认不泄答案 -> 交卷 -> 再取 409 -> 我的成绩 -> 越权 403 -> 清理
# 用法: bash scripts/e2e-exam-room.sh [base_url]
set -uo pipefail

BASE="${1:-http://127.0.0.1:8080}"
CURL=(curl -sS --max-time 25)
PASS=0
FAIL=0
ADMIN=""
STU=""
STU_ID=""

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
ok() { echo "  [ok]   $1"; PASS=$((PASS + 1)); }
bad() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }
check() { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1（期望 $3，实际 $2）"; fi; }

api() {
  local method="$1" path="$2" body="${3:-}" tok="${4:-$STU}"
  if [ -n "$body" ]; then
    "${CURL[@]}" -X "$method" "$BASE$path" -H 'content-type: application/json' \
      ${tok:+-H "Authorization: Bearer $tok"} -d "$body"
  else
    "${CURL[@]}" -X "$method" "$BASE$path" ${tok:+-H "Authorization: Bearer $tok"}
  fi
}
status() {
  local method="$1" path="$2" body="${3:-}" tok="${4:-$STU}"
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

ADMIN=$(login admin admin123 | py "d['data']['token']")
STU=$(login student03 student123 | py "d['data']['token']")
STU_ID=$(api GET /api/auth/me | py "d['data']['id']")
echo "  考生 student03 id=$STU_ID"

echo "== 1. 考试中心：可选试卷"
AVAIL=$(api GET /api/exams/available)
COUNT=$(printf '%s' "$AVAIL" | py "len(d['data'])")
if [ "$COUNT" -ge 1 ]; then ok "可用试卷 $COUNT 张"; else bad "没有可用试卷（$AVAIL）"; fi
check "默认都没交过（myScore 为 null）" "$(printf '%s' "$AVAIL" | py "'yes' if all(x['myScore'] is None for x in d['data']) else 'no'")" "yes"
PAPER=$(printf '%s' "$AVAIL" | py "d['data'][0]['paperId']")
TOTAL=$(printf '%s' "$AVAIL" | py "d['data'][0]['totalScore']")
echo "  选中试卷 id=$PAPER 总分=$TOTAL"

echo "== 2. 取题：不能泄露答案"
VIEW=$(api GET "/api/exams/$PAPER/questions")
check "拿到题目列表" "$(printf '%s' "$VIEW" | py "'yes' if len(d['data']['questions'])>0 else 'no'")" "yes"
LEAK=$(printf '%s' "$VIEW" | python -c "
import json,sys
d=json.load(sys.stdin)['data']
bad=[k for q in d['questions'] for k in q if k in ('answer','analysis')]
print('LEAK:'+','.join(sorted(set(bad))) if bad else 'clean')
")
check "题目里没有 answer / analysis" "$LEAK" "clean"
check "带 seq 且从 1 开始" "$(printf '%s' "$VIEW" | py "d['data']['questions'][0]['seq']")" "1"
check "每题都有分值" "$(printf '%s' "$VIEW" | py "'yes' if all('score' in q for q in d['data']['questions']) else 'no'")" "yes"

echo "== 3. 交卷（答 3 题，故意用错答案验证判分）"
Q1=$(printf '%s' "$VIEW" | py "d['data']['questions'][0]['questionId']")
Q2=$(printf '%s' "$VIEW" | py "d['data']['questions'][1]['questionId']")
Q3=$(printf '%s' "$VIEW" | py "d['data']['questions'][2]['questionId']")
SC=$(api POST /api/answers/submit "{\"paperId\":$PAPER,\"answers\":[{\"questionId\":$Q1,\"chosen\":\"Z\"},{\"questionId\":$Q2,\"chosen\":\"Z\"},{\"questionId\":$Q3,\"chosen\":\"Z\"}]}")
check "交卷返回成绩" "$(printf '%s' "$SC" | py "'yes' if d['data'] and 'totalScore' in d['data'] else 'no'")" "yes"
check "乱答得 0 分" "$(printf '%s' "$SC" | py "d['data']['totalScore']")" "0"
check "未答计入 blankCount" "$(printf '%s' "$SC" | py "'yes' if d['data']['blankCount'] > 0 else 'no'")" "yes"

echo "== 4. 交卷后不能再取题"
check "再取题 409" "$(status GET "/api/exams/$PAPER/questions")" "409"
check "考试中心显示已交" "$(api GET /api/exams/available | py "'yes' if any(x['paperId']==$PAPER and x['myScore'] is not None for x in d['data']) else 'no'")" "yes"

echo "== 5. 我的成绩与越权"
check "我的成绩有 1 条" "$(api GET '/api/scores/mine?page=1&size=10' | py "d['data']['total']")" "1"
check "成绩明细可看（自己的）" "$(status GET "/api/scores/$PAPER/$STU_ID")" "200"
check "看别人的成绩 403" "$(status GET "/api/scores/$PAPER/2")" "403"
# 用种子数据里确实存在的一条成绩（试卷 1 / 考生 2），避免测到不存在的记录
check "管理员能看任何人的成绩" "$(status GET "/api/scores/$PAPER/$STU_ID" '' "$ADMIN")" "200"

echo "== 6. 清理"
check "撤销这份成绩" "$(status DELETE "/api/scores/$PAPER/$STU_ID" '' "$ADMIN")" "200"
check "我的成绩回到 0 条" "$(api GET '/api/scores/mine?page=1&size=10' | py "d['data']['total']")" "0"
check "考试中心又能进了" "$(status GET "/api/exams/$PAPER/questions")" "200"

echo
echo "结果: $PASS 通过, $FAIL 失败"
[ "$FAIL" -eq 0 ]
