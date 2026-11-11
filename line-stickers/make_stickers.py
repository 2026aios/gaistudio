"""產生 LINE 動態貼圖（APNG）與逐格 PNG。

用法：python3 cutout.py && python3 make_stickers.py
輸出：out/NN_name/frame_XX.png、out/NN_name.png（APNG）、out/main.png、out/tab.png
規格（LINE Creators Market 動態貼圖）：
  - 最大 320x270，透明背景，5–20 格，播放總時間 ≤ 4 秒，檔案 ≤ 300KB
  - 主要圖片 240x240（APNG），標籤圖片 96x74（PNG）
"""
import math
import os
import random
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "smash"))
from make_smash import to_palette  # noqa: E402  共用色盤減色

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
W, H = 320, 270
SS = 2  # supersampling
CW, CH = W * SS, H * SS
FONT = os.path.join(HERE, "fonts", "jf-openhuninn-2.1.ttf")  # jf open 粉圓（SIL OFL，可商用）
INK = (74, 52, 46)  # 統一用深咖啡色字＋白色描邊（可愛貼圖風格）

cut = Image.open(os.path.join(HERE, "cut.png")).convert("RGBA")
cut = cut.crop(cut.getbbox())
FIG_H = 250 * SS  # figure height on canvas
BASE = cut.resize((round(cut.width * FIG_H / cut.height), FIG_H), Image.LANCZOS)


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def canvas():
    return Image.new("RGBA", (CW, CH), (0, 0, 0, 0))


def place(c, cx, bottom, sx=1.0, sy=1.0, angle=0.0, scale=1.0, img=BASE):
    """把人物以腳底中心 (cx, bottom) 為錨點放到畫布上，可擠壓/伸展/旋轉。"""
    w = max(1, round(img.width * sx * scale))
    h = max(1, round(img.height * sy * scale))
    s = img.resize((w, h), Image.LANCZOS)
    if angle:
        # 以腳底為軸旋轉：先把圖放進以底部中心為中心的方形
        pad = Image.new("RGBA", (w * 2 + h, h * 2), (0, 0, 0, 0))
        pad.paste(s, ((pad.width - w) // 2, 0), s)
        pad = pad.rotate(angle, resample=Image.BICUBIC, center=(pad.width / 2, h))
        c.alpha_composite(pad, (round(cx - pad.width / 2), round(bottom - h)))
    else:
        c.alpha_composite(s, (round(cx - w / 2), round(bottom - h)))


def shadow(c, cx, y, rx, alpha=60):
    d = ImageDraw.Draw(c)
    ry = rx * 0.22
    d.ellipse((cx - rx, y - ry, cx + rx, y + ry), fill=(40, 60, 90, alpha))


def text(c, s, xy, size, fill=(255, 214, 0), stroke=(30, 40, 110), angle=0, scale=1.0, anchor="mm"):
    size = max(4, int(size * scale))
    f = ImageFont.truetype(FONT, size)
    layer = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, s, font=f, fill=INK, stroke_width=max(2, size // 8),
                               stroke_fill=(255, 255, 255), anchor=anchor)
    if angle:
        layer = layer.rotate(angle, resample=Image.BICUBIC, center=xy)
    c.alpha_composite(layer)


def shuttle(c, x, y, ang, size=1.0):
    """羽毛球：ang 為飛行方向（度），球頭朝前。"""
    L = 34 * SS * size
    R = 9 * SS * size
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    d = ImageDraw.Draw(c)
    tail = (x - ux * L, y - uy * L)
    base = (x - ux * R * 0.6, y - uy * R * 0.6)
    spread = R * 2.0
    poly = [(base[0] + px * R * 0.8, base[1] + py * R * 0.8),
            (tail[0] + px * spread, tail[1] + py * spread),
            (tail[0] - px * spread, tail[1] - py * spread),
            (base[0] - px * R * 0.8, base[1] - py * R * 0.8)]
    d.polygon(poly, fill=(255, 255, 255, 255), outline=(40, 50, 90, 255), width=2 * SS)
    for k in (-0.5, 0, 0.5):
        d.line([base, (tail[0] + px * spread * k, tail[1] + py * spread * k)], fill=(150, 160, 190, 255), width=SS)
    d.ellipse((x - R, y - R, x + R, y + R), fill=(255, 248, 230, 255), outline=(40, 50, 90, 255), width=2 * SS)


def speed_lines(c, x, y, ang, n=3, length=50, alpha=200):
    d = ImageDraw.Draw(c)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    for k in range(n):
        off = (k - (n - 1) / 2) * 10 * SS
        sx, sy = x - ux * 40 * SS + px * off, y - uy * 40 * SS + py * off
        d.line([(sx, sy), (sx - ux * length * SS, sy - uy * length * SS)], fill=(80, 120, 230, alpha), width=3 * SS)


def star(c, x, y, r, rot=0, fill=(255, 214, 0, 255)):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(rot + i * 36 - 90)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    ImageDraw.Draw(c).polygon(pts, fill=fill, outline=(30, 40, 110, 255), width=SS)


def burst(c, x, y, r, n=8, rot=0, alpha=255):
    d = ImageDraw.Draw(c)
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        d.line([(x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.5),
                (x + math.cos(a) * r, y + math.sin(a) * r)], fill=(255, 170, 0, alpha), width=4 * SS)


def heart(c, x, y, r, fill=(255, 92, 140, 255)):
    d = ImageDraw.Draw(c)
    d.ellipse((x - r, y - r, x, y), fill=fill)
    d.ellipse((x, y - r, x + r, y), fill=fill)
    d.polygon([(x - r * 0.97, y - r * 0.35), (x + r * 0.97, y - r * 0.35), (x, y + r * 0.95)], fill=fill)


def sweat(c, x, y, s=1.0):
    r = 6 * SS * s
    d = ImageDraw.Draw(c)
    d.polygon([(x, y - r * 2.2), (x - r, y), (x + r, y)], fill=(120, 200, 255, 255))
    d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 200, 255, 255), outline=(40, 90, 170, 255), width=SS)


