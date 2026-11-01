# -*- coding: utf-8 -*-
"""
生成《赛博进京赶考系统》实验报告 docx。

做法：直接打开第六次作业报告当模板，保留封面（校徽、学院班级姓名学号）和页面设置，
删掉旧正文，按模板的字体字号行距重新写。最后可用 Word 转 PDF 自检。
"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = r'C:\Users\DDyu\Desktop\springboot\第六次作业\第五组作业报告.docx'
OUT = os.path.join(ROOT, 'docs', '赛博进京赶考系统-实验报告.docx')
DIAG = os.path.join(ROOT, 'docs', 'diagrams')

BODY_FONT_CN = '宋体'
BODY_FONT_EN = 'Times New Roman'
HEAD_FONT_EN = 'Arial'
HEAD_FONT_CN = '黑体'
CODE_FONT = 'Consolas'


# ---------------------------------------------------------------- 基础排版

CJK = r'一-龥　-〿！-｠'
_TIGHT_LEFT = re.compile(r'(?<=[' + CJK + r'])[ 	　]+(?=[A-Za-z0-9/@#])')
_TIGHT_RIGHT = re.compile(r'(?<=[A-Za-z0-9/@#])[ 	　]+(?=[' + CJK + r'])')


def tight(text):
    """中文与英文/数字之间不留空格，英文单词内部空格保留"""
    if not text:
        return text
    text = str(text)
    m = re.match(r'^(\d+(?:\.\d+)*\.)[ 	]+', text)
    prefix = m.group(0) if m else ''
    body = text[len(prefix):]
    return prefix + _TIGHT_RIGHT.sub('', _TIGHT_LEFT.sub('', body))


def set_run(run, cn=BODY_FONT_CN, en=BODY_FONT_EN, size=12, bold=False, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:ascii'), en)
    rfonts.set(qn('w:hAnsi'), en)
    rfonts.set(qn('w:eastAsia'), cn)
    if color:
        run.font.color.rgb = color


def para(text='', size=12, bold=False, cn=BODY_FONT_CN, en=BODY_FONT_EN,
         align=None, indent=True, before=0, after=0, line=1.5, left=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if indent:
        pf.first_line_indent = Pt(size * 2)
    if left:
        pf.left_indent = Cm(left)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == 'right':
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if text:
        set_run(p.add_run(tight(text)), cn, en, size, bold)
    return p


def h1(text):
    p = para(text, size=16, bold=True, cn=HEAD_FONT_CN, en=HEAD_FONT_EN,
             indent=False, before=18, after=8, line=1.5)
    return p


def h2(text):
    return para(text, size=14, bold=True, cn=HEAD_FONT_CN, en=HEAD_FONT_EN,
                indent=False, before=10, after=4, line=1.5)


def h3(text):
    return para(text, size=12, bold=True, indent=False, before=6, after=2, line=1.5)


def bullet(text, size=12):
    return para(text, size=size, indent=False, left=0.74, after=0, line=1.5)


def shade(p, fill='F5F5F5'):
    ppr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    ppr.append(shd)


def code_block(text, size=9):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.0
    pf.left_indent = Cm(0.5)
    pf.right_indent = Cm(0.2)
    run = p.add_run()
    lines = text.rstrip('\n').split('\n')
    for i, line in enumerate(lines):
        if i:
            run.add_break()
        run.add_text(line.replace('\t', '    '))
    set_run(run, CODE_FONT, CODE_FONT, size)
    shade(p, 'F5F5F5')
    return p


def caption(text, before=2, after=10):
    return para(text, size=10.5, indent=False, align='center', before=before, after=after, line=1.2)


def figure(path, cap, width=14.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width))
    caption(cap)


def shot(text, cap, height=5.2, hint=''):
    """截图留白框：虚线 1x1 表格，替换成图片即可"""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    cell = t.cell(0, 0)
    cell.width = Cm(14.2)
    tr = t.rows[0]
    tr.height = Cm(height)
    tcpr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'dashed')
        el.set(qn('w:sz'), '6')
        el.set(qn('w:color'), '999999')
        borders.append(el)
    tcpr.append(borders)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell.paragraphs[0].paragraph_format.space_before = Pt(0)
    line1 = cell.paragraphs[0].add_run(tight(f'【此处插入截图：{text}】'))
    set_run(line1, BODY_FONT_CN, BODY_FONT_EN, 10.5, color=None)
    if hint:
        r2 = cell.paragraphs[0].add_run('\n' + hint)
        set_run(r2, BODY_FONT_CN, BODY_FONT_EN, 9)
    caption(cap)


def _cell_borders(cell, edge_specs):
    tcpr = cell._tc.get_or_add_tcPr()
    old = tcpr.find(qn('w:tcBorders'))
    if old is not None:
        tcpr.remove(old)
    borders = OxmlElement('w:tcBorders')
    for edge, spec in edge_specs.items():
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), spec[0])
        el.set(qn('w:sz'), str(spec[1]))
        el.set(qn('w:color'), '000000')
        borders.append(el)
    tcpr.append(borders)


def table(headers, rows, cap=None, widths=None, size=10.5):
    if cap:
        para(cap, size=10.5, indent=False, align='center', before=8, after=3, line=1.2)
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblpr = t._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'bottom'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '12')
        el.set(qn('w:color'), '000000')
        borders.append(el)
    for edge in ('left', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'none')
        el.set(qn('w:sz'), '0')
        el.set(qn('w:color'), 'auto')
        borders.append(el)
    tblpr.append(borders)

    hdr = t.rows[0]
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        set_run(p.add_run(tight(text)), size=size, bold=True)
        _cell_borders(cell, {'bottom': ('single', 6)})
    # 跨页时表头重复
    trpr = hdr._tr.get_or_add_trPr()
    th = OxmlElement('w:tblHeader')
    th.set(qn('w:val'), 'true')
    trpr.append(th)
    for row in rows:
        tr = t.add_row()
        for i, text in enumerate(row):
            cell = tr.cells[i]
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            set_run(p.add_run(tight(str(text))), size=size)
    # 固定布局 + 真实列宽，否则 Word 会按内容均分
    widths = widths or [14.2 / len(headers)] * len(headers)
    tblpr2 = t._tbl.tblPr
    tblw = OxmlElement('w:tblW')
    tblw.set(qn('w:w'), str(int(sum(widths) * 567)))
    tblw.set(qn('w:type'), 'dxa')
    tblpr2.append(tblw)
    layout = OxmlElement('w:tblLayout')
    layout.set(qn('w:type'), 'fixed')
    tblpr2.append(layout)
    mar = OxmlElement('w:tblCellMar')
    for edge, w in (('left', 85), ('right', 85), ('top', 20), ('bottom', 20)):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:w'), str(w))
        el.set(qn('w:type'), 'dxa')
        mar.append(el)
    tblpr2.append(mar)
    grid = t._tbl.find(qn('w:tblGrid'))
    for i, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[i] * 567)))
    for row in t.rows:
        for i, cell in enumerate(row.cells):
            cell.width = Cm(widths[i])
    para('', size=6, indent=False, after=0, line=1.0)
    return t


def read(rel, start=None, end=None, max_lines=None):
    path = os.path.join(ROOT, rel)
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    if start:
        for i, l in enumerate(lines):
            if start in l:
                lines = lines[i:]
                break
    if end:
        for i, l in enumerate(lines):
            if end in l:
                lines = lines[:i + 1]
                break
    if max_lines:
        lines = lines[:max_lines]
    return '\n'.join(lines)


# ---------------------------------------------------------------- 封面
doc = Document(TEMPLATE)
for p in doc.paragraphs[20:]:
    p._element.getparent().remove(p._element)
for t in list(doc.tables):
    t._element.getparent().remove(t._element)
for sec in doc.sections:
    sec.header_distance = Cm(1.5)
    sec.footer_distance = Cm(1.75)

# 作业名称
cover = doc.paragraphs[19]
for r in cover.runs:
    if '悬壶' in r.text:
        r.text = '赛博进京赶考系统'
    elif '药品' in r.text:
        r.text = ''

# ---------------------------------------------------------------- 一、基础信息
h1('一、基础信息')

h2('（一）实验名称')
para('赛博进京赶考系统 —— 基于 Spring Boot + MyBatis-Plus + Redis + Vue 3 的前后端分离刷题考试平台。')

h2('（二）实验目的')
para('本实验以 408 考研刷题为业务背景，完整走一遍前后端分离项目的开发流程，重点验证四件事：')
bullet('1. 用 Spring Boot 搭建标准四层结构（Entity → Mapper → Service → Controller），各层职责清晰、单向调用；')
bullet('2. 用 MyBatis-Plus 与 XML 映射完成单表 CRUD、多表关联查询、分页与动态条件查询；')
bullet('3. 用 Redis 承载登录令牌、基础字典与排行榜三类缓存，理解 cache-aside 与失效策略；')
bullet('4. 用 Vue 3 + Element Plus 完成管理端与考生端两套界面，理解路由守卫、请求拦截器与前后端联调。')

h2('（三）实验环境')
table(['类别', '项目', '版本 / 说明'], [
    ['硬件', '处理器', 'Intel Core i7'],
    ['硬件', '内存 / 硬盘', '16 GB / 512 GB SSD'],
    ['软件', '操作系统', 'Windows 11 64 位'],
    ['软件', 'JDK', 'OpenJDK 21.0.12 (Temurin)'],
    ['软件', '构建工具', 'Apache Maven 3.9.16'],
    ['软件', '数据库', 'MySQL 8.0.46'],
    ['软件', '缓存', 'Redis 5.0.14.1'],
    ['软件', 'Node.js', 'v24.19.0'],
    ['框架', 'Spring Boot', '3.2.5'],
    ['框架', 'MyBatis-Plus', '3.5.9'],
    ['框架', 'Vue', '3.5'],
    ['框架', 'Element Plus', '2.14'],
    ['框架', 'Vite', '6.4'],
    ['框架', 'axios', '1.21'],
    ['工具', '开发工具', 'IntelliJ IDEA / VS Code'],
    ['工具', '接口测试', 'Postman'],
], cap='表 1-1 实验环境', widths=[2.2, 4.5, 7.5])

h2('（四）实验内容')
para('系统分管理员与考生两种角色，共 10 个功能模块、38 个接口、9 张数据表。核心功能如下：')
table(['序号', '功能', '角色', '说明'], [
    ['1', '登录 / 注册 / 登出', '全部', 'BCrypt 校验，Redis 令牌 30 分钟滑动过期，考生可自助注册'],
    ['2', '个人资料', '全部', 'sys_user 与 user_profile 一对一，可改昵称、学校、组别、手机号'],
    ['3', '题库管理', '管理员', '增删改查、分页、按组别筛选，组别可选可自定义'],
    ['4', '题目管理', '管理员', '单选 / 多选 / 判断，支持 Word 批量导入与批量移动'],
    ['5', '试卷管理', '管理员', '按题型随机抽题组卷，草稿 / 发布 / 结束状态流转'],
    ['6', '考试中心', '考生', '查看可考试卷，进入考场，倒计时答题'],
    ['7', '在线答题', '考生', '答题卡、自动交卷、重复交卷拦截'],
    ['8', '交卷判分', '考生', '单选判断全对得分，多选少选得一半，未答计 0'],
    ['9', '成绩管理', '管理员', '多表聚合、排行榜、逐题明细、撤销成绩'],
    ['10', '我的成绩', '考生', '只能看自己的成绩与明细'],
], cap='表 1-2 功能清单', widths=[1.4, 3.4, 2.2, 7.2])

h2('（五）小组分工')
table(['成员', '角色', '主要工作'], [
    ['张曦', '数据库设计', 'E-R 图、9 张表结构、索引与外键、测试数据脚本'],
    ['张智斐', '后端开发', '分层骨架、认证与 Redis、判分与组卷、Word 导入'],
    ['段茗耀', '前端开发', '页面与路由、请求封装、考场交互、手绘风样式'],
    ['夏康迪', '文档与答辩', '实验报告、接口文档、演示脚本、答辩材料'],
], cap='表 1-3 小组分工', widths=[2.2, 3.0, 9.0])

# ---------------------------------------------------------------- 二、数据库设计
h1('二、数据库设计')

h2('（一）设计思路')
para('系统围绕“题库—试卷—作答”这条主线建模。题库是题目的来源，试卷从题库按题型抽题，考生作答后按题落库，成绩由作答记录聚合而来。围绕这条主线拆出 9 张表，覆盖一对一、一对多、多对多三种关系。')
para('设计时遵循三条原则：第一，账号与资料拆开，账号表只放登录必需的字段；第二，试卷与题目用关系表连接，同一道题可以进不同试卷且分值不同；第三，成绩不单独建表，避免成绩与作答明细两份数据对不上。')

h2('（二）E-R 图')
para('系统 E-R 图如下，共 9 张表，图中标注了主键、外键与三种关联关系。')
figure(os.path.join(DIAG, 'er.png'), '图 2-1 系统 E-R 图', width=14.6)

h2('（三）数据表结构')
para('下面逐表说明字段名、类型、约束与业务含义。所有表使用 InnoDB 引擎与 utf8mb4 字符集。')

h3('1. sys_user 登录账号表')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK, AUTO_INCREMENT', '主键'],
    ['username', 'VARCHAR(32)', 'NOT NULL, UNIQUE', '登录名，唯一索引 uk_user_username'],
    ['password', 'VARCHAR(100)', 'NOT NULL', 'BCrypt 哈希，不存明文'],
    ['nickname', 'VARCHAR(32)', 'NOT NULL', '显示昵称'],
    ['role', 'VARCHAR(16)', 'NOT NULL, DEFAULT STUDENT', 'ADMIN 管理员 / STUDENT 考生'],
    ['status', 'TINYINT', 'NOT NULL, DEFAULT 1', '1 启用，0 停用'],
    ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
], cap='表 2-1 sys_user 表结构', widths=[3.0, 3.2, 4.6, 5.4])

h3('2. user_profile 用户资料表（一对一）')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['user_id', 'BIGINT', 'NOT NULL, UNIQUE, FK', '关联 sys_user.id，唯一约束保证一对一'],
    ['school', 'VARCHAR(64)', 'NULL', '学校'],
    ['group_name', 'VARCHAR(16)', 'NULL', '组别，可空、可自定义'],
    ['phone', 'VARCHAR(20)', 'NULL', '手机号'],
    ['avatar', 'VARCHAR(255)', 'NULL', '头像地址'],
], cap='表 2-2 user_profile 表结构', widths=[3.0, 3.2, 4.6, 5.4])

h3('3. question_bank 题库表')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['name', 'VARCHAR(64)', 'NOT NULL, UNIQUE', '题库名，唯一索引 uk_bank_name'],
    ['group_name', 'VARCHAR(16)', 'NULL', '组别，可空；空值在页面上显示为未分组'],
    ['description', 'VARCHAR(255)', 'NULL', '描述'],
    ['status', 'VARCHAR(16)', 'NOT NULL, DEFAULT ENABLED', 'ENABLED / DISABLED'],
    ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
], cap='表 2-3 question_bank 表结构', widths=[3.0, 3.2, 4.6, 5.4])

h3('4. question 题目表')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['bank_id', 'BIGINT', 'NOT NULL, FK, INDEX', '所属题库，索引 idx_question_bank'],
    ['type', 'VARCHAR(16)', 'NOT NULL, INDEX', 'single / multi / judge'],
    ['stem', 'TEXT', 'NOT NULL', '题干'],
    ['options', 'JSON', 'NULL', '选项数组，如 [{"key":"A","text":"..."}]'],
    ['answer', 'JSON', 'NOT NULL', '单选 "B"、多选 ["A","C"]、判断 "A"'],
    ['analysis', 'TEXT', 'NULL', '解析'],
    ['difficulty', 'TINYINT', 'DEFAULT 1', '1 易 / 2 中 / 3 难'],
    ['sort_no', 'INT', 'DEFAULT 0', '题库内排序'],
    ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
], cap='表 2-4 question 表结构', widths=[3.0, 3.2, 4.6, 5.4])

h3('5. tag 知识点标签表')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['name', 'VARCHAR(32)', 'NOT NULL, UNIQUE', '标签名，唯一索引 uk_tag_name'],
    ['color', 'VARCHAR(16)', 'NULL', '前端展示色值'],
], cap='表 2-5 tag 表结构', widths=[3.0, 3.2, 4.6, 5.4])

h3('6. question_tag 题目标签关联表（多对多）')
table(['字段', '类型', '约束', '说明'], [
    ['question_id', 'BIGINT', 'PK, FK, ON DELETE CASCADE', '题目，删除题目时关联自动清理'],
    ['tag_id', 'BIGINT', 'PK, FK, INDEX', '标签，索引 idx_qt_tag 支持反查'],
], cap='表 2-6 question_tag 表结构', widths=[3.4, 3.2, 5.0, 4.6])

h3('7. exam_paper 试卷表')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['title', 'VARCHAR(128)', 'NOT NULL', '试卷标题'],
    ['bank_id', 'BIGINT', 'NOT NULL, FK, INDEX', '来源题库'],
    ['judge_count / single_count / multi_count', 'INT', 'NOT NULL', '三种题型各抽几道'],
    ['judge_score / single_score / multi_score', 'INT', 'NOT NULL', '每题分值'],
    ['duration_sec', 'INT', 'NOT NULL', '考试时长（秒）'],
    ['total_score', 'INT', 'NOT NULL', '总分，创建时计算'],
    ['status', 'VARCHAR(16)', 'NOT NULL, DEFAULT DRAFT', 'DRAFT / PUBLISHED / CLOSED'],
    ['created_by', 'BIGINT', 'NULL', '创建人'],
    ['created_at', 'DATETIME', 'DEFAULT CURRENT_TIMESTAMP', '创建时间'],
], cap='表 2-7 exam_paper 表结构', widths=[4.6, 2.6, 4.4, 4.6])

h3('8. exam_paper_question 试卷题目表')
table(['字段', '类型', '约束', '说明'], [
    ['paper_id', 'BIGINT', 'PK, FK, ON DELETE CASCADE', '试卷'],
    ['question_id', 'BIGINT', 'PK, FK, INDEX', '题目'],
    ['seq', 'INT', 'NOT NULL', '题序，从 1 开始'],
    ['score', 'INT', 'NOT NULL', '该题在本卷的分值'],
], cap='表 2-8 exam_paper_question 表结构', widths=[3.4, 3.2, 5.0, 4.6])

h3('9. answer_record 作答记录表')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['paper_id', 'BIGINT', 'NOT NULL, FK', '试卷'],
    ['user_id', 'BIGINT', 'NOT NULL, FK, INDEX', '考生'],
    ['question_id', 'BIGINT', 'NOT NULL, FK, INDEX', '题目'],
    ['chosen', 'JSON', 'NULL', '考生作答，未答为 NULL'],
    ['correct', 'TINYINT', 'NOT NULL, DEFAULT 0', '1 对 / 0 错'],
    ['score', 'INT', 'NOT NULL, DEFAULT 0', '本题得分'],
    ['submitted_at', 'DATETIME', 'NOT NULL', '交卷时间'],
], cap='表 2-9 answer_record 表结构', widths=[3.4, 3.2, 4.6, 5.0])
para('组合索引 idx_answer_paper_user(paper_id, user_id) 支撑“查某人在某卷的成绩”，idx_answer_user 支撑“我的成绩”，idx_answer_question 支撑按题统计。')

h2('（四）表关系解析')
para('三种关系在表结构上的落地方式如下：')
table(['关系', '表 A', '表 B', '落地方式', '业务含义'], [
    ['一对一 1:1', 'sys_user', 'user_profile', 'B 表 user_id 唯一索引 + 外键', '一个账号一份资料'],
    ['一对多 1:N', 'question_bank', 'question', 'B 表 bank_id 外键 + 索引', '一个题库多道题'],
    ['一对多 1:N', 'exam_paper', 'exam_paper_question', '关系表 paper_id', '一份试卷多道题'],
    ['一对多 1:N', 'sys_user', 'answer_record', 'B 表 user_id 外键', '一个考生多条作答'],
    ['多对多 N:M', 'question', 'tag', '中间表 question_tag 联合主键', '一题多标签、一标签多题'],
], cap='表 2-10 三种实体关联关系', widths=[2.6, 3.0, 3.6, 4.4, 4.0])
para('一对一通过唯一索引在数据库层面保证不会出现一个账号两份资料；一对多把外键放在多的一方，查“题库下所有题”只需一次索引扫描；多对多用中间表把两个多对多方向拆成两个一对多，联合主键天然去重。')

h2('（五）索引与约束设计')
para('除主键外，系统建立了 4 个唯一索引和 7 个普通索引。唯一索引承担业务约束：用户名、资料 user_id、题库名、标签名不能重复。普通索引服务查询：题目按题库和题型筛选、试卷按题库和状态筛选、作答按试卷加考生查询。')
para('外键方面，user_profile、question、question_tag、exam_paper、exam_paper_question、answer_record 均声明了外键。question_tag 与 exam_paper_question 对主表使用 ON DELETE CASCADE，删除题目或试卷时自动清理关联；其余外键为 RESTRICT，配合 Service 层的业务校验给出更友好的中文提示。')

# ---------------------------------------------------------------- 三、系统架构
h1('三、系统架构设计')

h2('（一）系统整体分层架构')
para('系统采用前后端分离架构。前端 Vue 3 打包后由 Nginx 或 Vite 开发服务器提供静态资源，通过 /api 前缀调用后端；后端按 Controller → Service → Mapper → MySQL 四层组织，Redis 作为旁路缓存与令牌存储。')
figure(os.path.join(DIAG, 'architecture.png'), '图 3-1 系统分层架构图', width=14.6)

h2('（二）各层职责')
table(['层次', '包 / 目录', '职责', '约束'], [
    ['Controller 控制层', 'controller（9 个类）', '接收请求、参数校验、调用 Service、封装 Result', '不写业务判断，不直接注入 Mapper'],
    ['Service 业务层', 'service + service/impl（10 组）', '业务规则、事务、缓存、VO 组装、权限判断', '不做 HTTP 相关处理'],
    ['Mapper 数据访问层', 'mapper + resources/mapper（12 + 9 个 XML）', '单表 CRUD 与多表 SQL', '不写业务分支'],
    ['Entity 实体层', 'entity（9 个类）', '与数据表一一对应的数据载体', '不直接返回给前端'],
    ['VO 视图对象', 'vo（19 个类）', '面向前端的出参结构', '不包含密码、标准答案等敏感字段'],
    ['DTO 入参对象', 'dto（8 个类）', '面向前端的入参结构，承载校验注解', '不直接落库'],
], cap='表 3-1 各层职责与约束', widths=[3.4, 5.0, 6.0, 4.6])

h2('（三）业务模块关系')
para('每个业务功能都沿 Entity → Mapper/XML → Service → Controller 单向贯通。下图列出六个核心模块的完整链路。')
figure(os.path.join(DIAG, 'modules.png'), '图 3-2 业务模块关系图', width=14.6)

h2('（四）模块与代码映射')
table(['业务模块', 'Entity', 'Mapper / XML', 'Service', 'Controller'], [
    ['认证与资料', 'SysUser / UserProfile', 'UserMapper / UserProfileMapper.xml', 'AuthService / ProfileService', 'AuthController / ProfileController'],
    ['题库管理', 'QuestionBank', 'BankMapper / BankMapper.xml', 'BankService', 'BankController'],
    ['题目管理', 'Question / QuestionTag', 'QuestionMapper / QuestionMapper.xml', 'QuestionService', 'QuestionController'],
    ['标签管理', 'Tag', 'TagMapper / TagMapper.xml', 'TagService', 'TagController'],
    ['试卷与组卷', 'ExamPaper / ExamPaperQuestion', 'PaperMapper / PaperMapper.xml', 'PaperService', 'PaperController'],
    ['考试中心', 'ExamPaper / AnswerRecord', 'ExamMapper / ExamMapper.xml', 'ExamRoomService', 'ExamController'],
    ['交卷判分', 'AnswerRecord', 'AnswerRecordMapper / AnswerRecordMapper.xml', 'AnswerService', 'AnswerController'],
    ['成绩与排行', 'AnswerRecord', 'ScoreMapper / ScoreMapper.xml', 'ScoreService', 'ScoreController'],
], cap='表 3-2 模块与代码映射', widths=[2.8, 4.2, 5.2, 4.0, 4.4])

h2('（五）接口清单')
para('后端共 38 个接口，按模块分组如下。所有接口统一返回 {code, message, data}，除登录与注册外均需在请求头携带 Authorization: Bearer <token>。')
table(['模块', '方法与路径', '权限', '说明'], [
    ['认证', 'POST /api/auth/login', '公开', '登录，返回令牌与用户信息'],
    ['认证', 'POST /api/auth/register', '公开', '考生自助注册'],
    ['认证', 'POST /api/auth/logout', '登录', '登出，删除 Redis 令牌'],
    ['认证', 'GET /api/auth/me', '登录', '当前登录用户'],
    ['资料', 'GET /api/profile', '登录', '查询账号与一对一资料'],
    ['资料', 'PUT /api/profile', '登录', '更新昵称与资料，事务'],
    ['题库', 'GET /api/banks', '登录', '分页查询，支持名称/组别/状态'],
    ['题库', 'GET /api/banks/all', '登录', '字典全量，走 Redis 缓存'],
    ['题库', 'POST /api/banks', '管理员', '新增题库'],
    ['题库', 'PUT /api/banks/{id}', '管理员', '修改题库'],
    ['题库', 'DELETE /api/banks/{id}', '管理员', '删除，有题时 409'],
    ['题目', 'GET /api/questions', '登录', '分页查询，支持题库/题型/关键字'],
    ['题目', 'POST /api/questions', '管理员', '新增题目'],
    ['题目', 'PUT /api/questions/{id}', '管理员', '修改题目'],
    ['题目', 'DELETE /api/questions/{id}', '管理员', '删除，被试卷引用时 409'],
    ['题目', 'PATCH /api/questions/batch', '管理员', '批量移动到题库'],
    ['题目', 'POST /api/questions/import', '管理员', 'Word 批量导入，整批事务'],
    ['试卷', 'GET /api/papers', '登录', '分页查询'],
    ['试卷', 'GET /api/papers/{id}', '登录', '试卷详情与题目'],
    ['试卷', 'POST /api/papers', '管理员', '随机抽题组卷'],
    ['试卷', 'PUT /api/papers/{id}', '管理员', '改组卷，仅草稿'],
    ['试卷', 'POST /api/papers/{id}/publish', '管理员', '发布'],
    ['试卷', 'POST /api/papers/{id}/close', '管理员', '结束'],
    ['试卷', 'DELETE /api/papers/{id}', '管理员', '删除'],
    ['考试', 'GET /api/exams/available', '登录', '可考试卷与我的得分'],
    ['考试', 'GET /api/exams/{paperId}/questions', '登录', '进考场取题，不含答案'],
    ['作答', 'POST /api/answers/submit', '登录', '交卷判分，事务'],
    ['成绩', 'GET /api/scores', '管理员', '全部成绩，多表聚合'],
    ['成绩', 'GET /api/scores/stats', '管理员', '统计卡片'],
    ['成绩', 'GET /api/scores/mine', '登录', '我的成绩'],
    ['成绩', 'GET /api/scores/{paperId}/{userId}', '本人或管理员', '逐题明细'],
    ['成绩', 'GET /api/scores/ranking', '登录', '排行榜，走 Redis'],
    ['成绩', 'DELETE /api/scores/{paperId}/{userId}', '管理员', '撤销成绩'],
    ['标签', 'GET /api/tags', '登录', '标签列表'],
    ['标签', 'POST /api/tags', '管理员', '新增标签'],
    ['标签', 'DELETE /api/tags/{id}', '管理员', '删除标签'],
], cap='表 3-3 接口清单', widths=[1.8, 7.0, 2.6, 6.6])

# ---------------------------------------------------------------- 四、详细实验过程
h1('四、详细实验过程')

h2('（一）项目初始化')
para('使用 Spring Initializr 创建后端工程，Group 为 com.ddyu，Artifact 为 zhikao，JDK 选择 21。依赖勾选 Spring Web、Validation、MyBatis-Plus、MySQL Driver、Spring Data Redis、Lombok。前端用 npm create vite 创建 Vue 3 工程，再安装 Element Plus、Vue Router、axios。')
para('后端 pom.xml 的关键配置如下，统一锁定 Spring Boot 3.2.5 与 MyBatis-Plus 3.5.9：')
code_block(read('backend/pom.xml', '<parent>', '</dependencies>', 46), size=8.5)
shot('IDEA 中项目结构，左侧展开 controller / service / mapper / entity 包', '图 4-1 后端工程结构')

h2('（二）数据库建表与测试数据')
para('在 MySQL 中创建 zhikao 库，执行 sql/schema.sql 建 9 张表，再执行 sql/data.sql 导入测试数据。建表脚本对 InnoDB、utf8mb4、外键和索引都做了显式声明。以 user_profile 与 question 为例：')
code_block(read('sql/schema.sql', 'CREATE TABLE user_profile', 'CREATE TABLE question_bank'), size=8.5)
code_block(read('sql/schema.sql', 'CREATE TABLE question (', 'CREATE TABLE question_tag'), size=8.5)
shot('Navicat 中 zhikao 库的 9 张表，右侧显示 user_profile 表数据', '图 4-2 数据库表结构')
para('测试数据包含 4 个账号、2 个 408 题库、80 道题、10 个知识点标签、2 份已发布试卷和 60 条作答记录。为方便核对，导入后执行统计 SQL：')
code_block("""SELECT (SELECT COUNT(*) FROM question_bank) AS banks,
       (SELECT COUNT(*) FROM question)      AS questions,
       (SELECT COUNT(*) FROM exam_paper)    AS papers,
       (SELECT COUNT(*) FROM answer_record) AS answers;
