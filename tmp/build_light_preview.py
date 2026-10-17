"""Build the temporary, offline A/B/C background comparison. No project files modified."""
from pathlib import Path
import base64
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FONT_API = ('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600'
            '&family=Inter+Tight:wght@400;500&family=Geist+Mono:wght@500&display=swap')

def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()

font_css = get(FONT_API).decode()
embedded = {}
def embed(match):
    url = match.group(1)
    if url not in embedded:
        data = base64.b64encode(get(url)).decode()
        mime = 'font/woff2' if '.woff2' in url else 'font/ttf'
        embedded[url] = f'url(data:{mime};base64,{data})'
    return embedded[url]
font_css = re.sub(r'url\((https://[^)]+)\)', embed, font_css)
base_css = (ROOT / '.agents/skills/html-slides/assets/viewport-base.css').read_text()

symbol_cells = [(r, c) for r in range(5) for c in range(5)
                if c in (0, 4) or (r in (0, 4) and c in (1, 3))]
rects = ''.join(f'<rect x="{c*40+2.5}" y="{r*40+2.5}" width="35" height="35"/>'
                for r, c in symbol_cells)
symbol = (f'<svg class="symbol" viewBox="0 0 200 200" role="img" '
          f'aria-label="Estudio del símbolo modular con puertas abiertas y núcleo Halo">'
          f'{rects}<rect class="core" x="82.5" y="82.5" width="35" height="35"/></svg>')

candidates = [('a', 'A', '#F5F3EC', 'Marfil grisáceo', 'Cálido · equilibrado', 'Recomendado'),
              ('b', 'B', '#F2F1EB', 'Hueso neutro', 'Neutro · contenido', 'Alternativa'),
              ('c', 'C', '#F7F4ED', 'Marfil luminoso', 'Cálido · luminoso', 'Alternativa')]
sections = []
for key, letter, color, name, description, status in candidates:
    sections.append(f'''
<section class="slide" data-theme="{key}" id="candidate-{key}" aria-labelledby="title-{key}">
  <header class="masthead"><span class="brand">AI PlayGrounds</span><span class="mono study">ESTUDIO DE COLOR / LIGHT MODE</span></header>
  <div class="composition">
    <div class="editorial">
      <p class="eyebrow mono"><span class="square"></span> DESDE EL NÚCLEO</p>
      <h1 id="title-{key}">Entender la IA.<br>Desde dentro.</h1>
      <p class="intro">Probamos modelos, comprendemos cómo funcionan<br class="desktop-break"> y contamos lo que sirve.</p>
      <div class="method">
        <div><span class="mono">01</span><p>Exploramos.</p></div>
        <div><span class="mono">02</span><p>Practicamos.</p></div>
        <div><span class="mono">03</span><p>Comparamos.</p></div>
      </div>
    </div>
    <aside class="specimen" aria-label="Comparación de identidad sobre fondo claro">
      <div class="symbol-wrap">{symbol}</div>
      <div class="accent-swatches" aria-label="Acentos canónicos"><div class="swatch halo"><span>HALO</span></div><div class="swatch mint"><span>MENTA</span></div><div class="swatch lime"><span>LIMA</span></div></div>
      <p class="specimen-note mono">ACENTOS CANÓNICOS · SIN MODIFICAR</p>
    </aside>
  </div>
  <footer class="footer"><div class="candidate"><span class="candidate-letter">{letter}</span><div><span class="mono hex">{color} <span class="status">/ {status}</span></span><p>{name} <span class="description">— {description}</span></p></div></div><p class="disclaimer">Propuesta light · no oficial<br><span>Misma composición. Solo cambia el fondo.</span></p></footer>
</section>''')

