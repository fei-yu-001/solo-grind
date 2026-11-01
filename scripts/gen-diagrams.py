# 生成实验报告要用的三张图（SVG），再用无头 Chrome 转成 PNG
# 用法: python scripts/gen-diagrams.py docs/diagrams
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/diagrams"
os.makedirs(OUT, exist_ok=True)

FONT = "Microsoft YaHei, PingFang SC, sans-serif"

TABLES = {
    "sys_user": {
        "title": "sys_user 登录账号",
        "fields": ["PK id", "username 唯一", "password BCrypt", "nickname", "role ADMIN/STUDENT", "status"],
        "x": 40, "y": 60,
    },
    "user_profile": {
        "title": "user_profile 考生资料",
        "fields": ["PK id", "FK user_id 唯一", "school", "group_name", "phone", "avatar"],
        "x": 40, "y": 400,
    },
    "question_bank": {
        "title": "question_bank 题库",
        "fields": ["PK id", "name 唯一", "group_name", "description", "status"],
        "x": 430, "y": 60,
    },
    "question": {
        "title": "question 题目",
        "fields": ["PK id", "FK bank_id", "type single/multi/judge", "stem 题干", "options JSON", "answer JSON", "difficulty"],
        "x": 430, "y": 400,
    },
    "tag": {
        "title": "tag 知识点",
        "fields": ["PK id", "name 唯一", "color"],
        "x": 430, "y": 780,
    },
    "question_tag": {
        "title": "question_tag 题目标签",
        "fields": ["PK,FK question_id", "PK,FK tag_id"],
        "x": 800, "y": 780,
    },
    "exam_paper": {
        "title": "exam_paper 试卷",
        "fields": ["PK id", "title", "FK bank_id", "judge/single/multi_count", "total_score", "status"],
        "x": 800, "y": 60,
    },
    "exam_paper_question": {
        "title": "exam_paper_question 试卷题目",
        "fields": ["PK,FK paper_id", "PK,FK question_id", "seq 题序", "score 分值"],
        "x": 800, "y": 400,
    },
    "answer_record": {
        "title": "answer_record 作答记录",
        "fields": ["PK id", "FK paper_id", "FK user_id", "FK question_id", "chosen JSON", "correct / score", "submitted_at"],
        "x": 1180, "y": 400,
    },
}

W, H = 320, 0


def box(name):
    t = TABLES[name]
    width = W
    height = 46 + len(t["fields"]) * 26 + 12
    x, y = t["x"], t["y"]
    parts = [
        f'<g><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" fill="#ffffff" stroke="#409eff" stroke-width="2"/>',
        f'<rect x="{x}" y="{y}" width="{width}" height="40" rx="10" fill="#409eff"/>',
        f'<rect x="{x}" y="{y + 28}" width="{width}" height="12" fill="#409eff"/>',
        f'<text x="{x + 14}" y="{y + 26}" font-family="{FONT}" font-size="17" fill="#ffffff" font-weight="600">{t["title"]}</text>',
    ]
    for i, f in enumerate(t["fields"]):
        weight = "600" if f.startswith("PK") or f.startswith("FK") else "400"
        color = "#c0392b" if f.startswith("PK") else ("#1677ff" if f.startswith("FK") else "#303133")
        parts.append(
            f'<text x="{x + 14}" y="{y + 66 + i * 26}" font-family="{FONT}" font-size="15" fill="{color}" font-weight="{weight}">{f}</text>'
        )
    parts.append("</g>")
    return "\n".join(parts), height


def anchor(name, side):
    t = TABLES[name]
    _, h = box(name)
    if side == "right":
        return t["x"] + W, t["y"] + h / 2
    if side == "left":
        return t["x"], t["y"] + h / 2
    if side == "top":
        return t["x"] + W / 2, t["y"]
    return t["x"] + W / 2, t["y"] + h


def link(p1, p2, label, mid=None):
    """折线连接：先水平再垂直再水平"""
    x1, y1 = p1
    x2, y2 = p2
    mx = mid if mid is not None else (x1 + x2) / 2
    d = f"M {x1} {y1} L {mx} {y1} L {mx} {y2} L {x2} {y2}"
    lx, ly = mx + 8, (y1 + y2) / 2
    return (
        f'<path d="{d}" fill="none" stroke="#909399" stroke-width="2"/>'
        f'<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="14" fill="#606266">{label}</text>'
    )


boxes = "\n".join(box(n)[0] for n in TABLES)

# 先算出各表高度，图高按最低点定
lowest = max(TABLES[n]["y"] + box(n)[1] for n in TABLES)
height = lowest + 60
width = 1560

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    f'<rect width="{width}" height="{height}" fill="#fafafa"/>',
    f'<text x="40" y="34" font-family="{FONT}" font-size="22" font-weight="700" fill="#303133">赛博进京赶考系统 E-R 图（9 张表，含一对一 / 一对多 / 多对多）</text>',
    boxes,
]

