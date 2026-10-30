# -*- coding: utf-8 -*-
# 补测：多选半分判分、重复交卷 409、撤销成绩后成绩清空
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
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def check(name, actual, expect):
    (PASS if actual == expect else FAIL).append(name)
    print(("  [ok]   " if actual == expect else "  [FAIL] ") + name + "（期望 %s，实际 %s）" % (expect, actual))


def login(u, p):
    _, d = call("POST", "/api/auth/login", {"username": u, "password": p})
    return d["data"]["token"]


admin = login("admin", "admin123")
stu = login("student02", "student123")

# 1. 组卷：1 单选(1分) + 2 多选(2分)，发布
_, d = call("POST", "/api/papers", {"title": "补测判分卷", "bankId": 1, "judgeCount": 0, "singleCount": 1,
                                    "multiCount": 2, "judgeScore": 1, "singleScore": 1, "multiScore": 2,
                                    "durationSec": 600}, admin)
pid = d["data"]["id"]
call("POST", "/api/papers/%d/publish" % pid, None, admin)
_, d = call("GET", "/api/papers/%d" % pid, None, admin)
qs = d["data"]["questions"]
single = qs[0]
multis = qs[1:3]

# 2. 交卷：单选答错、多选1全对、多选2少选 → 0 + 2 + 1 = 3 分
wrong_key = "C" if single["answer"] != "C" else "B"
body = {
    "paperId": pid,
    "answers": [
        {"questionId": single["id"], "chosen": wrong_key},
        {"questionId": multis[0]["id"], "chosen": multis[0]["answer"]},
        {"questionId": multis[1]["id"], "chosen": multis[1]["answer"][:1]},
    ],
}
_, d = call("POST", "/api/answers/submit", body, stu)
s = d["data"]
check("多选全对+少选半分：totalScore=0+2+1", s["totalScore"], 3)
check("correctCount=1（只有全对的多选）", s["correctCount"], 1)
check("wrongCount=2（单选错+多选少选不算对）", s["wrongCount"], 2)
check("blankCount=0", s["blankCount"], 0)
check("questionCount=3", s["questionCount"], 3)

# 3. 同一考生同卷再交 409
code, _ = call("POST", "/api/answers/submit", body, stu)
check("重复交卷 409", code, 409)

# 4. 撤销成绩 → 200，成绩列表空、明细 404
code, _ = call("DELETE", "/api/scores/%d/3" % pid, None, admin)
check("撤销成绩 200", code, 200)
_, d = call("GET", "/api/scores?paperId=%d" % pid, None, admin)
check("撤销后成绩列表 total=0", d["data"]["total"], 0)
code, _ = call("GET", "/api/scores/%d/3" % pid, None, admin)
check("撤销后明细 404", code, 404)
_, d = call("GET", "/api/scores/ranking?paperId=%d" % pid, None, admin)
check("撤销后排行榜为空数组", d["data"], [])

# 5. 清理
call("DELETE", "/api/papers/%d" % pid, None, admin)

print("结果: %d 通过, %d 失败" % (len(PASS), len(FAIL)))
raise SystemExit(1 if FAIL else 0)
