"""Render the deck and execute reproducible browser and PDF checks."""
from pathlib import Path
import json
import re
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
shots = OUT/'screenshots'; shots.mkdir(exist_ok=True)
issues = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium-browser', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1920,'height':1080}, device_scale_factor=1)
    errors=[]; requests=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: requests.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    page.goto((OUT/'deck.html').as_uri());page.wait_for_function("document.documentElement.dataset.fonts === 'ready'")
    assert page.locator('.slide').count()==19
    for n in range(1,20):
        assert f'{n:02} / 19' in page.locator(f'#slide-{n:02}').inner_text()
    assert [page.locator(f'#slide-{n:02} .mode span').inner_text() for n in range(13,18)] == ['MODALIDAD 01 / 03','MODALIDAD 02 / 03','MODALIDAD 02 / 03','MODALIDAD 02 / 03','MODALIDAD 03 / 03']
    assert page.locator('#slide-13 .two-blocks article').count()==2
    assert 'Quiénes impulsan AI PlayGrounds.' in page.locator('#slide-18').inner_text()
    assert 'Seguimos construyendo.' in page.locator('#slide-19').inner_text()
    assert 'Interés' not in page.locator('body').inner_text() or 'Exploración' not in page.locator('body').inner_text()
    for n in range(1,20):
        page.evaluate('(n)=>deck.goTo(n)',n)
        page.screenshot(path=str(shots/f'slide-{n:02}.png'),animations='disabled')
    for n in range(20,25):
        path=shots/f'slide-{n:02}.png'
        if path.exists(): path.unlink()
    page.evaluate('deck.goTo(1)');page.keyboard.press('ArrowRight');assert page.evaluate('deck.current')==2
    page.keyboard.press('End');assert page.evaluate('deck.current')==19
    page.keyboard.press('ArrowRight');assert page.evaluate('deck.current')==19
    page.keyboard.press('Home');page.keyboard.press('ArrowLeft');assert page.evaluate('deck.current')==1
    page.keyboard.press('PageDown');assert page.evaluate('deck.current')==2
    page.keyboard.press('PageUp');assert page.evaluate('deck.current')==1
    page.keyboard.press('Space');assert page.evaluate('deck.current')==2
    page.locator('#full').click(force=True)
    assert page.evaluate('!!document.fullscreenElement')
    page.evaluate('document.exitFullscreen()')
    page.emulate_media(reduced_motion='reduce')
    for w,h in [(1920,1080),(1366,768),(1280,720)]:
        page.set_viewport_size({'width':w,'height':h})
        for n in range(1,20):
            page.evaluate('(n)=>deck.goTo(n)',n)
            data=page.evaluate('''() => {const c=document.querySelectorAll('.canvas')[deck.current-1],r=c.getBoundingClientRect();let bad=[];const walker=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);while(walker.nextNode()){const t=walker.currentNode;if(!t.textContent.trim()||t.parentElement.closest('svg'))continue;let range=document.createRange();range.selectNodeContents(t);for(const b of range.getClientRects())if(b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1)bad.push(t.textContent.trim().slice(0,80));}return bad}''')
            if data: issues.append({'slide':n,'viewport':[w,h],'outside':data})
    overlaps=[]
    for n in [5,9,12,13,14,15,16,17]:
        page.evaluate('(n)=>deck.goTo(n)',n)
        page.wait_for_timeout(40)
        pairs=page.evaluate('''() => {const s=document.querySelectorAll('.slide')[deck.current-1],w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT),a=[];while(w.nextNode()){let t=w.currentNode;if(!t.textContent.trim())continue;let r=document.createRange();r.selectNodeContents(t);for(let b of r.getClientRects())a.push({node:t,text:t.textContent.trim().slice(0,60),x:b.x,y:b.y,r:b.right,b:b.bottom});}let out=[];for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){let x=a[i],y=a[j];if(x.node!==y.node&&Math.min(x.r,y.r)-Math.max(x.x,y.x)>2&&Math.min(x.b,y.b)-Math.max(x.y,y.y)>2)out.push([x.text,y.text]);}return out}''')
        if pairs: overlaps.append({'slide':n,'pairs':pairs})
    source_copy = {n:page.locator(f'#slide-{n:02} main p:not(:has(b)), #slide-{n:02} main h1, #slide-{n:02} main h2').all_text_contents() for n in [5,9,12,13,14,15,16,17]}
    page.emulate_media(media='print',reduced_motion='reduce')
    page.pdf(path=str(OUT/'deck.pdf'),width='1152px',height='648px',print_background=True,prefer_css_page_size=True)
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':1920,'height':1080})
    nojs_page=nojs.new_page();nojs_page.goto((OUT/'deck.html').as_uri())
    assert nojs_page.locator('.slide').count()==19
    assert nojs_page.locator('#slide-19').inner_text().find('Seguimos construyendo')>=0
    nojs.close()
    browser.close()
info=subprocess.check_output(['pdfinfo',str(OUT/'deck.pdf')],text=True)
text=subprocess.check_output(['pdftotext',str(OUT/'deck.pdf'),'-'],text=True)
assert 'Pages:           19' in info and 'Seguimos construyendo' in text
normalize=lambda s:re.sub(r'\s+',' ',s).strip()
copy_errors=[]
for n, paragraphs in source_copy.items():
    page_text=normalize(subprocess.check_output(['pdftotext','-f',str(n),'-l',str(n),str(OUT/'deck.pdf'),'-'],text=True))
    for paragraph in paragraphs:
        if normalize(paragraph) not in page_text: copy_errors.append({'slide':n,'missing':paragraph})
report={'slides':19,'pdf_pages':19,'pdf_selectable':True,'js_errors':errors,'external_requests':requests,'text_outside':issues,'new_slide_overlaps':overlaps,'pdf_copy_errors':copy_errors,'viewports':['1920x1080','1366x768','1280x720'],'navigation':'arrows, space, PageUp/PageDown, Home/End and bounds passed','fullscreen':'entered and exited in headless Chromium','motion':'reduced-motion enabled; no hidden entrance animations','no_javascript':'19 slides and closing text present'}
(OUT/'qa-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if issues or errors or requests or overlaps or copy_errors: raise SystemExit(1)
