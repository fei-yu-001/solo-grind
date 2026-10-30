# 后端验证记录（VERIFY）

验证时间：2026-10-30 15:30 ~ 17:00（本机 Windows 11，JDK 21，Maven 3.9）

环境前提：MySQL `zhikao` 库已灌初始数据（185 题 / 2 题库 / 2 卷 / 170 作答），Redis 6379 无密码。
启动方式：`mvn -B spring-boot:run`（8080）。

> 注：本机 Git Bash 传 UTF-8 参数给原生 curl.exe 会被转码成 GBK，
> 架构师的 e2e-api.sh 里带中文的 URL/body 会因此失败。
> 验证时用 `/tmp/zhikao-bin/curl` 包装器（URL 百分号编码 + body 走临时文件），
> `export PATH=/tmp/zhikao-bin:$PATH` 后原样跑脚本，不改脚本本身。

## 1. 编译

```
mvn -B -q compile
（无输出，退出码 0）
```

## 2. 验收脚本 e2e-api.sh（架构师提供，51 条断言）

```
$ export PATH=/tmp/zhikao-bin:$PATH
$ bash scripts/e2e-api.sh
== 0. 未带令牌
  [ok]   GET /api/banks 无 token
== 1. 登录与身份
  [ok]   管理员登录取到 token
  [ok]   密码错误 401
  [ok]   当前用户是 admin
  [ok]   管理员角色
  基线：题库 2 个，题目 185 道
== 2. 题库：分页、条件、增改删
  [ok]   题库分页 size=1 返回 1 条
  [ok]   题库 total 等于基线
  [ok]   按组别过滤
  [ok]   题库带题目数
  [ok]   新增题库 id=5
  [ok]   按关键字查到自己
  [ok]   改题库名
== 3. 题目：分页、条件、标签、增改删、批量移动
  [ok]   题目总数等于基线
  [ok]   size=10 正好 10 条
  [ok]   按题型过滤（判断题 35）
  [ok]   按题库过滤（本科 85）
  [ok]   按标签过滤不报错
  [ok]   新增题目 id=187
  [ok]   详情带题库名
  [ok]   详情带标签（多对多）
  [ok]   题干可改
  [ok]   题型改成功
== 4. 试卷：组卷（事务）、明细、状态流转
  [ok]   组卷成功 id=4
  [ok]   组卷总分 2*1+3*1+1*2=7
  [ok]   组卷题目数 6
  [ok]   题序从 1 开始
  [ok]   题量超出题库 409
  [ok]   发布试卷
  [ok]   已发布不能改组卷 409
== 5. 交卷判分
  [ok]   考生交卷成功
  [ok]   得分等于答对题分（前两题都对）
  [ok]   答对题数 2
  [ok]   未答计入 blankCount
  [ok]   同一考生同卷再交 409
  [ok]   成绩列表能查到
  [ok]   成绩明细有逐题
  [ok]   排行榜可用
  [ok]   统计题目数不小于基线
== 6. 权限与引用校验
  [ok]   考生调管理接口 403
  [ok]   题库下有题不能删 409
  [ok]   题目被试卷引用不能删 409
== 7. Redis
  [ok]   令牌 TTL=1800s
  [ok]   题库字典进缓存
  [ok]   排行榜进缓存
== 8. 清理
  [ok]   撤销成绩
  [ok]   结束试卷
  [ok]   删除试卷
  [ok]   删除题目
  [ok]   删除题库
  [ok]   登出
  [ok]   登出后旧 token 401

结果: 51 通过, 0 失败
```

## 3. 判断题存修格式修复后的复验（fix: judge answer 存储统一为 "A"/"B" 字符串）

修复内容：toAnswerJson 删掉 judge 布尔特判（与单选一样存 JSON 字符串）；
parseAnswer 按 String 读、读失败兼容历史 true/false 映射成 A/B（Question/Paper/Answer/Score 四处）；
toOptionsJson 判断题默认 [{key:A,text:对},{key:B,text:错}]，前端传了用前端的；
QuestionForm 的 options 不再 @NotNull，判断题可不传。

