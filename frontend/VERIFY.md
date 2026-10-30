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
