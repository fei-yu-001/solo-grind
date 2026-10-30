# 生成实验报告 Word（python-docx）
# 用法: python scripts/gen-report.py [输出文件]
# 表结构从 sql/schema.sql 解析，代码节选从真实源文件读取，图从 docs/diagrams 读
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "智考刷题系统-实验报告.docx")

doc = Document()

def east_asia(run, font="宋体"):
    """给 run 设置中文字体，rPr/rFonts 可能还没创建，用 get_or_add 保证存在"""
    el = getattr(run, "_element", run)
    if not hasattr(el, "get_or_add_rPr"):
        el = el.element if hasattr(el, "element") else el
    rpr = el.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(fonts)
    fonts.set(qn("w:eastAsia"), font)
    return run



# ---------- 全局样式 ----------
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(10.5)
east_asia(normal.element, "宋体")
normal.paragraph_format.line_spacing = 1.4
normal.paragraph_format.space_after = Pt(4)

for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
    st = doc.styles[name]
    st.font.name = "Times New Roman"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0x1F, 0x2D, 0x3D)
    east_asia(st.element, "黑体")



def para(text, size=10.5, bold=False, align=None, space_after=4):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.font.name = "Times New Roman"
    east_asia(run, "宋体")
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def code(text, caption=None):
    if caption:
        c = doc.add_paragraph()
        r = c.add_run(caption)
        r.font.size = Pt(9)
        r.font.bold = True
        east_asia(r, "宋体")
        c.paragraph_format.space_after = Pt(2)
    for line in text.rstrip("\n").split("\n"):
        p = doc.add_paragraph()
        run = p.add_run(line if line.strip() else " ")
        run.font.name = "Consolas"
        east_asia(run, "Consolas")
        run.font.size = Pt(8)
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        pf.left_indent = Cm(0.4)


def picture(path, width_cm=15.5, caption=None):
    if not os.path.exists(path):
        para(f"[缺图: {os.path.basename(path)}]")
        return
    doc.add_picture(path, width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        p = doc.add_paragraph()
        r = p.add_run(caption)
        r.font.size = Pt(9)
        east_asia(r, "宋体")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)


def read(rel, limit=None):
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if limit:
        lines = text.split("\n")
        if len(lines) > limit:
            text = "\n".join(lines[:limit]) + "\n        // ...（其余略）"
    return text


# ---------- 封面 ----------
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("SpringBoot + MyBatis + Redis 前后端分离后台系统\n实验报告")
r.font.size = Pt(22)
r.font.bold = True
r.font.name = "Times New Roman"
east_asia(r, "黑体")
title.paragraph_format.space_before = Pt(80)
title.paragraph_format.space_after = Pt(30)

