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
    m = re.match(r'^((?:表|图)[ 	]*\d+(?:[-.]\d+)*|\d+(?:\.\d+)*\.)[ 	　]+', text)
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



def no_auto_space(p):
    """关闭 Word 的中西文自动间距，避免中英文之间出现视觉空隙"""
    ppr = p._p.get_or_add_pPr()
    for tag in ('w:autoSpaceDE', 'w:autoSpaceDN'):
        el = OxmlElement(tag)
        el.set(qn('w:val'), '0')
        ppr.append(el)

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
    no_auto_space(p)
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
    no_auto_space(p)
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
        no_auto_space(p)
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
            no_auto_space(p)
            set_run(p.add_run(tight(str(text))), size=size)
    # 固定布局 + 真实列宽，否则 Word 会按内容均分
    widths = widths or [14.2 / len(headers)] * len(headers)
    _sum = sum(widths)
    if _sum > 14.2:
        widths = [w * 14.2 / _sum for w in widths]
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

h2('（一）实验名称与目的')
para('实验名称：赛博进京赶考系统，一个基于Spring Boot + MyBatis-Plus + Redis + Vue 3的前后端分离刷题考试平台。')
para('实验目的：以408考研刷题为业务背景，完整走一遍前后端分离项目的开发流程，重点验证四件事：标准四层结构、MyBatis多表查询与分页、Redis三类缓存、Vue 3与Element Plus的前后端联调。')

h2('（二）实验环境')
table(['类别', '项目', '版本 / 说明'], [
    ['硬件', '处理器 / 内存', 'Intel Core i7 / 16 GB'],
    ['软件', '操作系统', 'Windows 11 64位'],
    ['软件', 'JDK / Maven', 'OpenJDK 21.0.12 / Maven 3.9.16'],
    ['软件', 'MySQL / Redis', 'MySQL 8.0.46 / Redis 5.0.14.1'],
    ['软件', 'Node.js', 'v24.19.0'],
    ['框架', 'Spring Boot / MyBatis-Plus', '3.2.5 / 3.5.9'],
    ['框架', 'Vue / Element Plus / Vite', '3.5 / 2.14 / 6.4'],
    ['工具', '开发与测试', 'IntelliJ IDEA、VS Code、Navicat、Postman'],
], cap='表 1-1 实验环境', widths=[2.0, 5.0, 7.2])

h2('（三）功能清单')
table(['序号', '功能', '角色', '说明'], [
    ['1', '登录 / 注册 / 登出', '全部', 'BCrypt校验，Redis令牌30分钟滑动过期'],
    ['2', '个人资料', '全部', 'sys_user与user_profile一对一'],
    ['3', '题库管理', '管理员', '增删改查、分页、组别可选可自定义'],
    ['4', '题目管理', '管理员', '三种题型，支持Word批量导入与批量移动'],
    ['5', '试卷管理', '管理员', '按题型随机抽题组卷，草稿/发布/结束'],
    ['6', '在线考试', '考生', '考试中心、倒计时答题、答题卡、自动交卷'],
    ['7', '交卷判分', '考生', '单选判断全对得分，多选少选得一半'],
    ['8', '成绩管理', '全部', '多表聚合、排行榜、逐题明细，考生只能看自己'],
], cap='表 1-2 功能清单', widths=[1.2, 3.6, 2.0, 7.4])

h2('（四）小组分工')
table(['成员', '角色', '主要工作'], [
    ['张曦', '数据库设计', 'E-R图、9张表结构、索引与外键、测试数据'],
    ['张智斐', '后端开发', '分层骨架、认证与Redis、判分与组卷、Word导入'],
    ['段茗耀', '前端开发', '页面与路由、请求封装、考场交互、手绘风样式'],
    ['夏康迪', '文档与答辩', '实验报告、接口文档、演示脚本、答辩材料'],
], cap='表 1-3 小组分工', widths=[2.0, 3.0, 9.2])

# ---------------------------------------------------------------- 二、数据库设计
h1('二、数据库设计')

