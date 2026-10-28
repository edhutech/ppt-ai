"""Build the nineteen-slide, self-contained presentation from editable sources."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'deck/reference'


def recovered(n, final_number):
    svg = (REF / f'{n:02}.svg').read_text()
    spans = json.loads((REF / f'{n:02}.json').read_text())
    out = []
    for s in spans:
        text = s['text']
        if re.fullmatch(r'\d\d / 16', text):
            text = f'{final_number:02} / 19'
        if n == 2:
            text = {'Quiénes somos': 'Identidad y trayectoria', 'Dónde profundizamos': 'Dirección y verticales', 'Lo que hemos hecho': 'Organización e iniciativas', 'Cómo participar': 'Personas y participación'}.get(text, text)
        if n == 11:
            text = {'Estamos construyendo una línea de programas, cursos': 'Construimos una iniciativa comercial de formación:', 'y workshops con práctica desde el primer día.': 'programas, cursos y workshops prácticos.'}.get(text,text)
        if n == 14:
            text = text.replace('Edhú Nuñes', 'Edhú Núñez')
        family = 'Space Grotesk' if 'SpaceGrotesk' in s['font'] else 'Geist Mono' if 'GeistMono' in s['font'] else 'Inter Tight'
        weight = 600 if 'SemiBold' in s['font'] else 500 if 'Medium' in s['font'] else 400
        x, y = s['origin']
        width = s['bbox'][2] - s['bbox'][0]
        changed = text != s['text'] and not re.fullmatch(r'\d\d / 19',text)
        fit = '' if changed else f'data-width="{width:.3f}"'
        out.append(f'<span class="pdf-text" {fit} style="left:{x:.3f}px;top:{y:.3f}px;font-family:\'{family}\';font-weight:{weight};font-size:{s["size"]:.3f}px;color:#{s["color"]:06x}">{html.escape(text)}</span>')
    return '<section class="canvas recovered">' + svg + ''.join(out) + '</section>'

parts = re.findall(r'<section class="new-slide.*?</section>', (ROOT/'deck/narrativa.html').read_text(), flags=re.S)
custom = {int(re.search(r'data-page="(\d+)"',s)[1]):s.replace('class="new-slide ', 'class="canvas new-slide ',1) for s in parts}
assert sorted(custom)==[5,9,12,13,14,15,16,17]
original={1:1,2:2,3:3,4:4,6:5,7:6,8:7,10:9,11:11,18:14,19:16}
sections=[recovered(original[n],n) if n in original else custom[n] for n in range(1,20)]
wrapped=''.join(f'<div class="slide" id="slide-{i:02}"><div class="frame">{s}</div></div>' for i,s in enumerate(sections,1))
fontcss=(ROOT/'deck/fonts.css').read_text()
base=(ROOT/'.agents/skills/html-slides/assets/viewport-base.css').read_text()
css=(ROOT/'deck/narrativa.css').read_text()
script=(ROOT/'deck/navigation.js').read_text()
doc=f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI PlayGrounds</title><style>{fontcss}\n{base}\n{css}</style></head><body><div>{wrapped}</div><nav class="controls" aria-label="Navegación"><button id="prev" aria-label="Anterior">←</button><button id="next" aria-label="Siguiente">→</button><button id="full" aria-label="Pantalla completa">⛶</button></nav><script>{script}</script></body></html>'
(ROOT/'output').mkdir(exist_ok=True)
(ROOT/'output/deck.html').write_text(doc)
print('19 diapositivas generadas')
