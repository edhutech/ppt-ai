"""Build the approved 24-slide deck. Inputs are read-only; output is self-contained."""
from pathlib import Path
import base64
import hashlib
import html
import json
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SPEC = (ROOT / 'deck/deck-spec.md').read_text()
BRAND = (ROOT / 'branding/brand-spec.md').read_text()
E = html.escape
SLIDES = []
for match in re.finditer(r'^## Slide (\d{2}) — (.*?)\n(.*?)(?=^## Slide |^# 10\.|\Z)', SPEC, re.M | re.S):
    n, name, block = match.groups()
    content = block.split('### Content\n', 1)[1].split('\n### Visual direction', 1)[0]
    fields = {}
    for f in re.finditer(r'^#### (.*?)\n(.*?)(?=^#### |\Z)', content, re.M | re.S):
        fields[f[1]] = f[2].strip()
    theme = re.search(r'### Theme\s+(dark|light)', block)[1]
    SLIDES.append({'number': int(n), 'name': name, 'theme': theme, 'fields': fields})
assert len(SLIDES) == 24

def clean(t):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', t).strip()

def field(n, key):
    return clean(SLIDES[n-1]['fields'][key])

def lines(n, key):
    return [re.sub(r'^(?:- |\d+\. )', '', clean(x)) for x in field(n, key).splitlines() if x.strip()]

def p(n, key, cls='body'):
    return f'<p class="{cls}" data-copy="{E(key)}">{E(field(n,key))}</p>'

def label(text):
    return f'<span class="bracket mono">{E(text)}</span>'

def title(n, cls=''):
    text=E(field(n,'Title')).replace('AI PlayGrounds','<span class="nowrap">AI PlayGrounds</span>')
    if n==8:text=text.replace('organización.','<span class="halo-text">organización.</span>')
    return f'<h1 class="title {cls}" data-copy="Title">{text}</h1>'

def step(content, k, cls=''):
    return f'<div class="build {cls}" data-step="{k}">{content}</div>'

def symbol(cls='', core=True):
    # 5u footprint, 14 occupied perimeter cells, 1/8u gap, fixed Halo center.
    cells=[(r,c) for r in range(5) for c in range(5) if c in (0,4) or (r in (0,4) and c in (1,3))]
    rects=''.join(f'<rect x="{c*40+2.5}" y="{r*40+2.5}" width="35" height="35"/>' for r,c in cells)
    if core: rects+='<rect class="halo-fill" x="82.5" y="82.5" width="35" height="35"/>'
    return f'<svg class="symbol {cls}" viewBox="0 0 200 200" aria-hidden="true">{rects}</svg>'

def orbit_field(cls='', core=True):
    perimeter=[(0,c) for c in range(5)]+[(r,4) for r in range(1,5)]+[(4,c) for c in range(3,-1,-1)]+[(r,0) for r in range(3,0,-1)]
    out=[]
    for r in range(4):
        for c in range(4):
            shift=(r*7+c*3)%16
            for j,(y,x) in enumerate(perimeter):
                if j not in (shift,(shift+8)%16):
                    out.append(f'<rect x="{c*120+x*20}" y="{r*120+y*20}" width="17.5" height="17.5"/>')
    if core: out.append('<rect class="halo-fill" x="280" y="280" width="17.5" height="17.5"/>')
    return f'<svg class="orbit-field {cls}" viewBox="0 0 460 460" aria-hidden="true">{"".join(out)}</svg>'

def flow(items, cls='', start=1):
    return f'<ol class="flow {cls}">'+''.join(f'<li class="build" data-step="{i+start}"><span class="step-module" aria-hidden="true"></span><p>{E(t)}</p>'+('<span class="flow-arrow" aria-hidden="true">→</span>' if i<len(items)-1 else '')+'</li>' for i,t in enumerate(items))+'</ol>'

def heading(n):
    eyebrow=SLIDES[n-1]['fields'].get('Eyebrow')
    return (f'<div class="eyebrow">{label(eyebrow)}</div>' if eyebrow else '')+title(n)