for line in ("选题：智考 · 刷题考试系统", "班级：软件工程 2402", "姓名：张智斐", "学号：42409210410"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = p.add_run(line)
    rr.font.size = Pt(14)
    east_asia(rr, "宋体")

doc.add_page_break()

# ---------- 一、实验基本信息 ----------
doc.add_heading("一、实验基本信息", level=1)

doc.add_heading("1.1 实验名称", level=2)
para("SpringBoot + MyBatis + Redis 前后端分离后台系统开发")

doc.add_heading("1.2 实验目的", level=2)
for t in (
    "掌握 Spring Boot 工程的搭建方式与分层结构，理解 Controller / Service / Mapper / Entity 的职责边界。",
    "掌握 MyBatis（本项目使用 MyBatis-Plus）的映射方式，能够编写 Mapper 接口与 XML 映射文件完成多表关联查询。",
    "掌握 MySQL 数据库设计与建表规范，能够设计满足一对一、一对多、多对多关系的表结构。",
    "掌握 Redis 在真实业务中的缓存用法，理解缓存穿透的成因与空值标记的解决思路。",
    "掌握 Vue 3 + Element Plus 开发管理后台页面，并与后端 RESTful 接口完成联调。",
):
    doc.add_paragraph(t, style="List Bullet")

doc.add_heading("1.3 实验环境", level=2)
env_rows = [
    ("操作系统", "Windows 11"),
    ("JDK", "Temurin 21.0.12"),
    ("构建工具", "Maven 3.9.16"),
    ("后端框架", "Spring Boot 3.2.5"),
    ("持久层", "MyBatis-Plus 3.5.9（含 mybatis-plus-jsqlparser 分页插件）"),
    ("数据库", "MySQL 8.0.46，字符集 utf8mb4"),
    ("缓存", "Redis 5.0.14"),
    ("前端", "Vue 3.5 + Vite 6 + Element Plus 2.9 + axios 1.7"),
    ("运行端口", "后端 8080，前端 5173"),
]
table = doc.add_table(rows=1, cols=2)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = table.rows[0].cells
hdr[0].text, hdr[1].text = "项目", "内容"
for k, v in env_rows:
    cells = table.add_row().cells
    cells[0].text, cells[1].text = k, v

doc.add_heading("1.4 实验内容", level=2)
para(
    "本项目把原有的「赛博进京赶考」刷题系统，按本课程要求的技术栈重构为 Spring Boot + MyBatis-Plus + MySQL + Redis + Vue 3 "
    "的前后端分离后台系统。系统面向第 17 届全国大学生市场调查与分析大赛的备考场景，题库沿用原系统的 185 道真题"
    "（本科组 85 道、专科组 100 道），提供题库管理、题目管理、试卷组卷、作答与成绩统计四类核心功能。"
)
para("系统共 9 张表、4 个核心功能模块、7 个 Controller，前端 6 个页面，后端 8080、前端 5173，本地一键启动。")

# ---------- 二、数据库设计 ----------
doc.add_page_break()
doc.add_heading("二、数据库设计", level=1)

doc.add_heading("2.1 E-R 图", level=2)
para("图 2-1 为系统 E-R 图（9 张表）。图中虚线为跨区域的一对多关系，实线为同区域关系，标注了 1:1、1:N、M:N 基数。")
picture(os.path.join(ROOT, "docs", "diagrams", "er.png"), 16.0, "图 2-1 智考刷题系统 E-R 图")

doc.add_heading("2.2 表结构说明", level=2)
para("建表脚本见 sql/schema.sql，以下字段说明由建表脚本中的 COMMENT 解析后整理。")

# 解析 schema.sql
with open(os.path.join(ROOT, "sql", "schema.sql"), encoding="utf-8") as f:
    schema = f.read()

blocks = re.findall(
    r"CREATE TABLE (\w+) \((.*?)\n\) ENGINE = InnoDB COMMENT '([^']*)';", schema, re.S
)
COL_RE = re.compile(r"^\s{4}(\w+)\s+([A-Za-z]+(?:\([^)]*\))?)(.*)$")
CMT_RE = re.compile(r"COMMENT '([^']*)'")

for idx, (name, body, comment) in enumerate(blocks, start=1):
    doc.add_heading(f"2.2.{idx} {name}（{comment}）", level=3)
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    head = t.rows[0].cells
    for i, txt in enumerate(("字段名", "类型", "约束", "说明")):
        head[i].text = txt
    for line in body.split("\n"):
        m = COL_RE.match(line)
        if not m:
            continue
        col, typ, rest = m.groups()
        if col.upper() in ("PRIMARY", "KEY", "UNIQUE", "CONSTRAINT", "INDEX"):
            continue
        cmt = CMT_RE.search(rest)
        constraint = CMT_RE.sub("", rest).strip()
        constraint = re.sub(r"\s+", " ", constraint).replace("AUTO_INCREMENT", "自增").strip().strip(",").strip()
        cells = t.add_row().cells
        cells[0].text = col
        cells[1].text = typ
        cells[2].text = constraint
        cells[3].text = cmt.group(1) if cmt else ""

doc.add_heading("2.3 表关系解析", level=2)
for t in (
    "一对一：sys_user ↔ user_profile。user_profile.user_id 上加了唯一约束 uk_profile_user，"
    "一个登录账号最多对应一条资料，物理上排除了重复数据的可能。",
    "一对多：question_bank → question（题库下多道题）、exam_paper → answer_record（一张卷子多条作答）、"
    "sys_user → answer_record（一个考生多条作答）。三处都用外键约束保证引用完整性。",
    "多对多：question ↔ tag 通过中间表 question_tag（联合主键），exam_paper ↔ question 通过中间表 exam_paper_question，"
    "后者额外带 seq 题序和 score 分值两个业务字段，因此不能简单地用两个外键拼成复合主键以外的方式建模。",
    "多表查询：题库分页带题目数、题目分页带题库名与标签、试卷分页带题库名与题数、成绩分页按试卷聚合、"
    "统计按题型与题库分组，均不是单表查询。",
):
    doc.add_paragraph(t, style="List Bullet")

# ---------- 三、系统架构设计 ----------
doc.add_page_break()
doc.add_heading("三、系统架构设计", level=1)

doc.add_heading("3.1 系统分层架构", level=2)
picture(os.path.join(ROOT, "docs", "diagrams", "architecture.png"), 16.0, "图 3-1 系统分层架构图")

doc.add_heading("3.2 各层职责", level=2)
layers = [
    ("表现层（Vue 3）", "六个页面 + axios 封装。request.js 统一携带 Bearer 令牌、拆解 {code,message,data} 信封、401 跳登录、错误弹提示，页面只关心业务数据。"),
    ("控制层（Controller）", "只做参数接收、权限入口、结果包装，返回 Result<T> 或 PageResult<VO>。Controller 里没有 SQL、没有业务判断。"),
    ("业务层（Service）", "事务控制、业务校验、判分、VO 组装、缓存读写、批量处理都在这一层，是本次实验的重点。"),
    ("数据访问层（Mapper + XML）", "MyBatis-Plus BaseMapper 提供单表基础 CRUD，复杂多表查询写在 resources/mapper/*.xml，使用 resultType/resultMap 显式映射。"),
    ("数据层（MySQL + Redis）", "MySQL 存业务数据；Redis 存登录令牌、题库字典、成绩排行榜。"),
]
for name, desc in layers:
    p = doc.add_paragraph()
    r1 = p.add_run(name + "：")
    r1.bold = True
    r1.font.size = Pt(10.5)
    east_asia(r1, "宋体")
    r2 = p.add_run(desc)
    r2.font.size = Pt(10.5)
    east_asia(r2, "宋体")

doc.add_heading("3.3 业务模块关系", level=2)
picture(os.path.join(ROOT, "docs", "diagrams", "modules.png"), 16.0, "图 3-2 业务模块关系图")
para(
    "四个核心功能分别对应一组 Entity / Mapper XML / Service / Controller。调用链严格单向："
    "Controller → Service → Mapper → XML → 数据库，反向不调用；Controller 不会直接引用 Mapper。"
)

# ---------- 四、详细实验过程 ----------
doc.add_page_break()
doc.add_heading("四、详细实验过程", level=1)

doc.add_heading("4.1 创建工程并配置依赖", level=2)
para("用 Maven 创建 Spring Boot 工程，引入 Web、Validation、MyBatis-Plus、MySQL 驱动、Redis、Lombok 等依赖。")
code(read("backend/pom.xml", limit=62), "代码 4-1 backend/pom.xml 依赖节选")
para(
    "踩坑记录：MyBatis-Plus 3.5.9 起把 jsqlparser 从主包里拆了出去，只引 mybatis-plus-spring-boot3-starter 会导致"
    "PaginationInnerInterceptor 找不到类，编译报「找不到符号」。必须额外引入 mybatis-plus-jsqlparser 同版本依赖。"
)

doc.add_heading("4.2 配置数据源与 Redis", level=2)
code(read("backend/src/main/resources/application.yml", limit=30), "代码 4-2 application.yml")

doc.add_heading("4.3 建库建表并导入数据", level=2)
para("执行 sql/schema.sql 建库建表，再执行 sql/data.sql 导入 185 道真题、10 个知识点标签、2 张试卷与历史作答。")
para(
    "踩坑记录：Windows 下 mysql 客户端默认按 GBK 发送数据，导入含中文的脚本会报 "
    "ERROR 1366 Incorrect string value。必须加 --default-character-set=utf8mb4。"
)
code(
    "mysql -uroot -p*** --default-character-set=utf8mb4 < sql/schema.sql\n"
    "mysql -uroot -p*** --default-character-set=utf8mb4 < sql/data.sql\n"
    "mysql -uroot -p*** zhikao -e \"select count(*) from question;\"   -- 185",
    "命令 4-1 建库与导入",
)

doc.add_heading("4.4 编写实体与 Mapper 映射", level=2)
para("实体与表一一对应，字段用驼峰命名，MyBatis-Plus 通过 map-underscore-to-camel-case 自动映射下划线列名。")
code(read("backend/src/main/java/com/ddyu/zhikao/entity/Question.java"), "代码 4-3 Question 实体")

doc.add_heading("4.5 多表查询写在 XML 里", level=2)
para(
    "题目分页需要带出题库名，并且支持按标签过滤、按借阅/作答情况统计。这里有两个要点："
    "一是分页 SQL 里不能出现一对多 join（会让结果按行翻倍，total 和页大小静默错位），"
    "二是标签过滤用 EXISTS 子查询而不是 join，标签数据再用第二次 IN 查询在 Service 里装配。"
)
code(read("backend/src/main/resources/mapper/QuestionMapper.xml", limit=46), "代码 4-4 QuestionMapper.xml 分页与条件查询")

doc.add_heading("4.6 实现 Service 层业务逻辑", level=2)
para(
    "Service 层承担了本次实验的全部复杂度要求。以交卷为例：先校验试卷状态与重复交卷，"
    "再按题型逐题判分（单选/判断严格相等，多选少选给一半分），最后批量写入作答记录，整个过程在一个事务里。"
)
code(read("backend/src/main/java/com/ddyu/zhikao/service/impl/AnswerServiceImpl.java", limit=78), "代码 4-5 AnswerServiceImpl 交卷与判分")

doc.add_heading("4.7 接入 Redis 缓存", level=2)
para(
    "题库字典是典型的读多写少数据，用 cache-aside 方式缓存：读的时候先查 Redis，命中直接返回；"
    "未命中回源数据库并写回缓存；查不到数据时写入 __EMPTY__ 空值标记并设置 60 秒过期，避免缓存穿透；"
    "题库增删改时主动删除缓存，保证一致性。"
)
code(read("backend/src/main/java/com/ddyu/zhikao/service/impl/BankServiceImpl.java"), "代码 4-6 BankServiceImpl 缓存与引用校验")

doc.add_heading("4.8 实现登录与令牌拦截", level=2)
para(
    "登录成功后生成 UUID 令牌，把管理员信息序列化成 JSON 存进 Redis（TTL 30 分钟），"
    "拦截器统一校验 Authorization 头，每次通过校验把 TTL 续期；登出直接删除 key。"
    "管理类接口只允许 role=ADMIN，考生调用返回 403。"
)
code(read("backend/src/main/java/com/ddyu/zhikao/config/TokenStore.java"), "代码 4-7 TokenStore 令牌缓存")

doc.add_heading("4.9 前端页面与联调", level=2)
para(
    "前端用 Vue 3 组合式 API + Element Plus，页面拆成六个视图，接口封装在 src/api 下，"
    "request.js 统一处理令牌、信封与异常。开发时通过 vite 代理把 /api 转发到 8080，避免跨域。"
)
code(read("frontend/src/api/request.js", limit=40), "代码 4-8 前端 axios 封装")

# ---------- 五、核心源代码 ----------
doc.add_page_break()
doc.add_heading("五、核心源代码", level=1)
para("以下为本项目的关键源码，按层收录，完整代码见提交的工程目录。")

doc.add_heading("5.1 Controller 层", level=2)
code(read("backend/src/main/java/com/ddyu/zhikao/controller/QuestionController.java"), "代码 5-1 QuestionController")

doc.add_heading("5.2 Service 接口与实现", level=2)
code(read("backend/src/main/java/com/ddyu/zhikao/service/QuestionService.java"), "代码 5-2 QuestionService 接口")
code(read("backend/src/main/java/com/ddyu/zhikao/service/impl/PaperServiceImpl.java", limit=120), "代码 5-3 PaperServiceImpl 组卷（事务 + 随机抽题）")

doc.add_heading("5.3 Mapper 接口与 XML", level=2)
code(read("backend/src/main/java/com/ddyu/zhikao/mapper/QuestionMapper.java"), "代码 5-4 QuestionMapper")
code(read("backend/src/main/resources/mapper/ScoreMapper.xml"), "代码 5-5 ScoreMapper.xml 成绩聚合与明细")

# ---------- 六、运行测试 ----------
doc.add_page_break()
doc.add_heading("六、运行测试过程", level=1)

doc.add_heading("6.1 启动系统", level=2)
code(
    "bash scripts/dev.sh\n"
    "== 1/4 检查 MySQL   库 zhikao 正常，题目 185 道\n"
    "== 2/4 检查 Redis   Redis 正常（PONG）\n"
    "== 3/4 启动后端     后端起来了\n"
    "== 4/4 启动前端     前端起来了",
    "命令 6-1 一键启动",
)
para("打开 http://127.0.0.1:5173，管理员 admin / admin123，考生 student01 / student123。")
picture(os.path.join(ROOT, "docs", "screenshots", "01-login.png"), 15.0, "图 6-1 登录页")

doc.add_heading("6.2 接口测试", level=2)
para(
    "用 curl 编写了自动化验收脚本 scripts/e2e-api.sh，覆盖 51 条断言；另有 scripts/e2e-extra.sh 覆盖 18 条"
    "缓存失效、判分细则、批量操作与权限断言。两者均全绿。"
)
code(
    "bash scripts/e2e-api.sh      -> 结果: 51 通过, 0 失败\n"
    "bash scripts/e2e-extra.sh    -> 结果: 18 通过, 0 失败",
    "命令 6-2 接口验收结果",
)
code(
    'curl -X POST http://127.0.0.1:8080/api/auth/login -H "content-type: application/json" \\\n'
    '     -d \'{"username":"admin","password":"admin123"}\'\n'
    '{"code":0,"message":"ok","data":{"token":"...","username":"admin","role":"ADMIN"}}\n\n'
    'curl -s http://127.0.0.1:8080/api/banks   # 不带令牌\n'
    '{"code":401,"message":"登录已失效，请重新登录","data":null}',
    "代码 6-1 登录接口与未授权访问",
)

doc.add_heading("6.3 管理页面", level=2)
picture(os.path.join(ROOT, "docs", "screenshots", "02-dashboard.png"), 15.5, "图 6-2 概览：题库数、题目数、平均分与题型分布")
picture(os.path.join(ROOT, "docs", "screenshots", "04-questions.png"), 15.5, "图 6-3 题目管理：条件查询、标签、分页（共 185 条）")
picture(os.path.join(ROOT, "docs", "screenshots", "05-papers.png"), 15.5, "图 6-4 试卷管理：题型配比、总分、状态")
picture(os.path.join(ROOT, "docs", "screenshots", "06-scores.png"), 15.5, "图 6-5 成绩管理：得分、正确率、答对答错未答")

doc.add_heading("6.4 增删改查与组卷演示", level=2)
para(
    "组卷弹窗按题型填写数量与分值，实时计算总分，提交后后端随机抽题并在一个事务里写入试卷与试卷题目。"
    "自动化脚本用真实鼠标事件走完了「选题库 → 加题量 → 预览 6 题 7 分 → 生成 → 列表出现 → 删除」全流程。"
)
code(
    "[ok] 来源题库选成「市调大赛17届·本科组」\n"
    "题量与分值: [\"2\",\"1\",\"3\",\"1\",\"1\",\"2\",\"100\"]\n"
    "[ok] 预览算对了：6 题 7 分\n"
    "[ok] 组卷成功 2 -> 3\n"
    "[ok] 列表出现新试卷\n"
    "[ok] 测试试卷已删除",
    "命令 6-3 组卷端到端流程（scripts/ui-flow.mjs）",
)

doc.add_heading("6.5 多表查询效果", level=2)
code(
    "-- 成绩分页：answer_record join sys_user join exam_paper，按 paper+user 聚合\n"
    "SELECT ar.paper_id, p.title, ar.user_id, u.nickname, SUM(ar.score) total,\n"
    "       SUM(ar.correct = 1) correct, SUM(ar.chosen IS NULL) blank\n"
    "  FROM answer_record ar\n"
    "  JOIN exam_paper p ON p.id = ar.paper_id\n"
    "  JOIN sys_user u ON u.id = ar.user_id\n"
    " GROUP BY ar.paper_id, ar.user_id, p.title, u.nickname;",
    "代码 6-2 成绩聚合查询",
)
para("执行结果（节选）：李同学 61 分、答对 61 题、未答 5 题；王同学 46 分、答对 46 题、未答 5 题。")

doc.add_heading("6.6 Redis 缓存效果", level=2)
code(
    "redis-cli ttl login:token:<token>   -> 1800\n"
    "redis-cli exists dict:banks         -> 1（首次查询后写入）\n"
    "redis-cli exists cache:ranking:1    -> 1（排行榜缓存 300 秒）\n"
    "# 新增题库后\n"
    "redis-cli exists dict:banks         -> 0（主动失效）",
    "命令 6-4 缓存验证",
)
para("服务端日志同时打印命中情况：`[cache] 题库字典 命中` / `[cache] 题库字典 未命中，回源数据库`。")

doc.add_heading("6.7 异常处理", level=2)
code(
    'POST /api/answers/submit 同一考生重复交卷 -> 409 {"code":409,"message":"该考生已交过这份试卷"}\n'
    'DELETE /api/banks/1（题库下有题）        -> 409 {"code":409,"message":"题库下还有 85 道题目，不能删除"}\n'
    'PUT /api/papers/1（已发布试卷改组卷）    -> 409 {"code":409,"message":"只有草稿状态可以修改"}\n'
    'POST /api/banks（考生身份）             -> 403 {"code":403,"message":"只有管理员可以执行该操作"}\n'
    'GET /api/banks（无令牌）                -> 401 {"code":401,"message":"登录已失效，请重新登录"}',
    "代码 6-3 业务异常返回",
)

# ---------- 七、实验总结 ----------
doc.add_page_break()
doc.add_heading("七、实验总结", level=1)

doc.add_heading("7.1 收获", level=2)
for t in (
    "理解了分层架构真正的边界：先把「谁能调谁」写进契约，写代码时就不会出现 Controller 里塞 SQL 的情况。",
    "MyBatis 的 XML 映射比注解更适合多表查询，条件分支用 <if> 拼装清晰，配合 resultType 直接映射 VO 省掉了大量转换代码。",
    "Redis 缓存不是加个注解就完事，要考虑三件事：key 怎么设计、什么时候失效、缓存穿透怎么防。",
    "分页与一对多关联混用时会出现静默错误——页大小和 total 都会错，但不报错。必须在设计阶段就避开。",
    "前后端分离下，一份写清楚的接口契约能省掉大量联调返工。",
):
    doc.add_paragraph(t, style="List Bullet")

doc.add_heading("7.2 遇到的问题与解决", level=2)
problems = [
    ("MyBatis-Plus 分页插件找不到类", "3.5.9 起 jsqlparser 被拆包，需单独引入 mybatis-plus-jsqlparser。"),
    ("中文数据导入报 1366", "Windows 版 mysql 客户端默认 GBK，需显式指定 --default-character-set=utf8mb4。"),
    ("判断题答案格式不统一", "旧系统用 JSON 布尔存判断题答案，新系统统一成 A/B 字符串，读取时兼容布尔回落，避免出现带引号的 \"B\"。"),
    ("分页 join 一对多导致页错位", "分页只查主表行，关联数据用第二次 IN 查询在 Service 装配。"),
    ("curl 传中文请求体 500", "Windows 命令行按 GBK 编码参数，改为把请求体写进 UTF-8 临时文件再用 --data-binary 发送。"),
]
for q, a in problems:
    p = doc.add_paragraph()
    r1 = p.add_run(q + "：")
    r1.bold = True
    r1.font.size = Pt(10.5)
    east_asia(r1, "宋体")
    r2 = p.add_run(a)
    r2.font.size = Pt(10.5)
    east_asia(r2, "宋体")

doc.add_heading("7.3 不足与改进方向", level=2)
for t in (
    "考生端在线答题界面还没做，目前交卷能力只在接口层，管理后台看不到答题过程。",
    "题目的知识点标签是按题干关键词自动打的，不是人工标注，统计颗粒度有限。",
    "缓存只做了单机 Redis，没有做集群与持久化策略，生产环境还需要考虑缓存雪崩的随机过期。",
    "没有接入单元测试框架，目前依赖 curl 端到端脚本验证，后续应补 Service 层单元测试。",
):
    doc.add_paragraph(t, style="List Bullet")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print("已生成:", OUT)
