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
mapping = {**{n:n for n in range(1,9)}, 10:9, 12:10, 13:11,
           **{n:n-2 for n in range(14,20)}, 21:18, 22:19}
for new, old in mapping.items():
    raw = subprocess.check_output(['git', 'show', f'{ref}:output/screenshots/slide-{old:02}.png'], cwd=ROOT)
    before = Image.open(BytesIO(raw)).convert('RGB')
    after = Image.open(ROOT / f'output/screenshots/slide-{new:02}.png').convert('RGB')
    assert before.size == after.size == (1920,1080)
    diff = ImageChops.difference(before, after)
    bbox = diff.getbbox()
    draw = ImageDraw.Draw(diff)
    draw.rectangle((1700, 30, 1850, 110), fill=(0, 0, 0))  # contador
    draw.rectangle((80, 980, 700, 1050), fill=(0, 0, 0))  # sección
    if new == 4:
        draw.rectangle((80, 730, 900, 960), fill=(0, 0, 0))  # métrica retirada
    if new in (17, 18):
        draw.rectangle((90, 145, 1400, 220), fill=(0, 0, 0))  # etiqueta de modalidad
    red, green, blue = diff.split()
    mask = ImageChops.lighter(ImageChops.lighter(red, green), blue).point(lambda x: 255 if x else 0)
    pixels = mask.histogram()[255]
    rows.append({'slide':new, 'previous_slide':old, 'full_difference_bbox':bbox,
                 'pixels_different_outside_expected_changes':pixels})
    # Allow only minute antialiasing variation in unchanged screenshots.
    if pixels > 1000:
        raise AssertionError(f'Slide {new}: {pixels} changed pixels outside expected changes')
result={'baseline':ref, 'resolution':'1920x1080', 'masked':'contador, pie; métrica en 04 y etiquetas de modalidad en 17–18', 'slides':rows}
(ROOT/'output/qa-reorder.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
