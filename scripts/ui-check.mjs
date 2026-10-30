// 智考前台页面巡检：登录 -> 逐个页面截图 + 抓控制台错误 + 数表格行
// 用法: node scripts/ui-check.mjs [base_url] [--user admin] [--pass admin123]
// 需要前后端都在跑（默认 http://localhost:5173），截图落到 docs/screenshots/
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { setTimeout as sleep } from "node:timers/promises";

const argv = process.argv.slice(2);
const BASE = (argv.find((a) => a.startsWith("http")) ?? "http://localhost:5173").replace(/\/$/, "");
const arg = (name, fallback) => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
};
const USER = arg("--user", "admin");
const PASS = arg("--pass", "admin123");
const OUT = "docs/screenshots";
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORT = 9251;

const pass = [];
const fail = [];
const ok = (m) => {
  console.log(`  [ok]   ${m}`);
  pass.push(m);
};
const bad = (m) => {
  console.log(`  [FAIL] ${m}`);
  fail.push(m);
};

mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  "--headless=new",
  `--remote-debugging-port=${PORT}`,
  "--disable-gpu",
  "--no-first-run",
  "--no-default-browser-check",
  `--user-data-dir=C:/Temp/cdp-zhikao-${Date.now()}`,
  "about:blank",
]);

async function findTarget() {
  for (let i = 0; i < 80; i += 1) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find((t) => t.type === "page");
      if (page) return page;
    } catch {
      // 等 Chrome 起来
    }
    await sleep(250);
  }
  throw new Error("CDP 没起来");
}

const target = await findTarget();
const ws = new WebSocket(target.webSocketDebuggerUrl);
let seq = 0;
const pending = new Map();
const events = [];
ws.addEventListener("message", (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { res, rej } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) rej(new Error(JSON.stringify(msg.error)));
    else res(msg.result);
  } else if (msg.method) {
    events.push(msg);
  }
});
await new Promise((res, rej) => {
  ws.addEventListener("open", res);
  ws.addEventListener("error", rej);
});
const send = (method, params = {}) =>
  new Promise((res, rej) => {
    seq += 1;
    pending.set(seq, { res, rej });
    ws.send(JSON.stringify({ id: seq, method, params }));
  });

await send("Runtime.enable");
await send("Log.enable");
await send("Page.enable");
await send("Network.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

const errors = [];
function drainErrors() {
  for (const ev of events.splice(0)) {
    if (ev.method === "Log.entryAdded" && ev.params.entry.level === "error") {
      errors.push(ev.params.entry.text.slice(0, 160));
    }
    if (ev.method === "Runtime.exceptionThrown") {
      const d = ev.params.exceptionDetails;
      errors.push(String(d.exception?.description ?? d.text ?? "").slice(0, 160));
    }
    if (ev.method === "Network.loadingFailed" && ev.params.type === "Fetch") {
      errors.push(`请求失败 ${ev.params.errorText}`);
    }
  }
}

async function evaluate(expression) {
  const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  return r.result.value;
}

async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.data, "base64"));
}

async function goto(path, waitMs = 2600) {
  await send("Page.navigate", { url: BASE + path });
  await sleep(waitMs);
  drainErrors();
}

console.log(`目标: ${BASE}  账号: ${USER}`);

// ---------- 登录 ----------
await goto("/login");
const loginText = await evaluate("document.body.innerText.replace(/\\s+/g,' ').slice(0,120)");
if (/登录|账号|密码/.test(loginText)) ok(`登录页渲染: ${loginText.slice(0, 60)}`);
else bad(`登录页没渲染出来: ${loginText}`);

await evaluate(`(() => {
  const inputs = [...document.querySelectorAll('input')];
  const set = (el, v) => {
    el.value = v;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };
  if (inputs[0]) set(inputs[0], ${JSON.stringify(USER)});
  if (inputs[1]) set(inputs[1], ${JSON.stringify(PASS)});
  return inputs.length;
})()`);
await sleep(300);
await shot("01-login");
await evaluate(`(() => {
  const btn = [...document.querySelectorAll('button')].find((b) => /登\\s*录/.test(b.textContent));
  if (btn) btn.click();
  return !!btn;
})()`);
await sleep(3200);
drainErrors();

const afterLogin = await evaluate("location.pathname + '|' + document.body.innerText.replace(/\\s+/g,' ').slice(0,120)");
if (/dashboard/.test(afterLogin)) ok(`登录成功跳到 ${afterLogin.split("|")[0]}`);
else bad(`登录后没进 dashboard: ${afterLogin}`);

