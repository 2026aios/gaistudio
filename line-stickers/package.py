"""挑選 8 張動態貼圖，改名成 01.png～08.png，連同 main.png、tab.png 打包成 LINE 上傳用 zip，並逐一檢查規格。"""
import os, shutil, zipfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
PICK = ["out/01_jump.png", "smash/out/smash_line.png", "out/03_cheer.png", "out/04_wiggle.png",
        "out/05_nice.png", "out/06_run.png", "out/07_thanks.png", "out/08_ready.png"]
DEST = os.path.join(HERE, "upload"); shutil.rmtree(DEST, ignore_errors=True); os.makedirs(DEST)
files = {f"{i+1:02d}.png": p for i, p in enumerate(PICK)}
files.update({"main.png": "out/main.png", "tab.png": "out/tab.png"})
ok = True
for name, src in files.items():
    dst = os.path.join(DEST, name); shutil.copy(os.path.join(HERE, src), dst)
    im = Image.open(dst); n = getattr(im, "n_frames", 1)
    total = sum((im.seek(k), im.info.get("duration", 0))[1] for k in range(n)) if n > 1 else 0
    loops = im.info.get("loop", 0); kb = os.path.getsize(dst) / 1024
    w, h = im.size
    errs = []
    if im.mode != "RGBA": errs.append(f"色彩模式 {im.mode}（需 RGBA）")
    if w % 2 or h % 2: errs.append("寬高需為偶數")
    if kb > 300: errs.append("超過 300KB")
    if name == "tab.png":
        if (w, h) != (96, 74): errs.append("需 96x74")
    elif name == "main.png":
        if (w, h) != (240, 240): errs.append("需 240x240")
    elif not (w <= 320 and h <= 270 and max(w, h) >= 270): errs.append("需最大 320x270、其中一邊 ≥270")
    if name != "tab.png":
        if not 5 <= n <= 20: errs.append(f"格數 {n}（需 5–20）")
        if total * max(loops, 1) not in (1000, 2000, 3000, 4000): errs.append("播放總時間需剛好 1/2/3/4 秒")
    ok &= not errs
    print(f"{name:9s} ← {src:28s} {w}x{h} {im.mode} {n:2d}格 {total*max(loops,1)/1000:.1f}s {kb:4.0f}KB  {'OK' if not errs else '✗ ' + '、'.join(errs)}")
zp = os.path.join(HERE, "line_animated_stickers.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for name in files: z.write(os.path.join(DEST, name), name)
print("zip:", zp, os.path.getsize(zp) // 1024, "KB", "全部符合" if ok else "有錯誤")
