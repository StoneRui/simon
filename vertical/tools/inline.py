# -*- coding: utf-8 -*-
"""
把 index.html 打成单文件版：图片与音乐全部转成 base64 内联，零外部依赖。
用法：python tools/inline.py
产出：请柬-竖屏版-单文件.html

注意：og:image（微信分享缩略图）必须是 http(s) 绝对地址，内联的 data URI 不生效；
因此 share-cover 保持原路径引用，并在文件头注释中提示上传后替换。
"""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")
DST = os.path.join(ROOT, "请柬-竖屏版-单文件.html")

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".mp3": "audio/mpeg", ".m4a": "audio/mp4"}

# 不内联的资源：分享缩略图必须是线上绝对地址
SKIP = ("assets/share-cover.jpg",)


def data_uri(rel):
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    ext = os.path.splitext(p)[1].lower()
    if ext not in MIME:
        raise SystemExit("不支持的资源类型: " + rel)
    with open(p, "rb") as f:
        b = f.read()
    print(f"  内联 {rel:36s} {len(b)/1024:8.0f} KB")
    return "data:%s;base64,%s" % (MIME[ext], base64.b64encode(b).decode("ascii"))


html = open(SRC, encoding="utf-8").read()

# 1) 所有本地资源（图片 / 音乐），跳过分享缩略图
paths = re.findall(r'"(assets/[^"\\]+\.(?:jpg|jpeg|png|webp|mp3|m4a))"', html)
paths = [p for p in sorted(set(paths)) if p not in SKIP]
print(f"待内联资源 {len(paths)} 个")
for rel in paths:
    html = html.replace('"%s"' % rel, '"%s"' % data_uri(rel))

# 2) 头部注释
note = ("<!-- 单文件版：照片与背景音乐已全部内联为 base64，可脱离 assets 目录独立打开。"
        "唯一外部依赖是 og:image 分享缩略图，上传后请改成 https 绝对地址。 -->\n")
html = html.replace("<title>", note + "<title>", 1)

open(DST, "w", encoding="utf-8").write(html)
print(f"\n-> {os.path.basename(DST)}  {os.path.getsize(DST)/1024/1024:.2f} MB")

leftover = re.findall(r'(?:src|href|content)="(assets/[^"]+)"', html)
print("残留本地引用（应仅有 share-cover）:", leftover or "无")