接口实测：
```
GET /api/questions?type=judge&page=1&size=1
  -> type= judge answer= 'B'（干净字符串，不带引号）
GET /api/papers/1
  -> seq=1 type=judge answer='B'；seq=2 type=judge answer='A'
```

e2e-api.sh（脚本更新后首跑，无需 curl 包装器）：51 通过, 0 失败（输出同第 2 节）。

判断题交卷判分手工验（scripts/e2e-judge-check.py，10 条断言全过）：
```
  [ok]   组卷成功
  [ok]   试卷里判断题 answer 是干净字符串
  [ok]   判断题字符串作答交卷不报 500
  [ok]   全对 totalScore=3
  [ok]   correctCount=3
  [ok]   blankCount=0
  [ok]   明细 answer 是干净字符串
  [ok]   明细 chosen 是干净字符串
  [ok]   1 对 2 错 totalScore=1
  [ok]   correctCount=1
结果: 10 通过, 0 失败
```

## 4. 考生在线答题（契约 4.8，scripts/e2e-examroom.py，30 条断言）

新增：ExamController（available / {paperId}/questions）、GET /api/scores/mine、
明细归属校验（考生只能看自己的，别人 403，管理员不限）。
防作弊：ExamQuestionVO 独立建，SQL 层就不查 answer/analysis，并递归检查整棵 JSON 无泄漏。

```
  [ok]   available 200 且 2 张卷子
  [ok]   按 id 倒序
  [ok]   myScore 都是 null
  [ok]   mySubmittedAt 都是 null
  [ok]   卡片字段齐全
  [ok]   exam view 200 且 85 题
  [ok]   questionCount=85
  [ok]   seq 从 1 连续到 85
  [ok]   整棵 JSON 无 answer/analysis
  [ok]   题目字段只含 seq/questionId/type/typeText/stem/options/score
  [ok]   题型分布 判断11/单选59/多选15
  [ok]   paper2 100 题
  [ok]   paper2 无 answer/analysis
  [ok]   交卷 200
  [ok]   questionCount=85（全卷落库）
  [ok]   totalScore >= 0
  [ok]   card1 myScore=0
  [ok]   card1 mySubmittedAt 非空
  [ok]   card2 myScore 仍为 null
  [ok]   已交卷再进考场 409
  [ok]   409 文案（你已经交过这份试卷了）
  [ok]   mine 200 且 1 条
  [ok]   mine 是自己的（userId=4）
  [ok]   mine totalScore 与交卷一致
  [ok]   考生查别人明细 403
  [ok]   考生查自己明细 200
  [ok]   admin 查别人明细 200
  [ok]   admin 撤销 student03 成绩 200
  [ok]   清理后 mine total=0
  [ok]   清理后 available myScore 恢复 null
结果: 30 通过, 0 失败
```

跑完回归旧 e2e：51 通过, 0 失败；数据库恢复基线：
```
mysql> select (select count(*) from exam_paper) p,(select count(*) from answer_record) a;
p    a
2    170
```

实现说明：available 用一条 SQL（试卷 + 题目数子查询 + 当前考生成绩 left join 聚合），无 N+1；
考场题目按 exam_paper_question.seq 排序，只查安全列；optionsJson 中转字段加 @JsonIgnore 不出 JSON。

## 5. 手工补测（scripts/e2e-supplement.py，10 条断言）

脚本没覆盖的四项 + 判分边界，`python scripts/e2e-supplement.py`（urllib 直连 8080）：

```
  [ok]   多选全对+少选半分：totalScore=0+2+1（期望 3，实际 3）
  [ok]   correctCount=1（只有全对的多选）（期望 1，实际 1）
  [ok]   wrongCount=2（单选错+多选少选不算对）（期望 2，实际 2）
  [ok]   blankCount=0（期望 0，实际 0）
  [ok]   questionCount=3（期望 3，实际 3）
  [ok]   重复交卷 409（期望 409，实际 409）
  [ok]   撤销成绩 200（期望 200，实际 200）
  [ok]   撤销后成绩列表 total=0（期望 0，实际 0）
  [ok]   撤销后明细 404（期望 404，实际 404）
  [ok]   撤销后排行榜为空数组（期望 []，实际 []）
结果: 10 通过, 0 失败
```

