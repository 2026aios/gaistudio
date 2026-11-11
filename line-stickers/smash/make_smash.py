"""「殺爆你！」動態貼圖：把 6 格殺球動作排成時間軸，加上文字與特效。

用法：python3 key.py && python3 make_smash.py
輸出（out/）：
  smash_line.png   LINE 動態貼圖用 APNG（320x270、透明、20 格、≤4 秒、≤300KB）
  smash.mp4        白底預覽影片（640x540，循環 3 次）
  smash_green.mp4  綠幕影片（給剪輯 App 用）
  smash.gif        GIF 預覽
  frames/          逐格透明 PNG（320x270）
"""
import math, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
W, H = 320, 270
SS = 2
CW, CH = W * SS, H * SS
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
TEXT_LINES = ["殺爆", "你！"]

cells = [Image.open(os.path.join(HERE, "cells", f"cell_{k}.png")).convert("RGBA") for k in range(1, 7)]
# 所有格共用同一個裁切框與縮放，保持角色大小一致、保留跳躍高度
boxes = [c.getbbox() for c in cells]
X0, Y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
X1, Y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
SCALE = (CH - 14 * SS) / (Y1 - Y0)
FIG_LEFT = 4 * SS
FIG_TOP = 6 * SS


def to_canvas(x, y):
    """格內座標 → 畫布座標"""
    return FIG_LEFT + (x - X0) * SCALE, FIG_TOP + (y - Y0) * SCALE


def figure(k, dx=0, dy=0):
    c = cells[k].crop((X0, Y0, X1, Y1))
    c = c.resize((round(c.width * SCALE), round(c.height * SCALE)), Image.LANCZOS)
    return c, (round(FIG_LEFT + dx), round(FIG_TOP + dy))


def burst(d, x, y, r, rot, alpha=255):
    for i in range(10):
        a = math.radians(rot + i * 36)
        r0 = r * (0.45 if i % 2 else 0.3)
        d.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r, y + math.sin(a) * r)],
               fill=(255, 190, 0, alpha), width=5 * SS)


def star(d, x, y, r, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(rot + i * 36 - 90)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=(255, 235, 60, 255), outline=(120, 20, 20, 255), width=SS)


def shuttle(d, x, y, ang, size=1.0):
    L, R = 26 * SS * size, 7 * SS * size
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); px, py = -uy, ux
    tail = (x - ux * L, y - uy * L); base = (x - ux * R * 0.6, y - uy * R * 0.6); sp = R * 2
    d.polygon([(base[0] + px * R * .8, base[1] + py * R * .8), (tail[0] + px * sp, tail[1] + py * sp),
               (tail[0] - px * sp, tail[1] - py * sp), (base[0] - px * R * .8, base[1] - py * R * .8)],
              fill=(255, 255, 255, 255), outline=(40, 50, 90, 255), width=2 * SS)
    d.ellipse((x - R, y - R, x + R, y + R), fill=(255, 248, 230, 255), outline=(40, 50, 90, 255), width=2 * SS)
    for k in range(3):
        off = (k - 1) * 9 * SS
        sx, sy = tail[0] + px * off - ux * 6 * SS, tail[1] + py * off - uy * 6 * SS
        d.line([(sx, sy), (sx - ux * 40 * SS, sy - uy * 40 * SS)], fill=(255, 80, 60, 220), width=3 * SS)