custom_css = '''
:root { --font-heading: "Space Grotesk", sans-serif; --font-body: "Inter Tight", sans-serif;
 --bg-primary:#F5F3EC; --text-primary:#191A18; --text-secondary:#484A43;
 --muted:#62645B; --line:#CECEC4; --halo:#8E8EFF; --mint:#49FF9E; --lime:#CEFF5F;
 --ease-out-expo:cubic-bezier(0.16,1,0.3,1); }
html { scroll-behavior:auto; scroll-snap-type:y mandatory; }
.slide { scroll-snap-align:start; background:var(--bg-primary); align-items:stretch;
 justify-content:space-between; padding:clamp(1.2rem,3.8vw,4rem) clamp(1.4rem,5vw,6rem);
 gap:clamp(1rem,3vh,2.5rem); }
[data-theme="a"] {--bg-primary:#F5F3EC;}
[data-theme="b"] {--bg-primary:#F2F1EB;}
[data-theme="c"] {--bg-primary:#F7F4ED;}
.mono, button {font-family:"Geist Mono",monospace;font-weight:500;font-size:clamp(.65rem,.85vw,.95rem);}
.masthead {display:flex;align-items:center;justify-content:space-between;gap:1rem;}
.brand {font-family:var(--font-heading);font-size:clamp(1rem,1.6vw,1.8rem);font-weight:600;letter-spacing:-.035em;}
.study {color:var(--muted);letter-spacing:.07em;}
.composition {display:grid;grid-template-columns:1.6fr 1fr;gap:clamp(2rem,6vw,7rem);align-items:center;min-height:0;}
.eyebrow {display:flex;align-items:center;gap:.7em;color:var(--muted);letter-spacing:.055em;margin-bottom:clamp(1rem,3vh,2.5rem);}
.square {width:.6em;height:.6em;background:var(--text-primary);display:inline-block;}
h1 {font-family:var(--font-heading);font-weight:600;font-size:clamp(2rem,min(6.2vw,10vh),7.5rem);line-height:1.01;letter-spacing:-.045em;}
.intro {color:var(--text-secondary);font-size:clamp(.95rem,1.65vw,1.9rem);line-height:1.5;margin-top:clamp(1rem,3vh,2.5rem);}
.method {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,110px),1fr));gap:clamp(.6rem,1.6vw,2rem);margin-top:clamp(1.2rem,5vh,4rem);}
.method>div {border-top:1px solid var(--line);padding-top:clamp(.65rem,1.4vh,1.2rem);}
.method span {color:var(--muted);}
.method p {font-size:clamp(.85rem,1.3vw,1.5rem);font-weight:500;margin-top:.35em;}
.specimen {min-width:0;display:flex;flex-direction:column;align-items:stretch;gap:clamp(.7rem,2vh,1.5rem);}
.symbol-wrap {display:flex;align-items:center;justify-content:center;min-height:0;margin-bottom:clamp(.5rem,2vh,2rem);}
.symbol {width:clamp(130px,min(22vw,31vh),340px);height:auto;fill:#000;}
.core {fill:var(--halo);}
.accent-swatches {display:grid;grid-template-columns:repeat(3,1fr);}
.swatch {height:clamp(2.6rem,7vh,5.5rem);display:flex;align-items:end;padding:clamp(.5rem,.9vw,1rem);color:#000;}
.swatch span {font-family:"Geist Mono",monospace;font-weight:500;font-size:clamp(.6rem,.7vw,.8rem);}
.halo{background:var(--halo);}.mint{background:var(--mint);}.lime{background:var(--lime);}
.specimen-note {color:var(--muted);font-size:clamp(.55rem,.65vw,.8rem);letter-spacing:.02em;}
.footer {display:flex;align-items:center;justify-content:space-between;gap:1rem;border-top:1px solid var(--line);padding-top:clamp(.8rem,2vh,1.5rem);padding-bottom:clamp(2.5rem,4vh,3rem);}
.candidate{display:flex;align-items:center;gap:clamp(.8rem,1.5vw,1.5rem);}
.candidate-letter {font-family:var(--font-heading);font-weight:600;font-size:clamp(2rem,3.2vw,4rem);line-height:1;letter-spacing:-.03em;}
.hex{font-size:clamp(.7rem,1vw,1.1rem);}
.status{color:var(--muted);}
.candidate p{font-size:clamp(.8rem,1.1vw,1.25rem);margin-top:.25rem;}
.description{color:var(--muted);}
.disclaimer{font-size:clamp(.65rem,.85vw,1rem);color:var(--text-secondary);text-align:right;line-height:1.5;}
.disclaimer span{color:var(--muted);}
.controls{position:fixed;z-index:10;bottom:clamp(.4rem,1.5vh,1rem);left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:.4rem;background:#191A18;color:#FFFFFF;padding:.3rem .5rem;}
.controls button{border:0;border-radius:0;background:transparent;color:#FFFFFF;padding:.45rem .65rem;cursor:pointer;min-width:2.4rem;}
.controls button[aria-current="true"]{background:var(--halo);color:#000;}
.controls button:focus-visible{outline:2px solid #FFFFFF;outline-offset:1px;}
.controls .hint{font-size:clamp(.55rem,.65vw,.75rem);font-family:"Geist Mono",monospace;color:#C7C7CC;padding:0 .5rem;}
@media(max-height:700px){.slide{padding-top:1.3rem;padding-bottom:1rem;gap:1rem;}.eyebrow{margin-bottom:1rem;}.method{margin-top:1.4rem;}.footer{padding-top:.65rem;}}
@media(max-height:600px){.intro{margin-top:.8rem;}.specimen{gap:.5rem;}.symbol-wrap{margin-bottom:.4rem;}.study{display:none;}.footer{padding-bottom:2.5rem;}}
@media(max-height:500px){.slide{gap:.6rem;padding-top:.8rem;}.eyebrow{margin-bottom:.5rem;}.method{margin-top:.8rem;}.specimen-note{display:none;}h1{font-size:clamp(1.7rem,min(5.5vw,10vh),4rem);}.intro{font-size:clamp(.75rem,1.4vw,1rem);}.footer{padding-top:.4rem;}.description{display:none;}.symbol{width:clamp(80px,23vh,160px);}}
@media(max-width:650px){.slide{gap:1rem;}.composition{grid-template-columns:1fr;gap:1.5rem;}.specimen{display:grid;grid-template-columns:auto 1fr;align-items:center;gap:1rem;}.symbol{width:clamp(70px,17vw,110px);}.symbol-wrap{margin:0;}.specimen-note{display:none;}.swatch{height:3rem;}.study{display:none;}h1{font-size:clamp(2rem,min(10vw,8vh),4rem);}.intro{font-size:clamp(.9rem,3.6vw,1.2rem);}.desktop-break{display:none;}.method{margin-top:1.4rem;}.footer{align-items:start;}.description,.status{display:none;}.disclaimer{max-width:42%;}.controls .hint{display:none;}}
@media(max-width:650px) and (max-height:600px){.specimen{display:none;}.method{margin-top:.7rem;}.intro{font-size:clamp(.75rem,3vw,1rem);}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto;}*,*::before,*::after{animation:none!important;transition:none!important;}}
@media print{@page{size:landscape;margin:0;}html{scroll-snap-type:none;}.controls{display:none;}.slide{break-after:page;print-color-adjust:exact;-webkit-print-color-adjust:exact;}}
'''

