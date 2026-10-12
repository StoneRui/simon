# -*- coding: utf-8 -*-
"""
用本机 Chrome 在精确移动视口下逐屏渲染并截图 + 量测。
用法：python tools/verify.py
"""
import os, sys, json
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "_shot")
URL = "http://127.0.0.1:8951/index.html"

DEVICES = [
    ("iPhone14-390x844", 390, 844, 3),
    ("iPhone8-375x667",  375, 667, 2),
    ("SE-320x568",       320, 568, 2),
    ("Desktop-1440x900", 1440, 900, 1),
]

SCENES = ["s-cover", "s-1", "s-2", "s-3", "s-book", "s-invite", "s-finale"]

MEASURE = """
() => {
  const out = {};
  document.querySelectorAll('.scene').forEach(sc => {
    out[sc.id] = { content: sc.scrollHeight, view: sc.clientHeight };
  });
  const g = s => { const e = document.querySelector(s); if(!e) return null;
    const r = e.getBoundingClientRect();
    return { w: Math.round(r.width), h: Math.round(r.height),
             top: Math.round(r.top), bot: Math.round(r.bottom),
             l: Math.round(r.left), r: Math.round(r.right) }; };
  out._boxes = {
    crest: g('.crest'), coverBottom: g('.cover-bottom'), names: g('.cover-names'),
    date: g('.cover-date'), place: g('.cover-place'), enter: g('.enter'),
    hint: g('.scroll-hint'), card: g('.card'), bookVp: g('.book-vp'),
    bookWrap: g('.book-wrap'), finInner: g('.fin-inner'), player: g('#player'),
    gate: g('#gate')
  };
  // 文字实际宽度：用 Range 量（scrollWidth 量的是块宽，不准）
  const tw = s => { const e = document.querySelector(s); if(!e) return null;
    const r = document.createRange(); r.selectNodeContents(e);
    const rects = [...r.getClientRects()];
    if(!rects.length) return 0;
    return Math.round(Math.max(...rects.map(x => x.width))); };
  const nl = s => { const e = document.querySelector(s); if(!e) return null;
    const r = document.createRange(); r.selectNodeContents(e);
    return [...r.getClientRects()].length; };
  out._textW = { names: tw('.cover-names'), date: tw('.cover-date'),
                 place: tw('.cover-place'), kicker: tw('.kicker'),
                 chTitle: tw('.ch-title'), finTitle: tw('.fin-title'),
                 cardH2: tw('.card h2') };
  out._textLines = { names: nl('.cover-names'), date: nl('.cover-date'),
                     kicker: nl('.kicker'), finTitle: nl('.fin-title'),
                     cardH2: nl('.card h2') };
  out._vw = window.innerWidth; out._vh = window.innerHeight;
  out._stage = document.getElementById('stage').clientHeight;
  return out;
}
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--force-color-profile=srgb"])
        for name, w, h, dsf in DEVICES:
            ctx = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=dsf,
                is_mobile=(w < 900),
                has_touch=(w < 900),
            )
            page = ctx.new_page()
            page.goto(URL, wait_until="load")
            page.wait_for_timeout(900)
            # 模拟首次点击（关掉「轻触开启音乐」遮罩）
            page.mouse.click(w // 2, int(h * 0.30))
            page.wait_for_timeout(1100)

            print("=" * 62)
            print("%s  (viewport %dx%d, dpr %d)" % (name, w, h, dsf))
            m = page.evaluate(MEASURE)
            print("  innerViewport = %dx%d   stageH = %d"
                  % (m["_vw"], m["_vh"], m["_stage"]))
            print("  -- 每屏是否溢出 --")
            for sc in SCENES:
                d = m[sc]
                flag = "  <<< OVERFLOW +%d" % (d["content"] - d["view"]) if d["content"] > d["view"] + 1 else ""
                print("     %-9s content=%-5d view=%-5d%s" % (sc, d["content"], d["view"], flag))
            print("  -- 文字实际宽度 / 行数 --")
            slotw = m["_vw"] - 40
            for k, v in m["_textW"].items():
                if v is None:
                    continue
                lines = m["_textLines"].get(k)
                extra = "" if lines is None else "  lines=%d" % lines
                wrap = "  <<< 换行" if (lines or 1) > 1 and k != "finTitle" else ""
                print("     %-9s textW=%-5d (可用约 %d)%s%s" % (k, v, slotw, extra, wrap))
            print("  -- 关键盒子 --")
            for k, v in m["_boxes"].items():
                if v:
                    print("     %-12s w=%-4d h=%-4d top=%-5d bot=%-5d" % (k, v["w"], v["h"], v["top"], v["bot"]))

            for sc in SCENES:
                page.evaluate(
                    "id => { const s=document.getElementById(id);"
                    "const st=document.getElementById('stage');"
                    "st.scrollTop=s.offsetTop; }", sc)
                page.wait_for_timeout(1500)
                path = os.path.join(OUT, "%s__%s.png" % (name, sc))
                page.screenshot(path=path)
            print()
            ctx.close()
        browser.close()

    print("截图输出目录:", OUT)


if __name__ == "__main__":
    main()
