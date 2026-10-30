# 接口与分层契约（唯一真源）

智考 · 刷题考试系统。前后端两个 agent 都按这里写，**不要自己改字段名**。发现契约有问题先停下来问。

## 1. 技术栈与端口

| 层 | 技术 | 端口 |
| --- | --- | --- |
| 后端 | Spring Boot 3.2.5 + MyBatis-Plus 3.5.9 + JDK 21 | 8080 |
| 数据库 | MySQL 8.0（库名 `zhikao`） | 3306 |
| 缓存 | Redis 5（无密码，db 0） | 6379 |
| 前端 | Vue 3 + Vite + Element Plus + axios | 5173 |

前端 dev server 用 vite proxy 把 `/api` 转到 `http://localhost:8080`，代码里一律写相对路径 `/api/xxx`。

## 2. 统一返回格式

```json
{ "code": 0, "message": "ok", "data": {} }
```

分页：

```json
{ "code": 0, "message": "ok", "data": { "total": 185, "page": 1, "size": 10, "records": [] } }
```

| code | HTTP | 含义 |
| --- | --- | --- |
| 0 | 200 | 成功 |
| 400 | 400 | 参数校验失败 |
| 401 | 401 | 未登录 / 令牌失效 |
| 403 | 403 | 无权限（非管理员做管理操作） |
| 404 | 404 | 资源不存在 |
| 409 | 409 | 业务冲突（被引用不能删、状态不允许、重复交卷） |
| 500 | 500 | 服务端异常 |

## 3. 认证

除 `POST /api/auth/login` 外，所有 `/api/**` 都要带 `Authorization: Bearer <token>`。
令牌存 Redis，key `login:token:<token>`，value 是 `{id, username, nickname, role}` 的 JSON，TTL 1800 秒，每次校验续期。

管理类接口（增删改）只允许 `role=ADMIN`，否则 403。

## 4. 接口清单

### 4.1 认证

| 方法 | 路径 | 入参 | 出参 data |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | `{username, password}` | `{token, id, username, nickname, role}` |
| POST | `/api/auth/logout` | - | `null` |
| GET | `/api/auth/me` | - | `{id, username, nickname, role}` |

### 4.2 题库（核心功能一）

| 方法 | 路径 | 入参 | 出参 data |
| --- | --- | --- | --- |
| GET | `/api/banks` | `keyword` `groupName` `status` `page` `size` | 分页 `BankVO` |
| GET | `/api/banks/all` | - | `BankVO[]`（下拉用，走 Redis 字典缓存） |
| GET | `/api/banks/{id}` | - | `BankVO` |
| POST | `/api/banks` | `{name, groupName, description, status}` | `BankVO` |
| PUT | `/api/banks/{id}` | 同上 | `BankVO` |
| DELETE | `/api/banks/{id}` | - | `null`，题库下有题目时 409 |

`BankVO`：`{ "id":1, "name":"市调大赛17届·本科组", "groupName":"本科组", "description":"...", "status":"ENABLED", "statusText":"启用", "questionCount":85, "createdAt":"2026-10-30 10:00:00" }`

`questionCount` 是这个题库的题目数（多表统计）。

### 4.3 题目（核心功能二）

| 方法 | 路径 | 入参 | 出参 data |
| --- | --- | --- | --- |
| GET | `/api/questions` | `bankId` `type` `keyword` `difficulty` `tagId` `page` `size` | 分页 `QuestionVO` |
| GET | `/api/questions/{id}` | - | `QuestionVO` |
| POST | `/api/questions` | `QuestionForm` | `QuestionVO` |
| PUT | `/api/questions/{id}` | `QuestionForm` | `QuestionVO` |
| DELETE | `/api/questions/{id}` | - | `null`，被试卷引用时 409 |
| PATCH | `/api/questions/batch` | `{ids:[1,2], bankId:3}` | `{updated:2}`（批量移动到题库） |

`QuestionForm`：

