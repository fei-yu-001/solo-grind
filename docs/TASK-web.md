# 前端任务书（agent: zhikao-web）

你负责 `frontend/**`。契约在 `docs/CONTRACT.md`，**先完整读一遍再动手**，字段名一个都不许改。

## 0. 环境

- Node 24 / npm 11，registry 已配 npmmirror
- 工作目录：`C:\Users\DDyu\Desktop\springboot\第七次实验\zhikao\frontend`
- 后端由另一个 agent 同时写，最终跑在 `http://localhost:8080`，你不用等它，按契约把接口调用写好
- 只在本地跑，不部署，不碰线上服务器

## 1. 已经有的东西（别重造）

```
frontend/
├── package.json        vue 3.5 / vue-router 4.5 / element-plus 2.9 / axios 1.7 / vite 6
├── vite.config.js      端口 5173，/api 代理到 localhost:8080，@ 别名指向 src
├── index.html
├── package-lock.json
└── src/
    ├── main.js         已挂 Element Plus 和 router
    ├── App.vue
    ├── api/request.js  axios 实例：自动带 token、拆 {code,message,data} 信封、401 跳登录、错误弹提示
    ├── api/auth.js     登录/登出/当前用户，接口签名已经对好契约
    ├── stores/auth.js  token 与用户信息存 localStorage
    └── styles/index.css
```

`src/layouts/AdminLayout.vue` 和 `src/router/index.js` 现在是上一个项目（图书借阅）留下来的，**内容要按刷题系统重写**，结构可以沿用。

`node_modules` 已经装好了，直接 `npm run dev` 就行；如果报缺包再 `npm install`。

## 2. 页面（Element Plus，中文界面，不要 emoji）

左侧菜单五项 + 登录页：

### `/login` 登录
用户名、密码、登录按钮，回车提交。登录成功存 token 和 `role`，跳 `/dashboard`。
角色分流：`ADMIN` 看全部菜单；`STUDENT` 只看到「我的成绩」。
页面下方小字给演示账号：`admin / admin123`、`student01 / student123`。

### `/dashboard` 概览
卡片：题库数、题目总数、试卷数、考生数、已交卷次数、平均分、通过率。
下面用 Element Plus 的 `el-progress` 或表格展示：按题型分布（`stats.byType`）、按题库分布（`stats.byBank`）。
数据全来自 `GET /api/scores/stats`，不要前端自己算。

### `/banks` 题库管理
筛选：关键字、组别、状态。表格列：题库名、组别、题目数、状态标签、说明、创建时间、操作。
新增/编辑弹窗；删除时如果 409，把后端 message 原样弹出来。

### `/questions` 题目管理（重点）
筛选：题库下拉（`/api/banks/all`）、题型下拉、难度下拉、标签下拉（`/api/tags`）、关键字。
表格列：ID、题干（超长省略，`show-overflow-tooltip`）、题型标签、题库、难度标签、标签（多个用 `el-tag` 小标签铺开）、操作（编辑/删除）。
勾选多行 + 「批量移动到题库」按钮，弹窗选题库，调 `PATCH /api/questions/batch`。
新增/编辑弹窗（组件抽到 `components/QuestionFormDialog.vue`）：
- 题型用 `el-radio-group`，选单选/判断时选项固定 A-D / A-B，选多选时 4-6 个选项可增删
- 选项是 `[{key,text}]` 数组，编辑时能把已有选项回填
- 答案：单选用 `el-radio-group`（只允许选一个），多选用 `el-checkbox-group`，判断用「对/错」两个按钮，提交时转成 `"A"` / `"B"`
- 标签多选 `el-select multiple`，难度 `el-rate` 或 radio
- 题干用 `el-input type="textarea"` 4 行

### `/papers` 试卷管理
筛选：关键字、状态、题库。表格列：试卷名、来源题库、题量（判断/单选/多选）、总分、时长（分钟）、状态、操作。
操作：查看题目（抽屉里列题目，含答案）、编辑、删除、发布（DRAFT）、结束（PUBLISHED）。
「组卷」弹窗：填标题、选题库、填三种题型数量和分值、时长，提交调 `POST /api/papers`，成功后提示「已生成 85 道题，总分 100」。

### `/scores` 成绩管理
筛选：试卷下拉（`/api/papers`）、关键字（考生名/账号）。表格列：考生、试卷、得分/满分、正确率、答对/答错/未答、交卷时间、操作。
操作：看明细（抽屉逐题展开：题干、你的答案、正确答案、得分）、撤销成绩（二次确认）、导出？不做。
右上角「排行榜」按钮：拉 `/api/scores/ranking?paperId=x` 用弹窗列前十。

## 3. 目录约定（报告里要画模块图）

```
src/
├── api/            request.js + 每模块一个 api 文件（banks/questions/tags/papers/scores）
├── components/     QuestionFormDialog.vue、PaperFormDialog.vue 之类
├── layouts/        AdminLayout.vue（侧边菜单 + 顶栏 + router-view）
├── router/index.js 路由表 + 登录守卫 + 角色守卫
├── stores/auth.js
└── views/          Login/Dashboard/Bank/Question/Paper/Score 六个
```

## 4. 样式

Element Plus 默认主题，页面 padding 20px，卡片间距 16px，表格操作列按钮用 `link` 类型，宽度固定。中文界面，不要 emoji。

## 5. 验收（真跑，不许写「应该可以」）

1. `npm run build` 通过，零报错
2. `npm run dev` 起得来，`curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/` 返回 200
3. 无头 Chrome 打开 `/login` 截图（`C:/Program Files/Google/Chrome/Application/chrome.exe --headless=new --screenshot=login.png --window-size=1440,900 --virtual-time-budget=8000 http://localhost:5173/login`），确认不白屏
4. 如果 8080 已经有后端在跑：用无头 Chrome + CDP 脚本把登录后的页面都过一遍，确认没有 JS 报错、表格有数据、分页能翻页。没跑就如实写「联调待架构师验证」，**不要造假数据糊弄截图**
5. 把真实命令和输出写进 `frontend/VERIFY.md`

## 6. 交付

- commit message 用英文 `feat(web): ...`，一个 commit 一件事
- 只提交 `frontend/` 下的东西，不要动 backend/docs/sql
- 干完在最后一条消息说：改了哪些文件、跑了哪些命令、真实输出摘要、没验证什么
- 拿不准停下问，不要改 `docs/CONTRACT.md`