h2('（一）设计思路')
para('系统围绕“题库—试卷—作答”主线建模：题库是题目来源，试卷从题库按题型抽题，考生作答后按题落库，成绩由作答记录聚合而来。共9张表，覆盖一对一、一对多、多对多三种关系。')

h2('（二）E-R图')
figure(os.path.join(DIAG, 'er.png'), '图 2-1 系统 E-R 图', width=14.4)

h2('（三）数据表结构')
para('9张表均使用InnoDB引擎与utf8mb4字符集，表名与作用如下：')
table(['表名', '中文名', '作用', '关系'], [
    ['sys_user', '登录账号', '管理员与考生共用，role区分', '1:1资料，1:N作答'],
    ['user_profile', '用户资料', '学校、组别、手机号', '1:1账号'],
    ['question_bank', '题库', '一批同源题目', '1:N题目'],
    ['question', '题目', '题干、选项、答案、解析', 'N:1题库，N:M标签'],
    ['tag', '知识点标签', '数据结构、操作系统等', 'N:M题目'],
    ['question_tag', '题目标签', '多对多中间表', '联合主键'],
    ['exam_paper', '试卷', '题量、分值、时长、状态', '1:N试卷题目'],
    ['exam_paper_question', '试卷题目', '题序与每题分值', '联合主键'],
    ['answer_record', '作答记录', '作答、对错、得分', '成绩的原始数据'],
], cap='表 2-1 数据表清单', widths=[3.8, 2.6, 4.8, 3.0])
para('三张核心表的字段设计如下，其余表的字段见建表脚本。')
table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['username', 'VARCHAR(32)', 'NOT NULL, UNIQUE', '登录名'],
    ['password', 'VARCHAR(100)', 'NOT NULL', 'BCrypt哈希'],
    ['nickname', 'VARCHAR(32)', 'NOT NULL', '昵称'],
    ['role', 'VARCHAR(16)', 'NOT NULL', 'ADMIN / STUDENT'],
    ['status', 'TINYINT', 'NOT NULL', '1启用 / 0停用'],
], cap='表 2-2 sys_user 表结构', widths=[2.6, 3.4, 4.6, 3.6])

table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['bank_id', 'BIGINT', 'NOT NULL, FK, INDEX', '所属题库'],
    ['type', 'VARCHAR(16)', 'NOT NULL', 'single / multi / judge'],
    ['stem', 'TEXT', 'NOT NULL', '题干'],
    ['options', 'JSON', 'NULL', '选项数组'],
    ['answer', 'JSON', 'NOT NULL', '单选"B"/多选["A","C"]/判断"A"'],
], cap='表 2-3 question 表结构', widths=[2.6, 3.0, 4.4, 4.2])

table(['字段', '类型', '约束', '说明'], [
    ['id', 'BIGINT', 'PK', '主键'],
    ['paper_id', 'BIGINT', 'NOT NULL, FK', '试卷'],
    ['user_id', 'BIGINT', 'NOT NULL, FK', '考生'],
    ['question_id', 'BIGINT', 'NOT NULL, FK', '题目'],
    ['chosen', 'JSON', 'NULL', '作答，未答为NULL'],
    ['correct / score', 'TINYINT / INT', 'NOT NULL', '是否正确 / 得分'],
], cap='表 2-4 answer_record 表结构', widths=[3.0, 3.2, 3.6, 4.4])

h2('（四）三种关系')
table(['关系', '表A', '表B', '落地方式'], [
    ['一对一 1:1', 'sys_user', 'user_profile', 'B表user_id唯一索引+外键'],
    ['一对多 1:N', 'question_bank', 'question', 'B表bank_id外键+索引'],
    ['一对多 1:N', 'exam_paper', 'exam_paper_question', '关系表paper_id'],
    ['多对多 N:M', 'question', 'tag', '中间表question_tag联合主键'],
], cap='表 2-5 三种实体关联关系', widths=[2.6, 4.0, 4.4, 3.2])
para('一对一靠唯一索引，一对多把外键放在多的一方，多对多靠中间表加联合主键。question_tag对主表使用ON DELETE CASCADE，删题时关联自动清理。')