```json
{
  "bankId": 1,
  "type": "single",
  "stem": "在市场经济条件下，企业的活动与市场的关系表现为（ ）。",
  "options": [{ "key": "A", "text": "与市场可以有联系" }],
  "answer": "B",
  "analysis": "解析文字，可为空",
  "difficulty": 1,
  "sortNo": 1,
  "tagIds": [1, 3]
}
```

`answer` 的类型：单选是字符串 `"B"`，多选是数组 `["A","C"]`，判断是 `"A"`（对）或 `"B"`（错）。

`QuestionVO`：

```json
{
  "id": 1, "bankId": 1, "bankName": "市调大赛17届·本科组",
  "type": "single", "typeText": "单选题",
  "stem": "...", "options": [{ "key": "A", "text": "..." }],
  "answer": "B", "analysis": "...",
  "difficulty": 1, "difficultyText": "易", "sortNo": 1,
  "tags": [{ "id": 1, "name": "抽样方法" }],
  "createdAt": "2026-10-30 10:00:00"
}
```

### 4.4 标签（只读 + 轻量增删，供题目表单多选）

| 方法 | 路径 | 入参 | 出参 data |
| --- | --- | --- | --- |
| GET | `/api/tags` | - | `TagVO[]` |
| POST | `/api/tags` | `{name, color}` | `TagVO` |
| DELETE | `/api/tags/{id}` | - | `null` |

`TagVO`：`{ "id":1, "name":"抽样方法", "color":"#e6a23c", "questionCount": 23 }`

### 4.5 试卷（核心功能三）

| 方法 | 路径 | 入参 | 出参 data |
| --- | --- | --- | --- |
| GET | `/api/papers` | `keyword` `status` `bankId` `page` `size` | 分页 `PaperVO` |
| GET | `/api/papers/{id}` | - | `PaperDetailVO`（含题目） |
| POST | `/api/papers` | `PaperForm` | `PaperVO`（组卷，事务） |
| PUT | `/api/papers/{id}` | `PaperForm` | `PaperVO`（仅 DRAFT 可改） |
| DELETE | `/api/papers/{id}` | - | `null` |
| POST | `/api/papers/{id}/publish` | - | `PaperVO`（DRAFT → PUBLISHED） |
| POST | `/api/papers/{id}/close` | - | `PaperVO`（PUBLISHED → CLOSED） |

`PaperForm`（组卷参数，后端按题型从题库随机抽题）：

```json
{
  "title": "第17届市调大赛·本科组全真模考",
  "bankId": 1,
  "judgeCount": 11, "singleCount": 59, "multiCount": 15,
  "judgeScore": 1, "singleScore": 1, "multiScore": 2,
  "durationSec": 6000
}
```

`PaperVO`：

```json
{
  "id": 1, "title": "...", "bankId": 1, "bankName": "...",
  "judgeCount": 11, "singleCount": 59, "multiCount": 15,
  "judgeScore": 1, "singleScore": 1, "multiScore": 2,
  "durationSec": 6000, "totalScore": 100, "questionCount": 85,
  "status": "PUBLISHED", "statusText": "已发布",
  "createdAt": "2026-10-30 10:00:00"
}
```

`PaperDetailVO` = `PaperVO` + `questions: PaperQuestionVO[]`：

```json
{ "seq": 1, "score": 1, "id": 12, "type": "judge", "typeText": "判断题", "stem": "...", "options": [], "answer": "A", "analysis": null, "tags": [] }
```

### 4.6 成绩与作答（核心功能四）

| 方法 | 路径 | 入参 | 出参 data |
| --- | --- | --- | --- |
| POST | `/api/answers/submit` | `{paperId, answers:[{questionId, chosen}]}` | `ScoreVO`（交卷判分，事务） |
| GET | `/api/scores` | `paperId` `keyword` `page` `size` | 分页 `ScoreVO` |
| GET | `/api/scores/{paperId}/{userId}` | - | `ScoreDetailVO`（逐题明细） |
| DELETE | `/api/scores/{paperId}/{userId}` | - | `null`（撤销成绩） |
| GET | `/api/scores/stats` | - | `StatsVO` |
| GET | `/api/scores/ranking` | `paperId` `limit`(默认10) | `RankingVO[]`（Redis 缓存 300 秒） |

