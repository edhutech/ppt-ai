"""Browser QA and individual renders for output/deck.html (requires Playwright)."""
from pathlib import Path
import hashlib
import html
import importlib.util
import json
import re
import sys
from playwright.sync_api import sync_playwright

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('deck_builder',ROOT/'tmp/build_deck.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
out=ROOT/'output/screenshots';out.mkdir(exist_ok=True)

MEASURE=r'''() => {
 const s=document.querySelectorAll('.slide')[window.deck.current-1];
 const canvas=s.querySelector('.canvas'), frame=canvas.getBoundingClientRect();
 const content=s.querySelector('.content'), bounds=content.getBoundingClientRect();
 const elements=[...content.querySelectorAll('*')].filter(e=>!e.closest('[aria-hidden="true"]')&&e.getBoundingClientRect().width&&e.getBoundingClientRect().height);
 const overflow=elements.filter(e=>{const r=e.getBoundingClientRect();return r.left<frame.left-1||r.right>frame.right+1||r.top<frame.top-1||r.bottom>frame.bottom+1}).map(e=>({tag:e.tagName,cls:e.className,text:e.textContent.slice(0,80)}));
 const footer=s.querySelector('.footer').getBoundingClientRect();
 const footerOverlap=elements.filter(e=>{if(e.children.length)return false;const r=e.getBoundingClientRect();return r.bottom>footer.top-10&&r.width&&r.height}).map(e=>e.textContent.slice(0,100));
 const textOutside=[];
 const walker=document.createTreeWalker(content,NodeFilter.SHOW_TEXT);
 let node;while(node=walker.nextNode()){if(!node.textContent.trim()||node.parentElement.closest('[aria-hidden="true"]'))continue;let range=document.createRange();range.selectNodeContents(node);for(const r of range.getClientRects()){if(r.right>frame.right+1||r.left<frame.left-1||r.bottom>footer.top-4)textOutside.push(node.textContent.slice(0,80));}}
 return {slide:window.deck.current,theme:s.dataset.theme,surface:s.dataset.surface,overflow,footerOverlap,textOutside,builds:s.querySelectorAll('.build').length,visibleBuilds:s.querySelectorAll('.build.visible').length,canvas:{width:frame.width,height:frame.height},text:content.innerText};
}'''

def normalize(s):return re.sub(r'\s+',' ',s).strip()

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium-browser',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
    errors=[];external=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:external.append(r.url) if r.url.startswith(('https:','http:')) else None)
    page.goto((ROOT/'output/deck.html').as_uri())
    page.evaluate('document.fonts.ready')
    page.wait_for_function('document.documentElement.dataset.fonts === "ready"')
    assert page.locator('.slide').count()==24
    assert page.evaluate('document.fonts.check(\'600 88px "Space Grotesk"\') && document.fonts.check(\'400 36px "Inter Tight"\') && document.fonts.check(\'500 24px "Geist Mono"\')')
    rows=[];copy_errors=[]
    for n,s in enumerate(builder.SLIDES,1):
        page.evaluate('(n)=>window.deck.goTo(n)',n)
        page.wait_for_timeout(1900)
        result=page.evaluate(MEASURE)
        assert result['theme']==s['theme']
        visible=normalize(result['text'])
        assert normalize(page.locator(f'.s{n:02} h1').inner_text())==normalize(builder.field(n,'Title'))
        for key,value in s['fields'].items():
            comparison_text=normalize(page.locator(f'.s{n:02} .footer').inner_text()) if key=='Optional footer' else visible
            # Lists/flows can be composed spatially; each literal text line must remain visible.
            for line in builder.clean(value).splitlines():
                line=re.sub(r'^(?:- |\d+\. |→\s*)','',line.strip())
                parts=[p.strip() for p in line.split('→') if p.strip()]
                for text in parts:
                    if normalize(text) not in comparison_text:copy_errors.append({'slide':n,'field':key,'missing':text})
        result.pop('text');rows.append(result)
        page.screenshot(path=str(out/f'slide-{n:02}.png'),animations='disabled')
    # Key navigation and boundary handling.
    page.evaluate('window.deck.goTo(1,false)');page.keyboard.press('ArrowRight');assert page.evaluate('window.deck.current')==2
    page.keyboard.press('PageDown');assert page.evaluate('window.deck.current')==3
    page.keyboard.press('PageUp');assert page.evaluate('window.deck.current')==2
    page.keyboard.press('Space');assert page.evaluate('window.deck.current')==3
    page.keyboard.press('End');assert page.evaluate('window.deck.current')==24
    page.keyboard.press('ArrowRight');assert page.evaluate('window.deck.current')==24
    page.keyboard.press('Home');assert page.evaluate('window.deck.current')==1
    page.keyboard.press('ArrowLeft');assert page.evaluate('window.deck.current')==1
    page.locator('#next').focus();page.keyboard.press('Enter');assert page.evaluate('window.deck.current')==2
    page.locator('#prev').focus();page.keyboard.press('Enter');assert page.evaluate('window.deck.current')==1
    # Animation actually progresses before settling, and reduced motion exposes everything.
    page.evaluate('window.deck.goTo(8)')
    before=page.locator('.s08 .build.visible').count();page.wait_for_timeout(1500);after=page.locator('.s08 .build.visible').count()
    assert before<after and after==page.locator('.s08 .build').count()
    page.emulate_media(reduced_motion='reduce')
    page.evaluate('window.deck.goTo(19)');page.wait_for_timeout(40)
    assert page.locator('.s19 .build.visible').count()==page.locator('.s19 .build').count()
    responsive=[]
    for w,h in [(2560,1440),(1920,1200),(1600,900),(1366,768),(1280,720),(1024,768),(844,390)]:
        page.set_viewport_size({'width':w,'height':h})
        for n in range(1,25):
            page.evaluate('(n)=>window.deck.goTo(n,false)',n)
            result=page.evaluate(MEASURE)
            if result['overflow'] or result['footerOverlap'] or result['textOutside']:responsive.append({'viewport':[w,h],**result})
    # Swipe on a touch-enabled viewport.
    touch=browser.new_context(viewport={'width':1280,'height':720},has_touch=True)
    tp=touch.new_page();tp.goto((ROOT/'output/deck.html').as_uri());tp.wait_for_function('!!window.deck')
    tp.evaluate('''() => {for(const [type,x] of [['touchstart',900],['touchend',300]]){const e=new Event(type,{bubbles:true});Object.defineProperty(e,'changedTouches',{value:[{clientX:x,clientY:300}]});document.querySelector('main').dispatchEvent(e);}}''')
    assert tp.evaluate('window.deck.current')==2
    # Without JavaScript all 24 slides remain visible and printable.
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':1920,'height':1080})
    np=nojs.new_page();np.goto((ROOT/'output/deck.html').as_uri());assert np.locator('.slide').count()==24
    assert np.locator('.s24 h1').is_visible()
    report={'slides':rows,'copyErrors':copy_errors,'responsiveErrors':responsive,'jsErrors':errors,'externalRequests':external,'navigation':'arrows, space, PageUp/PageDown, Home/End, buttons, boundaries and swipe passed','animation':'progressive reveal and prefers-reduced-motion passed','noJS':'24 slides visible without JavaScript','fonts':'Space Grotesk, Inter Tight and Geist Mono loaded locally from embedded data'}
    browser.close()

protected=json.loads(Path('/tmp/opencode/aipg-input-hashes.json').read_text())
report['protectedInputsUnchanged']=all((ROOT/p).is_file() and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items())
(ROOT/'tmp/deck-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='slides'},ensure_ascii=False,indent=2))
for row in rows:
    if row['overflow'] or row['footerOverlap'] or row['textOutside']:print('LAYOUT:',json.dumps(row,ensure_ascii=False))
print('Screenshots:',len(list(out.glob('slide-??.png'))))
assert not copy_errors and not responsive and not errors and not external
assert all(not row['overflow'] and not row['footerOverlap'] and not row['textOutside'] for row in rows)
assert report['protectedInputsUnchanged']