def content(n):
    if n==1:
        return f'<div class="cover-copy">{title(n)}{p(n,"Subtitle","cover-subtitle")}{p(n,"Optional metadata","mono metadata")}</div><div class="cover-symbol">{symbol()}</div>'
    if n==2:
        items=lines(n,'Items')
        return heading(n)+'<ol class="agenda">'+''.join(step(f'<span class="agenda-number">0{i}</span><p>{E(t)}</p>',i,'agenda-row') for i,t in enumerate(items,1))+'</ol>'
    if n==3:
        activities=['encuentros','práctica','demos','MVPs']
        graph='<div class="community-map"><div class="map-core">'+symbol()+'<span class="map-name">comunidad</span></div>'+''.join(step(label(t),i+1,f'satellite satellite-{i}') for i,t in enumerate(activities))+'</div>'
        return '<div class="split narrative"><div>'+title(n)+p(n,'Body')+p(n,'Supporting idea','support')+'</div>'+graph+'</div>'
    if n==4:
        return '<div class="depth-copy">'+title(n)+p(n,'Body')+'</div><div class="depth-graphic"><div class="depth-frame outer"></div><div class="depth-frame middle"></div><div class="depth-frame inner"></div><div class="depth-core"></div></div>'
    if n==5:
        return '<div class="questions-head">'+title(n)+p(n,'Body')+'</div><div class="questions">'+''.join(step(f'<span class="mono question-index">0{i}</span><p>{E(t)}</p>',i,'question') for i,t in enumerate(lines(n,'Questions'),1))+'</div>'
    if n==6:
        diagram=flow(['comunidad','profundidad técnica','formación como oferta visible'],'configuration')
        return heading(n)+p(n,'Body','body wide')+diagram+p(n,'Supporting idea','support bottom-support')
    if n==7:
        diagram='<div class="formation-field"><div class="formation-cell build" data-step="1"><span class="mono">AI PlayGrounds</span><strong>Formación</strong><div class="growth-bars"><i></i><i></i><i></i><i></i></div></div><div class="other-spaces">'+''.join(f'<span>{E(t)}</span>' for t in ['comunidad','AI Labs','investigación','productos','nuevas iniciativas'])+'</div></div>'
        return '<div class="split narrative"><div>'+title(n)+p(n,'Body')+p(n,'Supporting idea','support')+'</div>'+diagram+'</div>'
    if n==8:
        return '<div class="reveal-copy">'+step(label(field(n,'Eyebrow')),0)+step(title(n),1)+step(p(n,'Statement','statement-body'),4)+'</div><div class="reveal-field">'+step(orbit_field(core=False),2)+step('<span class="reveal-core"></span>',3)+'</div>'
    if n==9:
        areas=[]
        for i in range(1,5):
            a=lines(n,f'Area 0{i}')
            areas.append(step(f'<div class="area-top"><span class="mono">0{i}</span><span class="area-marker"></span></div><h2>{E(a[0])}</h2><p>{E(a[1])}</p>',i,'area'))
        return heading(n)+p(n,'Intro','intro')+'<div class="area-grid">'+''.join(areas)+'</div>'
    if n==10:
        names=['AI Foundations','AI for Software','AI for Science','AI for Finance']
        activities=lines(n,'Activity types')
        left=''.join(step(label(t),2+i,'activity') for i,t in enumerate(activities[:4]))
        right=''.join(step(label(t),6+i,'activity') for i,t in enumerate(activities[4:]))
        middle=step('<div class="mini-areas">'+''.join(f'<span>{t}</span>' for t in names)+'</div>',1)
        return heading(n)+p(n,'Core statement','intro')+'<div class="activity-map"><div class="activity-side">'+left+'</div><div class="bidirectional" aria-hidden="true">↔</div>'+middle+'<div class="bidirectional" aria-hidden="true">↔</div><div class="activity-side">'+right+'</div></div>'
    if n==11:
        connections='<svg class="human-connections" viewBox="0 0 720 620" aria-hidden="true"><path d="M64 94H244V64M244 64V190H335V305H514V306M335 305H104V294M335 305V444H214M335 444H624V484M335 190H674V204M335 444V516H396M104 294V514H34"/></svg>'
        grid='<div class="human-field">'+step(connections,1)+''.join(step('<span></span>',i+1,f'human human-{i}') for i in range(12))+'<div class="human-core"></div></div>'
        return '<div class="split narrative"><div>'+heading(n)+p(n,'Body')+'</div>'+grid+'</div>'
    if n==12:
        return heading(n)+flow([x.strip() for x in field(n,'Flow').split('→')],'labs-flow')+p(n,'Supporting idea','support bottom-support')
    if n==13:
        return heading(n)+flow([x.strip() for x in field(n,'Flow').split('→')],'maturation')+p(n,'Supporting idea','support bottom-support')
    if n==14:
        formats=['programas','cursos','workshops','full days','otras experiencias de aprendizaje']
        return '<div class="split academy"><div>'+heading(n)+p(n,'Body')+p(n,'Note','note academy-note')+'</div><div class="academy-system">'+step('<span class="mono master-label">AI PlayGrounds</span><h2>AI Academy</h2>',1)+step('<div class="formats">'+''.join(label(t) for t in formats)+'</div>',2)+'</div></div>'
    if n==15:
        return heading(n)+'<ol class="reasons">'+''.join(step(f'<span class="reason-number">0{i}</span><p>{E(field(n,f"Point 0{i}"))}</p>',i,'reason') for i in range(1,4))+'</ol>'
    if n==16:
        nodes=field(n,'Diagram nodes')
        groups=re.findall(r'(?m)^(AI PlayGrounds Association|S\.A\.C\.|AI Academy)\n((?:- .*\n?)+)',nodes)
        assert len(groups)==3
        ass,sac,academy=groups
        def bullets(t): return '<ul>'+''.join(f'<li>{E(x[2:])}</li>' for x in t.strip().splitlines())+'</ul>'
        institutional='<div class="institutional"><div class="association build" data-step="1"><h2>'+E(ass[0])+'</h2>'+bullets(ass[1])+'</div><div class="institution-link build" data-step="4" aria-hidden="true">↔</div><div class="sac build" data-step="2"><h2>'+E(sac[0])+'</h2>'+bullets(sac[1])+'<div class="academy-line build" data-step="3"><h3>'+E(academy[0])+'</h3>'+bullets(academy[1])+'</div></div></div>'
        return heading(n)+institutional+p(n,'Legal note','note legal')
    if n==17:
        items=lines(n,'Examples')
        assets='<div class="knowledge-orbit"><div class="knowledge-core">'+symbol()+'</div><div class="asset-column">'+''.join(step(label(t),i+1) for i,t in enumerate(items[:4]))+'</div><div class="asset-column">'+''.join(step(label(t),i+5) for i,t in enumerate(items[4:]))+'</div></div>'
        return heading(n)+assets+p(n,'Supporting idea','support bottom-support')
    if n==18:
        return heading(n)+'<div class="layers"><div class="layer build" data-step="1"><span class="mono">Association</span>'+p(n,'Association')+'</div><div class="layer-connector build" data-step="3" aria-hidden="true">→</div><div class="layer build" data-step="2"><span class="mono">S.A.C. / AI Academy</span>'+p(n,'S.A.C. / AI Academy')+'</div></div>'+p(n,'Supporting idea','support bottom-support')
    if n==19:
        outbound=[x.lstrip('→ ').strip() for x in lines(n,'Flow')]
        returned=[x.lstrip('→ ').strip() for x in lines(n,'Return')]
        return heading(n)+flow(outbound,'license-flow')+'<div class="return-flow build" data-step="6">'+''.join(f'<div><p>{E(t)}</p></div>'+('<span aria-hidden="true">←</span>' if i<2 else '') for i,t in enumerate(reversed(returned)))+'</div>'+p(n,'Note','note legal')
    if n==20:
        return heading(n)+p(n,'Body','body wide')+flow(['donante / sponsor','AI PlayGrounds Association','beca','estudiante'],'scholarship')+p(n,'Example','support example')+p(n,'Note','note legal')
    if n==21:
        example=lines(n,'Example')
        return heading(n)+f'<p class="intro">{E(example[0])}</p><div class="convergence"><div class="funding-sources">'+''.join(step(f'<p>{E(t)}</p>',i+1,'funding-source') for i,t in enumerate(example[1:]))+'</div><div class="merge-lines build" data-step="3"><svg viewBox="0 0 240 360" aria-hidden="true"><path d="M0 60H90V180H230M0 300H90V180"/><path d="m215 165 15 15-15 15"/></svg></div>'+step('<div class="cohort"><div class="cohort-modules">'+''.join('<i></i>' for _ in range(15))+'</div><span class="mono">Una misma cohorte</span></div>',3)+'</div>'+p(n,'Supporting idea','support bottom-support')
    if n==22:
        example=lines(n,'Examples')
        return '<div class="split future"><div>'+heading(n)+p(n,'Body')+f'<p class="intro small-intro">{E(example[0])}</p><ul class="possibilities">'+''.join(step(f'<p>{E(t)}</p>',i+2,'possibility') for i,t in enumerate(example[1:]))+'</ul></div><div class="mature-field">'+step('<div class="mature-module"><span>AI Academy</span></div>',1)+step(orbit_field(core=False),2)+'</div></div>'
    if n==23:
        statements=[x for x in field(n,'Supporting statements').split('\n\n') if x.strip()]
        assert len(statements)==6
        return title(n)+f'<p class="synthesis-lead">{E(statements[0])}</p><div class="synthesis">'+''.join(step(f'<span class="synthesis-marker"></span><p>{E(t)}</p>',i+1,'synthesis-item') for i,t in enumerate(statements[1:5]))+'</div>'+step(f'<p class="support synthesis-end">{E(statements[5])}</p>',5)+orbit_field('synthesis-field',False)
    if n==24:
        return '<div class="closing">'+symbol('closing-symbol')+title(n)+p(n,'Optional subtitle','closing-subtitle')+'</div>'

