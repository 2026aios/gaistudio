"""把 out/ 內的 APNG 與逐格圖嵌入一個可在手機上開啟的預覽 HTML。"""
import base64, glob, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "preview.html")
LABELS = ["跳躍", "殺爆你！", "加油！", "開心搖擺", "好球！", "衝啊！", "謝謝", "來比一場？"]
# 上傳用的 8 張（與 package.py 相同）：(上傳檔, 逐格資料夾)
PICK = [("upload/01.png", "out/01_jump"), ("upload/02.png", "smash/out/frames"), ("upload/03.png", "out/03_cheer"),
        ("upload/04.png", "out/04_wiggle"), ("upload/05.png", "out/05_nice"), ("upload/06.png", "out/06_run"),
        ("upload/07.png", "out/07_thanks"), ("upload/08.png", "out/08_ready")]
def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
cards = []
for idx, (rel, fdir) in enumerate(PICK):
    p = os.path.join(HERE, rel); name = os.path.basename(p)[:-4]; label = LABELS[idx]
    im = Image.open(p); n = len(glob.glob(os.path.join(HERE, fdir, "*.png")))
    total = sum((im.seek(k), im.info.get("duration", 0))[1] for k in range(im.n_frames)); dur = total / n
    loops = im.info.get("loop", 1)
    kb = os.path.getsize(p) / 1024
    frames = "".join(f'<img src="{uri(f)}" alt="第 {i+1} 格" width="80" height="68">'
                     for i, f in enumerate(sorted(glob.glob(os.path.join(HERE, fdir, "*.png")))))
    cards.append(f'''<article class="card"><div class="stage"><img class="anim" src="{uri(p)}" alt="{label}" width="320" height="270"></div>
<div class="meta"><h2>{label}</h2><span class="file">{name}.png</span></div>
<dl><div><dt>格數</dt><dd>{n}</dd></div><div><dt>每格</dt><dd>{int(dur)}ms</dd></div><div><dt>播放</dt><dd>{total/1000:g}s × {loops}</dd></div><div><dt>大小</dt><dd class="{'ok' if kb<=300 else 'bad'}">{kb:.0f}KB</dd></div></dl>
<details><summary>逐格圖片</summary><div class="strip">{frames}</div></details></article>''')
html = open(os.path.join(HERE, "preview_template.html"), encoding="utf-8").read()
html = html.replace("{{CARDS}}", "\n".join(cards)).replace("{{MAIN}}", uri(os.path.join(HERE, "upload", "main.png"))).replace("{{TAB}}", uri(os.path.join(HERE, "upload", "tab.png")))
open(dest, "w", encoding="utf-8").write(html); print(dest, os.path.getsize(dest)//1024, "KB")
