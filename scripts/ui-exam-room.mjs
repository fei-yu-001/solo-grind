// 考生答题全流程巡检：考试中心 -> 进考场 -> 答题 -> 交卷 -> 成绩明细
// 用法: node scripts/ui-exam-room.mjs [base_url]
// 会真的交一份卷子，跑完自动撤销该成绩，不污染数据
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { setTimeout as sleep } from "node:timers/promises";

const BASE = (process.argv[2] ?? "http://127.0.0.1:5173").replace(/\/$/, "");
const API = BASE.includes("5173") ? "http://127.0.0.1:8080" : BASE;
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORT = 9279;
const OUT = "docs/screenshots";

const chrome = spawn(CHROME, [
  "--headless=new",
  `--remote-debugging-port=${PORT}`,
  "--disable-gpu",
  "--no-first-run",
  "--no-default-browser-check",
  `--user-data-dir=C:/Temp/cdp-room-${Date.now()}`,
  "about:blank",
]);

async function findTarget() {
  for (let i = 0; i < 80; i += 1) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find((t) => t.type === "page");
      if (page) return page;
    } catch {
      // 等
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
  } else if (msg.method) events.push(msg);
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
const ev = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  return r.result.value;
};
const shot = async (name) => {
  const r = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.data, "base64"));
};

await send("Runtime.enable");
await send("Log.enable");
await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

const fail = [];
const ok = (m) => console.log(`  [ok]   ${m}`);
const bad = (m) => {
  console.log(`  [FAIL] ${m}`);
  fail.push(m);
};
const errors = [];
const drain = () => {
  for (const e of events.splice(0)) {
    if (e.method === "Log.entryAdded" && e.params.entry.level === "error") errors.push(e.params.entry.text.slice(0, 150));
    if (e.method === "Runtime.exceptionThrown") errors.push(String(e.params.exceptionDetails.exception?.description ?? "").slice(0, 150));
  }
};

// 登录
await send("Page.navigate", { url: `${BASE}/login` });
await sleep(2600);
await ev(`(()=>{const i=[...document.querySelectorAll('input')];const s=(e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));};s(i[0],'student03');s(i[1],'student123');return 1})()`);
await sleep(200);
await ev(`(()=>{const b=[...document.querySelectorAll('button')].find(x=>/登\s*录/.test(x.textContent));b&&b.click();return 1})()`);
await sleep(3000);
drain();

// 考试中心
await send("Page.navigate", { url: `${BASE}/exam-center` });
await sleep(2800);
const center = await ev(`(()=>{
  const text = document.body.innerText.replace(/\s+/g,' ');
  const cards = document.querySelectorAll('.el-card').length;
  const rows = document.querySelectorAll('.el-table__body-wrapper tbody tr').length;
  return JSON.stringify({text: text.slice(0,200), cards, rows});
})()`);
const c = JSON.parse(center);
console.log("  考试中心:", c.text.slice(0, 120));
if (c.cards + c.rows === 0) bad("考试中心没有卷子");
else ok(`考试中心渲染（卡片 ${c.cards} / 表格 ${c.rows} 行）`);
await shot("09-exam-center");