CSS = r'''
:root{--halo:#8E8EFF;--mint:#49FF9E;--lime:#CEFF5F;--black:#000000;--white:#FFFFFF;--gray1:#1A1A1F;--gray2:#6B6B73;--gray3:#C7C7CC;--light-primary:#F5F3EC;--light-secondary:#ECEAE2;--light-elevated:#FAF9F4;--light-contrast:#E3E2DA;--font-heading:"Space Grotesk",sans-serif;--font-body:"Inter Tight",sans-serif;--ease-out-expo:cubic-bezier(.16,1,.3,1)}
html{scroll-behavior:auto;scroll-snap-type:y mandatory;background:#000}body{background:#000}.slide{padding:0;scroll-snap-align:start;background:#000;justify-content:center;align-items:center;isolation:isolate}
.canvas{width:min(100vw,177.777778vh);width:min(100vw,177.777778dvh);aspect-ratio:16/9;position:relative;container-type:inline-size;overflow:hidden;background:var(--bg-primary);color:var(--text-primary)}
[data-theme="dark"]{--bg-primary:#000;--text-primary:#FFF;--text-secondary:#C7C7CC;--muted:#C7C7CC;--line:#1A1A1F;--field:#1A1A1F;--surface:#1A1A1F;--ink:#FFF}
[data-theme="light"]{--bg-primary:#F5F3EC;--text-primary:#191A18;--text-secondary:#484A43;--muted:#62645B;--line:#CECEC4;--field:#DEDFD5;--surface:#FAF9F4;--ink:#000}
[data-surface="secondary"]{--bg-primary:#ECEAE2}[data-surface="contrast"]{--bg-primary:#E3E2DA}
.masthead{position:absolute;top:52px;left:96px;right:96px;display:flex;justify-content:space-between;align-items:center;font-size:24px;color:var(--muted)}
.masthead .brand-name{font-family:var(--font-heading);font-weight:600;letter-spacing:-.025em;color:var(--text-primary);font-size:28px}.chapter{font-family:"Geist Mono",monospace;font-size:22px;font-weight:400}
.content{position:absolute;left:96px;right:96px;top:160px;bottom:128px;min-width:0}
.footer{position:absolute;bottom:48px;left:96px;right:96px;display:flex;justify-content:space-between;align-items:center;font-family:"Geist Mono",monospace;font-size:22px;color:var(--muted)}
.footer .progress-track{width:144px;height:4px;background:var(--line)}.progress-track span{display:block;height:100%;background:var(--halo);width:var(--progress)}
.title{font-family:var(--font-heading);font-size:88px;font-weight:600;line-height:1.04;letter-spacing:-.035em;margin:0;max-width:1600px;text-wrap:pretty}
.nowrap{white-space:nowrap}.halo-text{color:var(--halo)}
.body{font-size:36px;line-height:1.5;color:var(--text-secondary);margin-top:38px;max-width:1040px}.wide{max-width:1510px}.intro{font-size:34px;line-height:1.5;color:var(--text-secondary);margin-top:24px;max-width:1550px}
.support{font-size:32px;line-height:1.5;color:var(--text-secondary);max-width:1440px}.note{font-size:26px;line-height:1.5;color:var(--muted)}.legal{position:absolute;bottom:0;max-width:1640px;border-top:1px solid var(--line);padding-top:22px}.bottom-support{position:absolute;bottom:0;max-width:1510px}
.mono{font-family:"Geist Mono",monospace;font-size:24px;font-weight:500}.bracket{display:inline-block;position:relative;padding:4px 28px;line-height:1.25;color:var(--text-primary)}.bracket:before,.bracket:after{content:"";position:absolute;top:0;bottom:0;width:14px;border-top:5px solid currentColor;border-bottom:5px solid currentColor}.bracket:before{left:0;border-left:5px solid currentColor}.bracket:after{right:0;border-right:5px solid currentColor}.eyebrow{margin-bottom:32px}
.symbol{fill:var(--ink);width:100%;height:100%;display:block}.halo-fill{fill:var(--halo)}.orbit-field{fill:var(--field);width:100%;height:auto;display:block}
.split{display:grid;grid-template-columns:1.18fr 1fr;gap:96px;height:100%;align-items:center}.narrative .title{font-size:82px}.narrative .support{margin-top:28px}.split .body{max-width:940px}
.cover-copy{position:absolute;top:215px;left:0;z-index:2}.cover-copy .title{font-size:154px;letter-spacing:-.045em;line-height:1}.cover-subtitle{font-family:var(--font-heading);font-size:64px;font-weight:500;letter-spacing:-.025em;margin-top:34px}.metadata{color:var(--muted);margin-top:105px}.cover-symbol{position:absolute;right:40px;top:180px;width:370px;height:370px}.cover-field{position:absolute;width:520px;right:-96px;bottom:-128px;opacity:.8}.s01 .content{top:128px}.s01 .cover-copy{max-width:1260px}.s01 .cover-copy .title{font-size:138px}
.agenda{margin-top:58px;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:0 88px}.agenda-row{border-top:2px solid var(--line);display:flex;gap:32px;align-items:start;min-height:210px;padding:32px 0}.agenda-number{font-family:var(--font-heading);font-weight:600;letter-spacing:-.04em;font-size:80px;line-height:1;color:var(--text-primary)}.agenda-row p{font-size:40px;line-height:1.25;padding-top:4px;max-width:590px}
.community-map{height:600px;position:relative}.map-core{position:absolute;left:225px;top:180px;width:230px;height:230px}.map-name{display:block;font-family:var(--font-heading);font-size:42px;text-align:center;letter-spacing:-.025em;margin-top:30px}.satellite{position:absolute}.satellite-0{top:50px;left:28px}.satellite-1{right:0;top:135px}.satellite-2{left:0;bottom:100px}.satellite-3{right:0;bottom:60px}
.depth-copy{position:relative;z-index:2;width:1120px;top:90px}.depth-copy .title{font-size:122px;max-width:1120px}.depth-copy .body{max-width:1080px;margin-top:52px}.depth-graphic{position:absolute;right:0;top:60px;width:520px;height:600px}.depth-frame{position:absolute;border-left:4px solid var(--field);border-right:4px solid var(--field)}.depth-frame:before,.depth-frame:after{content:"";position:absolute;left:-4px;right:-4px;height:32px;border-left:4px solid var(--field);border-right:4px solid var(--field)}.depth-frame:before{top:0;border-top:4px solid var(--field)}.depth-frame:after{bottom:0;border-bottom:4px solid var(--field)}.outer{inset:0}.middle{inset:80px 65px}.inner{inset:160px 130px}.depth-core{position:absolute;width:80px;height:80px;background:var(--halo);left:220px;top:260px}
.questions-head{display:grid;grid-template-columns:1fr 1fr;gap:100px;align-items:start}.questions-head .title{font-size:76px}.questions-head .body{margin:0}.questions{margin-top:44px;display:grid;grid-template-columns:1fr 1fr;gap:0 72px}.question{display:flex;align-items:start;gap:20px;border-top:1px solid var(--line);padding:26px 0;min-height:105px}.question p{font-family:var(--font-heading);font-weight:500;font-size:40px;line-height:1.2;letter-spacing:-.02em}.question-index{padding-top:8px;color:var(--muted)}.question:last-child{grid-column:1/3;max-width:1320px}
.flow{list-style:none;display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:30px;position:relative;margin-top:100px}.flow li{position:relative;min-width:0;padding-right:24px}.step-module{display:block;width:64px;height:64px;background:var(--halo);margin-bottom:30px;border:2px solid var(--ink)}.flow p{font-family:var(--font-heading);font-size:38px;line-height:1.18;font-weight:500;letter-spacing:-.025em}.flow-arrow{position:absolute;right:0;top:6px;font-size:40px;color:var(--muted)}.configuration{margin-top:90px;gap:70px}.configuration p{max-width:400px;font-size:48px}.configuration .step-module{width:80px;height:80px}.configuration li:nth-child(1) .step-module{background:transparent}.configuration li:nth-child(2) .step-module{background:var(--field)}
.formation-field{height:620px;border-top:2px solid var(--line);border-bottom:2px solid var(--line);display:grid;grid-template-columns:1.25fr 1fr;gap:40px;align-items:center}.formation-cell{position:relative;padding:40px 24px;border-left:5px solid var(--halo)}.formation-cell strong{font-family:var(--font-heading);font-size:60px;letter-spacing:-.03em;display:block;margin-top:50px}.growth-bars{display:flex;gap:10px;align-items:end;margin-top:36px;height:130px}.growth-bars i{display:block;width:38px;background:var(--halo);height:35%}.growth-bars i:nth-child(2){height:55%}.growth-bars i:nth-child(3){height:78%}.growth-bars i:nth-child(4){height:100%}.other-spaces{display:grid;gap:30px}.other-spaces span{font-size:30px;line-height:1.2;color:var(--text-secondary);border-top:1px solid var(--line);padding-top:18px}
.reveal-copy{width:1010px;position:relative;z-index:2;top:20px}.reveal-copy .title{font-size:108px;margin-top:38px}.statement-body{font-size:36px;line-height:1.5;color:var(--text-secondary);margin-top:48px;max-width:990px}.reveal-field{position:absolute;right:-25px;top:100px;width:650px;height:650px}.reveal-core{position:absolute;width:25px;height:25px;left:396px;top:396px;background:var(--halo)}
.area-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 80px;margin-top:42px}.area{border-top:2px solid var(--line);padding:25px 0 28px}.area-top{display:flex;align-items:center;justify-content:space-between;color:var(--muted)}.area-marker{width:20px;height:20px;background:var(--halo);border:2px solid var(--ink)}.area h2{font-family:var(--font-heading);font-size:50px;font-weight:600;letter-spacing:-.03em;line-height:1.1;margin:18px 0}.area p{font-size:32px;line-height:1.45;max-width:750px}.s09 .title{font-size:84px}.s09 .eyebrow{margin-bottom:22px}
.activity-map{display:grid;grid-template-columns:1fr 80px 1.35fr 80px 1fr;align-items:center;gap:14px;margin-top:65px}.activity-side{display:grid;gap:35px}.activity{min-width:0}.activity .bracket{font-size:26px}.bidirectional{font-size:48px;color:var(--muted);text-align:center}.mini-areas{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:3px solid var(--ink);border-bottom:3px solid var(--ink);padding:25px 0}.mini-areas span{font-family:var(--font-heading);font-size:34px;font-weight:500;letter-spacing:-.025em;padding:25px 16px;line-height:1.15}.mini-areas span:nth-child(odd){border-right:1px solid var(--line)}
.human-field{height:620px;position:relative}.human-connections{position:absolute;inset:0;width:100%;height:100%;fill:none;stroke:var(--muted);stroke-width:2}.human{position:absolute;width:48px;height:48px;background:var(--ink)}.human:nth-child(3n){width:32px;height:32px}.human-core{position:absolute;left:300px;top:270px;width:70px;height:70px;background:var(--halo);border:2px solid var(--ink)}
.human-0{left:40px;top:70px}.human-1{left:220px;top:40px}.human-2{left:500px;top:85px}.human-3{left:650px;top:180px}.human-4{left:80px;top:270px}.human-5{left:490px;top:290px}.human-6{left:190px;top:420px}.human-7{left:600px;top:460px}.human-8{left:380px;top:500px}.human-9{left:10px;top:490px}.human-10{left:630px;top:40px}.human-11{left:380px;top:100px}
.labs-flow{margin-top:116px;gap:40px}.labs-flow .step-module{width:100px;height:100px;border:2px solid var(--gray3)}.labs-flow li:first-child .step-module{background:transparent}.labs-flow li:nth-child(2) .step-module{background:var(--gray1)}.labs-flow li:nth-child(3) .step-module{background:var(--gray3)}.labs-flow li:last-child .step-module{background:var(--mint)}.labs-flow .flow-arrow{top:22px}
.maturation{gap:22px;margin-top:125px}.maturation p{font-size:29px;line-height:1.25}.maturation .step-module{width:40px;height:40px;margin-bottom:35px}.maturation li:nth-child(2) .step-module{width:50px;height:50px}.maturation li:nth-child(3) .step-module{width:60px;height:60px}.maturation li:nth-child(4) .step-module{width:70px;height:70px}.maturation li:nth-child(5) .step-module{width:80px;height:80px}.maturation li:nth-child(6) .step-module{width:90px;height:90px}.maturation li:nth-child(7) .step-module{width:100px;height:100px}.maturation .flow-arrow{top:16px;font-size:32px}.maturation li:last-child{padding-right:0}.maturation li{display:flex;flex-direction:column;justify-content:end;min-height:220px}.maturation li p{height:120px}
.academy .title{font-size:90px}.academy .body{max-width:850px}.academy-note{margin-top:60px;max-width:800px}.academy-system{border-left:3px solid var(--ink);padding:50px 0 50px 60px}.master-label{color:var(--muted)}.academy-system h2{font-family:var(--font-heading);font-weight:500;letter-spacing:-.03em;font-size:76px;margin-top:30px}.formats{display:grid;justify-items:start;gap:28px;margin-top:50px}.formats .bracket{font-size:24px}
.reasons{margin-top:62px;list-style:none}.reason{display:grid;grid-template-columns:140px 1fr;gap:50px;padding:30px 0;border-top:1px solid var(--line)}.reason-number{font-family:var(--font-heading);font-size:76px;line-height:1;letter-spacing:-.04em}.reason p{font-size:40px;line-height:1.3;max-width:1420px}.reason:nth-child(2){padding-left:110px}.reason:nth-child(3){padding-left:220px}
.institutional{display:grid;grid-template-columns:1fr 110px 1fr;gap:20px;margin-top:42px;align-items:stretch}.association,.sac{padding:32px 40px;border:2px solid var(--gray3);position:relative}.association{border-left:8px solid var(--halo)}.institutional h2{font-family:var(--font-heading);font-weight:600;letter-spacing:-.025em;font-size:42px;line-height:1.1}.institutional ul{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:10px 30px;margin-top:24px}.institutional li{font-size:28px;color:var(--text-secondary);line-height:1.3}.institutional li:before{content:"▪";margin-right:10px;color:var(--halo)}.institution-link{font-size:56px;align-self:center;text-align:center;color:var(--gray3)}.academy-line{padding:22px 26px;margin-top:32px;background:var(--gray1);border-left:6px solid var(--halo)}.academy-line h3{font-family:var(--font-heading);font-weight:500;letter-spacing:-.025em;font-size:36px}.academy-line ul{grid-template-columns:1fr;margin-top:12px}.academy-line li{font-size:26px}.s16 .title{font-size:86px}.s16 .eyebrow{margin-bottom:22px}.s16 .legal{font-size:26px}
.knowledge-orbit{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:560px;margin-top:65px}.asset-column{display:grid;gap:25px;align-items:center}.asset-column .bracket{font-size:28px}.knowledge-core{position:absolute;left:680px;top:20px;width:300px;height:300px}
.layers{display:grid;grid-template-columns:1fr 100px 1fr;gap:30px;margin-top:100px;align-items:center}.layer{padding:44px;border-top:3px solid var(--ink);border-bottom:1px solid var(--line);min-height:330px}.layer .mono{font-size:28px}.layer .body{margin-top:34px}.layer-connector{font-size:58px;text-align:center;color:var(--muted)}
.license-flow{margin-top:75px;grid-template-columns:1.15fr 1.05fr 1fr 1.05fr .75fr;gap:28px}.license-flow p{font-size:32px;line-height:1.3;letter-spacing:-.02em}.license-flow .step-module{width:48px;height:48px;border:0}.license-flow li:nth-child(1) .step-module,.license-flow li:nth-child(4) .step-module,.license-flow li:nth-child(5) .step-module{background:var(--gray3)}.license-flow .flow-arrow{font-size:36px;top:0}
.return-flow{display:flex;align-items:center;justify-content:space-between;gap:25px;border-bottom:2px solid var(--mint);padding:30px 32px;margin-top:70px;background:var(--gray1)}.return-flow div{max-width:480px}.return-flow p{font-size:32px;line-height:1.3}.return-flow>span{color:var(--mint);font-size:46px}.s19 .title{font-size:88px}
.scholarship{margin-top:62px;gap:60px}.scholarship p{font-size:36px}.scholarship .step-module{width:56px;height:56px}.scholarship li:nth-child(3) .step-module{background:var(--mint)}.example{margin-top:60px;max-width:1560px}.s20 .title{max-width:1620px;font-size:84px}.s20 .body{margin-top:28px;font-size:34px}.s20 .legal{font-size:25px}
.convergence{display:grid;grid-template-columns:1fr 250px .9fr;gap:36px;align-items:center;margin-top:62px}.funding-sources{display:grid;gap:40px}.funding-source{border-top:2px solid var(--line);padding:24px 0}.funding-source p{font-size:36px;line-height:1.4}.merge-lines svg{width:100%;height:340px;fill:none;stroke:var(--ink);stroke-width:3}.cohort{padding:30px;border-left:3px solid var(--ink)}.cohort-modules{display:grid;grid-template-columns:repeat(5,48px);gap:20px;margin-bottom:30px}.cohort-modules i{width:48px;height:48px;display:block;background:var(--halo);border:2px solid var(--ink)}.cohort .mono{font-size:28px}
.future{grid-template-columns:1.25fr .8fr;gap:100px;align-items:start}.future .title{font-size:86px}.future .body{font-size:34px}.small-intro{font-size:30px;margin-top:30px}.possibilities{list-style:none;margin-top:14px}.possibility{padding:13px 0 13px 28px;border-left:4px solid var(--line)}.possibility p{font-size:30px;line-height:1.35}.mature-field{position:relative;height:100%;padding-top:20px}.mature-module{display:flex;align-items:center;justify-content:center;background:var(--halo);border:2px solid #000;width:340px;height:200px;margin:10px auto 60px;color:#000}.mature-module span{font-family:var(--font-heading);font-size:48px;font-weight:500;letter-spacing:-.025em}.mature-field .orbit-field{width:470px;margin:auto}
.s23 .title{font-size:100px;max-width:1550px;position:relative;z-index:2}.synthesis-lead{font-size:38px;line-height:1.4;margin-top:30px;color:var(--gray3);max-width:1400px}.synthesis{display:grid;grid-template-columns:1fr 1fr;gap:30px 60px;margin-top:65px;position:relative;z-index:2;max-width:1550px}.synthesis-item{display:flex;align-items:start;gap:24px;border-top:2px solid var(--gray1);padding-top:20px}.synthesis-item p{font-size:34px;line-height:1.35}.synthesis-marker{display:block;flex-shrink:0;width:18px;height:18px;background:var(--halo);margin-top:12px}.synthesis-end{margin-top:45px;position:relative;z-index:2;font-size:30px;max-width:1450px}.synthesis-field{position:absolute;width:530px;right:-200px;bottom:-200px;opacity:.65}
.closing{position:absolute;top:95px;left:0;right:0}.closing-symbol{width:160px;height:160px;margin-bottom:75px}.closing .title{font-size:148px;max-width:1660px}.closing-subtitle{font-size:40px;line-height:1.5;max-width:1120px;color:var(--gray3);margin-top:50px}
.depth-frame:before,.depth-frame:after{top:0;bottom:0;width:32px;height:auto;border-left:0;border-right:0;border-top:4px solid var(--field);border-bottom:4px solid var(--field)}.depth-frame:before{left:-4px;right:auto}.depth-frame:after{right:-4px;left:auto}
.s09 .area-grid{gap:0 68px;margin-top:32px}.s09 .area{padding:20px 0}.s09 .area h2{margin:14px 0}.s09 .area p{max-width:790px}
.synthesis-field{width:150px;right:0;bottom:0;opacity:1}
.js .build{opacity:0;transform:translateY(10px)}.js .build.visible{opacity:1;transform:none;transition:opacity 180ms var(--ease-out-expo),transform 180ms var(--ease-out-expo)}
.controls{position:fixed;bottom:8px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:4px;z-index:100;background:#1A1A1F;color:#FFFFFF;padding:4px 8px;opacity:0;transition:opacity .15s}.controls:hover,.controls:focus-within,body.controls-visible .controls{opacity:1}.controls button{border:0;border-radius:0;background:transparent;color:#FFFFFF;cursor:pointer;padding:6px 14px;font-family:"Geist Mono",monospace;font-size:clamp(11px,1vw,14px)}.controls button:focus-visible{outline:2px solid #8E8EFF}.controls output{font-family:"Geist Mono",monospace;font-size:clamp(11px,1vw,14px);padding:0 8px}
.live-status{position:fixed;width:1px;height:1px;clip-path:inset(50%);overflow:hidden}
@media(max-height:700px){.slide{padding:0}}@media(max-height:600px){.slide{padding:0}.controls{bottom:2px}}@media(max-height:500px){.slide{padding:0}}
@media(prefers-reduced-motion:reduce){.js .build{opacity:1;transform:none}.js .build.visible{transition:none}.controls{transition:none}}
@media print{@page{size:16in 9in;margin:0}html{scroll-snap-type:none}.slide{height:9in;width:16in;padding:0;break-after:page;page-break-after:always}.canvas{width:16in;height:9in;print-color-adjust:exact;-webkit-print-color-adjust:exact}.controls,.live-status{display:none!important}.js .build{opacity:1;transform:none}.footer{display:flex}}
'''

