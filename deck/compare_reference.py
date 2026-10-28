"""Compare reference and final PDF rasterizations to the browser screenshots."""
from pathlib import Path
import json
import subprocess
import tempfile
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'

def mae(a,b):
    diff=ImageChops.difference(a,b)
    return round(sum(ImageStat.Stat(diff).mean)/3/255*100,3)

with tempfile.TemporaryDirectory(prefix='aipg-compare-') as tmp:
    tmp=Path(tmp)
    for source,name in [(ROOT/'reference/AI_PlayGrounds_deck.pdf','ref'),(OUT/'deck.pdf','final')]:
        subprocess.run(['pdftoppm','-png','-scale-to-x','960','-scale-to-y','540',str(source),str(tmp/name)],check=True)
    rows=[]
    for n in range(1,23):
        browser=Image.open(OUT/f'screenshots/slide-{n:02}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS)
        final=Image.open(tmp/f'final-{n:02}.png').convert('RGB')
        row={'slide':n,'browser_vs_pdf_mae_percent':mae(browser,final)}
        original={1:1,2:2,3:3,4:4,6:5,7:6,8:7,12:9,13:11,21:14,22:16}
        if n in original:
            ref=original[n]
            original=Image.open(tmp/f'ref-{ref:02}.png').convert('RGB')
            row.update(reference_page=ref,browser_vs_reference_mae_percent=mae(browser,original))
        rows.append(row)
    (OUT/'qa-comparison.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False,indent=2))
