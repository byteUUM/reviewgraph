const $ = (s) => document.querySelector(s);
const SAMPLE = `import os
from utils import *

def load(path, cache=[]):
    try:
        data = eval(open(path).read())
    except:
        return None
    if data == None:
        return cache
    return data
`;
$("#code").value = SAMPLE;
$("#sample").onclick = () => ($("#code").value = SAMPLE);

function reset() {
  document.querySelectorAll("#rail li").forEach((li) => { li.className = ""; li.querySelector("em").textContent = ""; });
  $("#loop").hidden = true;
  $("#report").textContent = "审查中…";
}

function mark(node, upd) {
  const li = document.querySelector(`#rail li[data-node="${node}"]`);
  li.classList.add("done");
  const em = li.querySelector("em");
  if (node === "static") em.textContent = upd.syntax_error ? "语法错误" : `${upd.findings.length} 项发现`;
  if (node === "review") em.textContent = `第 ${upd.iteration} 轮`;
  if (node === "critic") {
    em.textContent = `覆盖率 ${Math.round(upd.score * 100)}%`;
    if (upd.score < 0.9) {
      $("#loop").hidden = false;
      $("#loop").textContent = `覆盖率 ${Math.round(upd.score * 100)}% 低于 90%，返回「模型审查」补全。`;
    }
  }
  if (node === "report") $("#report").textContent = upd.report;
}

$("#run").onclick = async () => {
  const btn = $("#run");
  btn.disabled = true; reset();
  try {
    const res = await fetch("/api/stream", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: $("#code").value }),
    });
    const reader = res.body.getReader(), dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const parts = buf.split("\n\n"); buf = parts.pop();
      for (const p of parts) {
        const m = JSON.parse(p.replace(/^data: /, ""));
        if (m.node) mark(m.node, m.update);
      }
    }
  } catch (e) {
    $("#report").textContent = "请求失败：" + e.message;
  } finally { btn.disabled = false; }
};