# Translate design-space dimensions to container units, preserving the 16:9 composition.
# Every text size is clamp-based; the small physical minimum permits proportional scaling.
def scale_css(css):
    # Only slide design rules; navigation/media/print rules below remain viewport-based.
    i=css.index('.js .build')
    design,rest=css[:i],css[i:]
    design=re.sub(r'font-size:([\d.]+)px',lambda m:f'font-size:clamp(1px,{float(m[1])/19.2:.7f}cqw,{float(m[1])*4:g}px)',design)
    # Do not rescale the upper bounds inside the newly created clamp expressions.
    holds=[]
    def hold(m):holds.append(m[0]);return f'__FONT{len(holds)-1}__'
    design=re.sub(r'clamp\(1px,[^)]*\)',hold,design)
    design=re.sub(r'(-?[\d.]+)px',lambda m:f'{float(m[1])/19.2:.7f}cqw',design)
    for j,t in enumerate(holds):design=design.replace(f'__FONT{j}__',t)
    return design+rest

SCRIPT = r'''
document.documentElement.classList.add('js');
const slides=[...document.querySelectorAll('.slide')];
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let active=0,timers=[],hideTimer;
const counter=document.querySelector('#counter'),status=document.querySelector('#status');
function finish(){timers.forEach(clearTimeout);timers=[];slides[active].querySelectorAll('.build').forEach(e=>e.classList.add('visible'));}
function play(i){timers.forEach(clearTimeout);timers=[];const s=slides[i],items=[...s.querySelectorAll('.build')];items.forEach(e=>e.classList.remove('visible'));if(reduced.matches){items.forEach(e=>e.classList.add('visible'));return;}items.forEach(e=>timers.push(setTimeout(()=>e.classList.add('visible'),Number(e.dataset.step||0)*160)));}
function update(i,animate=true){const changed=i!==active;active=i;slides.forEach((s,j)=>{s.setAttribute('aria-current',String(j===i));if(document.documentElement.classList.contains('js'))s.inert=j!==i;});counter.textContent=String(i+1).padStart(2,'0')+' / 24';status.textContent='Slide '+(i+1)+': '+slides[i].querySelector('h1').textContent;document.querySelector('#prev').disabled=i===0;document.querySelector('#next').disabled=i===23;if(changed&&animate)play(i);}
function go(i,animate=true){i=Math.max(0,Math.min(slides.length-1,i));slides[i].scrollIntoView({behavior:'instant',block:'start'});update(i,animate);if(!animate)finish();history.replaceState(null,'','#slide-'+String(i+1).padStart(2,'0'));}
window.deck={goTo:(n,animate=true)=>go(n-1,animate),finishAnimations:finish,get current(){return active+1},get count(){return slides.length}};
document.querySelector('#prev').addEventListener('click',()=>go(active-1));document.querySelector('#next').addEventListener('click',()=>go(active+1));
document.querySelector('#fullscreen').addEventListener('click',()=>{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen?.().catch(()=>{});});
function showControls(){document.body.classList.add('controls-visible');clearTimeout(hideTimer);hideTimer=setTimeout(()=>document.body.classList.remove('controls-visible'),1800);}
document.addEventListener('pointermove',showControls);
document.addEventListener('keydown',e=>{if(e.ctrlKey||e.altKey||e.metaKey||e.target.closest('input,textarea,[contenteditable="true"]'))return;const forward=['ArrowRight','ArrowDown','PageDown',' '],back=['ArrowLeft','ArrowUp','PageUp'];if(e.target.closest('button')&&e.key===' ')return;if(forward.includes(e.key)){e.preventDefault();go(active+1);}if(back.includes(e.key)){e.preventDefault();go(active-1);}if(e.key==='Home'){e.preventDefault();go(0);}if(e.key==='End'){e.preventDefault();go(23);}if(e.key==='Escape')finish();showControls();});
const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting)update(slides.indexOf(e.target));},{threshold:.65});slides.forEach(s=>observer.observe(s));
let touch=null;document.addEventListener('touchstart',e=>{if(!e.target.closest('nav'))touch={x:e.changedTouches[0].clientX,y:e.changedTouches[0].clientY};},{passive:true});document.addEventListener('touchend',e=>{if(!touch)return;const dx=e.changedTouches[0].clientX-touch.x,dy=e.changedTouches[0].clientY-touch.y;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))go(active+(dx<0?1:-1));touch=null;},{passive:true});
reduced.addEventListener('change',()=>finish());
const initial=Math.max(0,slides.findIndex(s=>'#'+s.id===location.hash));go(initial);play(initial);
window.addEventListener('hashchange',()=>{const i=slides.findIndex(s=>'#'+s.id===location.hash);if(i>=0)go(i);});
document.fonts.ready.then(()=>document.documentElement.dataset.fonts='ready');
'''

