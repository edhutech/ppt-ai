"""Compare the reordered screenshots with a previous committed deck.

Usage: python deck/compare_reorder.py <previous-git-ref>
"""
from io import BytesIO
from pathlib import Path
import json
import subprocess
import sys
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) != 2:
    raise SystemExit('Usage: python deck/compare_reorder.py <previous-git-ref>')
ref = sys.argv[1]
rows = []
for new in range(1, 20):
    old = new if new <= 11 or new == 19 else 12 if new == 18 else new + 1
    raw = subprocess.check_output(['git', 'show', f'{ref}:output/screenshots/slide-{old:02}.png'], cwd=ROOT)
    before = Image.open(BytesIO(raw)).convert('RGB')
    after = Image.open(ROOT / f'output/screenshots/slide-{new:02}.png').convert('RGB')
    assert before.size == after.size == (1920,1080)
    diff = ImageChops.difference(before, after)
    bbox = diff.getbbox()
    if new != old:
        ImageDraw.Draw(diff).rectangle((1700, 30, 1850, 110), fill=(0, 0, 0))
    red, green, blue = diff.split()
    mask = ImageChops.lighter(ImageChops.lighter(red, green), blue).point(lambda x: 255 if x else 0)
    pixels = mask.histogram()[255]
    rows.append({'slide':new, 'previous_slide':old, 'full_difference_bbox':bbox,
                 'pixels_different_outside_counter':pixels})
    # Allow only minute antialiasing variation in unchanged screenshots.
    if pixels > 100:
        raise AssertionError(f'Slide {new}: {pixels} changed pixels outside counter')
result={'baseline':ref, 'resolution':'1920x1080', 'counter_mask':'x=1700..1850, y=30..110', 'slides':rows}
(ROOT/'output/qa-reorder.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