def puff(c, x, y, r, alpha):
    d = ImageDraw.Draw(c)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(220, 225, 235, alpha), outline=(150, 160, 180, alpha), width=SS)


CX = CW // 2
FLOOR = CH - 8 * SS

# 人物在畫布上的幾個參考點（相對比例，用於特效定位）
fw = BASE.width
RACKET = (CX - fw * 0.20, FLOOR - FIG_H * 0.93)  # 拍面約略位置
HEAD = (CX - fw * 0.02, FLOOR - FIG_H * 0.80)


# ---------------- 各張貼圖 ----------------
def s_jump(i, n):
    """01 跳躍：蹲 → 起跳 → 落地（擠壓伸展）"""
    t = i / n
    c = canvas()
    if t < 0.15:
        k = t / 0.15
        sx, sy, lift = 1 + 0.06 * k, 1 - 0.08 * k, 0
    elif t < 0.75:
        k = (t - 0.15) / 0.6
        lift = math.sin(math.pi * k) * 14 * SS
        sx, sy = 0.97, 1.03
    else:
        k = (t - 0.75) / 0.25
        sq = math.sin(math.pi * k)
        sx, sy, lift = 1 + 0.06 * sq, 1 - 0.07 * sq, 0
    shadow(c, CX, FLOOR, fw * 0.33 * (1 - lift / (40 * SS)), 70)
    place(c, CX, FLOOR - lift, sx * 0.92, sy * 0.92)
    return c


def s_smash(i, n):
    """02 殺球！：球從右上飛入→擊中爆星→球朝右下飛走＋文字"""
    t = i / n
    c = canvas()
    shake = 0
    hit = 0.45
    if abs(t - hit) < 0.12:
        shake = (1 if i % 2 else -1) * 3 * SS
    place(c, CX - 40 * SS + shake, FLOOR, 0.92, 0.92, angle=-4 if t > hit else 0)
    rx, ry = CX - 40 * SS - fw * 0.17, FLOOR - FIG_H * 0.86
    if t < hit:
        k = ease(t / hit)
        x = CW + 20 * SS + (rx - CW - 20 * SS) * k
        y = -10 * SS + (ry + 10 * SS) * k
        shuttle(c, x, y, 200)
    else:
        k = (t - hit) / (1 - hit)
        if k < 0.35:
            burst(c, rx, ry, (20 + 40 * k) * SS, rot=k * 90)
            star(c, rx, ry, (14 + 10 * k) * SS, rot=k * 120)
        x = rx + (CW - rx) * k * 1.3
        y = ry + (FLOOR - ry) * k * 0.9
        speed_lines(c, x, y, 35)
        shuttle(c, x, y, 35)
        text(c, "殺！", (CW - 62 * SS, 60 * SS), 54 * SS, scale=min(1, 0.4 + k * 2), angle=10)
    return c


