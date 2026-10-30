# 新增任务：考生在线答题

目标：让考生能自己进考场做题。现在系统只有管理后台 + 成绩查看，考生没法答题。

接口定义已经写进 `docs/CONTRACT.md` 第 4.8 节，**先读那一节，字段名照抄**。

## 后端（zhikao-api）

新增三个接口，全部对 STUDENT 开放：

1. `GET /api/exams/available` → `ExamCardVO[]`
   - 只查 `status = PUBLISHED` 的试卷
   - 每张卷子带上当前考生的 `myScore` / `mySubmittedAt`（没交过为 null）
   - 一次查询解决：试卷 join 试卷题目数（子查询）+ 当前考生的成绩聚合（left join 或子查询），不要 N+1

2. `GET /api/exams/{paperId}/questions` → `ExamPaperViewVO`
   - 非 PUBLISHED → 409
   - 已交卷 → 409「你已经交过这份试卷了」
   - **返回体里不能出现 answer、analysis**（防作弊）。单独建一个 `ExamQuestionVO`（seq/questionId/type/typeText/stem/options/score），不要复用 QuestionVO 再用 @JsonIgnore 糊
   - 题目按 `exam_paper_question.seq` 排序

3. `GET /api/scores/mine?page=&size=` → 分页 `ScoreVO`
   - 只查当前登录考生的成绩
   - 复用现有的成绩聚合 SQL，加 userId 条件即可

另外改一处权限：`GET /api/scores/{paperId}/{userId}` 现在谁都能查，要改成「考生只能看自己的，看别人的 403，管理员不限」。

写一个 `ExamRoomService` 或挂到 PaperService/ScoreService 上都行，但 Controller 里不许写 SQL。要有 VO 组装、有校验。

验收（真跑，贴输出进 `backend/VERIFY.md`）：

```
# 用 student03 登录（id=4，还没交过任何卷子）
GET /api/exams/available            -> 2 张卷子，myScore 都是 null
GET /api/exams/1/questions          -> 85 道题，逐条检查 JSON 里没有 answer/analysis
GET /api/exams/2/questions          -> 100 道题
交卷 student03 答 3 道 -> POST /api/answers/submit
GET /api/exams/available            -> 这张卷子的 myScore 有值了
GET /api/exams/1/questions          -> 409
GET /api/scores/mine                -> 1 条，是自己的
student03 查 student01 的成绩       -> 403
admin 查 student01 的成绩           -> 200
# 清理：admin 撤销 student03 这份成绩，恢复原状
```

清理一定要做，数据库要回到 2 卷 / 170 条作答。

## 前端（zhikao-web）

新增两个页面 + 路由 + 菜单：

1. `/exam-center` 考试中心（考生主页）
   - 卡片或表格列出 `/api/exams/available`
   - 每张卷子显示：试卷名、题库、题量、总分、时长（分钟）
   - 没交过 → 「进入考场」按钮；交过 → 显示得分 + 「已交卷」，按钮变「查看成绩」
   - 顶部一句提示：「交卷后不能重考」

2. `/exam/:paperId` 答题页
   - 顶部固定：试卷名、倒计时（`durationSec` 秒，`mm:ss` 或 `hh:mm:ss`）、已答/总题数、交卷按钮
   - 左侧题干区：题号 + 题型标签 + 分值 + 题干 + 选项
     - 单选、判断：点一个（判断只有 A 对 / B 错 两个选项，按后端返回的 options 渲染）
     - 多选：可多选，再点取消
   - 右侧答题卡：题目序号宫格，已答高亮，点击跳题；底部「上一题 / 下一题」
   - 键盘：`A`-`E` 或 `1`-`5` 选选项，`←` `→` 翻题，`Enter` 下一题
   - 交卷前弹确认框，提示还有几题没答
   - 倒计时归零自动交卷
   - 交卷成功跳到成绩详情（用 `/api/scores/{paperId}/{userId}`），能看到逐题对错、你的答案、正确答案、得分
   - 答题过程中**绝不能**在页面上出现答案或解析（后端本来也不给）

3. 菜单与守卫
   - 考生菜单：「考试中心」「我的成绩」
   - 管理员菜单保持原样（概览/题库/题目/试卷/成绩），额外也加一个「考试中心」方便预览
   - 考生访问管理页仍然被挡回

样式沿用现有 Element Plus 风格，中文界面，不要 emoji。答题页要能在一屏内看到题干、选项和答题卡，不要整页滚动（这条是硬要求，我会用无头 Chrome 量）。

验收（真跑）：

1. `npm run build` 零报错
2. 用 student03 登录 → 考试中心能看到 2 张卷子 → 进考场 → 答几题 → 交卷 → 看到成绩明细
3. 把实际命令和结果写进 `frontend/VERIFY.md`；如果后端 8080 没起来就写「联调待架构师验证」，不要造假

## 边界

- 后端只碰 `backend/**`，前端只碰 `frontend/**`，都不要改 `docs/`
- 提交信息用英文 `feat(backend): ...` / `feat(web): ...`
