# -*- coding: utf-8 -*-
# 手工补验：判断题（字符串 "A"/"B" 存法）交卷判分
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


admin = login("admin", "admin123")
stu = login("student03", "student123")

# 组一张全判断卷：3 判断 x 1 分，发布
_, d = call("POST", "/api/papers", {"title": "JUDGE-FORMAT-CHECK", "bankId": 1, "judgeCount": 3,
                                    "singleCount": 0, "multiCount": 0, "judgeScore": 1,
                                    "singleScore": 1, "multiScore": 2, "durationSec": 600}, admin)
pid = d["data"]["id"]
check("组卷成功", d["code"], 0)
call("POST", "/api/papers/%d/publish" % pid, None, admin)
_, d = call("GET", "/api/papers/%d" % pid, None, admin)
qs = d["data"]["questions"]
check("试卷里判断题 answer 是干净字符串",
      all(isinstance(q["answer"], str) and q["answer"] in ("A", "B") for q in qs), True)

# 全对交卷
body = {"paperId": pid, "answers": [{"questionId": q["id"], "chosen": q["answer"]} for q in qs]}
code, d = call("POST", "/api/answers/submit", body, stu)
check("判断题字符串作答交卷不报 500", code, 200)
check("全对 totalScore=3", d["data"]["totalScore"], 3)
check("correctCount=3", d["data"]["correctCount"], 3)
check("blankCount=0", d["data"]["blankCount"], 0)

# 成绩明细里 answer/chosen 都应是干净字符串
_, d = call("GET", "/api/scores/%d/4" % pid, None, admin)
items = d["data"]["items"]
check("明细 answer 是干净字符串",
      all(isinstance(i["answer"], str) and i["answer"] in ("A", "B") for i in items), True)
check("明细 chosen 是干净字符串",
      all(isinstance(i["chosen"], str) and i["chosen"] in ("A", "B") for i in items), True)

# 撤销成绩，再交一次：1 对 2 错 -> 1 分（用反向答案）
call("DELETE", "/api/scores/%d/4" % pid, None, admin)
flip = {"A": "B", "B": "A"}
body2 = {"paperId": pid, "answers": [{"questionId": q["id"], "chosen": flip[q["answer"]]} for q in qs]}
body2["answers"][0]["chosen"] = qs[0]["answer"]  # 第一题答对
code, d = call("POST", "/api/answers/submit", body2, stu)
check("1 对 2 错 totalScore=1", d["data"]["totalScore"], 1)
check("correctCount=1", d["data"]["correctCount"], 1)

# 清理
call("DELETE", "/api/scores/%d/4" % pid, None, admin)
call("DELETE", "/api/papers/%d" % pid, None, admin)

print("结果: %d 通过, %d 失败" % (len(PASS), len(FAIL)))
raise SystemExit(1 if FAIL else 0)
