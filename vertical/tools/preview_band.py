# -*- coding: utf-8 -*-
"""针对某张横构图源图，模拟「竖屏 cover 裁切」后的真实可见范围，出候选对比图。

用法：python tools/preview_band.py 源文件名 中心位置1 中心位置2 ...
      中心位置 = 可见竖条在源图中的水平中心（0~1）
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

SRC = "D:/BaiduNetdiskDownload/精修 -二次"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_shot")
FRAME = 390 / 844          # 目标机型屏幕比例（iPhone14）
TH = 520                   # 预览高度

src = sys.argv[1]
centers = [float(a) for a in sys.argv[2:]]

im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, src))).convert("RGB")
W, H = im.size
band = H * FRAME           # 竖屏实际可见的源图宽度（像素）
print("%s  %dx%d  可见带宽 %.1f%% 源图宽" % (src, W, H, band / W * 100))

tiles = []
for c in centers:
    left = c * W - band / 2
    left = max(0, min(W - band, left))
    t = im.crop((round(left), 0, round(left + band), H))
    t = t.resize((round(TH * FRAME), TH), Image.LANCZOS)
    tiles.append((c, t))

pad = 12
tw = round(TH * FRAME)
sheet = Image.new("RGB", ((tw + pad) * len(tiles) + pad, TH + 34), (26, 24, 32))
d = ImageDraw.Draw(sheet)
for i, (c, t) in enumerate(tiles):
    x = pad + i * (tw + pad)
    sheet.paste(t, (round(x), 30))
    d.text((x + 4, 8), "center=%.2f" % c, fill=(255, 220, 150))
name = os.path.splitext(src)[0]
sheet.save(os.path.join(OUT, "_band-%s.png" % name))
print("-> _shot/_band-%s.png" % name)
