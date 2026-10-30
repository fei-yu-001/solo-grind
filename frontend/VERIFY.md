# 前端验收记录（zhikao-web）

时间：2026-10-30 15:00-15:30　环境：Windows 11 / Git Bash / Node 24 / npm 11

## 1. 依赖安装

任务书说 node_modules 已装好，实际目录为空，执行了 `npm install`（npmmirror 源）：

```
$ npm install
added 271 packages in 2m
npm warn allow-scripts 1 package has install scripts not yet covered by allowScripts:
npm warn allow-scripts   esbuild@0.25.12 (postinstall: node install.js)
```

esbuild 的 postinstall 被 allow-scripts 拦了，但不影响 build（vite 6 自带的二进制解析正常）。

## 2. 构建

```
$ npm run build
> vite build

vite v6.4.5 building for production...
transforming...
✓ 1701 modules transformed.
rendering chunks...
dist/index.html                     0.41 kB │ gzip:   0.30 kB
dist/assets/Dashboard-DK_za8fW.css  0.04 kB │ gzip:   0.06 kB
dist/assets/Question-DMGocdiu.css   0.16 kB │ gzip:   0.14 kB
dist/assets/Score-BeMPyun3.css      0.28 kB │ gzip:   0.17 kB
dist/assets/Paper-5UdmMFZh.css      0.29 kB │ gzip:   0.20 kB
dist/assets/Login-CMrJAEyF.css      0.32 kB │ gzip:   0.22 kB
dist/assets/index-BPZrmKwl.css    362.73 kB │ gzip:  48.61 kB
...（省略若干 js chunk）
dist/assets/index-BcRyxy_U.js   1,121.84 kB │ gzip: 372.04 kB
✓ built in 5.78s
```

零报错。唯一警告是 index chunk 超过 500 kB（Element Plus 全量注册所致，实验项目不做拆包优化）。

## 3. Dev server

首次启动时 5173 被上一项目（图书管理系统）残留的 vite 进程占用（vite 自动落到 5174），
已结束该残留进程（PID 4260）后重启，标准端口正常：

```
$ npm run dev
VITE v6.4.5  ready in 280 ms
➜  Local:   http://localhost:5173/

$ curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/
200
$ curl -s http://localhost:5173/ | grep title
<title>智考刷题系统</title>
```

（index.html 里遗留的「图书管理系统」标题已顺手改为「智考刷题系统」。）

## 4. 登录页截图

```
$ "C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new \
  --screenshot=$TEMP/zhikao_login.png --window-size=1440,900 \
  --virtual-time-budget=8000 http://localhost:5173/login
299741 bytes written to file C:/Users/DDyu/AppData/Local/Temp/zhikao_login.png
```

截图已人工查看：蓝色渐变背景 + 登录卡片（标题「智考刷题系统」、用户名/密码框、登录按钮、
演示账号小字）渲染完整，无白屏。副本存于 `frontend/login.png`。

说明：Chrome 无权限向项目目录直接写截图（Failed to write file login.png: 拒绝访问），
先写到 %TEMP% 再复制回仓库，命令效果与任务书一致。

## 5. 联调（8080）

```
$ curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:8080/api/scores/stats
000
```

后端 8080 尚未启动，登录后的六个页面联调**待架构师验证**。接口调用均已按
docs/CONTRACT.md 写好（相对路径 /api/xxx，由 vite proxy 转发到 8080）。

## 6. 静态检查补充

所有 SFC 用脚本做过结构校验（template/script 配对、script 花括号闭合），Question.vue /
Paper.vue / Score.vue / 三个弹窗组件均通过；`npm run build` 的 vue 编译亦无告警。

---

# 第二轮：考生在线答题（TASK-exam-room）

时间：2026-10-30 16:40-17:10。后端 8080 本轮已在运行（ ExamController 已部署），
以下全部为真实联调结果，数据已清理回原状。

## 0. 后端探活与接口预检（curl）