def s_cheer(i, n):
    """03 加油：彈跳＋文字跳動"""
    t = i / n
    c = canvas()
    b = abs(math.sin(2 * math.pi * t))
    lift = b * 10 * SS
    sq = 1 - b
    shadow(c, CX - 45 * SS, FLOOR, fw * 0.30, 60)
    place(c, CX - 45 * SS, FLOOR - lift, 0.92 * (1 + 0.04 * sq), 0.92 * (1 - 0.04 * sq))
    for k, ch in enumerate("加油"):
        ph = math.sin(2 * math.pi * t - k * 1.2)
        text(c, ch, (CW - 96 * SS + k * 40 * SS, 62 * SS + k * 34 * SS - ph * 8 * SS), 52 * SS,
             angle=8 - ph * 6)
    text(c, "!", (CW - 30 * SS, 150 * SS - math.sin(2 * math.pi * t) * 6 * SS), 52 * SS)
    return c


def s_wiggle(i, n):
    """04 開心搖擺：左右擺動＋愛心飄"""
    t = i / n
    c = canvas()
    ang = math.sin(2 * math.pi * t) * 6
    shadow(c, CX, FLOOR, fw * 0.30, 60)
    place(c, CX, FLOOR, 0.92, 0.92, angle=ang)
    for k in range(3):
        p = (t + k / 3) % 1
        x = CX + 95 * SS + math.sin(p * 6 + k) * 10 * SS - k * 20 * SS
        y = FLOOR - 60 * SS - p * 170 * SS
        heart(c, x, y, (10 + 4 * k) * SS * (0.6 + 0.4 * math.sin(p * math.pi)))
    return c


def s_nice(i, n):
    """05 好球！：放大彈出＋星星旋轉"""
    t = i / n
    c = canvas()
    if t < 0.3:
        k = t / 0.3
        sc = 0.75 + 0.3 * math.sin(k * math.pi * 0.5) + 0.05 * math.sin(k * math.pi)
    else:
        sc = 1.0 + 0.02 * math.sin((t - 0.3) * 8 * math.pi)
    place(c, CX - 35 * SS, FLOOR, 0.88 * sc, 0.88 * sc)
    for k in range(4):
        a = 2 * math.pi * (t + k / 4)
        star(c, CX + 85 * SS + math.cos(a) * 30 * SS, 130 * SS + math.sin(a) * 18 * SS, 9 * SS, rot=t * 360)
    text(c, "好球！", (CX + 85 * SS, 60 * SS), 46 * SS, scale=min(1.0, 0.3 + t * 3), angle=6,
         fill=(255, 255, 255), stroke=(220, 40, 90))
    return c


def s_run(i, n):
    """06 衝啊！：前後奔跑抖動＋煙塵＋汗"""
    t = i / n
    c = canvas()
    bob = abs(math.sin(4 * math.pi * t)) * 6 * SS
    x = CX - 20 * SS + math.sin(2 * math.pi * t) * 6 * SS
    for k in range(3):
        p = (t + k / 3) % 1
        puff(c, x - 50 * SS - p * 60 * SS, FLOOR - 8 * SS - p * 12 * SS, (8 + p * 14) * SS, int(200 * (1 - p)))
    place(c, x, FLOOR - bob, 0.92, 0.92, angle=-5)
    sweat(c, HEAD[0] + 40 * SS, HEAD[1] - 10 * SS + (t * 30 % 10) * SS)
    for k in range(3):
        y = 90 * SS + k * 40 * SS
        ImageDraw.Draw(c).line([(18 * SS, y), ((40 + 20 * ((i + k) % 2)) * SS, y)], fill=(80, 120, 230, 200), width=3 * SS)
    text(c, "衝啊！", (CW - 66 * SS, 48 * SS), 44 * SS, angle=8 + math.sin(4 * math.pi * t) * 4)
    return c


