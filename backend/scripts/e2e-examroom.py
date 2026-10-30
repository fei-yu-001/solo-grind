# -*- coding: utf-8 -*-
# 验收：考生在线答题接口（契约 4.8）+ 成绩明细权限
import json
import urllib.request

BASE = "http://127.0.0.1:8080"
PASS = []
FAIL = []


def call(method, path, body=None, token=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("content-type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    try:
        with urllib.request.urlopen(req, data) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, None


def check(name, actual, expect):
    (PASS if actual == expect else FAIL).append(name)
    print(("  [ok]   " if actual == expect else "  [FAIL] ") + name)


def login(u, p):
    _, d = call("POST", "/api/auth/login", {"username": u, "password": p})
    return d["data"]["token"]


def walk_no_leak(node):
    """递归检查 JSON 里没有 answer / analysis 键"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("answer", "analysis"):
                return False
            if not walk_no_leak(v):
                return False
    elif isinstance(node, list):
        return all(walk_no_leak(x) for x in node)
    return True


s3 = login("student03", "student123")
s1 = login("student01", "student123")
admin = login("admin", "admin123")

# 1. 考试中心：student03 没交过任何卷子
code, d = call("GET", "/api/exams/available", None, s3)
cards = d["data"]
check("available 200 且 2 张卷子", (code, len(cards)), (200, 2))
check("按 id 倒序", [c["paperId"] for c in cards] == sorted([c["paperId"] for c in cards], reverse=True), True)
check("myScore 都是 null", all(c["myScore"] is None for c in cards), True)
check("mySubmittedAt 都是 null", all(c["mySubmittedAt"] is None for c in cards), True)
check("卡片字段齐全", all(
    set(c) == {"paperId", "title", "bankName", "questionCount", "totalScore", "durationSec",
               "myScore", "mySubmittedAt"} and c["questionCount"] in (85, 100) and c["totalScore"] == 100
    for c in cards), True)

# 2. 进考场 paper 1：85 题、逐条无 answer/analysis、按 seq 排
code, d = call("GET", "/api/exams/1/questions", None, s3)
view = d["data"]
qs = view["questions"]
check("exam view 200 且 85 题", (code, len(qs)), (200, 85))
check("questionCount=85", view["questionCount"], 85)
check("seq 从 1 连续到 85", [q["seq"] for q in qs] == list(range(1, 86)), True)
check("整棵 JSON 无 answer/analysis", walk_no_leak(view), True)
check("题目字段只含 seq/questionId/type/typeText/stem/options/score",
      all(set(q) == {"seq", "questionId", "type", "typeText", "stem", "options", "score"} for q in qs), True)
check("题型分布 判断11/单选59/多选15",
      ([q["type"] for q in qs].count("judge"),
       [q["type"] for q in qs].count("single"),
       [q["type"] for q in qs].count("multi")) == (11, 59, 15), True)

code, d = call("GET", "/api/exams/2/questions", None, s3)
check("paper2 100 题", len(d["data"]["questions"]), 100)
check("paper2 无 answer/analysis", walk_no_leak(d["data"]), True)

# 3. 交卷 3 道（前 3 题判断题，按返回 typeText 用作答里没有的答案字段交卷：
#    这里故意乱答，重点是有分且状态变化）
body = {"paperId": 1, "answers": [{"questionId": qs[0]["questionId"], "chosen": "A"},
                                  {"questionId": qs[1]["questionId"], "chosen": "B"},
                                  {"questionId": qs[2]["questionId"], "chosen": "A"}]}
code, d = call("POST", "/api/answers/submit", body, s3)
check("交卷 200", code, 200)
check("questionCount=85（全卷落库）", d["data"]["questionCount"], 85)
score_val = d["data"]["totalScore"]
check("totalScore >= 0", score_val >= 0, True)

# 4. 交卷后状态
code, d = call("GET", "/api/exams/available", None, s3)
card1 = [c for c in d["data"] if c["paperId"] == 1][0]
card2 = [c for c in d["data"] if c["paperId"] == 2][0]
check("card1 myScore=%d" % score_val, card1["myScore"], score_val)
check("card1 mySubmittedAt 非空", card1["mySubmittedAt"] is not None, True)
check("card2 myScore 仍为 null", card2["myScore"] is None, True)

code, d = call("GET", "/api/exams/1/questions", None, s3)
check("已交卷再进考场 409", code, 409)
check("409 文案", d["message"], "你已经交过这份试卷了")

# 5. scores/mine
code, d = call("GET", "/api/scores/mine?page=1&size=10", None, s3)
rows = d["data"]["records"]
check("mine 200 且 1 条", (code, d["data"]["total"]), (200, 1))
check("mine 是自己的（userId=4）", rows[0]["userId"], 4)
check("mine totalScore 与交卷一致", rows[0]["totalScore"], score_val)

# 6. 明细权限
code, _ = call("GET", "/api/scores/1/2", None, s3)     # student03 看 student01（user 2）的成绩
check("考生查别人明细 403", code, 403)
code, d = call("GET", "/api/scores/1/4", None, s3)     # 看自己的
check("考生查自己明细 200", code, 200)
code, d = call("GET", "/api/scores/1/2", None, admin)  # admin 查别人的
check("admin 查别人明细 200", code, 200)

# 7. 清理：撤销 student03 的成绩，恢复 170 条
code, _ = call("DELETE", "/api/scores/1/4", None, admin)
check("admin 撤销 student03 成绩 200", code, 200)
code, d = call("GET", "/api/scores/mine?page=1&size=10", None, s3)
check("清理后 mine total=0", d["data"]["total"], 0)
code, d = call("GET", "/api/exams/available", None, s3)
check("清理后 available myScore 恢复 null", all(c["myScore"] is None for c in d["data"]), True)

print("结果: %d 通过, %d 失败" % (len(PASS), len(FAIL)))
raise SystemExit(1 if FAIL else 0)