// 进考场
const entered = await ev(`(()=>{
  const b=[...document.querySelectorAll('button')].find(x=>/进入考场|开始考试/.test(x.innerText));
  if(!b) return 'no-btn';
  b.click(); return 'clicked';
})()`);
await sleep(3200);
drain();
const path1 = await ev("location.pathname");
if (/no-btn/.test(entered)) bad("找不到「进入考场」按钮");
else if (!/\/exam\//.test(path1)) bad(`点了按钮没进考场（当前 ${path1}）`);
else ok(`进入考场 ${path1}`);

// 一屏 + 不泄答案
const L = JSON.parse(await ev(`(()=>{
  const doc = document.scrollingElement;
  const timer = document.querySelector('.exam-timer')?.textContent?.trim() || '';
  const progress = document.querySelector('.exam-progress')?.textContent?.trim() || '';
  const opts = document.querySelectorAll('.opt-item').length;
  const cardItems = document.querySelectorAll('.card-item').length;
  const text = document.body.innerText;
  return JSON.stringify({
    overflowY: doc.scrollHeight - doc.clientHeight,
    timer, progress, opts, cardItems,
    leak: /正确答案|答案：|解析：/.test(text),
    text: text.replace(/\s+/g,' ').slice(0,120),
  });
})()`));
console.log("  答题页:", L.text.slice(0, 90));
if (L.overflowY > 4) bad(`答题页整页还能滚 ${L.overflowY}px（题干+选项+答题卡应在一屏内）`);
else ok("答题页一屏装下");
if (L.opts === 0) bad("看不到选项");
else ok(`选项渲染了 ${L.opts} 个`);
if (L.cardItems === 0) bad("看不到答题卡");
else ok(`答题卡 ${L.cardItems} 格`);
if (!/\d+:\d{2}/.test(L.timer)) bad(`倒计时不对: ${L.timer}`);
else ok(`倒计时 ${L.timer}`);
if (L.leak) bad("页面上出现了答案或解析");
else ok("页面上没有答案/解析");
await shot("10-exam-room");

// 答 3 题
const A = JSON.parse(await ev(`(async()=>{
  let clicked = 0;
  for (let i = 0; i < 3; i += 1) {
    const opt = document.querySelectorAll('.opt-item')[i % Math.max(1, document.querySelectorAll('.opt-item').length)];
    if (opt) { opt.click(); clicked += 1; await new Promise(r=>setTimeout(r,250)); }
    const next = [...document.querySelectorAll('button')].find(b=>/下一题/.test(b.innerText));
    if (next) { next.click(); await new Promise(r=>setTimeout(r,350)); }
  }
  return JSON.stringify({
    clicked,
    progress: document.querySelector('.exam-progress')?.textContent?.trim() || '',
    done: document.querySelectorAll('.card-item.done').length,
  });
})()`));
console.log("  作答:", A.progress, "| 已答格子", A.done);
if (A.clicked === 0) bad("选项没点上");
else ok(`点了 ${A.clicked} 个选项`);
if (A.done === 0) bad("答题卡没有标记已答");
else ok(`答题卡标记已答 ${A.done} 格`);
await shot("11-exam-answering");

// 交卷
await ev(`(()=>{const b=[...document.querySelectorAll('button')].find(x=>/交\s*卷/.test(x.innerText));b&&b.click();return 1})()`);
await sleep(900);
const confirmText = await ev("(()=>{const m=document.querySelector('.el-message-box');return m?m.innerText.replace(/\s+/g,' ').slice(0,120):'no-box'})()");
console.log("  确认框:", confirmText);
await ev(`(()=>{const b=[...document.querySelectorAll('.el-message-box__btns button')].find(x=>/确\s*定/.test(x.innerText));b&&b.click();return 1})()`);
await sleep(4000);
drain();
const after = await ev("location.pathname + ' | ' + document.body.innerText.replace(/\s+/g,' ').slice(0,150)");
console.log("  交卷后:", after.slice(0, 120));
if (/得分|成绩|分\s*\/|totalScore|正确/.test(after)) ok("交卷后看到成绩");
else bad(`交卷后没看到成绩：${after.slice(0, 80)}`);
await shot("12-exam-result");

if (errors.length === 0) ok("全程无控制台报错");
else {
  bad(`控制台报错 ${errors.length} 处`);
  for (const e of [...new Set(errors)].slice(0, 5)) console.log(`         ${e}`);
}

ws.close();
chrome.kill();
await sleep(300);

// 清理：撤销这次考试成绩，避免污染演示数据
try {
  const login = await fetch(`${API}/api/auth/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username: "admin", password: "admin123" }),
  }).then((r) => r.json());
  const token = login.data.token;
  const me = await fetch(`${API}/api/auth/me`, {
    headers: { Authorization: `Bearer ${login.data.token}` },
  });
  const papers = await fetch(`${API}/api/papers?page=1&size=20`, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.json());
  const ids = papers.data.records.map((p) => p.id);
  const users = await fetch(`${API}/api/readers`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null);
  // 逐个试卷尝试撤销 student03(id=4) 的成绩
  let removed = 0;
  for (const id of ids) {
    const r = await fetch(`${API}/api/scores/${id}/4`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) removed += 1;
  }
  console.log(`  已撤销 student03 的成绩 ${removed} 份（清理用）`);
} catch (e) {
  console.log(`  清理失败，手动删一下: ${e.message}`);
}

console.log(`\n结果: ${fail.length === 0 ? "PASS" : `FAIL (${fail.length})`}`);
process.exit(fail.length === 0 ? 0 : 1);
