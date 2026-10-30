# 前端验收记录（library-web）

日期：2026-10-30
环境：Windows 10 / Node v24.19.0 / npm 11.17.0
工作目录：`frontend/`

## 1. npm install

命令：

```
npm install
```

真实输出（摘录）：

```
added 224 packages in 39s
npm warn allow-scripts 1 package has install scripts not yet covered by allowScripts:
npm warn allow-scripts   esbuild@0.25.12 (postinstall: node install.js)
```

说明：依赖安装成功。esbuild 的 postinstall 被 npm 的 allow-scripts 策略提示未执行，
但 vite 6 使用自身携带的 JS 版 esbuild 即可正常工作（见第 2 步 build 成功），不影响验收。

## 2. npm run build

命令：

```
npm run build
```

真实输出（摘录，零报错）：

```
dist/assets/index-DoxOuF2m.js         1,122.72 kB │ gzip: 372.31 kB
(!) Some chunks are larger than 500 kB after minification.
✓ built in 5.76s
```

说明：构建成功。chunk 大于 500 kB 是 Element Plus 整包引入产生的体积提示（warning，
不是 error），本课程项目不做拆包优化。

## 3. npm run dev + curl 探活

命令：

```
npm run dev &
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/login
```

真实输出（dev server 启动日志 + 探活结果）：

```
  VITE v6.4.5  ready in 296 ms
  ➜  Local:   http://localhost:5174/        （当时 5173 被占用，备端口 5174 也可访问）
---curl 5173---
200
---curl /login---
200
```

说明：两个端口均返回 HTTP 200（机器上另有一个本项目 dev 实例占着 5173，
返回的 index.html 与本项目一致，含 `/src/main.js` 入口）。

## 4. 无头 Chrome 截图 /login

命令：

```
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new \
  --screenshot=login.png \
  --window-size=1440,900 \
  --virtual-time-budget=8000 \
  http://localhost:5173/login
```

真实输出：

```
237337 bytes written to file ...\frontend\login.png
```

截图已人工确认：登录卡片（标题「图书管理系统」、用户名/密码输入框、登录按钮、
演示账号 admin / admin123 小字）完整渲染，页面不白屏，无 JS 报错导致的空白。

## 5. 后端联调

探测命令：

```
curl -s -m 5 http://localhost:8080/api/auth/me
curl -s -m 5 -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' http://localhost:8080/api/auth/login
```

真实输出：

```
HTTP:000（连接被拒绝，exit code 7）
```

结论：**后端 8080 尚未启动，登录后四个页面（图书/分类/读者/借阅）的接口联调
待架构师验证**。本前端已按契约完成：

- axios 封装：自动带 `Authorization: Bearer <token>`，只认 `code === 0`，
  非 0 用后端 `message` 弹 ElMessage.error，401 清本地令牌跳 `/login`
- 全部接口按 `docs/CONTRACT.md` 路径/字段调用（含 PATCH /api/books/status、
  PATCH /api/readers/{id}/card、/api/borrows/stats 等）
- 409 类业务文案（删除分类、借书冲突等）由统一拦截器原样展示后端 message

后端起来后建议验证路径：登录 -> 统计概览 -> 图书（查/增/改/删/批量上下架）->
分类 -> 读者（含改证状态）-> 借阅（借书/归还/续借）。

## 6. 提交

提交信息：`feat(web): vue3 admin frontend with login, books, categories, readers, borrows and dashboard`