# ---------------------------------------------------------------- 三、系统架构
h1('三、系统架构设计')

h2('（一）分层架构')
para('前端Vue 3打包后由Nginx提供静态资源，通过/api调用后端；后端按Controller → Service → Mapper → MySQL四层组织，Redis作为旁路缓存与令牌存储。')
figure(os.path.join(DIAG, 'architecture.png'), '图 3-1 系统分层架构图', width=14.4)
table(['层次', '职责', '约束'], [
    ['Controller', '接参数、校验、调Service、包Result', '不写业务判断，不直接调Mapper'],
    ['Service', '业务规则、事务、缓存、VO组装', '不做HTTP相关处理'],
    ['Mapper', '单表CRUD与多表SQL', '不写业务分支'],
    ['Entity / VO', '实体与视图对象', 'Entity不直接返回前端'],
], cap='表 3-1 各层职责', widths=[3.0, 7.4, 3.8])

h2('（二）业务模块关系')
figure(os.path.join(DIAG, 'modules.png'), '图 3-2 业务模块关系图', width=14.4)
table(['模块', 'Entity', 'Mapper / XML', 'Service', 'Controller'], [
    ['认证与资料', 'SysUser / UserProfile', 'UserMapper / UserProfileMapper.xml', 'AuthService / ProfileService', 'AuthController / ProfileController'],
    ['题库与题目', 'QuestionBank / Question', 'BankMapper / QuestionMapper.xml', 'BankService / QuestionService', 'BankController / QuestionController'],
    ['试卷与考试', 'ExamPaper / ExamPaperQuestion', 'PaperMapper / ExamMapper.xml', 'PaperService / ExamRoomService', 'PaperController / ExamController'],
    ['交卷与成绩', 'AnswerRecord', 'AnswerRecordMapper / ScoreMapper.xml', 'AnswerService / ScoreService', 'AnswerController / ScoreController'],
], cap='表 3-2 模块与代码映射', widths=[2.4, 4.0, 5.2, 4.4, 4.6])

h2('（三）接口清单')
table(['模块', '接口数', '代表接口'], [
    ['认证', '4', 'login / register / logout / me'],
    ['资料', '2', 'GET /api/profile、PUT /api/profile'],
    ['题库', '5', '分页、字典、增、改、删'],
    ['题目', '6', '分页、增、改、删、批量移动、Word导入'],
    ['试卷', '7', '分页、详情、组卷、改组卷、发布、结束、删除'],
    ['考试', '2', '可考试卷、进考场取题'],
    ['作答', '1', 'POST /api/answers/submit'],
    ['成绩', '6', '全量、统计、我的、明细、排行榜、撤销'],
    ['标签', '3', '查、增、删'],
], cap='表 3-3 接口清单（共38个）', widths=[2.2, 2.2, 9.8])

# ---------------------------------------------------------------- 四、开发过程
h1('四、详细实验过程')

h2('（一）项目初始化')
para('后端用Spring Initializr创建，Group为com.ddyu，Artifact为zhikao，JDK 21，依赖Spring Web、Validation、MyBatis-Plus、MySQL Driver、Spring Data Redis、Lombok。前端用npm create vite创建Vue 3工程，再安装Element Plus、Vue Router、axios。')
code_block(read('backend/pom.xml', '<parent>', '</dependencies>', 32), size=8)

h2('（二）建表与测试数据')
para('执行sql/schema.sql建9张表，再执行sql/data.sql导入测试数据。以user_profile为例，user_id加唯一索引保证一对一：')
code_block(read('sql/schema.sql', 'CREATE TABLE user_profile', 'CREATE TABLE question_bank'), size=8)
para('导入后共4个账号、2个408题库、80道题、2份试卷、60条作答记录。')

h2('（三）统一返回与异常')
para('所有接口返回Result<T>，业务异常统一抛BizException，由GlobalExceptionHandler转成对应HTTP状态码，Controller里不写try-catch。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/common/GlobalExceptionHandler.java', None, None, 42), size=8)