def s_thanks(i, n):
    """07 謝謝：前傾鞠躬＋文字淡入"""
    t = i / n
    c = canvas()
    k = math.sin(math.pi * t)
    shadow(c, CX - 30 * SS, FLOOR, fw * 0.30, 60)
    place(c, CX - 30 * SS, FLOOR, 0.92, 0.92 * (1 - 0.04 * k), angle=-14 * k)
    text(c, "謝謝", (CW - 60 * SS, 70 * SS), 52 * SS, fill=(255, 255, 255), stroke=(40, 110, 200),
         scale=0.85 + 0.15 * k)
    for j in range(2):
        star(c, CW - 30 * SS - j * 70 * SS, 120 * SS + j * 10 * SS, 7 * SS * (0.5 + k), rot=t * 200)
    return c


def s_ready(i, n):
    """08 等你來：原地輕晃＋羽毛球在上方拋接"""
    t = i / n
    c = canvas()
    breathe = math.sin(2 * math.pi * t)
    place(c, CX - 50 * SS, FLOOR, 0.92 * (1 + 0.01 * breathe), 0.92 * (1 - 0.012 * breathe))
    h = math.sin(math.pi * t)
    x = CX + 70 * SS
    y = 240 * SS - h * 140 * SS
    shuttle(c, x, y, 90 if t < 0.5 else -90, 0.9)
    text(c, "來比\n一場？", (CW - 58 * SS, 52 * SS), 34 * SS, fill=(255, 255, 255), stroke=(30, 40, 110))
    return c


# (名稱, 函式, 格數, 每格毫秒)：格數 × 毫秒 × 循環次數 必須剛好是 1～4 秒（LINE 規定）
STICKERS = [
    ("01_jump", s_jump, 10, 100),     # 1 秒 × 4 次
    ("02_smash", s_smash, 20, 100),   # 2 秒 × 2 次
    ("03_cheer", s_cheer, 10, 100),   # 1 秒 × 4 次
    ("04_wiggle", s_wiggle, 10, 100), # 1 秒 × 4 次
    ("05_nice", s_nice, 10, 150),     # 1.5 秒 × 2 次 = 3 秒
    ("06_run", s_run, 10, 100),       # 1 秒 × 4 次
    ("07_thanks", s_thanks, 10, 150), # 1.5 秒 × 2 次 = 3 秒
    ("08_ready", s_ready, 10, 100),   # 1 秒 × 4 次
]


def save_apng(frames, path, dur, size=None):
    if size:
        frames = [f.resize(size, Image.LANCZOS) for f in frames]
    total = dur * len(frames)
    loops = max(1, min(4, 4000 // total))  # 播放總時間 ≤ 4 秒
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=dur, loop=loops,
                   disposal=1, blend=0, optimize=True)
    return loops, total


COLORS = 64


def quantize(img):
    """減色以控制檔案大小（保留透明）"""
    a = img.getchannel("A").point(lambda v: 255 if v > 110 else 0)
    img = img.copy()
    img.putalpha(a)
    return img.quantize(colors=COLORS, method=Image.FASTOCTREE, dither=Image.NONE).convert("RGBA")


def main():
    os.makedirs(OUT, exist_ok=True)
    random.seed(1)
    report = []
    for name, fn, n, dur in STICKERS:
        d = os.path.join(OUT, name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        raw = [fn(i, n).resize((W, H), Image.LANCZOS) for i in range(n)]
        p = os.path.join(OUT, f"{name}.png")
        for colors in (256, 192, 128, 96, 64):
            frames = [f.convert("RGBA") for f in to_palette(raw, colors)]
            loops, total = save_apng(frames, p, dur)
            if os.path.getsize(p) <= 300 * 1024:
                break
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"frame_{i:02d}.png"), optimize=True)
        kb = os.path.getsize(p) / 1024
        report.append(f"{name}: {n} 格, {dur}ms/格, 單次 {total/1000:.2f}s × {loops} 次, {colors} 色, {kb:.0f}KB")
    # 主要圖片 240x240：用 01 跳躍
    frames = []
    for i in range(10):
        big = s_jump(i, 10)
        sq = Image.new("RGBA", (CW, CW), (0, 0, 0, 0))
        sq.alpha_composite(big, (0, (CW - CH) // 2))
        frames.append(sq.resize((240, 240), Image.LANCZOS))
    save_apng([f.convert("RGBA") for f in to_palette(frames)], os.path.join(OUT, "main.png"), 100)
    # 標籤圖片 96x74（靜態）
    tab = s_nice(9, 10).resize((96, 81), Image.LANCZOS).crop((0, 4, 96, 78))
    tab.save(os.path.join(OUT, "tab.png"), optimize=True)
    print("\n".join(report))


if __name__ == "__main__":
    main()