def fonts():
    cache_path=Path('/tmp/opencode/aipg-deck-fonts.css')
    if cache_path.exists():return cache_path.read_text()
    url='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter+Tight:wght@400;500&family=Geist+Mono:wght@400;500&display=swap'
    def get(u):
        with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:return response.read()
    css=get(url).decode();cache={}
    def replace(m):
        u=m[1]
        if u not in cache:
            mime='font/woff2' if '.woff2' in u else 'font/ttf'
            cache[u]=f'url(data:{mime};base64,{base64.b64encode(get(u)).decode()})'
        return cache[u]
    css=re.sub(r'url\((https://[^)]+)\)',replace,css)
    cache_path.write_text(css)
    return css

def build():
    sections=[]
    secondary={6,10,13,17,18,20,21}
    for s in SLIDES:
        n=s['number'];phase='PROPUESTA DE EVOLUCIÓN' if n<16 else 'HIPÓTESIS INSTITUCIONAL' if n<23 else 'AI PLAYGROUNDS'
        surface='secondary' if n in secondary else 'contrast' if n in {14,22} else 'primary'
        footer='AI PlayGrounds' if n==24 else phase
        sections.append(f'<section class="slide s{n:02}" data-theme="{s["theme"]}" data-surface="{surface}" id="slide-{n:02}" aria-label="Slide {n} de 24"><div class="canvas"><header class="masthead"><span class="brand-name">AI PlayGrounds</span><span class="chapter">{n:02} / 24</span></header><div class="content">{content(n)}</div><footer class="footer"><span>{footer}</span><div class="progress-track" aria-hidden="true"><span class="progress-{n}"></span></div></footer></div></section>')
    progress=''.join(f'.progress-{n}'+'{width:'+str(n/24*100)+'%;}' for n in range(1,25))
    base=(ROOT/'.agents/skills/html-slides/assets/viewport-base.css').read_text()
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'deck/deck-spec.md',ROOT/'branding/brand-spec.md',ROOT/'branding/branding-base.pdf']}
    metadata={'sources':hashes,'symbol':'SVG geometric reconstruction from PDF pp. 4–6: 5×5, 14/16, 1/8u gaps, fixed Halo core; not a new official asset. Brand name rendered as presentation text, not a newly designed logo.','conflicts':'No new real conflict found. Known small-size, favicon and color exceptions remain as documented in brand-spec.md.','motion':'Finite 160ms cadence and 180ms opacity/translation reveals; narrative sequences from deck-spec. No idle loops. Optional Depth zoom omitted to keep statement contained.','slideSource':SLIDES}
    doc='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark light"><title>AI PlayGrounds — De comunidad a organización</title><style>'+fonts()+'\n'+base+'\n'+scale_css(CSS)+'\n'+progress+'</style></head><body><main>'+''.join(sections)+'</main><nav class="controls" aria-label="Navegación de presentación"><button id="prev" type="button" aria-label="Slide anterior">←</button><output id="counter">01 / 24</output><button id="next" type="button" aria-label="Slide siguiente">→</button><button id="fullscreen" type="button" aria-label="Pantalla completa">⛶</button></nav><div id="status" class="live-status" role="status" aria-live="polite"></div><script type="application/json" id="deck-provenance">'+json.dumps(metadata,ensure_ascii=False).replace('</','<\\/')+'</script><script>'+SCRIPT+'</script></body></html>'
    (ROOT/'output/deck.html').write_text(doc)
    print('Built output/deck.html:',len(SLIDES),'slides;',len(doc.encode()),'bytes.')

if __name__=='__main__':build()
