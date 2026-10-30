# 后端任务书（agent: zhikao-api）

你负责 `backend/**`。契约在 `docs/CONTRACT.md`，**先完整读一遍再动手**。骨架已经搭好并编译过，你只补业务。

## 0. 环境

- JDK 21、Maven 3.9、MySQL 8（root / DDyu-996）、Redis 5（6379，无密码）都已就绪
- 工作目录：`C:\Users\DDyu\Desktop\springboot\第七次实验\zhikao\backend`
- 编译 `mvn -B -q compile`，启动 `mvn -B spring-boot:run`（8080）
- 只在本地跑，不部署，不碰线上服务器

## 1. 数据库已经建好，直接用

```bash
mysql -uroot -pDDyu-996 --default-character-set=utf8mb4 zhikao -e "select count(*) from question;"
```

已有数据（都是真的，从旧系统导出来的真题）：

| 表 | 行数 | 说明 |
| --- | --- | --- |
| `sys_user` | 4 | admin/admin123（ADMIN），student01~03/student123（STUDENT） |
| `user_profile` | 4 | 与 sys_user 一对一 |
| `question_bank` | 2 | 本科组 85 题、专科组 100 题 |
| `question` | 185 | 单选 135、判断 35、多选 15 |
| `tag` | 10 | 知识点 |
| `question_tag` | 114 | 多对多关联 |
| `exam_paper` | 2 | 本科组卷 85 题 / 专科组卷 100 题，都是 100 分、已发布 |
| `exam_paper_question` | 185 | 试卷题目多对多，带题序和分值 |
| `answer_record` | 170 | 两位考生的历史作答 |

**不要重新造数据，也不要在代码里写死题目。** 需要补测试数据时用 SQL 插，别改 `sql/*.sql`（那是架构师的）。

注意 MySQL 客户端要带 `--default-character-set=utf8mb4`，否则中文会报 1366。

## 2. 要写的代码

按 `docs/CONTRACT.md` 第 4/5/6 节实现，目录已在：`entity / mapper / service / service/impl / controller / dto / vo`，XML 放 `resources/mapper/`。

四个核心功能，每个都要有增、删、改、条件查询、分页：

1. **题库管理** `BankController` — 分页查（关键字/组别/状态）、全部（走 Redis 字典）、详情、增、改、删（有题 409）
2. **题目管理** `QuestionController` — 分页查（题库/题型/关键字/难度/标签）、详情、增（带 tagIds）、改、删（被试卷引用 409）、批量移动题库
3. **试卷管理** `PaperController` — 分页查（关键字/状态/题库）、详情（含题目）、组卷（随机抽题，事务）、改（仅 DRAFT）、删、发布、结束
4. **成绩与作答** `AnswerController` + `ScoreController` — 交卷判分（事务）、成绩分页查、成绩明细、撤销成绩、统计、排行榜（Redis）

外加 `AuthController`（登录/登出/当前用户）和 `TagController`（标签列表 + 增删）。
`TokenStore`、`AuthInterceptor`、`Result`、`PageResult`、`BizException`、全局异常都写好了，直接用。

## 3. Service 层必须做出来的东西（评分点）

- **事务**：组卷（写 exam_paper + 批量写 exam_paper_question）、交卷（批量写 answer_record）、批量移动题目、删题库/删题目
- **业务校验**（每条给不同文案）：
  - 题库下还有题目 → 不能删（409）
  - 题目被试卷引用 → 不能删（409）
  - 组卷时某个题型题量不够 → 409「题库里多选题只剩 3 道，组不出来 15 道」
  - 只有 DRAFT 能改组卷，PUBLISHED/CLOSED 拒绝（409）
  - 只有 PUBLISHED 能交卷（409）
  - 同一考生同一试卷只能交一次（409）
  - 非 ADMIN 做管理操作 → 403
- **判分**：严格按契约 4.7，多选支持少选得一半分；写在 Service 里，Controller 不许算分
- **VO 组装**：All 查询返回 VO（`bankName`、`typeText`、`tags`、`questionCount`、`accuracy` 这些都在 Service 拼）
- **缓存**：契约第 5 节三个场景，读缓存打命中/未命中日志
- **批量**：交卷批量写、批量移动题目、统计聚合按题型/题库分组

## 4. 多表查询写 XML，且分页不许踩坑

XML 里要有的多表查询：

- `QuestionMapper.xml`：分页查（question join question_bank，条件多）+ 按 id 批量查 + 标签二次查询（`IN`）
- `BankMapper.xml`：分页查（bank + 题目数子查询）
- `PaperMapper.xml`：分页查（paper join bank + 题目数子查询）、试卷明细（paper_question join question，按 seq 排）
- `ScoreMapper.xml`：成绩分页（answer_record join sys_user join exam_paper，按 paper+user 分组聚合）、逐题明细（answer_record join question）、统计聚合

**硬规则**：分页查询的 SQL 里不许出现一对多 join。`question_tag`、`exam_paper_question` 这类会导致行数翻倍的关联，一律拆成「先分页拿主键，再一次 `IN` 查回来在 Service 装配」。踩了这个坑不会报错，只是页大小和 total 静默错位。

## 5. 验收（必须真跑，不许写「应该可以」）

1. `mvn -B -q compile` 通过，`mvn -B spring-boot:run` 起得来，日志无异常
2. **跑架构师的验收脚本**：`bash ../scripts/e2e-api.sh`（我写好了 40 多条断言，全绿才算过）
3. 另外手工补测脚本没覆盖的：批量移动题目、撤销成绩、非 ADMIN 调管理接口 403、交卷两次 409
4. 把真实命令和真实输出贴进 `backend/VERIFY.md`
5. 抽查一条分页 SQL，确认 total 与页大小对得上（比如 size=10 时每页正好 10 条、最后一页是余数）

## 6. 交付

- commit message 用英文 `feat(backend): ...`，一个 commit 一件事
- 只提交 `backend/` 下的东西
- 干完在最后一条消息说：改了哪些文件、跑了哪些命令、真实输出摘要、没做什么
- 拿不准停下来问，不要改 `docs/`