script = '''
const slides=[...document.querySelectorAll('.slide')];
const buttons=[...document.querySelectorAll('[data-go]')];
let active=0;
function update(i){active=i;buttons.forEach(b=>b.setAttribute('aria-current',String(Number(b.dataset.go)===i)));}
function go(i){i=Math.max(0,Math.min(slides.length-1,i));slides[i].scrollIntoView({behavior:'instant',block:'start'});update(i);history.replaceState(null,'','#'+slides[i].id);}
buttons.forEach(b=>b.addEventListener('click',()=>go(Number(b.dataset.go))));
document.addEventListener('keydown',e=>{
 if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest('button,input,textarea,[contenteditable="true"]'))return;
 if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();go(active+1);}
 if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();go(active-1);}
 if(['1','2','3'].includes(e.key))go(Number(e.key)-1);
 if(e.key==='Home'){e.preventDefault();go(0);}if(e.key==='End'){e.preventDefault();go(2);}
});
const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)update(slides.indexOf(e.target));}),{threshold:.6});
slides.forEach(s=>observer.observe(s));
let start=null;
document.addEventListener('touchstart',e=>{if(!e.target.closest('nav'))start={x:e.changedTouches[0].clientX,y:e.changedTouches[0].clientY};},{passive:true});
document.addEventListener('touchend',e=>{if(!start)return;const dx=e.changedTouches[0].clientX-start.x,dy=e.changedTouches[0].clientY-start.y;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))go(active+(dx<0?1:-1));start=null;},{passive:true});
if(location.hash){const i=slides.findIndex(s=>'#'+s.id===location.hash);if(i>=0)update(i);}else update(0);
'''

html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>AI PlayGrounds — Comparación light A / B / C</title>
<style>{font_css}\n{base_css}\n{custom_css}</style></head><body>
<main>{''.join(sections)}</main>
<nav class="controls" aria-label="Elegir candidato"><span class="hint">FONDO</span>
<button type="button" data-go="0" aria-label="Candidato A, marfil grisáceo" aria-current="true">A</button>
<button type="button" data-go="1" aria-label="Candidato B, hueso neutro" aria-current="false">B</button>
<button type="button" data-go="2" aria-label="Candidato C, marfil luminoso" aria-current="false">C</button>
<span class="hint">← → / 1 2 3</span></nav>
<script>{script}</script></body></html>'''
output = ROOT / 'tmp/light-candidates.html'
output.write_text(html)
print(f'Created {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes); embedded {len(embedded)} font resources.')
