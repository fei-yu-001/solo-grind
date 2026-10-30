// 组卷端到端流程：登录 -> 组卷弹窗 -> 选题库/加题量 -> 生成 -> 校验列表 -> 删除
// 用法: node scripts/ui-flow.mjs [base_url]
import { spawn } from "node:child_process";
import { setTimeout as sleep } from "node:timers/promises";
const BASE = (process.argv[2] ?? "http://127.0.0.1:5173").replace(/\/$/, "");
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORT = 9273;
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, "--disable-gpu", "--no-first-run",
  "--no-default-browser-check", `--user-data-dir=C:/Temp/cdp-flow3-${Date.now()}`, "about:blank"]);
async function t(){for(let i=0;i<80;i++){try{const l=await(await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();const p=l.find(x=>x.type==="page");if(p)return p;}catch{}await sleep(250);}throw new Error("no cdp");}
const page = await t();
const ws = new WebSocket(page.webSocketDebuggerUrl);
let seq=0; const pending=new Map(); const errs=[];
ws.addEventListener("message",(e)=>{const m=JSON.parse(e.data);
  if(m.id&&pending.has(m.id)){const{res,rej}=pending.get(m.id);pending.delete(m.id);m.error?rej(new Error(JSON.stringify(m.error))):res(m.result);}
  else if(m.method==="Runtime.exceptionThrown") errs.push(String(m.params.exceptionDetails.exception?.description??"").slice(0,160));
  else if(m.method==="Log.entryAdded"&&m.params.entry.level==="error") errs.push(m.params.entry.text.slice(0,160));});
await new Promise((r,j)=>{ws.addEventListener("open",r);ws.addEventListener("error",j);});
const send=(m,p={})=>new Promise((res,rej)=>{seq++;pending.set(seq,{res,rej});ws.send(JSON.stringify({id:seq,method:m,params:p}));});
const ev=async(x)=>{const r=await send("Runtime.evaluate",{expression:x,returnByValue:true,awaitPromise:true});return r.result.value;};
await send("Runtime.enable"); await send("Log.enable"); await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride",{width:1500,height:1000,deviceScaleFactor:1,mobile:false});

const clickAt = async (selector, index = 0) => {
  const box = await ev(`(()=>{const els=document.querySelectorAll(${JSON.stringify(selector)});const e=els[${index}];if(!e)return null;const r=e.getBoundingClientRect();return JSON.stringify({x:r.x+r.width/2,y:r.y+r.height/2});})()`);
  if (!box) return false;
  const {x, y} = JSON.parse(box);
  await send("Input.dispatchMouseEvent", {type:"mousePressed", x, y, button:"left", clickCount:1});
  await send("Input.dispatchMouseEvent", {type:"mouseReleased", x, y, button:"left", clickCount:1});
  return true;
};

const fail=[]; const ok=(m)=>console.log("  [ok]   "+m); const bad=(m)=>{console.log("  [FAIL] "+m);fail.push(m);};

await send("Page.navigate",{url:BASE+"/login"});
await sleep(2600);
await ev("(()=>{const i=[...document.querySelectorAll('input')];const s=(e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));};s(i[0],'admin');s(i[1],'admin123');return 1})()");
await sleep(200);
await ev("(()=>{const b=[...document.querySelectorAll('button')].find(x=>/登\s*录/.test(x.textContent));b&&b.click();return 1})()");
await sleep(3200);
await send("Page.navigate",{url:BASE+"/papers"});
await sleep(3200);
const before = await ev("document.querySelectorAll('.el-table__body-wrapper tbody tr').length");
await ev("(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.innerText.trim()==='组卷');b&&b.click();return 1})()");
await sleep(1200);
await clickAt('.el-dialog .el-select__wrapper', 0);
await sleep(700);
await ev("(()=>{const o=[...document.querySelectorAll('.el-select-dropdown__item')].filter(x=>x.offsetParent!==null);o[0]&&o[0].click();return 1})()");
await sleep(600);
const bump = async (idx, times) => {
  for (let k = 0; k < times; k += 1) {
    await clickAt('.el-dialog .el-input-number__increase', idx);
    await sleep(160);
  }
};
await bump(0, 2);  // 判断题
await bump(2, 3);  // 单选题
await bump(4, 1);  // 多选题
const vals = await ev("[...document.querySelectorAll('.el-dialog .el-input-number input')].map(i=>i.value)");
console.log("  题量与分值:", JSON.stringify(vals));
const preview = await ev("(()=>{const d=[...document.querySelectorAll('.el-dialog')].find(x=>x.offsetParent!==null);const t=d.innerText.replace(/\s+/g,' ');const m=t.match(/共\s*\d+\s*题，总分\s*\d+\s*分/);return m?m[0]:t.slice(-60)})()");
console.log("  预览:", preview);
if(/共\s*6\s*题，总分\s*7\s*分/.test(String(preview))) ok("预览算对了：6 题 7 分"); else bad(`预览不对: ${preview}`);
await ev("(()=>{const d=[...document.querySelectorAll('.el-dialog')].find(x=>x.offsetParent!==null);const i=d.querySelector('input');i.value='UI-FLOW-PAPER';i.dispatchEvent(new Event('input',{bubbles:true}));return 1})()");
await sleep(400);
await ev("(()=>{const d=[...document.querySelectorAll('.el-dialog')].find(x=>x.offsetParent!==null);[...d.querySelectorAll('button')].find(x=>/生成试卷/.test(x.innerText))?.click();return 1})()");
await sleep(4000);
const after = await ev("document.querySelectorAll('.el-table__body-wrapper tbody tr').length");
const msg = await ev("[...document.querySelectorAll('.el-message')].map(m=>m.innerText).join(' | ')");
console.log("  提示:", msg || "(无)", "| 行数", before, "->", after);
if(after > before) ok(`组卷成功 ${before} -> ${after}`); else bad("组卷没成功");
const rowText = await ev("(()=>{const r=[...document.querySelectorAll('.el-table__body-wrapper tbody tr')].find(x=>x.innerText.includes('UI-FLOW-PAPER'));return r?r.innerText.replace(/\s+/g,' ').slice(0,80):'no-row'})()");
console.log("  新行:", rowText);
if(/no-row/.test(rowText)) bad("列表里没有新试卷"); else ok("列表出现新试卷");
const del = await ev(`(async()=>{
  const row=[...document.querySelectorAll('.el-table__body-wrapper tbody tr')].find(x=>x.innerText.includes('UI-FLOW-PAPER'));
  if(!row) return 'no-row';
  [...row.querySelectorAll('button')].find(b=>b.innerText.includes('删除'))?.click();
  await new Promise(r=>setTimeout(r,900));
  [...document.querySelectorAll('.el-message-box__btns button')].find(b=>/确\s*定/.test(b.innerText))?.click();
  await new Promise(r=>setTimeout(r,2200));
  return 'done';
})()`);
await sleep(800);
const left = await ev("document.body.innerText.includes('UI-FLOW-PAPER')");
if(!left) ok("测试试卷已删除"); else bad("测试试卷没删掉");
if(errs.length){bad(`控制台报错 ${errs.length} 处`);for(const e of errs.slice(0,4))console.log("        ",e);}else ok("全程无控制台报错");
ws.close(); chrome.kill();
console.log(`\n结果: ${fail.length?"FAIL":"PASS"}`);
process.exit(fail.length?1:0);
