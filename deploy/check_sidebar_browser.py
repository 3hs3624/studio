import json,os,subprocess,tempfile,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];errors=[];checks=[]
ARTIFACTS=Path(os.environ.get('SIDEBAR_ARTIFACT_DIR','/tmp/studio-sidebar-check'));ARTIFACTS.mkdir(parents=True,exist_ok=True)
renderer="import os,sys,re\nfrom pathlib import Path\nfrom types import SimpleNamespace as S\nsys.path.insert(0,str(Path.cwd()));os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings');os.environ['DEBUG']='1'\nimport django;django.setup()\nfrom django.template.loader import render_to_string\nbase={'user':S(is_authenticated=True),'actor':S(display_name='검증 관리자'),'org':S(name='검증 조직'),'active_area':'portal','area_name':'통합 ITSM','nav_groups':[{'title':'서비스 이용','links':[{'url':'/portal','label':'서비스 현황','active':True}]}],'common_links':[{'url':'/notifications','label':'알림'}],'systems':[],'console_groups':[{'title':'업무 구성','links':[{'url':'/console','label':'화면 관리','active':True}]}],'console_mode':False}\nfor name,t in [('portal','desk/base.html'),('console','desk/console-base.html')]:\n html=render_to_string(t,base);(Path(os.environ['SIDEBAR_FIXTURE_DIR'])/(name+'.html')).write_text(html)\nprint('Rendered portal and console templates')\n"
fixtures=tempfile.TemporaryDirectory();env=dict(os.environ,SIDEBAR_FIXTURE_DIR=fixtures.name)
subprocess.run([os.environ.get('DJANGO_PYTHON',str(ROOT/'.venv/bin/python')),'-c',renderer],cwd=ROOT,env=env,check=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':1000})
 def route(r):
  path=r.request.url.split('studio.test',1)[-1]
  if path.startswith('/static/desk/'):
   f=ROOT/'desk/static/desk'/path.rsplit('/',1)[-1];r.fulfill(body=f.read_bytes(),content_type='text/css' if f.suffix=='.css' else 'application/javascript')
  else:r.fulfill(body=(Path(fixtures.name)/(('console' if path.startswith('/console') else 'portal')+'.html')).read_text(),content_type='text/html')
 context.route('http://studio.test/**',route);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://studio.test/portal')
 toggle=page.locator('[data-sidebar-toggle]');handle=page.locator('[data-sidebar-resizer]');nav=page.locator('#primary-navigation')
 def width():return round(nav.bounding_box()['width'])
 def record(s):checks.append(s)
 assert width()==256;record('default width')
 handle.focus();page.keyboard.press('ArrowRight');assert width()==266
 page.keyboard.press('Shift+ArrowRight');assert width()==316;record('keyboard increments')
 page.keyboard.press('End');assert width()==480
 page.keyboard.press('Home');assert width()==220;record('keyboard bounds')
 handle.dblclick();assert width()==256;record('default reset')
 b=handle.bounding_box();page.mouse.move(b['x']+4,b['y']+100);page.mouse.down();page.mouse.move(b['x']+104,b['y']+100);page.mouse.up();assert width()==356;record('pointer resize')
 b=handle.bounding_box();page.mouse.move(b['x']+4,b['y']+100);page.mouse.down();page.mouse.move(b['x']+64,b['y']+100);page.keyboard.press('Escape');page.mouse.up();assert width()==356;record('Escape cancels unsaved drag')
 toggle.click();assert page.evaluate("document.getElementById('primary-navigation').inert");assert toggle.get_attribute('aria-expanded')=='false';assert not handle.is_visible();assert page.locator('.shell').bounding_box()['x']==0;record('collapse removes navigation from focus and expands content')
 page.reload();assert toggle.get_attribute('aria-expanded')=='false';toggle.click();assert width()==356;record('reload restores collapse and width')
 page.goto('http://studio.test/console');assert width()==356;record('portal/console preference shared')
 toggle.click();page.set_viewport_size({'width':390,'height':844});assert not page.evaluate("document.getElementById('primary-navigation').inert");assert not toggle.is_visible();mobile=page.locator('.shell-menu-toggle');mobile.click();assert mobile.get_attribute('aria-expanded')=='true';page.keyboard.press('Escape');assert mobile.get_attribute('aria-expanded')=='false';record('mobile menu independent from desktop collapse')
 page.set_viewport_size({'width':1440,'height':1000});page.wait_for_function("document.querySelector('[data-sidebar-toggle]').getAttribute('aria-expanded')==='false'");assert toggle.get_attribute('aria-expanded')=='false';toggle.click();assert width()==356;record('desktop state restored after mobile')
 handle.focus();page.keyboard.press('End');page.set_viewport_size({'width':700,'height':900});page.wait_for_function("Math.round(document.getElementById('primary-navigation').getBoundingClientRect().width)===315");assert width()==315;page.set_viewport_size({'width':1440,'height':1000});page.wait_for_function("Math.round(document.getElementById('primary-navigation').getBoundingClientRect().width)===480");assert width()==480;record('viewport clamps effective width without overwriting preferred width')
 page.set_viewport_size({'width':700,'height':900});page.wait_for_function("Math.round(document.getElementById('primary-navigation').getBoundingClientRect().width)===315");handle.focus();page.keyboard.press('ArrowLeft');assert width()==305;record('keyboard uses visible width after viewport clamp')
 page.set_viewport_size({'width':1440,'height':1000})
 page.evaluate("localStorage.setItem('studio.sidebar.v1', '{bad json')");page.reload();assert width()==256;record('corrupted storage fallback')
 page.evaluate("localStorage.setItem('studio.sidebar.v1', JSON.stringify({width:'999px',collapsed:'yes'}))");page.reload();assert width()==256;record('invalid storage types ignored')
 page.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})");page.reload();toggle.click();toggle.click();assert width()==256;record('storage denial keeps controls functional')
 page.screenshot(path=str(ARTIFACTS/'desktop.png'));page.set_viewport_size({'width':390,'height':844});mobile.click();page.screenshot(path=str(ARTIFACTS/'mobile.png'));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');record('mobile has no horizontal overflow')
 assert not errors,errors
 (ARTIFACTS/'result.json').write_text(json.dumps({'checks':checks,'page_errors':errors},ensure_ascii=False,indent=2));print(json.dumps({'passed':len(checks),'page_errors':errors}))
 browser.close()

fixtures.cleanup()