// ---------- 各页面 ----------
const pages = [
  ["/dashboard", "02-dashboard", /概览|题库数|题目总数|平均分/],
  ["/banks", "03-banks", /题库|题目数/],
  ["/questions", "04-questions", /题干|题型|难度/],
  ["/papers", "05-papers", /试卷|总分|时长/],
  ["/scores", "06-scores", /考生|得分|正确率/],
];

for (const [path, name, pattern] of pages) {
  await goto(path, 3000);
  const info = await evaluate(`(() => {
    const rows = document.querySelectorAll('.el-table__body-wrapper tbody tr').length;
    const cards = document.querySelectorAll('.el-card').length;
    const text = document.body.innerText.replace(/\\s+/g, ' ').slice(0, 200);
    const total = (document.querySelector('.el-pagination__total')?.textContent || '').trim();
    return JSON.stringify({ rows, cards, text, total });
  })()`);
  const s = JSON.parse(info);
  await shot(name);
  if (!pattern.test(s.text)) bad(`${path} 内容不对: ${s.text.slice(0, 80)}`);
  else if (s.rows === 0 && s.cards === 0) bad(`${path} 没有数据渲染`);
  else ok(`${path} 渲染正常（表格 ${s.rows} 行，卡片 ${s.cards} 个${s.total ? "，" + s.total : ""}）`);
}

// ---------- 分页翻页 ----------
await goto("/questions", 3000);
const firstCell = await evaluate(
  "document.querySelector('.el-table__body-wrapper tbody tr td:nth-child(2)')?.innerText ?? ''",
);
const clicked = await evaluate(`(() => {
  const next = document.querySelector('.el-pagination .btn-next');
  if (!next || next.disabled) return false;
  next.click();
  return true;
})()`);
await sleep(2200);
drainErrors();
const secondCell = await evaluate(
  "document.querySelector('.el-table__body-wrapper tbody tr td:nth-child(2)')?.innerText ?? ''",
);
if (!clicked) bad("题目列表没有可用的下一页");
else if (firstCell && secondCell && firstCell !== secondCell) ok("分页翻页后首行内容变了");
else bad(`翻页后内容没变（都是 ${String(firstCell).slice(0, 20)}）`);
await shot("07-questions-page2");

// ---------- 搜索结果 ----------
await goto("/questions", 2600);
await evaluate(`(() => {
  const input = document.querySelector('.el-input__inner');
  if (!input) return false;
  input.value = '抽样';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
})()`);
await sleep(400);
await evaluate(`(() => {
  const btn = [...document.querySelectorAll('button')].find((b) => /查\\s*询|搜\\s*索/.test(b.textContent));
  if (btn) btn.click();
  return !!btn;
})()`);
await sleep(2400);
drainErrors();
const searchRows = await evaluate("document.querySelectorAll('.el-table__body-wrapper tbody tr').length");
if (searchRows > 0) ok(`关键字搜索「抽样」返回 ${searchRows} 行`);
else bad("关键字搜索没有结果");

// ---------- 考生视角 ----------
await evaluate("localStorage.clear()");
await goto("/login");
await evaluate(`(() => {
  const inputs = [...document.querySelectorAll('input')];
  const set = (el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); };
  if (inputs[0]) set(inputs[0], 'student01');
  if (inputs[1]) set(inputs[1], 'student123');
  return true;
})()`);
await sleep(300);
await evaluate(`(() => {
  const btn = [...document.querySelectorAll('button')].find((b) => /登\\s*录/.test(b.textContent));
  if (btn) btn.click();
  return true;
})()`);
await sleep(3200);
drainErrors();
const menuText = await evaluate("document.querySelector('.el-menu')?.innerText.replace(/\\s+/g,' ') ?? ''");
if (/题库|题目|试卷/.test(menuText)) bad(`考生还能看到管理菜单: ${menuText}`);
else ok(`考生菜单已收窄: ${menuText}`);
const studentScores = await evaluate("location.pathname");
await shot("08-student-scores");
if (/scores|dashboard/.test(studentScores)) ok(`考生落地页 ${studentScores}`);
else bad(`考生被弹到了 ${studentScores}`);

// ---------- 结果 ----------
if (errors.length === 0) ok("全程无控制台报错");
else {
  bad(`控制台报错 ${errors.length} 处`);
  for (const e of [...new Set(errors)].slice(0, 8)) console.log(`         ${e}`);
}

ws.close();
chrome.kill();
await sleep(300);
console.log(`\n截图: ${OUT}/  共 ${pass.length + fail.length} 项检查`);
console.log(`结果: ${fail.length === 0 ? "PASS" : `FAIL (${fail.length})`}`);
process.exit(fail.length === 0 ? 0 : 1);
