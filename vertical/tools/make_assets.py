# -*- coding: utf-8 -*-
r"""
竖屏版请柬 · 资源生成（迪士尼童话升级版）
源：D:\BaiduNetdiskDownload\精修 -二次
出：vertical/assets/img/

版式需求：
  hero-castle   0.62 竖  —— 首页城堡主视觉（视差 + 缓慢缩放）
                          源图为 6000x4000 横构图，必须裁到「城堡中段」这一竖条：
                          取景窗左边界固定在 46% 处，正好把原图左侧被切到的新人排除在画面外
  chapter-1..3  1.90 横  —— 三章叙事页的低透明度氛围底图
  book-01..12   0.75 竖  —— 3D 翻书相册内页（3:4，跨页不裁人）
  finale        0.62 竖  —— 结尾合照背景（取景窗中心对准两人，人像居画面正中）
  invite        1.50 横  —— 诚邀赴宴页底部照片带（原图不裁，两人同框）
"""
import os
from PIL import Image, ImageOps

SRC = r"D:\BaiduNetdiskDownload\精修 -二次"
OUT = r"C:\Users\Stone\WorkBuddy\小八\wedding-invitation\vertical\assets\img"

# (输出文件, 源文件, 比例, 横向锚点, 纵向锚点, 说明)
PICKS = [
    # 首页城堡主视觉：竖条取景，castle 居中，不含人物
    ("hero-castle.jpg", "DQ6A0857.jpg", 0.62, 0.784, 0.50, "城堡竖条取景（无人）"),

    # 三章氛围底图
    ("chapter-1.jpg", "DQ6A0777.jpg", 1.90, 0.50, 0.46, "相识 · 室内古堡暖金"),
    ("chapter-2.jpg", "DQ6A1003.jpg", 1.90, 0.50, 0.46, "相恋 · 石墙双人"),
    ("chapter-3.jpg", "DQ6A1040.jpg", 1.90, 0.50, 0.46, "携手 · 海边同行"),

    # 相册 12 内页（3:4）
    ("book-01.jpg",  "DQ6A0777.jpg", 0.75, 0.50, 0.45, "室内沙发双人"),
    ("book-02.jpg",  "DQ6A0753.jpg", 0.75, 0.52, 0.44, "古堡厅内双人"),
    ("book-03.jpg",  "DQ6A0779.jpg", 0.75, 0.50, 0.33, "贴脸近景"),
    ("book-04.jpg",  "DQ6A1003.jpg", 0.75, 0.50, 0.46, "石墙前双人"),
    ("book-05.jpg",  "DQ6A0998.jpg", 0.75, 0.50, 0.42, "拱门双人"),
    ("book-06.jpg",  "DQ6A0897.jpg", 0.75, 0.50, 0.46, "金厅栏杆双人"),
    ("book-07.jpg",  "DQ6A1040.jpg", 0.75, 0.50, 0.46, "海边牵手散步"),
    ("book-08.jpg",  "DQ6A1046.jpg", 0.75, 0.50, 0.42, "海边双人晴日"),
    ("book-09.jpg",  "DQ6A1187.jpg", 0.75, 0.50, 0.44, "礁石日落双人"),
    ("book-10.jpg",  "DQ6A0851.jpg", 0.75, 0.50, 0.44, "城堡台阶"),
    ("book-11.jpg",  "DQ6A1024.jpg", 0.75, 0.50, 0.42, "城堡前近景"),
    ("book-12.jpg",  "DQ6A1201.jpg", 0.75, 0.50, 0.44, "礁石日落仙女棒"),

    # 结尾合照背景：取景窗横移，让两人正好落在竖屏画面正中
    ("finale.jpg", "DQ6A1222.jpg", 0.62, 0.619, 0.50, "礁石仙女棒蓝调 · 人像居中"),

    # 诚邀赴宴页底部照片带：原图 3:2 不裁，两人同框
    ("invite.jpg", "DQ6A1016.jpg", 1.50, 0.50, 0.50, "城堡前牵手 · 原图全幅"),
]

MAXW = {0.62: 1080, 0.72: 1080, 1.90: 1200, 0.75: 880, 1.50: 1400}

os.makedirs(OUT, exist_ok=True)
total = 0
for dst, src, ratio, ax, ay, note in PICKS:
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, src))).convert("RGB")
    w = MAXW[ratio]
    size = (w, round(w / ratio))
    out = ImageOps.fit(im, size, Image.LANCZOS, centering=(ax, ay))
    p = os.path.join(OUT, dst)
    out.save(p, "JPEG", quality=78, optimize=True, progressive=True)
    kb = os.path.getsize(p) / 1024
    total += kb
    print(f"{dst:18s} {size[0]}x{size[1]:5d}  {kb:6.0f} KB   {note}")

# 朋友圈分享缩略图：改用城堡全景（视觉辨识度最高）
im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, "DQ6A0857.jpg"))).convert("RGB")
sq = ImageOps.fit(im, (600, 600), Image.LANCZOS, centering=(0.52, 0.36))
sq.save(r"C:\Users\Stone\WorkBuddy\小八\wedding-invitation\vertical\assets\share-cover.jpg",
        "JPEG", quality=86, optimize=True, progressive=True)
print("share-cover.jpg    600x600   %6.0f KB" % (
    os.path.getsize(r"C:\Users\Stone\WorkBuddy\小八\wedding-invitation\vertical\assets\share-cover.jpg") / 1024))

print(f"\n合计 {total/1024:.2f} MB / {len(PICKS)+1} 张")