`ScoreVO`：

```json
{
  "paperId": 1, "paperTitle": "...", "maxScore": 100,
  "userId": 2, "username": "student01", "nickname": "李同学",
  "totalScore": 72, "correctCount": 61, "wrongCount": 20, "blankCount": 4,
  "questionCount": 85, "accuracy": 0.72,
  "submittedAt": "2026-10-28 10:00:00"
}
```

`ScoreDetailVO` = `ScoreVO` + `items: [{seq, questionId, typeText, stem, chosen, answer, correct, score}]`

`StatsVO`：

```json
{
  "bankCount": 2, "questionCount": 185, "paperCount": 2, "userCount": 4,
  "submittedCount": 2, "avgScore": 63.5, "maxScore": 72, "passRate": 0.5,
  "byType": [{ "typeText": "单选题", "count": 135 }],
  "byBank": [{ "bankName": "市调大赛17届·本科组", "questionCount": 85 }]
}
```

`RankingVO`：`{ "rank": 1, "userId": 2, "nickname": "李同学", "totalScore": 72 }`

### 4.7 判分规则（后端 Service 实现，前端不允许自己算分）

- 单选、判断：作答与标准答案完全一致得满分，否则 0 分
- 多选：全对得满分；少选（作答是标准答案的真子集）得一半分（向下取整）；多选或错选 0 分
- 未作答：0 分，计入 `blankCount`
- 满分 = 各题分值之和，就是 `exam_paper.total_score`

## 5. Redis 使用点

| 场景 | key | 结构 | TTL | 说明 |
| --- | --- | --- | --- | --- |
| 登录令牌 | `login:token:<token>` | String(JSON) | 1800s | 登录写入，校验后续期，登出删除 |
| 题库字典 | `dict:banks` | String(JSON 数组) | 3600s | cache-aside；查不到写 `__EMPTY__` 空值标记 60 秒防穿透；题库增删改后删除 |
| 成绩排行 | `cache:ranking:<paperId>` | String(JSON 数组) | 300s | 排行榜缓存；交卷/撤销成绩后删除 `cache:ranking:*` |

读缓存要有日志：`log.info("[cache] 题库字典 命中/未命中")`，报告要截图。

## 6. 分层与文件归属

```
com.ddyu.zhikao
├── ZhikaoApplication.java
├── common/     Result、PageResult、BizException、全局异常、LoginUser、LoginContext、CacheKeys
├── config/     MybatisPlus 分页、TokenStore、AuthInterceptor、WebConfig、SecurityConfig
├── entity/     与表一一对应
├── mapper/     Mapper 接口（继承 BaseMapper）
├── service/ + service/impl/
├── controller/
├── dto/        入参对象
└── vo/         出参对象
```

硬性规矩：

1. Controller 不写 SQL、不调 Mapper，只能调 Service
2. Service 不返回 Entity，一律 VO 或 `PageResult<VO>`
3. 多表查询写进 `resources/mapper/*.xml`，`resultMap` 显式映射，禁止 `SELECT *`
4. 组卷、交卷、批量移动、删题库/题目必须 `@Transactional`
5. **分页查询不许 join 一对多集合**（会按行切页导致页边界错乱）：分页只查主表行，关联数据用第二次 IN 查询在 Service 里装配
6. 参数校验用 `jakarta.validation` + `@Valid`，由全局异常处理转 400

## 7. 文件归属

| 目录 | 归属 |
| --- | --- |
| `backend/**` | 后端 agent |
| `frontend/**` | 前端 agent |
| `sql/**`、`docs/**`、`scripts/**`、`README.md` | 架构师（agent 不要改） |

两个 agent 只在本地跑，不部署、不碰任何线上服务器。
