"""One-time recovery of editable text and SVG shapes from the supplied PDF."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deck/reference'
OUT.mkdir(exist_ok=True)
doc = pymupdf.open(ROOT / 'reference/AI_PlayGrounds_deck.pdf')
assert len(doc) == 16
for index in list(range(14)) + [15]:
    page = doc[index]
    svg = page.get_svg_image(text_as_path=False)
    # Shapes remain vector paths; all textual content is stored separately.
    svg = re.sub(r'<text\b[^>]*>.*?</text>', '', svg, flags=re.S)
    svg = re.sub(r'\bclip_(\d+)', f'p{index+1}_clip_\\1', svg)
    (OUT / f'{index+1:02}.svg').write_text(svg)
    spans = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                spans.append({k: span[k] for k in ('text', 'font', 'size', 'color', 'origin', 'bbox')})
    (OUT / f'{index+1:02}.json').write_text(json.dumps(spans, ensure_ascii=False, indent=2) + '\n')
