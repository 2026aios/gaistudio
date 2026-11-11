"""把 out/ 內的 APNG 與逐格圖嵌入一個可在手機上開啟的預覽 HTML。"""
import base64, glob, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "preview.html")
LABEL = {"01_jump": "跳躍", "02_smash": "殺！", "03_cheer": "加油！", "04_wiggle": "開心搖擺",
         "05_nice": "好球！", "06_run": "衝啊！", "07_thanks": "謝謝", "08_ready": "來比一場？"}
def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
cards = []
for p in sorted(glob.glob(os.path.join(OUT, "0*.png"))):
    name = os.path.basename(p)[:-4]
    im = Image.open(p); n = im.n_frames; dur = im.info.get("duration", 100); loops = im.info.get("loop", 1)
    kb = os.path.getsize(p) / 1024
    frames = "".join(f'<img src="{uri(f)}" alt="第 {i+1} 格" width="80" height="68">'
                     for i, f in enumerate(sorted(glob.glob(os.path.join(OUT, name, "*.png")))))
    cards.append(f'''<article class="card"><div class="stage"><img class="anim" src="{uri(p)}" alt="{LABEL[name]}" width="320" height="270"></div>
<div class="meta"><h2>{LABEL[name]}</h2><span class="file">{name}.png</span></div>
<dl><div><dt>格數</dt><dd>{n}</dd></div><div><dt>每格</dt><dd>{int(dur)}ms</dd></div><div><dt>播放</dt><dd>{n*dur/1000:.2f}s × {loops}</dd></div><div><dt>大小</dt><dd class="{'ok' if kb<=300 else 'bad'}">{kb:.0f}KB</dd></div></dl>
<details><summary>逐格圖片</summary><div class="strip">{frames}</div></details></article>''')
html = open(os.path.join(HERE, "preview_template.html"), encoding="utf-8").read()
html = html.replace("{{CARDS}}", "\n".join(cards)).replace("{{MAIN}}", uri(os.path.join(OUT, "main.png"))).replace("{{TAB}}", uri(os.path.join(OUT, "tab.png")))
open(dest, "w", encoding="utf-8").write(html); print(dest, os.path.getsize(dest)//1024, "KB")
