# 赛博进京赶考系统

第 17 届市调大赛题库的刷题与模考后台。Spring Boot + MyBatis-Plus + MySQL + Redis + Vue 3 前后端分离。

原有版本是 Node + Hono + SQLite 的本地刷题系统，这次按课程实验要求重构成 Java 技术栈，题库沿用原来的 185 道真题。

## 目录

```
zhikao/
├── backend/     Spring Boot 3.2.5 + MyBatis-Plus 3.5.9（8080）
├── frontend/    Vue 3 + Vite + Element Plus（5173）
├── sql/         schema.sql 建表、data.sql 测试数据
├── scripts/     gen-data.py 生成测试数据、e2e-api.sh 接口验收
└── docs/        CONTRACT.md 接口契约、PLAN.md 任务书对照、TASK-*.md 分工
```

## 一键启动

```bash
bash scripts/dev.sh          # 检查 MySQL/Redis 并起后端 8080 + 前端 5173
bash scripts/dev.sh stop     # 停掉两个服务
```

打开 http://127.0.0.1:5173

## 手工起环境（等价）

前置：JDK 21、Maven 3.9、Node 18+、MySQL 8（root / DDyu-996）、Redis 5（6379）。

```bash
# 1. 建库建表（Windows 下必须带 utf8mb4，否则中文报 1366）
mysql -uroot -pDDyu-996 --default-character-set=utf8mb4 < sql/schema.sql
mysql -uroot -pDDyu-996 --default-character-set=utf8mb4 < sql/data.sql

# 2. 起后端
cd backend && mvn spring-boot:run

# 3. 起前端
cd frontend && npm install && npm run dev
```

打开 http://localhost:5173

| 账号 | 密码 | 角色 |
| --- | --- | --- |
| admin | admin123 | 管理员 |
| student01 / student02 / student03 | student123 | 考生 |

## 接口

统一信封 `{code, message, data}`，除登录外都要 `Authorization: Bearer <token>`。
完整清单见 `docs/CONTRACT.md`。

## 数据库

9 张表，覆盖一对一（账号-资料）、一对多（题库-题目、试卷-作答、账号-作答）、多对多（题目-标签、试卷-题目）。

已有真实数据：185 道真题（本科组 85、专科组 100）、10 个知识点标签、2 张 100 分试卷、170 条历史作答。

## 验收

```bash
bash scripts/e2e-api.sh                              # 接口 51 条断言
bash scripts/e2e-exam-room.sh                        # 考生答题流程 18 条
bash scripts/e2e-extra.sh                            # 缓存/判分/批量/权限 18 条
node scripts/ui-check.mjs http://127.0.0.1:5173      # 六个页面巡检 + 截图
node scripts/ui-flow.mjs  http://127.0.0.1:5173      # 组卷端到端（真实鼠标事件）
node scripts/ui-exam-room.mjs http://127.0.0.1:5173  # 考试中心→答题→交卷→成绩明细
```

验收记录见 `docs/VERIFY.md`。

## 实验报告

- 报告：`docs/智考刷题系统-实验报告.docx`（由 `scripts/gen-report.py` 生成，表结构从建表脚本解析）
- 配图：`docs/diagrams/`（E-R 图、分层架构图、业务模块关系图，源文件是 SVG）
- 截图：`docs/screenshots/`

重新生成：

```bash
python scripts/gen-diagrams.py docs/diagrams
python scripts/gen-report.py
```
