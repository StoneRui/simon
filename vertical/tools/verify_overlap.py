# -*- coding: utf-8 -*-
"""浮层/文字遮挡检查（修正版：选择器限定在当前场景内）
   两个状态都测：① 未点击（音乐提示在播放条内） ② 已点击"""
import os, itertools
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "http://127.0.0.1:8951/index.html"

SCENES = ["s-cover", "s-1", "s-2", "s-3", "s-book", "s-invite", "s-finale"]

TARGETS = {
    "s-cover":  [".cover-top", ".cover-bottom", ".scroll-hint"],
    "s-1":      [".ch-body", ".corner.tl", ".corner.bl"],
    "s-2":      [".ch-body", ".corner.tl", ".corner.bl"],
    "s-3":      [".ch-body", ".corner.tl", ".corner.bl"],
    "s-book":   [".book-head", ".book-vp", ".dots", ".book-bar"],
    "s-invite": [".card", ".inv-photo"],
    "s-finale": [".fin-inner"],
}
ALWAYS = ["#player"]

JS = """
([sceneId, sels]) => {
  const root = document.getElementById(sceneId);
  const out = {};
  sels.forEach(s => {
    const e = root.querySelector(s);
    if (!e) { out[s] = null; return; }
    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.02) { out[s] = 'hidden'; return; }
    const r = e.getBoundingClientRect();
    out[s] = { t: Math.round(r.top), b: Math.round(r.bottom), l: Math.round(r.left), r: Math.round(r.right) };
  });
  out.__vh = window.innerHeight; out.__vw = window.innerWidth;
  return out;
}
"""

SCROLL = """
(id) => {
  const st = document.getElementById('stage');
  st.style.scrollBehavior = 'auto';
  st.scrollTop = document.getElementById(id).offsetTop;
  return st.scrollTop;
}
"""

def overlap(a, b):
    ox = min(a["r"], b["r"]) - max(a["l"], b["l"])
    oy = min(a["b"], b["b"]) - max(a["t"], b["t"])
    return (ox > 2 and oy > 2), ox, oy

CASES = [("390x844", 390, 844, 3), ("430x932", 430, 932, 3), ("375x667", 375, 667, 2),
         ("360x740", 360, 740, 3), ("320x568", 320, 568, 2),
         ("Desktop1440x900", 1440, 900, 1)]

problems = []

def measure(pg, label, sc, phase):
    sels = TARGETS[sc] + ALWAYS
    d = pg.evaluate(JS, [sc, sels])
    vw, vh = d["__vw"], d["__vh"]
    boxes = {k: v for k, v in d.items() if not k.startswith("__") and isinstance(v, dict)}
    for k, v in boxes.items():
        if v["l"] < -1 or v["r"] > vw + 1:
            problems.append("%s|%s|%s: %s 横向越界 l=%d r=%d vw=%d" % (label, sc, phase, k, v["l"], v["r"], vw))
        if v["b"] > vh + 1:
            problems.append("%s|%s|%s: %s 超出底部 b=%d vh=%d" % (label, sc, phase, k, v["b"], vh))
    for a, bb in itertools.combinations(boxes.items(), 2):
        ov, ox, oy = overlap(a[1], bb[1])
        if ov:
            problems.append("%s|%s|%s: %s 与 %s 重叠 %dx%d" % (label, sc, phase, a[0], bb[0], ox, oy))
    return boxes

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    for label, w, h, dsf in CASES:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dsf,
                            is_mobile=(w < 900), has_touch=(w < 900))
        pg = ctx.new_page()
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1200)
        print("════════ %s ════════" % label)
        meta = pg.evaluate("""()=>({
          stageH: document.getElementById('stage').clientHeight,
          sceneH: [...document.querySelectorAll('.scene')].map(s=>s.id+'='+Math.round(s.getBoundingClientRect().height))
        })""")
        print("  舞台高=%d   各屏高: %s" % (meta["stageH"], "  ".join(meta["sceneH"])))

        for phase in ("未点击", "已点击"):
            if phase == "已点击":
                pg.mouse.click(w // 2, int(h * 0.22))
                pg.wait_for_timeout(1100)
            for sc in SCENES:
                pg.evaluate(SCROLL, sc)
                pg.wait_for_timeout(650)
                bx = measure(pg, label, sc, phase)
                print("  [%s][%s] %s" % (sc, phase, "  ".join(
                    "%s=%s" % (k, "隐" if v == "hidden" else ("无" if v is None else "%d-%d" % (v["t"], v["b"])))
                    for k, v in bx.items())))
        print()
        ctx.close()
    b.close()

print("=" * 62)
print("问题数:", len(problems))
for x in problems:
    print("  -", x)
