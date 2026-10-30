# 从旧系统导出的题目 JSON 生成 data.sql
# 用法: python scripts/gen-data.py /tmp/grind-export.json sql/data.sql
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
data = json.load(open(src, encoding="utf-8"))

TAGS = [
    ("描述统计", "#409eff"),
    ("概率分布", "#67c23a"),
    ("抽样方法", "#e6a23c"),
    ("问卷设计", "#f56c6c"),
    ("假设检验", "#909399"),
    ("回归分析", "#9254de"),
    ("多元统计", "#13c2c2"),
    ("时间序列", "#eb2f96"),
    ("信度与效度", "#fa8c16"),
    ("市场营销", "#2f54eb"),
]

RULES = [
    ("抽样方法", ["抽样", "样本量", "抽样框", "简单随机", "分层", "整群"]),
    ("问卷设计", ["问卷", "量表", "李克特", "访问", "访谈", "调查方法"]),
    ("假设检验", ["假设检验", "显著性", "原假设", "备择假设", "拒绝域", "t 检验", "t检验", "z 检验"]),
    ("回归分析", ["回归", "自变量", "因变量", "决定系数", "R2", "R²"]),
    ("多元统计", ["聚类", "因子", "主成分", "判别", "对应分析", "多维"]),
    ("时间序列", ["时间序列", "季节", "趋势", "移动平均", "指数平滑"]),
    ("信度与效度", ["信度", "效度", "一致性", "Cronbach"]),
    ("概率分布", ["概率", "正态", "二项", "泊松", "分布", "期望", "方差"]),
    ("描述统计", ["均值", "中位数", "众数", "标准差", "频数", "集中趋势", "离散程度", "四分位"]),
    ("市场营销", ["市场", "营销", "消费者", "品牌", "价格", "渠道", "促销"]),
]


def pick_tags(stem):
    hit = []
    for name, words in RULES:
        if any(w in stem for w in words):
            hit.append(name)
    return hit[:2]


def q(s):
    """SQL 字符串字面量：单引号翻倍"""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"


banks = data["banks"]
questions = data["questions"]
bank_index = {b["id"]: i + 1 for i, b in enumerate(banks)}

out = []
out.append("-- 智考 · 刷题考试系统 · 测试数据")
out.append("-- 由 scripts/gen-data.py 从旧系统导出的 185 道真题生成，不要手改")
out.append("USE zhikao;")
out.append("")
out.append("-- 账号：admin/admin123，三个考生 student123")
out.append(
    "INSERT INTO sys_user (id, username, password, nickname, role) VALUES\n"
    "  (1, 'admin', '$2a$10$/CywyXxCkNIJtGyivXAZk./r2KJ5Y9SseePayKjDa4QmMPQEA6aTW', '张老师', 'ADMIN'),\n"
    "  (2, 'student01', '$2a$10$zCqAe/q.jifliHwc3SYUsOq6ElpLJA73W5l55U16vMjZ/tZYRY8Pu', '李同学', 'STUDENT'),\n"
    "  (3, 'student02', '$2a$10$zCqAe/q.jifliHwc3SYUsOq6ElpLJA73W5l55U16vMjZ/tZYRY8Pu', '王同学', 'STUDENT'),\n"
    "  (4, 'student03', '$2a$10$zCqAe/q.jifliHwc3SYUsOq6ElpLJA73W5l55U16vMjZ/tZYRY8Pu', '陈同学', 'STUDENT');"
)
out.append("")
out.append(
    "INSERT INTO user_profile (user_id, school, group_name, phone) VALUES\n"
    "  (1, NULL, NULL, NULL),\n"
    "  (2, '南京信息工程大学', '本科组', '13800000001'),\n"
    "  (3, '南京信息工程大学', '本科组', '13800000002'),\n"
    "  (4, '南京工业职业技术大学', '专科组', '13800000003');"
)
out.append("")

rows = []
for b in banks:
    rows.append(
        f"  ({bank_index[b['id']]}, {q(b['name'])}, {q('本科组' if '本科' in b['name'] else '专科组')}, "
        f"{q(b.get('description') or '第17届全国大学生市场调查与分析大赛模拟题')}, 'ENABLED')"
    )
out.append("INSERT INTO question_bank (id, name, group_name, description, status) VALUES\n" + ",\n".join(rows) + ";")
out.append("")

tag_rows = ",\n".join(f"  ({i + 1}, {q(n)}, {q(c)})" for i, (n, c) in enumerate(TAGS))
out.append("INSERT INTO tag (id, name, color) VALUES\n" + tag_rows + ";")
out.append("")