补测用例说明：

- **多选半分**：临时组卷 1 单选(1分)+2 多选(2分)，交卷（单选故意答错、多选1全对、多选2少选1个），
  验证 0 + 2 + 1 = 3 分，即契约 4.7 的「少选（真子集）得一半分（向下取整）」
- **correct 口径**：`correct = (本题得满分)`，因此 correct + wrong + blank 恒等于题目数，
  多选少选（得一半分）计入 wrongCount
- **重复交卷**：同一考生同卷第二次 submit → 409
- **撤销成绩**：DELETE /api/scores/{paperId}/{userId} → 200，之后成绩列表 total=0、明细 404、排行榜空
- **批量移动**（e2e 前置验证，同批命令）：
  `PATCH /api/questions/batch {"ids":[188,189],"bankId":7}` → `{"updated":2}`，
  详情确认两题 bankId/bankName 已变为目标题库，测完删除
- **403 全套**（15 条，考生 token 调全部管理接口，均 403）：
  POST/PUT/DELETE /api/banks、POST/PUT/DELETE /api/questions、PATCH /api/questions/batch、
  POST/PUT/DELETE /api/papers、POST /api/papers/{id}/publish、POST /api/papers/{id}/close、
  POST/DELETE /api/tags、DELETE /api/scores/{paperId}/{userId}
- **分页边界抽查**：题目 total=187 时（含临时题），size=10 第 19 页 7 条、第 20 页 0 条，total 与页大小对得上

## 6. Redis 缓存日志（服务端 /tmp/zhikao-server.log 摘录）

```
[cache] 登录令牌写入 token=667115f6... admin=admin
[cache] 交卷后清除排行榜缓存 1 个
[cache] 排行榜 paperId=6 未命中，回源数据库
[cache] 题库增删改，删除字典缓存
[cache] 题库字典 未命中，回源数据库
[cache] 排行榜 paperId=7 未命中，回源数据库
[cache] 排行榜 paperId=7 命中
```

字典 TTL 3600s、空值标记 60s（`dict:banks` 存 `__EMPTY__`），排行榜 TTL 300s（`cache:ranking:<paperId>`），
交卷/撤销成绩后删 `cache:ranking:*`，题库增删改后删 `dict:banks`。

## 7. 数据一致性

跑完所有验证后数据库与初始状态一致，无残留：

```
mysql> select (select count(*) from question) q,(select count(*) from question_bank) b,
              (select count(*) from exam_paper) p,(select count(*) from answer_record) a,
              (select count(*) from sys_user) u,(select count(*) from tag) t;
q    b    p    a    u    t
185  2    2    170  4    10
```

## 8. 实现说明（对照任务书）

- 分页 SQL 均无一对多 join：question/bank/paper/score 分页只查主表行，
  标签用二次 `question_tag IN` 查询在 Service 装配；试卷题目明细只用于单卷详情
- 判分全部在 `AnswerServiceImpl.grade()`（契约 4.7），Controller 不算分
- 事务：组卷（exam_paper + 批量 exam_paper_question）、交卷（全卷批量 answer_record，含未答题落库）、
  批量移动、删题库/删题目/删标签、撤销成绩
- 业务校验：题库有题 409、题目被卷引用 409、题量不足 409（文案带题型和余量）、
  仅 DRAFT 可改/可发布、仅 PUBLISHED 可交卷/可结束、同卷同考生仅一次、非 ADMIN 403
- stats 的 questionCount 是 `select count(*) from question` 全表数，多少报多少，无特殊处理

## 9. 顺带修正的骨架问题（超出 backend/** 业务代码的最小改动）

- `common/LoginUser.java`：skeleton 版只有 id/username/realName（图书系统遗留），
  没有 nickname/role，403 判断和契约 3 的身份字段都无法实现 → 改为 id/username/nickname/role
- `common/CacheKeys.java`：skeleton 版是 dict:categories / cache:hot:books（图书系统遗留）→
  改为契约第 5 节的 dict:banks / cache:ranking:<paperId>
- `ZhikaoApplication.java` 注释仍写着「图书借阅管理后台」，未动（不影响功能，属架构师文件）