```
$ curl -X POST http://localhost:8080/api/auth/login -d '{"username":"student03",...}'
{"code":0,"data":{"token":"...","id":4,"username":"student03","nickname":"陈同学","role":"STUDENT"}}

GET /api/exams/available   -> 2 张卷（paper 2 专科组 100 题 / paper 1 本科组 85 题），myScore 全 null
GET /api/exams/1/questions -> 85 题，响应体全文检索无 "answer" / "analysis"（防作弊要求达成）
GET /api/scores/mine       -> {"total":0,...}（student03 初始无成绩）
```

## 1. 构建

```
$ npm run build
vite v6.4.5 building for production...
✓ 1707 modules transformed.
✓ built in 6.20s
```
（零报错；仅既有 chunk 体积提示）

## 2. 真实登录 + 全流程（无头 Chrome + CDP，1440x900，student03/student123）

脚本驱动真实浏览器完成：登录 → 考试中心 → 进考场 → 键盘作答 → 交卷确认 → 成绩明细。

- 登录后跳 /dashboard，考生侧边菜单只有「考试中心」「我的成绩」两项（截图确认）
- 考试中心：两张卷子卡片，题量/总分/时长齐全，顶部警示条，按钮「进入考场」（截图 zhikao_center.png）
- 答题页 /exam/1（截图 zhikao_room.png）：
  - 顶栏：卷名 + 「剩余时间 01:39:57」（hh:mm:ss 倒计时在走）+ 「已答 3 / 85 题」+ 交卷按钮
  - 左侧：题型标签 + 第 N 题/共 85 题 + 分值 + 题干 + A/B 选项（判断题按后端 options 渲染）
  - 右侧答题卡：85 宫格、已答高亮、图例、上一题/下一题
  - **一屏校验（无头 Chrome 实测）：scrollHeight 802 = clientHeight 802，整页零滚动**
  - **答案泄露检查：/正确答案|答案：|解析/ 全页正则 = false**
- 键盘操作实测：`A` 答判断题并自动跳下一题 → `→` 翻题 → `B` 作答 → 数字键 `1` 同样生效；
  答题卡高亮数量与按键次数一致（3 题）
- 交卷：点交卷 → 确认框「还有 82 题未作答，确定要交卷吗？」（截图 zhikao_confirm.png）
  → 确定交卷 → 跳 /my-scores?paperId=1&userId=4 并自动打开明细抽屉：
  得分 2/100、正确率 2%、逐题「答对/答错」（截图 zhikao_detail.png）——与 3 次作答对 2 题吻合
- 全程 Runtime.exceptionThrown 监听：**无 JS 报错**

## 3. 多选交互专项（现有两卷无多选题，临时组卷验证后删除）

题库中有 15 道多选题（bank 1）。用 admin 真实调 `POST /api/papers` 组测试卷
（id=23，2 判断+2 单选+3 多选，10 分）并发布，CDP 实测 /exam/23：

```
跳到第 5 题（多选，5 个选项）：
按 A → 2 active（A+C 后）→ 再按 C → 1 active（再点取消）→ 按 B → 2 active
多选不自动跳题，停留在原题继续勾选 ✓（截图 zhikao_multi.png）
```

验证后 admin 删除该试卷。数据恢复：available 回到 2 张卷，student03 成绩撤销、
`/api/scores/mine` total=0，与任务书要求的「2 卷 / 170 条作答」基线一致（清理前后都核过）。

## 4. 管理员菜单

admin 登录：概览 | 题库 | 题目 | 试卷 | 成绩 | 考试中心（无「我的成绩」），
考试中心可预览两张卷子（截图 zhikao_admin_center.png）。

## 5. 测试过程造成的数据变动与清理（如实记录）

- CDP 脚本第一次试跑时意外真实交卷一次（student03 / paper 1，得 2 分）
- 已用 admin `DELETE /api/scores/1/4` 撤销，恢复原状，并复核 available/mine 均回 null/0
- 多选验证卷（id=23）已删除

## 6. 未验证项

- 倒计时归零自动交卷：逻辑为 remaining<=0 时 stopTimer + doSubmit(true)，未实等 90/100 分钟，
  也不打算为验证改短数据库里的时长（如实说明，未实测）