# 一对一：sys_user -> user_profile
svg.append(link(anchor("sys_user", "bottom"), anchor("user_profile", "top"), "1 : 1", mid=TABLES["sys_user"]["x"] + 60))
# 一对多：question_bank -> question
svg.append(link(anchor("question_bank", "bottom"), anchor("question", "top"), "1 : N", mid=TABLES["question_bank"]["x"] + 60))
# 多对多：question <-> tag 经 question_tag
svg.append(link(anchor("question", "bottom"), anchor("question_tag", "top"), "1 : N", mid=TABLES["question"]["x"] + 250))
svg.append(link(anchor("tag", "right"), anchor("question_tag", "left"), "", mid=TABLES["tag"]["x"] + W + 30))
# 多对多：exam_paper <-> question 经 exam_paper_question
svg.append(link(anchor("exam_paper", "bottom"), anchor("exam_paper_question", "top"), "1 : N", mid=TABLES["exam_paper"]["x"] + 60))
svg.append(link(anchor("question", "right"), anchor("exam_paper_question", "left"), "N : 1", mid=TABLES["question"]["x"] + W + 20))
# 一对多：exam_paper -> answer_record，sys_user -> answer_record
svg.append(
    f'<path d="M {TABLES["exam_paper"]["x"] + W} {TABLES["exam_paper"]["y"] + 60} '
    f'L {TABLES["answer_record"]["x"] - 20} {TABLES["exam_paper"]["y"] + 60} '
    f'L {TABLES["answer_record"]["x"] - 20} {TABLES["answer_record"]["y"] + 120} '
    f'L {TABLES["answer_record"]["x"]} {TABLES["answer_record"]["y"] + 120}" '
    f'fill="none" stroke="#909399" stroke-width="2"/>'
    f'<text x="{TABLES["answer_record"]["x"] - 90}" y="{TABLES["exam_paper"]["y"] + 52}" font-family="{FONT}" font-size="14" fill="#606266">1 : N</text>'
)
# 一对多：sys_user -> answer_record，绕左下角走，避免穿过中间的框
su = TABLES["sys_user"]; ar = TABLES["answer_record"]
_, su_h = box("sys_user")
_, ar_h = box("answer_record")
svg.append(
    f'<path d="M {su["x"]} {su["y"] + su_h / 2} L 20 {su["y"] + su_h / 2} L 20 {height - 30} '
    f'L {ar["x"] + W / 2} {height - 30} L {ar["x"] + W / 2} {ar["y"] + ar_h}" '
    f'fill="none" stroke="#909399" stroke-width="2" stroke-dasharray="6 4"/>'
    f'<text x="{ar["x"] + W / 2 + 10}" y="{height - 38}" font-family="{FONT}" font-size="14" fill="#606266">1 : N（账号 → 作答记录）</text>'
)
# 题库 -> 试卷
svg.append(
    f'<path d="M {TABLES["question_bank"]["x"] + W} {TABLES["question_bank"]["y"] + 80} '
    f'L {TABLES["exam_paper"]["x"]} {TABLES["question_bank"]["y"] + 80}" '
    f'fill="none" stroke="#909399" stroke-width="2"/>'
    f'<text x="{TABLES["question_bank"]["x"] + W + 20}" y="{TABLES["question_bank"]["y"] + 72}" font-family="{FONT}" font-size="14" fill="#606266">1 : N</text>'
)

svg.append("</svg>")
open(os.path.join(OUT, "er.svg"), "w", encoding="utf-8").write("\n".join(svg))

# ---------- 分层架构图 ----------
layers = [
    ("表现层 Vue 3 + Element Plus（5173）", "登录 / 概览 / 题库 / 题目 / 试卷 / 成绩 六个页面，axios 统一带 token", "#e6f4ff", "#1677ff"),
    ("控制层 Controller（8080）", "AuthController / BankController / QuestionController / PaperController / AnswerController / ScoreController / TagController，只收参数、包 Result，不写业务", "#f6ffed", "#389e0d"),
    ("业务层 Service", "事务（组卷 / 交卷 / 批量移动）、业务校验（状态流转 / 引用校验 / 权限）、VO 组装、缓存读写、判分逻辑", "#fff7e6", "#d46b08"),
    ("数据访问层 Mapper + XML", "MyBatis-Plus BaseMapper + 7 个映射 XML，多表 join、分页、聚合统计都写在这里", "#f9f0ff", "#722ed1"),
    ("数据层 MySQL 8 / Redis 5", "zhikao 库 9 张表；Redis 存登录令牌、题库字典、成绩排行", "#fff1f0", "#cf1322"),
]
aw, ah = 1500, 0
blocks = []
y = 80
for title, desc, bg, border in layers:
    blocks.append(
        f'<rect x="50" y="{y}" width="{aw - 100}" height="120" rx="12" fill="{bg}" stroke="{border}" stroke-width="2"/>'
        f'<text x="80" y="{y + 44}" font-family="{FONT}" font-size="22" font-weight="700" fill="{border}">{title}</text>'
        f'<text x="80" y="{y + 82}" font-family="{FONT}" font-size="16" fill="#303133">{desc}</text>'
    )
    y += 150
