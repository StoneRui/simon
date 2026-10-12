# -*- coding: utf-8 -*-
"""精确量文字排版：矩形并集宽度、是否横向溢出、真实行数"""
import os
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "http://127.0.0.1:8951/index.html"

JS = """
() => {
  function info(sel){
    const e = document.querySelector(sel);
    if(!e) return null;
    const r = document.createRange(); r.selectNodeContents(e);
    const rects = [...r.getClientRects()].filter(x => x.width > 0 && x.height > 0);
    if(!rects.length) return {empty:true};
    const left = Math.min(...rects.map(x=>x.left));
    const right = Math.max(...rects.map(x=>x.right));
    // 真实行数：按 top 聚类
    const tops = [...new Set(rects.map(x=>Math.round(x.top)))].sort((a,b)=>a-b);
    const lines = [];
    tops.forEach(t => { if(!lines.length || t - lines[lines.length-1] > 4) lines.push(t); });
    const box = e.getBoundingClientRect();
    return {
      unionW: Math.round(right - left),
      lines: lines.length,
      clientW: e.clientWidth,
      scrollW: e.scrollWidth,
      boxH: Math.round(box.height),
      fontSize: getComputedStyle(e).fontSize,
      overflowX: (left < -1 || right > window.innerWidth + 1),
      clip: e.scrollWidth > e.clientWidth + 1
    };
  }
  return {
    vw: window.innerWidth,
    stageW: document.getElementById('stage').clientWidth,
    names: info('.cover-names'),
    date: info('.cover-date'),
    place: info('.cover-place'),
    kicker: info('.kicker'),
    chTitle: info('.ch-title'),
    chText: info('.ch-text'),
    finTitle: info('.fin-title'),
    finSub: info('.fin-sub'),
    cardH2: info('.card h2'),
    bookCap: info('.face.front .cap span')
  };
}
"""

CASES = [
    ("iPhone14 390x844", 390, 844, 3),
    ("iPhoneProMax 430x932", 430, 932, 3),
    ("iPhone8 375x667", 375, 667, 2),
    ("iPhoneSE1 320x568", 320, 568, 2),
    ("GalaxyS8 360x740", 360, 740, 3),
    ("Desktop 1440x900", 1440, 900, 1),
]

KEYS = ["names", "date", "place", "kicker", "chTitle", "chText", "finTitle", "finSub", "cardH2"]

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    for label, w, h, dsf in CASES:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dsf,
                            is_mobile=(w < 900), has_touch=(w < 900))
        pg = ctx.new_page()
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(900)
        d = pg.evaluate(JS)
        print("════ %s   vw=%d  stageW=%d" % (label, d["vw"], d["stageW"]))
        for k in KEYS:
            v = d.get(k)
            if not v or v.get("empty"):
                continue
            flag = ""
            if v["lines"] > 1 and k in ("names",):
                flag = "   <<< 不该换行！"
            if v["clip"]:
                flag += "   <<< 裁切!"
            if v["overflowX"]:
                flag += "   <<< 越出屏幕!"
            print("   %-9s 文字宽=%-4d 行=%d 字号=%-6s 盒宽=%-4d scrollW=%-4d 盒高=%-3d%s"
                  % (k, v["unionW"], v["lines"], v["fontSize"], v["clientW"], v["scrollW"], v["boxH"], flag))
        print()
        ctx.close()
    b.close()