def big_text(c, scale, shake, rot):
    """兩行大字，紅黃配色＋粗描邊，以右側為中心"""
    size = int(64 * SS * scale)
    if size < 6:
        return
    f = ImageFont.truetype(FONT, size)
    layer = Image.new("RGBA", c.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = CW - 82 * SS + shake[0], 92 * SS + shake[1]
    for i, line in enumerate(TEXT_LINES):
        y = cy + (i - 0.5) * size * 1.02
        x = cx + (i * 14 - 7) * SS * scale
        d.text((x + 4 * SS, y + 5 * SS), line, font=f, fill=(60, 10, 10, 160), anchor="mm")  # 陰影
        d.text((x, y), line, font=f, fill=(255, 40, 40), stroke_width=max(3, size // 7),
               stroke_fill=(255, 245, 120), anchor="mm")
        d.text((x, y), line, font=f, fill=(230, 20, 30), stroke_width=max(1, size // 22),
               stroke_fill=(70, 0, 10), anchor="mm")
    layer = layer.rotate(rot, resample=Image.BICUBIC, center=(cx, cy))
    c.alpha_composite(layer)


# 時間軸：每格 (動作格 index, 是否擊球瞬間)
TIMELINE = [0, 0, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5]
IMPACT = 6           # 擊球瞬間的時間點
DUR = 90             # 每格毫秒
RACKET4 = to_canvas(362, 30)  # 第 4 格球拍面位置（格內座標）


def render(i):
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    k = TIMELINE[i]
    t = i - IMPACT
    shake = (0, 0)
    if 0 <= t <= 3:
        shake = ((-1) ** i * (4 - t) * 1.5 * SS, (-1) ** (i // 2) * (4 - t) * SS)
    fig, pos = figure(k, *shake)
    d = ImageDraw.Draw(c)
    if 0 <= t <= 2:  # 擊球閃光
        burst(d, RACKET4[0] + shake[0], RACKET4[1] + shake[1], (26 + t * 14) * SS, t * 25, 255 - t * 60)
    c.alpha_composite(fig, pos)
    d = ImageDraw.Draw(c)
    if 0 <= t <= 1:
        star(d, RACKET4[0], RACKET4[1], (14 + t * 6) * SS, t * 40)
    if t >= 0:  # 文字彈出：0.3 → 1.25 → 1.0，之後微微抖動
        pop = [0.35, 1.25, 1.05, 0.97, 1.0]
        sc = pop[t] if t < len(pop) else 1.0 + 0.03 * math.sin(t * 2.1)
        tshake = (shake[0] * 0.6, shake[1] * 0.6) if t < 4 else ((-1) ** i * 1 * SS, 0)
        big_text(c, sc, tshake, 8 + (2 if t % 2 else -2) * (t < 4))
    d = ImageDraw.Draw(c)
    if t >= 1:  # 球被殺向右下
        p = min(1.0, (t - 1) / 4)
        sx = RACKET4[0] + 30 * SS + p * (CW - RACKET4[0] - 10 * SS)
        sy = RACKET4[1] + 20 * SS + p * (CH - RACKET4[1] - 40 * SS)
        if p < 1:
            shuttle(d, sx, sy, math.degrees(math.atan2(CH - RACKET4[1] - 60 * SS, CW - RACKET4[0] - 40 * SS)), 0.9)
    return c.resize((W, H), Image.LANCZOS)


def to_palette(raw, colors=256):
    """所有格共用一組色盤（P 模式＋透明索引），讓 APNG 只存差異區塊，檔案小很多"""
    import numpy as np
    mont = Image.new("RGB", (raw[0].width * len(raw), raw[0].height), (255, 255, 255))
    for i, f in enumerate(raw):
        mont.paste(f.convert("RGB"), (i * f.width, 0), f.getchannel("A").point(lambda v: 255 if v > 110 else 0))
    pal = mont.quantize(colors=colors - 1, method=Image.MEDIANCUT)
    pl = pal.getpalette()[: 3 * (colors - 1)]
    pl += [0] * (768 - len(pl))
    out = []
    for f in raw:
        arr = np.array(f.convert("RGB").quantize(palette=pal, dither=Image.NONE))
        arr[np.array(f.getchannel("A")) <= 110] = colors - 1
        q = Image.fromarray(arr.astype(np.uint8), "P")
        q.putpalette(pl)
        q.info["transparency"] = colors - 1
        out.append(q)
    return out


def main():
    fdir = os.path.join(OUT, "frames")
    shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    raw = [render(i) for i in range(len(TIMELINE))]

    # LINE APNG：共用色盤，必要時降色直到 ≤ 300KB
    apng = os.path.join(OUT, "smash_line.png")
    loops = max(1, min(4, 4000 // (DUR * len(raw))))
    for colors in (256, 192, 128, 96):
        frames = to_palette(raw, colors)
        frames[0].save(apng, save_all=True, append_images=frames[1:], duration=DUR, loop=loops,
                       transparency=colors - 1, disposal=0, blend=0, optimize=True)
        if os.path.getsize(apng) <= 300 * 1024:
            break
    for i, f in enumerate(frames):
        f.save(os.path.join(fdir, f"frame_{i:02d}.png"), transparency=colors - 1, optimize=True)
    print(f"APNG: {len(frames)} 格 × {DUR}ms × {loops} 次 = {len(frames)*DUR*loops/1000:.1f}s, "
          f"{colors} 色, {os.path.getsize(apng)//1024}KB")

    # 影片用高解析版本（2x）
    vdir = os.path.join(OUT, "_video"); shutil.rmtree(vdir, ignore_errors=True); os.makedirs(vdir)
    global W, H
    W, H = CW, CH
    for i in range(len(TIMELINE)):
        f = render(i)
        for bg, tag in (((255, 255, 255), "w"), ((0, 255, 0), "g")):
            b = Image.new("RGBA", f.size, bg + (255,)); b.alpha_composite(f)
            b.convert("RGB").save(os.path.join(vdir, f"{tag}_{i:02d}.png"))
    fps = 1000 / DUR
    for tag, name in (("w", "smash.mp4"), ("g", "smash_green.mp4")):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "2", "-framerate", f"{fps}",
                        "-i", os.path.join(vdir, f"{tag}_%02d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-r", "30", "-movflags", "+faststart", os.path.join(OUT, name)], check=True)
    gif = [Image.open(os.path.join(vdir, f"w_{i:02d}.png")).resize((320, 270), Image.LANCZOS) for i in range(len(TIMELINE))]
    gif[0].save(os.path.join(OUT, "smash.gif"), save_all=True, append_images=gif[1:], duration=DUR, loop=0)
    shutil.rmtree(vdir)
    print("done")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    main()
