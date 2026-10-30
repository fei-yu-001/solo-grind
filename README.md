# 智考 · 刷题考试系统

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

## 起本地环境

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
bash scripts/e2e-api.sh
```