h2('（四）登录认证与Redis令牌')
para('登录时用BCrypt校验密码，通过后生成32位UUID作为令牌，把用户信息写入Redis，key为login:token:<token>，有效期30分钟，每次请求续期。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AuthServiceImpl.java', 'public LoginVO login', 'public void logout'), size=8)
shot('Redis中login:token:*的键与TTL', '图 4-1 Redis 登录令牌', height=3.6)

h2('（五）题库与题目CRUD')
para('题库列表要显示题目数量，用相关子查询一次查出，避免N+1；删除时Service先校验题库下是否还有题，有则返回409。')
code_block(read('backend/src/main/resources/mapper/BankMapper.xml', '<sql id="bankVoColumns">', '</sql>'), size=8)
shot('题库管理页面，含筛选栏、表格与分页', '图 4-2 题库管理', height=4.2)

h2('（六）Word题库导入')
para('docx本质是zip包，用JDK自带ZipFile解压出word/document.xml，按段落提取w:t文本，再解析题干、选项、答案、题型，不引入第三方库。任意一题不合法就收集错误并整批回滚。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/QuestionServiceImpl.java', 'public QuestionImportVO importDocx', 'private void'), size=8)
shot('Word导入弹窗与导入结果', '图 4-3 Word 导入', height=4.0)
shot('错误文件导入失败，逐条列出错误', '图 4-4 导入回滚', height=3.6)

h2('（七）组卷与交卷判分')
para('组卷按题型分别随机抽题，SQL用ORDER BY RAND() LIMIT，题序按判断→单选→多选排列。交卷在一个事务里完成状态校验、重复交卷拦截、逐题判分、批量落库、清排行榜缓存。')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AnswerServiceImpl.java', 'int grade', 'private String toChosenJson'), size=8)
shot('考场页面，倒计时与答题卡', '图 4-5 在线考场', height=4.2)

h2('（八）成绩聚合与排行榜')
para('成绩不单独建表，从answer_record聚合，一条SQL算出总分、正确数、未答数、正确率。排行榜按总分倒序，结果写入Redis，交卷时删除缓存。')
code_block(read('backend/src/main/resources/mapper/ScoreMapper.xml', '<sql id="scoreAggregates">', '</sql>'), size=8)
shot('成绩管理页面与逐题明细', '图 4-6 成绩管理', height=4.2)

h2('（九）前端请求封装')
para('开发时Vite把/api代理到8080，避免跨域。axios统一加Bearer令牌，响应拦截器判断code，成功直接返回data，失败弹提示，401跳登录页。')
code_block(read('frontend/src/api/request.js', None, None, 38), size=8)

# ---------------------------------------------------------------- 五、核心源码
h1('五、核心源代码')
para('完整源码见交付压缩包，本章只收录最能体现分层与业务复杂度的文件。各层文件数量如下：')
table(['层', '包 / 目录', '文件数', '代表文件'], [
    ['Entity', 'entity', '9', 'SysUser、Question、AnswerRecord'],
    ['Mapper接口', 'mapper', '12', 'BankMapper、ScoreMapper、UserProfileMapper'],
    ['Mapper XML', 'resources/mapper', '9', 'ScoreMapper.xml、QuestionMapper.xml'],
    ['Service接口', 'service', '10', 'BankService、AnswerService、ScoreService'],
    ['Service实现', 'service/impl', '10', 'AnswerServiceImpl、QuestionServiceImpl'],
    ['Controller', 'controller', '9', 'AuthController、AnswerController'],
], cap='表 5-1 分层文件清单', widths=[2.6, 4.0, 2.2, 5.4])

h2('（一）Entity：SysUser')
code_block(read('backend/src/main/java/com/ddyu/zhikao/entity/SysUser.java'), size=8)

h2('（二）Mapper XML：ScoreMapper 聚合查询')
code_block(read('backend/src/main/resources/mapper/ScoreMapper.xml'), size=8)

h2('（三）Service：交卷判分')
code_block(read('backend/src/main/java/com/ddyu/zhikao/service/impl/AnswerServiceImpl.java'), size=7.5)

h2('（四）Controller：AnswerController')
code_block(read('backend/src/main/java/com/ddyu/zhikao/controller/AnswerController.java'), size=8)

