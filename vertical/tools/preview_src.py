# -*- coding: utf-8 -*-
"""预览指定源图的构图（带坐标网格），用于确定裁切锚点。"""
import os
import sys
from PIL import Image, ImageDraw, ImageOps

SRC = "D:/BaiduNetdiskDownload/精修 -二次"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_shot")

for src in sys.argv[1:]:
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, src))).convert("RGB")
    W, H = im.size
    v = im.resize((1000, round(1000 * H / W)), Image.LANCZOS)
    d = ImageDraw.Draw(v)
    for i in range(1, 10):
        x = i * v.size[0] // 10
        d.line([(x, 0), (x, v.size[1])], fill=(255, 70, 70), width=1)
        d.text((x + 3, 4), "%.1f" % (i / 10), fill=(255, 220, 120))
    for i in range(1, 6):
        y = i * v.size[1] // 6
        d.line([(0, y), (v.size[0], y)], fill=(90, 180, 255), width=1)
        d.text((4, y + 3), "%.2f" % (i / 6), fill=(140, 210, 255))
    name = os.path.splitext(src)[0]
    v.save(os.path.join(OUT, "_src-%s.png" % name))
    print(src, im.size, "ratio", round(W / H, 3))
