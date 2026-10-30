# 实验任务书逐条对照表

任务书：`实验一：SpringBoot+MyBatis+Redis 前后端分离后台系统开发实验任务书.pdf`
选题：**智考 · 刷题考试系统**（原有赶考系统的 Spring Boot 重构版）
本表既是开发检查表，也是实验报告「系统架构设计」一章的底稿。

## 二、技术栈硬性要求

| 任务书要求 | 本项目实现 | 证据 |
| --- | --- | --- |
| Spring Boot + MyBatis/MyBatisPlus | Spring Boot 3.2.5 + MyBatis-Plus 3.5.9 | `backend/pom.xml` |
| MySQL | MySQL 8.0.46，库 `zhikao` | `sql/schema.sql` |
| Redis | Redis 5.0，三处缓存业务 | `config/TokenStore.java`、`service/impl/*` |
| Vue 或 Thymeleaf | Vue 3 + Vite + Element Plus | `frontend/` |
| 前后端分离 + RESTful | 前端 5173 / 后端 8080，全 `/api/**` | `docs/CONTRACT.md` |

## 三、数据库设计要求

| 任务书要求 | 本项目实现 | 证据 |
| --- | --- | --- |
| ≥4 张表 | 9 张 | `sql/schema.sql` |
| 一对一 | `sys_user` ↔ `user_profile`（`user_id` 唯一约束 `uk_profile_user`） | 外键 `fk_profile_user` |
| 一对多 | `question_bank` → `question`；`exam_paper` → `answer_record`；`sys_user` → `answer_record` | `fk_question_bank`、`fk_answer_paper`、`fk_answer_user` |
| 多对多 | `question` ↔ `tag`（`question_tag`）；`exam_paper` ↔ `question`（`exam_paper_question`） | 两张联合主键中间表 |
| E-R 图 + 字段说明 | 报告阶段出图 | 待产出 |
| 禁止只用单表查询 | 题库/题目/试卷/成绩四个分页查询全是多表 join，统计接口三表聚合 | `resources/mapper/*.xml` |

表清单：

| 表 | 含义 | 行数（已有真实数据） |
| --- | --- | --- |
| `sys_user` | 登录账号（ADMIN / STUDENT） | 4 |
| `user_profile` | 考生资料，与账号一对一 | 4 |
| `question_bank` | 题库 | 2 |
| `question` | 题目，含选项 JSON、答案 JSON | 185 |
| `tag` | 知识点标签 | 10 |
| `question_tag` | 题目标签多对多 | 114 |
| `exam_paper` | 试卷，含题型配比与分值 | 2 |
| `exam_paper_question` | 试卷题目多对多，带题序和分值 | 185 |
| `answer_record` | 作答记录 | 170 |

## 四、功能开发要求

四个核心功能，每个都有「增、删、改、条件查询、分页查询」：

| 核心功能 | 增 | 删 | 改 | 条件查询 + 分页 |
| --- | --- | --- | --- | --- |
| 题库管理 | `POST /api/banks` | `DELETE /api/banks/{id}`（有题 409） | `PUT /api/banks/{id}` | `GET /api/banks?keyword&groupName&status&page&size` |
| 题目管理 | `POST /api/questions`（带 tagIds） | `DELETE /api/questions/{id}`（被引用 409） | `PUT`、`PATCH /api/questions/batch` 批量移动 | `GET /api/questions?bankId&type&keyword&difficulty&tagId&page&size` |
| 试卷管理 | `POST /api/papers`（组卷，事务） | `DELETE /api/papers/{id}` | `PUT /api/papers/{id}`（仅草稿）、`publish`/`close` 状态流转 | `GET /api/papers?keyword&status&bankId&page&size` |
| 成绩与作答 | `POST /api/answers/submit`（交卷判分） | `DELETE /api/scores/{paperId}/{userId}` | 交卷即写入，撤销后重交 | `GET /api/scores?paperId&keyword&page&size` |

Redis 应用（任务书要求至少一项，本项目三项）：

| 场景 | key | 策略 |
| --- | --- | --- |
| 登录令牌缓存 | `login:token:<token>` | 写 30 分钟，每次校验续期，登出删除 |
| 题库字典缓存 | `dict:banks` | cache-aside，空值标记 60 秒防穿透，题库变更失效 |
| 成绩排行缓存 | `cache:ranking:<paperId>` | 300 秒 TTL，交卷/撤销后清 |

## 五、Service 层硬性约束

任务书要求至少两项，本项目五项全做：

| 要求 | 本项目做法 |
| --- | --- |
| 事务管理 | 组卷（写试卷 + 批量写试卷题目）、交卷（批量写作答记录）、批量移动题目、删题库/题目，全部 `@Transactional` |
| 业务校验 | 题库有题不能删、题目被引用不能删、组卷题量超出题库 409、只有草稿能改组卷、只有已发布能交卷、同卷只能交一次、非管理员 403 |
| 数据封装 | `BankVO` 带题目数、`QuestionVO` 带题库名与标签、`PaperVO` 带题库名与题数、`ScoreVO` 聚合正确率与未答数，Controller 不返回 Entity |
| 缓存逻辑 | 先查缓存 → 未命中查库 → 回写；空结果写 `__EMPTY__` 防穿透；变更后主动失效 |
| 批量处理 | 交卷批量写、批量移动题目、统计按题型/题库分组聚合、排行榜一次查出 |

## 六、分层与模块

```
Entity（9 个） → Mapper（9 个接口 + XML） → Service（6 个接口 + 实现） → Controller（7 个）
```

禁止跨层：Controller 不写 SQL、不调 Mapper；Service 不返回 Entity。

## 七、报告阶段要产出

1. 系统分层架构图
2. 业务模块关系图（Entity → Mapper/XML → Service → Controller）
3. E-R 图 + 字段说明表
4. 核心源码节选
5. 运行测试截图：接口测试、前端页面、增删改查、多表查询、Redis 缓存、异常处理（401/403/409）
6. 实验总结