# ---------------------------------------------------------------- 六、运行测试
h1('六、运行测试过程')

h2('（一）启动')
para('启动顺序为MySQL → Redis →后端8080 →前端5173。项目提供scripts/dev.sh一键启动，启动成功后访问http://127.0.0.1:5173。')
shot('后端启动日志，Started ZhikaoApplication', '图 6-1 后端启动', height=3.6)
shot('前端Vite启动日志', '图 6-2 前端启动', height=3.0)

h2('（二）Postman接口测试')
table(['接口', '请求要点', '预期', '实际'], [
    ['POST /api/auth/login', 'admin / admin123', '200，返回token', '通过'],
    ['POST /api/auth/register', '用户名已存在', '400，用户名已被注册', '通过'],
    ['GET /api/banks', '不带令牌', '401，登录已失效', '通过'],
    ['POST /api/banks', '考生令牌', '403，无权限', '通过'],
    ['POST /api/questions/import', 'multipart + bankId', '200，imported=20', '通过'],
    ['POST /api/answers/submit', '同一试卷交两次', '第二次409', '通过'],
], cap='表 6-1 Postman 测试记录', widths=[5.6, 4.6, 5.0, 2.0])
shot('Postman登录接口，请求体与返回token', '图 6-3 Postman 登录', height=3.6)
shot('Postman无令牌访问返回401', '图 6-4 Postman 未授权', height=3.2)

h2('（三）页面功能演示')
table(['操作', '验证点'], [
    ['管理员登录进概览', '四个统计卡片显示题库、题目、试卷、考生数量'],
    ['新增题库，组别填“第一章”', '组别可自定义，列表显示“第一章”'],
    ['题库组别留空', '列表显示“未分组”，不报错'],
    ['Word导入20题', '导入成功提示，列表新增20条'],
    ['新建试卷并发布', '状态从草稿变已发布，总分100'],
    ['考生进考场答题交卷', '倒计时正常，交卷后出分'],
    ['管理员看成绩明细', '逐题显示对错与得分'],
    ['个人资料改昵称', '顶栏昵称立即更新'],
], cap='表 6-2 页面功能演示', widths=[6.0, 8.0])
shot('管理员概览页', '图 6-5 概览', height=3.8)
shot('新增题库弹窗，组别填“第一章”', '图 6-6 新增题库', height=3.8)
shot('考试中心，显示可考试卷与我的得分', '图 6-7 考试中心', height=3.8)
shot('交卷后的成绩页', '图 6-8 交卷成绩', height=3.8)

h2('（四）多表查询')
para('成绩聚合一条SQL同时关联answer_record、exam_paper、sys_user，算出总分、正确数、未答数和正确率：')
code_block('''SELECT ar.paper_id, p.title, u.nickname,
       SUM(ar.score)                            AS totalScore,
       SUM(ar.correct = 1)                      AS correctCount,
       SUM(ar.chosen IS NULL)                   AS blankCount,
       ROUND(SUM(ar.correct = 1) / COUNT(*), 2) AS accuracy
FROM answer_record ar
JOIN exam_paper p ON p.id = ar.paper_id
JOIN sys_user  u ON u.id = ar.user_id
GROUP BY ar.paper_id, ar.user_id, p.title, u.nickname
ORDER BY ar.paper_id, totalScore DESC;''', size=8)
table(['试卷', '考生', '总分', '正确', '正确率'], [
    ['408数据结构与计算机组成原理', '李同学', '92', '18', '0.90'],
    ['408数据结构与计算机组成原理', '陈同学', '68', '12', '0.60'],
    ['408操作系统与计算机网络', '王同学', '84', '16', '0.80'],
], cap='表 6-3 成绩聚合结果', widths=[7.4, 2.6, 1.8, 1.8, 1.8])
shot('Navicat执行聚合SQL的结果', '图 6-9 多表查询', height=3.8)