tag_id = {n: i + 1 for i, (n, _) in enumerate(TAGS)}
type_cn = {"single": "单选题", "multi": "多选题", "judge": "判断题"}

qrows, link_rows = [], []
for i, item in enumerate(questions, start=1):
    options = item["options"]
    options_sql = "NULL" if not options or options == "[]" else q(options)
    answer = item["answer"]
    if isinstance(answer, str):
        try:
            parsed = json.loads(answer)
        except json.JSONDecodeError:
            parsed = answer
        answer = parsed
    answer_sql = q(json.dumps(answer, ensure_ascii=False))
    qrows.append(
        f"  ({i}, {bank_index[item['bank_id']]}, {q(item['type'])}, {q(item['stem'])}, "
        f"{options_sql}, {answer_sql}, {q(item.get('analysis'))}, 1, {int(item['ext_id'] or i)})"
    )
    for name in pick_tags(item["stem"]):
        link_rows.append(f"  ({i}, {tag_id[name]})")

out.append("-- 185 道真题，题型：single 单选 / multi 多选 / judge 判断")
out.append(
    "INSERT INTO question (id, bank_id, type, stem, options, answer, analysis, difficulty, sort_no) VALUES\n"
    + ",\n".join(qrows)
    + ";"
)
out.append("")
out.append("INSERT INTO question_tag (question_id, tag_id) VALUES\n" + ",\n".join(link_rows) + ";")
out.append("")

# 试卷：本科组全真模考（11 判断 + 59 单选 + 15 多选，满分 100）
by_type = {}
for i, item in enumerate(questions, start=1):
    by_type.setdefault((bank_index[item["bank_id"]], item["type"]), []).append(i)

paper_plan = [
    (1, "第17届市调大赛·本科组全真模考", 1, {"judge": 11, "single": 59, "multi": 15}, 1, 1, 2, 6000),
    (2, "第17届市调大赛·专科组全真模考", 2, {"judge": 24, "single": 76, "multi": 0}, 1, 1, 2, 5400),
]
prows, pqrows = [], []
for pid, title, bank_id, plan, js, ss, ms, dur in paper_plan:
    total = plan["judge"] * js + plan["single"] * ss + plan["multi"] * ms
    prows.append(
        f"  ({pid}, {q(title)}, {bank_id}, {plan['judge']}, {plan['single']}, {plan['multi']}, "
        f"{js}, {ss}, {ms}, {dur}, {total}, 'PUBLISHED', 1)"
    )
    seq = 0
    for t in ("judge", "single", "multi"):
        score = {"judge": js, "single": ss, "multi": ms}[t]
        pool = by_type.get((bank_id, t), [])
        n = min(plan[t], len(pool))
        for qid in pool[:n]:
            seq += 1
            pqrows.append(f"  ({pid}, {qid}, {seq}, {score})")

out.append("INSERT INTO exam_paper (id, title, bank_id, judge_count, single_count, multi_count, judge_score, single_score, multi_score, duration_sec, total_score, status, created_by) VALUES\n" + ",\n".join(prows) + ";")
out.append("")
out.append("INSERT INTO exam_paper_question (paper_id, question_id, seq, score) VALUES\n" + ",\n".join(pqrows) + ";")
out.append("")

# 作答记录：两位考生交过本科组卷子
paper1 = [(int(r.split(",")[1]), int(r.split(",")[3].strip(" )"))) for r in pqrows if r.strip().startswith("(1,")]
arows = []
rid = 0
for user_id, ratio in ((2, 0.72), (3, 0.55)):
    hit = int(len(paper1) * ratio)
    for idx, (qid, score) in enumerate(paper1):
        rid += 1
        correct = 1 if idx < hit else 0
        got = score if correct else 0
        arows.append(
            f"  ({rid}, 1, {user_id}, {qid}, NULL, {correct}, {got}, '2026-10-28 10:00:00')"
        )

out.append("-- 两位考生已完成本科组模考，用于成绩列表和统计的演示数据")
out.append(
    "INSERT INTO answer_record (id, paper_id, user_id, question_id, chosen, correct, score, submitted_at) VALUES\n"
    + ",\n".join(arows)
    + ";"
)

open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("题目", len(questions), "题目标签", len(link_rows), "试卷题目", len(pqrows), "作答记录", len(arows))
print("题库", len(banks), "标签", len(TAGS), "试卷", len(paper_plan))
