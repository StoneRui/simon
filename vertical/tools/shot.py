# -*- coding: utf-8 -*-
"""对单个场景在指定机型下截图，用于人工目检。"""
import os
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8951/index.html"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_shot")
DEVS = {
    "iPhone14": (390, 844, 3),
    "iPhone8": (375, 667, 2),
    "SE": (320, 568, 2),
    "Desktop": (1440, 900, 1),
}

scenes = sys.argv[1].split(",")
devs = sys.argv[2].split(",") if len(sys.argv) > 2 else ["iPhone14"]

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    for dn in devs:
        w, h, dpr = DEVS[dn]
        c = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr,
                          is_mobile=(dn != "Desktop"), has_touch=(dn != "Desktop"))
        pg = c.new_page()
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(2200)
        for sid in scenes:
            pg.locator("#" + sid).scroll_into_view_if_needed()
            pg.wait_for_timeout(700)
            pg.locator("#" + sid).screenshot(path=os.path.join(OUT, "v-%s-%s.png" % (dn, sid)))
        c.close()
    b.close()
print("ok")