h2('（五）Redis缓存')
code_block('''127.0.0.1:6379> KEYS login:token:*
1) "login:token:9f2c4e1a7b8d4c3e9a6f5d2b1c0e8a7f"
127.0.0.1:6379> TTL login:token:9f2c4e1a7b8d4c3e9a6f5d2b1c0e8a7f
(integer) 1793
127.0.0.1:6379> TTL dict:banks
(integer) 1745
127.0.0.1:6379> KEYS cache:ranking:*
1) "cache:ranking:1"''', size=8)
shot('redis-cli查看三类缓存key与TTL', '图 6-10 Redis 缓存', height=3.4)

h2('（六）异常处理')
table(['场景', '状态码', '返回信息'], [
    ['未带令牌', '401', '登录已失效，请重新登录'],
    ['考生调管理接口', '403', '无权限，仅管理员可操作'],
    ['题目不存在', '404', '题目不存在'],
    ['题库下有题仍删除', '409', '题库下还有题目，不能删除'],
    ['重复交卷', '409', '同一考生同一试卷只能交一次卷'],
    ['用户名重复注册', '400', '用户名已被注册，请换一个'],
], cap='表 6-4 异常处理场景', widths=[6.2, 2.4, 5.4])
shot('重复交卷返回409', '图 6-11 重复交卷', height=3.2)

h2('（七）自动化测试')
para('三个端到端脚本用curl直接打接口并断言，共87条断言，覆盖登录、权限、题库、题目、试卷、考试、交卷、成绩、缓存与异常。')
table(['脚本', '覆盖内容', '断言', '结果'], [
    ['e2e-api.sh', '认证、题库、题目、试卷、交卷、成绩、权限、缓存', '51', '通过'],
    ['e2e-extra.sh', '批量移动、撤销成绩、排行榜缓存、边界校验', '18', '通过'],
    ['e2e-exam-room.sh', '考试中心、进考场、答题、交卷、我的成绩', '18', '通过'],
], cap='表 6-5 自动化测试结果', widths=[4.6, 7.4, 1.6, 1.6])
shot('终端执行三个e2e脚本全部通过', '图 6-12 自动化测试', height=3.2)

# ---------------------------------------------------------------- 七、实验总结
h1('七、实验总结')

h2('（一）实验收获')
para('第一，分层不是形式。把判分规则、事务边界、缓存失效都放进Service后，改需求只需要动一个文件；Controller里只留接参数和包Result。')
para('第二，事务要真的抛异常。Word导入要求“错一道全批回滚”，一开始把解析异常catch成返回值，事务不回滚，改成抛BizException后才正确。')
para('第三，缓存难在失效。题库字典新增后要删、排行榜交卷后要删，否则页面一直是旧数据。')

h2('（二）问题与解决')
table(['问题', '原因', '解决'], [
    ['Word导入事务不回滚', '解析异常被catch成返回值', '改为抛BizException'],
    ['考生登录后被踢回登录页', '成绩接口改管理员专用，落地页仍调管理接口', '按角色分流到考试中心'],
    ['题库组别只能选本科/专科', 'DTO固定枚举，数据库列不允许空', '组别改为可选可自定义'],
    ['同一考生能重复交卷', '只在前端禁用按钮', 'Service先count再返回409'],
    ['多选少选给了满分', '只比较集合是否相等', '先判子集再判长度，真子集给一半'],
    ['排行榜分数不更新', '缓存写入后没失效', '交卷后delete排行榜key'],
    ['表格列宽在Word里被均分', '只设单元格宽度，没设tblGrid', 'tblLayout=fixed并同步gridCol'],
], cap='表 7-1 问题与解决方案', widths=[5.8, 7.0, 5.4])

h2('（三）不足与改进')
bullet('1. 令牌只有30分钟滑动过期，没有刷新令牌与单点登录踢下线。')
bullet('2. Element Plus全量引入，打包体积偏大，后续改按需引入。')
bullet('3. Word导入只支持固定文本格式，图片题与公式题暂不支持。')
bullet('4. 重复交卷是“先查后插”，高并发下仍可能重复，应加唯一索引兜底。')
bullet('5. 缓存只做了穿透保护，没有击穿互斥与雪崩随机过期。')
if __name__ == '__main__':
    doc.save(OUT)
    print('saved', OUT)