-- 结果：banks=2, questions=80, papers=2, answers=60""", size=9)

h2('（三）配置文件')
para('application.yml 配置数据源、Redis、MyBatis-Plus 与文件上传限制。MyBatis-Plus 开启驼峰映射并把 XML 位置指向 classpath:mapper；multipart 单文件上限设为 10MB，避免 Word 导入被默认 1MB 限制拦住。')
code_block(read('backend/src/main/resources/application.yml', None, None, 42), size=8.5)
shot('application.yml 配置界面，数据源与 Redis 部分', '图 4-3 后端配置文件')

h2('（四）统一返回与全局异常')
para('所有接口返回 Result<T>，包含 code、message、data 三个字段。业务异常统一抛 BizException，由 GlobalExceptionHandler 转成对应的 HTTP 状态码。这样 Controller 里不需要写 try-catch，业务代码只关心规则本身。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/common/Result.java', None, None, 40), size=8.5)
code_block(read('backend/src/main/java/com/ddyu/zhikao/common/GlobalExceptionHandler.java', None, None, 50), size=8.5)
shot('Postman 调用一个不存在的题目，返回 404 与中文提示', '图 4-4 全局异常处理效果')

h2('（五）登录认证与 Redis 令牌')
para('登录时用用户名查 sys_user，再用 BCryptPasswordEncoder.matches 校验密码。校验通过后生成 32 位 UUID 作为令牌，把用户信息序列化成 JSON 写入 Redis，key 为 login:token:<token>，有效期 30 分钟。之后每个请求由 AuthInterceptor 校验令牌，命中后把 TTL 续到 30 分钟，实现滑动过期。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AuthServiceImpl.java', 'public LoginVO login', 'public void logout'), size=8.5)
code_block(read('backend/src/main/java/com/ddyu/zhikao/config/TokenStore.java', 'public String create', 'public void refresh'), size=8.5)
shot('Redis Desktop / redis-cli 中 login:token:* 的键与 TTL', '图 4-5 Redis 登录令牌')
para('令牌校验通过后，用户信息放进 ThreadLocal，Service 层用 LoginContext.get() 取当前用户，避免每个方法都传 userId。拦截器在 afterCompletion 里清理 ThreadLocal，防止线程池复用导致串号。')

h2('（六）题库与题目 CRUD')
para('题库与题目都实现了新增、修改、删除、条件查询和分页查询。分页用 MyBatis-Plus 的 Page 对象，XML 里写动态 where 条件。题库列表还要显示题目数量，用相关子查询一次查出，避免 N+1。')
code_block(read('backend/src/main/resources/mapper/BankMapper.xml', '<sql id="bankVoColumns">', '</sql>'), size=8.5)
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/BankServiceImpl.java', 'public List<BankVO> listAll', 'public BankVO create'), size=8.5)
shot('题库管理页面，包含筛选栏、表格与分页', '图 4-6 题库管理页面')
para('删除操作有两层保护：Service 先查该题库下是否还有题目，有则抛 409；数据库外键再做一次兜底。题目被试卷引用时同样返回 409，并提示先从试卷移除。')

h2('（七）Word 题库导入')
para('这是本项目自行实现的功能，解决“题目原本在 Word 里、不想手敲”的问题。docx 本质是 zip 包，用 JDK 自带 ZipFile 解压出 word/document.xml，按段落提取 w:t 文本，再按约定格式解析题干、选项、答案、题型。整个过程不引入 Apache POI 等第三方库。')
para('解析器先按“数字-题目：”“数字-选项：”“数字-答案：”切块，再逐题校验：题型必须是单选、多选或判断；单选答案必须是一个 A-E 字母；多选至少两个字母且不能重复；判断只能是 A 或 B；选项至少两个。任意一题不合法就收集错误，最后统一抛出，整批回滚。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/word/DocxTextExtractor.java', None, None, 60), size=8.5)
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/QuestionServiceImpl.java', 'public QuestionImportVO importDocx', 'private void validate'), size=8.5)
shot('题目管理页点击 Word 导入后的弹窗，选择文件并显示导入结果', '图 4-7 Word 导入弹窗')
shot('导入错误文件时，弹窗逐条列出 6 条错误，数据库无新增', '图 4-8 导入失败整批回滚')
para('实测四个 408 文件各 20 题全部导入成功；故意做错的演示文件返回 400，errors 数组包含 6 条具体错误，question 表数量不变，验证了事务回滚。')

h2('（八）组卷与状态流转')
para('组卷时按题型分别随机抽题，SQL 使用 ORDER BY RAND() LIMIT。抽出的题目按“判断 → 单选 → 多选”写入 exam_paper_question，题序从 1 连续编号，分值存在关系表上。试卷状态为 DRAFT → PUBLISHED → CLOSED，只有 DRAFT 能改组卷，只有 PUBLISHED 能考试和交卷。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/PaperServiceImpl.java', 'public PaperVO create', 'public PaperVO update'), size=8.5)
shot('新建试卷弹窗，选择题库、三种题型数量与分值', '图 4-9 新建试卷')
shot('试卷列表，状态列显示草稿 / 已发布 / 已结束', '图 4-10 试卷管理')

h2('（九）交卷判分')
para('交卷是整个系统业务最重的一段：校验试卷状态、拦截重复交卷、校验作答题目都属于本卷、逐题判分、批量落库、清排行榜缓存、重新聚合返回成绩，全部在一个事务里完成。未作答的题也要落库，chosen 为 NULL，这样成绩明细才能显示“未答”。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AnswerServiceImpl.java', 'int grade', 'private String toChosenJson'), size=8.5)
shot('考场页面，左侧答题卡、右侧题目、顶部倒计时', '图 4-11 在线考场')
shot('交卷确认弹窗，提示还有几题未作答', '图 4-12 交卷二次确认')

h2('（十）成绩聚合与排行榜')
para('成绩不单独建表，而是从 answer_record 聚合。一条 SQL 同时算出总分、正确数、错误数、未答数、总题数、正确率和交卷时间，再按试卷和考生分组。排行榜按总分倒序取前 N 名，结果写入 Redis，key 为 cache:ranking:<paperId>，有人交卷时删除缓存。')
code_block(read('backend/src/main/resources/mapper/ScoreMapper.xml', '<sql id="scoreAggregates">', '</sql>'), size=8.5)
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/ScoreServiceImpl.java', 'public List<RankingVO> ranking', 'private void fillItem'), size=8.5)
shot('成绩管理页面，含总分、正确率、排行榜入口', '图 4-13 成绩管理')
shot('成绩明细弹窗，逐题显示我的答案、标准答案与得分', '图 4-14 成绩明细')

h2('（十一）个人资料一对一')
para('个人资料用 user_profile 表与 sys_user 做一对一。查询时用 LEFT JOIN，保证没填资料的账号也能查出来；MyBatis 用 association 把 user_profile 的字段映射到 ProfileVO 的内部类 Detail。更新时同时改 sys_user.nickname 和 user_profile，两个表在同一个事务里。')
code_block(read('backend/src/main/resources/mapper/UserProfileMapper.xml', None, None, 45), size=8.5)
shot('个人资料页面，显示账号、角色、学校、组别、手机号', '图 4-15 个人资料')
shot('修改昵称后，右上角顶栏同步更新', '图 4-16 昵称同步')

h2('（十二）前端工程与请求封装')
para('前端用 Vite 创建，开发服务器把 /api 代理到 8080，避免跨域。axios 实例统一设置 baseURL、超时和两个拦截器：请求拦截器自动加 Bearer 令牌；响应拦截器判断 code，成功直接返回 data，失败统一弹 ElMessage，401 时清除登录信息并跳登录页。')
code_block(read('frontend/vite.config.js', None, None, 30), size=8.5)
code_block(read('frontend/src/api/request.js', None, None, 60), size=8.5)
shot('VS Code 中前端目录结构', '图 4-17 前端工程结构')

h2('（十三）页面开发与手绘涂鸦风')
para('页面用 Vue 3 组合式 API 与 Element Plus 开发。视觉上没有沿用后台管理系统的蓝色默认主题，而是做了一套“纸张 + 墨水”的手绘风：米白纸色、墨黑文字、虚线边框、硬边偏移阴影、红蓝绿三色标记笔。实现方式是覆盖 Element Plus 的 CSS 变量，不引入 Tailwind，也不改组件结构。')
code_block(read('frontend/src/styles/index.css', '/* 手绘涂鸦 */', '/* 表格 */', 55), size=8.5)
shot('登录页，展示手绘风卡片与标题', '图 4-18 登录页')
shot('考试中心页面，卡片式考试列表', '图 4-19 考试中心')

# ---------------------------------------------------------------- 五、核心源代码
h1('五、核心源代码')
para('本章按 Entity → Mapper 接口 → Mapper XML → Service 接口 → Service 实现 → Controller 的顺序收录关键源码，每段标注文件路径与对应功能。受篇幅限制，Service 实现只收录业务最重的六个类，其余实现类的结构与它们一致。')

h2('（一）Entity 实体层')
para('9 个实体与 9 张表一一对应，使用 Lombok 的 @Data 生成 getter/setter，字段名采用驼峰，由 MyBatis-Plus 自动映射下划线列名。')
for name in ['SysUser', 'UserProfile', 'QuestionBank', 'Question', 'Tag', 'QuestionTag', 'ExamPaper', 'ExamPaperQuestion', 'AnswerRecord']:
    h3(f'entity/{name}.java')
    code_block(read(f'backend/src/main/java/com/ddyu/zhikao/entity/{name}.java'), size=8)

h2('（二）Mapper 接口层')
para('Mapper 接口继承 BaseMapper 获得单表 CRUD，多表查询在接口上声明方法，由同名 XML 实现。')
for name in ['UserMapper', 'UserProfileMapper', 'BankMapper', 'QuestionMapper', 'TagMapper', 'QuestionTagMapper', 'PaperMapper', 'ExamPaperMapper', 'ExamPaperQuestionMapper', 'ExamMapper', 'AnswerRecordMapper', 'ScoreMapper']:
    h3(f'mapper/{name}.java')
    code_block(read(f'backend/src/main/java/com/ddyu/zhikao/mapper/{name}.java'), size=8)

h2('（三）Mapper XML 映射层')
para('XML 承载多表关联、动态条件、聚合统计和一对一 association 映射。下面按业务顺序收录 9 个映射文件。')
for name in ['UserMapper', 'UserProfileMapper', 'BankMapper', 'QuestionMapper', 'TagMapper', 'PaperMapper', 'ExamMapper', 'AnswerRecordMapper', 'ScoreMapper']:
    h3(f'mapper/{name}.xml')
    code_block(read(f'backend/src/main/resources/mapper/{name}.xml'), size=8)

h2('（四）Service 接口层')
para('Service 接口只声明业务方法，入参用 DTO、出参用 VO，不暴露 Entity。')
for name in ['AuthService', 'ProfileService', 'BankService', 'QuestionService', 'PaperService', 'ExamRoomService', 'AnswerService', 'ScoreService', 'TagService', 'AdminGuardService']:
    h3(f'service/{name}.java')
    code_block(read(f'backend/src/main/java/com/ddyu/zhikao/service/{name}.java'), size=8)

h2('（五）Service 实现层')
para('业务规则、事务、缓存、权限判断都写在实现类里。下面收录认证、题库、Word 导入、交卷判分、成绩聚合、个人资料六个类的核心代码。')

h3('service/impl/AuthServiceImpl.java（登录、注册、登出）')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AuthServiceImpl.java'), size=8)

h3('service/impl/BankServiceImpl.java（题库 CRUD 与字典缓存）')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/BankServiceImpl.java'), size=8)

h3('service/impl/QuestionServiceImpl.java（题目 CRUD、批量移动、Word 导入）')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/QuestionServiceImpl.java'), size=8)

h3('service/impl/AnswerServiceImpl.java（交卷、判分、缓存失效）')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AnswerServiceImpl.java'), size=8)

h3('service/impl/ScoreServiceImpl.java（成绩分页、明细、排行榜）')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/ScoreServiceImpl.java'), size=8)

h3('service/impl/ProfileServiceImpl.java（一对一资料读写与令牌刷新）')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/ProfileServiceImpl.java'), size=8)

para('其余四个实现类的职责：PaperServiceImpl 负责组卷、改组卷、发布、结束、删除与状态校验；ExamRoomServiceImpl 负责考试中心列表与进考场取题（题目视图不含标准答案）；TagServiceImpl 负责标签增删查；AdminGuardServiceImpl 负责从 LoginContext 取当前用户并校验 ADMIN 角色。它们的共同点是：先做业务校验，再操作 Mapper，最后组装 VO。')

h2('（六）Controller 控制层')
para('Controller 只做三件事：接参数、调 Service、包 Result。管理类接口第一行统一调用 adminGuardService.checkAdmin()。')
for name in ['AuthController', 'ProfileController', 'BankController', 'QuestionController', 'PaperController', 'ExamController', 'AnswerController', 'ScoreController', 'TagController']:
    h3(f'controller/{name}.java')
    code_block(read(f'backend/src/main/java/com/ddyu/zhikao/controller/{name}.java'), size=8)
# ---------------------------------------------------------------- 六、运行测试
h1('六、运行测试过程')

h2('（一）启动与运行')
para('本地启动顺序为 MySQL → Redis → 后端 → 前端。项目提供 scripts/dev.sh 一键启动脚本，先检查数据库连接，再拉起 Redis、后端 8080 与前端 5173。启动成功后访问 http://127.0.0.1:5173 即可打开登录页。')
code_block('''== 1/4 检查 MySQL
  MySQL 连接正常
  库 zhikao 正常，题目 80 道
== 2/4 检查 Redis
  Redis 已启动
== 3/4 启动后端（8080）
  后端起来了
== 4/4 启动前端（5173）
  前端起来了''', size=9)
shot('IDEA 控制台，Spring Boot 启动完成，端口 8080', '图 6-1 后端启动日志')
shot('终端执行 npm run dev，Vite 启动完成，端口 5173', '图 6-2 前端启动日志')

h2('（二）Postman 接口测试')
para('接口测试使用 Postman，先调登录接口拿到 token，再在后续请求的 Authorization 里选择 Bearer Token。下面列出 8 个代表性接口的测试记录。')
table(['序号', '接口', '请求要点', '预期结果', '实际结果'], [
    ['1', 'POST /api/auth/login', 'admin / admin123', '200，返回 token 与角色', '通过'],
    ['2', 'POST /api/auth/register', '用户名已存在', '400，用户名已被注册', '通过'],
    ['3', 'GET /api/banks?page=1&size=10', '带 Bearer 令牌', '200，分页数据', '通过'],
    ['4', 'GET /api/banks（不带令牌）', '删除 Authorization', '401，登录已失效', '通过'],
    ['5', 'POST /api/banks（考生令牌）', 'student01 的 token', '403，无权限', '通过'],
    ['6', 'POST /api/questions/import', 'multipart 文件 + bankId', '200，imported=20', '通过'],
    ['7', 'POST /api/answers/submit', '同一试卷交两次', '第一次 200，第二次 409', '通过'],
    ['8', 'GET /api/scores/{paperId}/{userId}', '考生查别人成绩', '403', '通过'],
], cap='表 6-1 Postman 接口测试记录', widths=[1.4, 6.2, 4.6, 5.4, 2.2])
shot('Postman 登录接口，请求体与返回的 token', '图 6-3 Postman 登录接口')
shot('Postman 题库分页接口，Header 中带 Bearer Token', '图 6-4 Postman 题库接口')
shot('Postman 无令牌访问，返回 401', '图 6-5 Postman 未授权')
shot('Postman 考生调用管理接口，返回 403', '图 6-6 Postman 越权')

h2('（三）页面功能演示')
para('按管理员与考生两条线走完整流程，每一步都保留截图。')
table(['序号', '操作', '验证点'], [
    ['1', '管理员登录，进入概览', '四个统计卡片显示题库、题目、试卷、考生数量'],
    ['2', '新增题库，组别填“第一章”', '组别可自定义，列表显示“第一章”'],
    ['3', '新增题库，组别留空', '列表显示“未分组”，不报错'],
    ['4', '题目管理，Word 导入 20 题', '导入成功提示，列表新增 20 条'],
    ['5', 'Word 导入错误文件', '弹出 6 条错误，题目数不变'],
    ['6', '新建试卷并发布', '状态从草稿变为已发布，总分 100'],
    ['7', '考生登录，进入考场答题', '倒计时正常，答题卡高亮已答'],
    ['8', '交卷', '弹出确认，交卷后跳转成绩，分数正确'],
    ['9', '管理员查看成绩明细', '逐题显示对错与得分'],
    ['10', '个人资料改昵称', '顶栏昵称立即更新'],
], cap='表 6-2 页面功能演示清单', widths=[1.4, 7.0, 11.4])
for title, cap in [
    ('管理员概览页，四个统计卡片', '图 6-7 概览页'),
    ('题库新增弹窗，组别填“第一章”', '图 6-8 新增题库'),
    ('题目管理列表与筛选栏', '图 6-9 题目管理'),
    ('试卷新建弹窗，题型数量与分值', '图 6-10 新建试卷'),
    ('考生考试中心，显示可考试卷与我的得分', '图 6-11 考试中心'),
    ('考场答题页，倒计时与答题卡', '图 6-12 在线答题'),
    ('交卷后的成绩页', '图 6-13 交卷成绩'),
    ('成绩明细弹窗，逐题对错', '图 6-14 成绩明细'),
]:
    shot(title, cap)

h2('（四）多表查询效果')
para('系统中典型的多表查询有三处，下面给出 SQL 与实际结果。')
para('第一处是成绩聚合，answer_record 同时关联 exam_paper 和 sys_user，一条 SQL 算出总分、正确数、正确率：')
code_block('''SELECT ar.paper_id, p.title, u.nickname,
       SUM(ar.score)                              AS totalScore,
       SUM(ar.correct = 1)                        AS correctCount,
       SUM(ar.chosen IS NULL)                     AS blankCount,
       ROUND(SUM(ar.correct = 1) / COUNT(*), 2)   AS accuracy
FROM answer_record ar
JOIN exam_paper p ON p.id = ar.paper_id
JOIN sys_user  u ON u.id = ar.user_id
GROUP BY ar.paper_id, ar.user_id, p.title, u.nickname
ORDER BY ar.paper_id, totalScore DESC;''', size=8.5)
table(['试卷', '考生', '总分', '正确', '未答', '正确率'], [
    ['408 数据结构与计算机组成原理', '李同学', '92', '18', '0', '0.90'],
    ['408 数据结构与计算机组成原理', '陈同学', '68', '12', '0', '0.60'],
    ['408 操作系统与计算机网络', '王同学', '84', '16', '0', '0.80'],
], cap='表 6-3 成绩聚合查询结果', widths=[7.0, 3.0, 2.2, 2.2, 2.2, 2.4])
para('第二处是题库列表带题目数量，用相关子查询避免 N+1：')
code_block('''SELECT b.id, b.name, b.group_name,
       (SELECT COUNT(*) FROM question q WHERE q.bank_id = b.id) AS questionCount
FROM question_bank b
ORDER BY b.id;''', size=8.5)
para('第三处是个人资料一对一，sys_user LEFT JOIN user_profile，MyBatis 用 association 映射到 VO 的内部类：')
code_block('''SELECT u.id, u.username, u.nickname, u.role,
       p.id AS profile_id, p.school, p.group_name, p.phone
FROM sys_user u
LEFT JOIN user_profile p ON p.user_id = u.id
WHERE u.id = #{userId};''', size=8.5)
shot('Navicat 执行成绩聚合 SQL 的结果', '图 6-15 多表查询结果')

h2('（五）Redis 缓存验证')
para('Redis 在本项目承担三类缓存。验证方式是先用 redis-cli 查看 key，再观察后端日志里的“命中 / 未命中”记录。')
code_block('''127.0.0.1:6379> KEYS login:token:*
1) "login:token:9f2c4e1a7b8d4c3e9a6f5d2b1c0e8a7f"
127.0.0.1:6379> TTL login:token:9f2c4e1a7b8d4c3e9a6f5d2b1c0e8a7f
(integer) 1793
127.0.0.1:6379> GET dict:banks
"[{\\"id\\":1,\\"name\\":\\"408 数据结构与计算机组成原理\\"...}]"
127.0.0.1:6379> TTL dict:banks
(integer) 1745
127.0.0.1:6379> KEYS cache:ranking:*
1) "cache:ranking:1"''', size=8.5)
para('后端日志对应输出：首次查询字典打印“未命中，回源数据库”，第二次打印“命中”；交卷后排行榜 key 被删除，下次查询重新回源。缓存读失败时 catch 异常回源，不影响业务。')
shot('redis-cli 查看三类缓存 key 与 TTL', '图 6-16 Redis 缓存')
shot('后端日志中的缓存命中与未命中记录', '图 6-17 缓存日志')

h2('（六）异常处理演示')
para('系统的异常分业务异常与系统异常两类，HTTP 状态码与业务码保持一致。下面列出 7 种典型场景。')
table(['场景', 'HTTP 状态', '返回信息'], [
    ['未带令牌访问', '401', '登录已失效，请重新登录'],
    ['考生调用管理接口', '403', '无权限，仅管理员可操作'],
    ['题目不存在', '404', '题目不存在'],
    ['题库下有题仍删除', '409', '题库下还有题目，不能删除'],
    ['同一试卷重复交卷', '409', '同一考生同一试卷只能交一次卷'],
    ['用户名重复注册', '400', '用户名已被注册，请换一个'],
    ['Word 格式错误', '400', '单选题答案必须是一个字母（附 errors 数组）'],
], cap='表 6-4 异常处理场景', widths=[7.0, 3.0, 9.8])
shot('Postman 重复交卷，返回 409 与中文提示', '图 6-18 重复交卷 409')
shot('Word 导入失败，前端弹窗逐条显示错误', '图 6-19 导入错误提示')

h2('（七）自动化回归测试')
para('除手工测试外，项目编写了三个端到端脚本，用 curl 直接打接口并断言结果。三个脚本共 87 条断言，覆盖登录、权限、题库、题目、试卷、考试、交卷、成绩、缓存与异常。')
table(['脚本', '覆盖内容', '断言数', '结果'], [
    ['scripts/e2e-api.sh', '认证、题库、题目、试卷、交卷、成绩、权限、缓存', '51', '全部通过'],
    ['scripts/e2e-extra.sh', '批量移动、撤销成绩、排行榜缓存、边界校验', '18', '全部通过'],
    ['scripts/e2e-exam-room.sh', '考试中心、进考场、答题、交卷、我的成绩', '18', '全部通过'],
], cap='表 6-5 自动化测试结果', widths=[5.4, 8.6, 2.4, 3.4])
code_block('''$ bash scripts/e2e-api.sh
结果: 51 通过, 0 失败
$ bash scripts/e2e-extra.sh
结果: 18 通过, 0 失败
$ bash scripts/e2e-exam-room.sh
结果: 18 通过, 0 失败''', size=9)
shot('终端执行三个 e2e 脚本，全部通过', '图 6-20 自动化测试')
# ---------------------------------------------------------------- 七、实验总结
h1('七、实验总结')

h2('（一）实验收获')
para('第一，真正理解了分层不是形式。刚开始写的时候，Controller 里忍不住想直接注入 Mapper 查一下，后来强制自己把每个业务判断都放进 Service，才发现好处：判分规则、事务边界、缓存失效都集中在一处，改需求只需要动一个文件。')
para('第二，事务不是加个注解就万事大吉。Word 导入要求“错一道全批回滚”，交卷要求“一半成功也不许落库”，这些都必须让异常真正抛出去、且是 RuntimeException。我们一开始把解析异常 catch 住转成了返回值，结果事务不回滚，排查后才改成抛 BizException。')
para('第三，缓存要考虑失效，不只是写入。题库字典在新增题库后必须删掉，否则下拉框一直是旧数据；排行榜在交卷后必须删掉，否则分数不变。缓存的一致性比缓存本身更难。')
para('第四，前端和后端的约定要提前定死。返回结构、错误码、字段命名一旦对齐，联调就很快；否则会出现“前端以为 data 是数组、后端返回的是对象”这类低级问题。')

h2('（二）开发中遇到的问题与解决方案')
table(['问题', '原因', '解决方式'], [
    ['Word 导入后事务不回滚', '解析异常被 catch 成返回值，没有抛出去', '改为收集错误后抛 BizException，继承 RuntimeException'],
    ['考生登录后被踢回登录页', '成绩接口改成仅管理员，考生落地页仍调管理员接口', '按角色分流：管理员去概览，考生去考试中心'],
    ['题库组别只能选本科组/专科组', 'DTO 用了固定枚举校验，数据库列也不允许空', '组别改为可选、可自定义，空字符串在 Service 转 NULL'],
    ['同一考生能重复交卷', '只在前端禁用按钮，接口没拦', 'Service 先 count(paper_id, user_id)，大于 0 返回 409'],
    ['多选少选给了满分', '判分只比较集合是否相等', '改为先判子集，再判长度：真子集给一半，向下取整'],
    ['排行榜分数不更新', '缓存写入后没有失效', '交卷成功后 delete cache:ranking:<paperId>'],
    ['中文在 Windows 终端乱码', 'curl 默认按 GBK 发送表单', '请求体先写 UTF-8 文件，再用 --data-binary 发送'],
    ['表格列宽在 Word 里被均分', '只设了单元格宽度，没设 tblGrid 与固定布局', '设置 tblLayout=fixed 并同步 gridCol 宽度'],
], cap='表 7-1 问题与解决方案', widths=[6.4, 6.4, 6.8])

h2('（三）不足与改进方向')
bullet('1. 令牌只做了 30 分钟滑动过期，没有刷新令牌与单点登录踢下线，后续可以加 refresh token。')
bullet('2. 前端 Element Plus 目前全量引入，打包体积偏大，后续改用 unplugin-vue-components 按需引入。')
bullet('3. Word 导入只支持固定文本格式，图片题、公式题、复杂表格暂时无法解析，后续可以接 POI 或引入模板占位符。')
bullet('4. 交卷的防重复目前是“先查后插”，高并发下仍可能重复，后续给 (paper_id, user_id) 加唯一索引兜底。')
bullet('5. 缓存只做了穿透保护，没有做击穿互斥与雪崩随机过期，后续可以加分布式锁与 TTL 抖动。')
bullet('6. 配置里的数据库密码是明文，生产环境应改为环境变量或配置中心，并开启 HTTPS。')

if __name__ == '__main__':
    doc.save(OUT)
    print('saved', OUT)