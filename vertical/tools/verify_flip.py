# -*- coding: utf-8 -*-
"""翻书交互验证（含 z-index 复位、连点收敛、尾页、回翻）"""
import os
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "_shot")
URL = "http://127.0.0.1:8951/index.html"

STATE = """
() => {
  const leaves = [...document.querySelectorAll('.leaf')];
  const flipped = leaves.filter(l => l.classList.contains('flipped')).length;
  const turning = leaves.filter(l => l.classList.contains('turning')).length;
  let best = -1, bi = -1;
  leaves.forEach((l,i) => { const z = +l.style.zIndex || 0; if (z > best) { best = z; bi = i; } });
  return {
    n: leaves.length, flipped, turning, topLeaf: bi,
    counter: document.querySelector('#bNow').textContent,
    all: document.querySelector('#bAll').textContent,
    onDots: document.querySelectorAll('#dots i.on').length,
    onDotIdx: [...document.querySelectorAll('#dots i')].findIndex(d => d.classList.contains('on')),
    prevDis: document.querySelector('#bPrev').disabled,
    nextDis: document.querySelector('#bNext').disabled
  };
}
"""

fails = []

def chk(cond, msg):
    print(("   PASS  " if cond else "   FAIL  ") + msg)
    if not cond:
        fails.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                        is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(800)
    pg.mouse.click(195, 250)
    pg.wait_for_timeout(900)
    pg.evaluate("document.getElementById('stage').scrollTop = document.getElementById('s-book').offsetTop")
    pg.wait_for_timeout(1400)

    print("=== 1. 初始状态 ===")
    s = pg.evaluate(STATE)
    print("   ", s)
    chk(s["n"] == 13, "13 个 leaf（12 照片 + 1 尾页）")
    chk(s["flipped"] == 0, "初始无翻页")
    chk(s["topLeaf"] == 0, "最上层是 leaf0")
    chk(s["prevDis"] is True, "首页上一页按钮禁用")
    chk(s["onDots"] == 1 and s["onDotIdx"] == 0, "圆点唯一且在第 0 位")

    print("=== 2. 单击下一页（中途 + 完成） ===")
    pg.click("#bNext"); pg.wait_for_timeout(260)
    m = pg.evaluate(STATE)
    chk(m["turning"] == 1, "翻页中 turning=1")
    chk(m["topLeaf"] == 0, "翻页中：正在翻的 leaf0 置顶（z=999）")
    pg.screenshot(path=os.path.join(OUT, "flip-01-mid.png"))
    pg.wait_for_timeout(900)
    s = pg.evaluate(STATE)
    print("   ", s)
    chk(s["flipped"] == 1, "翻页完成 flipped=1")
    chk(s["turning"] == 0, "turning 已清除")
    chk(s["topLeaf"] == 1, "z-index 已复位 → 最上层为 leaf1（修复前是 leaf0）")
    chk(s["onDotIdx"] == 1, "圆点跟到第 1 位")
    pg.screenshot(path=os.path.join(OUT, "flip-02.png"))

    print("=== 3. 连点 3 次 → 应逐页收敛 ===")
    pg.click("#bNext"); pg.click("#bNext"); pg.click("#bNext")
    pg.wait_for_timeout(3000)
    s = pg.evaluate(STATE)
    print("   ", s)
    chk(s["flipped"] == 4, "连点 3 次后 flipped=4（页码连续，不跳页）")
    chk(s["topLeaf"] == 4, "最上层为 leaf4")
    chk(s["turning"] == 0, "动画已全部结束")

    print("=== 4. 回翻 1 页 ===")
    pg.click("#bPrev"); pg.wait_for_timeout(1100)
    s = pg.evaluate(STATE)
    print("   ", s)
    chk(s["flipped"] == 3, "回翻后 flipped=3")
    chk(s["topLeaf"] == 3, "最上层为 leaf3")
    pg.screenshot(path=os.path.join(OUT, "flip-04-back.png"))

    print("=== 5. 拖拽翻页 ===")
    rect = pg.evaluate("()=>{const r=document.getElementById('bookVp').getBoundingClientRect();return {l:Math.round(r.left),t:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)};}")
    print("    bookVp rect:", rect)
    pg.mouse.move(300, 520); pg.mouse.down()
    pg.mouse.move(120, 524, steps=8); pg.mouse.up()
    pg.wait_for_timeout(1100)
    s = pg.evaluate(STATE)
    chk(s["flipped"] == 4, "左滑前进 1 页")

    print("=== 6. 一路翻到尾页 ===")
    for _ in range(14):
        try:
            pg.click("#bNext", timeout=1500)
        except Exception:
            break
        pg.wait_for_timeout(180)
    pg.wait_for_timeout(5000)
    s = pg.evaluate(STATE)
    print("   ", s)
    chk(s["flipped"] == 12, "12 张照片全部翻过")
    chk(s["counter"] == "尾声", "计数器显示「尾声」")
    chk(s["all"] == "", "总数占位已清空")
    chk(s["nextDis"] is True, "末页下一页按钮禁用")
    chk(s["onDotIdx"] == 12, "圆点在最后一位")
    pg.screenshot(path=os.path.join(OUT, "flip-05-end.png"))

    print("=== 7. 键盘（桌面端） ===")
    pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(1000)
    s = pg.evaluate(STATE)
    chk(s["flipped"] == 11, "← 键回翻一页")

    ctx.close(); b.close()

print()
print("失败项:", fails if fails else "无 ✓")