ah = y + 10
arrows = []
for i in range(len(layers) - 1):
    y1 = 80 + i * 150 + 120
    arrows.append(
        f'<path d="M {aw / 2} {y1} L {aw / 2} {y1 + 30}" stroke="#909399" stroke-width="2" marker-end="url(#a)"/>'
    )
arch = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{aw}" height="{ah}" viewBox="0 0 {aw} {ah}">',
    '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#909399"/></marker></defs>',
    f'<rect width="{aw}" height="{ah}" fill="#fafafa"/>',
    f'<text x="50" y="46" font-family="{FONT}" font-size="24" font-weight="700" fill="#303133">系统分层架构（上层只依赖下一层，禁止跨层调用）</text>',
    "\n".join(blocks),
    "\n".join(arrows),
    "</svg>",
]
open(os.path.join(OUT, "architecture.svg"), "w", encoding="utf-8").write("\n".join(arch))

# ---------- 业务模块关系图 ----------
mods = [
    ("题库管理", "QuestionBank", "BankMapper.xml", "BankService", "BankController"),
    ("题目管理", "Question / QuestionTag", "QuestionMapper.xml", "QuestionService", "QuestionController"),
    ("试卷管理", "ExamPaper / ExamPaperQuestion", "PaperMapper.xml", "PaperService", "PaperController"),
    ("作答与成绩", "AnswerRecord", "ScoreMapper.xml", "AnswerService / ScoreService", "AnswerController / ScoreController"),
]
rows = []
y = 110
for name, entity, xml, svc, ctrl in mods:
    rows.append(
        f'<text x="50" y="{y + 40}" font-family="{FONT}" font-size="18" font-weight="700" fill="#303133">{name}</text>'
        f'<rect x="190" y="{y}" width="300" height="56" rx="10" fill="#e6f4ff" stroke="#1677ff"/>'
        f'<text x="205" y="{y + 34}" font-family="{FONT}" font-size="15" fill="#0958d9">{entity}</text>'
        f'<rect x="530" y="{y}" width="250" height="56" rx="10" fill="#f9f0ff" stroke="#722ed1"/>'
        f'<text x="545" y="{y + 34}" font-family="{FONT}" font-size="15" fill="#531dab">{xml}</text>'
        f'<rect x="820" y="{y}" width="280" height="56" rx="10" fill="#fff7e6" stroke="#d46b08"/>'
        f'<text x="835" y="{y + 34}" font-family="{FONT}" font-size="15" fill="#ad4e00">{svc}</text>'
        f'<rect x="1140" y="{y}" width="300" height="56" rx="10" fill="#f6ffed" stroke="#389e0d"/>'
        f'<text x="1155" y="{y + 34}" font-family="{FONT}" font-size="15" fill="#237804">{ctrl}</text>'
        f'<path d="M 490 {y + 28} L 530 {y + 28}" stroke="#909399" stroke-width="2" marker-end="url(#b)"/>'
        f'<path d="M 780 {y + 28} L 820 {y + 28}" stroke="#909399" stroke-width="2" marker-end="url(#b)"/>'
        f'<path d="M 1100 {y + 28} L 1140 {y + 28}" stroke="#909399" stroke-width="2" marker-end="url(#b)"/>'
    )
    y += 80
mw, mh = 1500, y + 40
modules = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{mw}" height="{mh}" viewBox="0 0 {mw} {mh}">',
    '<defs><marker id="b" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#909399"/></marker></defs>',
    f'<rect width="{mw}" height="{mh}" fill="#fafafa"/>',
    f'<text x="50" y="46" font-family="{FONT}" font-size="24" font-weight="700" fill="#303133">业务模块关系：Entity → Mapper/XML → Service → Controller</text>',
    f'<text x="190" y="88" font-family="{FONT}" font-size="15" fill="#606266">实体</text>',
    f'<text x="530" y="88" font-family="{FONT}" font-size="15" fill="#606266">映射 XML</text>',
    f'<text x="820" y="88" font-family="{FONT}" font-size="15" fill="#606266">业务实现</text>',
    f'<text x="1140" y="88" font-family="{FONT}" font-size="15" fill="#606266">对外接口</text>',
    "\n".join(rows),
    "</svg>",
]
open(os.path.join(OUT, "modules.svg"), "w", encoding="utf-8").write("\n".join(modules))

print("已生成:", ", ".join(sorted(os.listdir(OUT))))
