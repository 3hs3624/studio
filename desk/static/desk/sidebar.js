/* Browser-local layout preference. No account data, permissions or server state. */
(()=>{'use strict';
 const toggle=document.querySelector('[data-sidebar-toggle]'),handle=document.querySelector('[data-sidebar-resizer]'),nav=document.getElementById('primary-navigation');
 if(!toggle||!handle||!nav)return;
 const storageKey='studio.sidebar.v1',desktop=window.matchMedia('(min-width:681px)');
 let width=256,collapsed=false,drag=null;
 try{const saved=JSON.parse(localStorage.getItem(storageKey));if(saved&&typeof saved==='object'){if(Number.isFinite(saved.width)&&saved.width>=220&&saved.width<=480)width=saved.width;if(typeof saved.collapsed==='boolean')collapsed=saved.collapsed;}}catch(_){/* Storage may be disabled or malformed; layout still works. */}
 const maximum=()=>Math.max(220,Math.min(480,Math.floor(window.innerWidth*.45)));
 const clamp=value=>Math.max(220,Math.min(maximum(),Math.round(value)));
 const save=()=>{try{localStorage.setItem(storageKey,JSON.stringify({width,collapsed}));}catch(_){/* Current page remains usable without persistence. */}};
 function apply(){
  const effective=clamp(width),hidden=desktop.matches&&collapsed;
  document.body.style.setProperty('--sidebar-preferred-width',effective+'px');
  document.body.classList.toggle('sidebar-collapsed',hidden);nav.inert=hidden;
  toggle.setAttribute('aria-expanded',String(!hidden));toggle.setAttribute('aria-label',hidden?'사이드바 펼치기':'사이드바 접기');
  handle.setAttribute('aria-valuemax',String(maximum()));handle.setAttribute('aria-valuenow',String(effective));handle.setAttribute('aria-valuetext',effective+'px');
 }
 function finish(cancel=false){if(!drag)return;const old=drag;drag=null;if(cancel)width=old.width;else save();document.body.classList.remove('sidebar-resizing');apply();if(handle.hasPointerCapture(old.id))handle.releasePointerCapture(old.id);}
 toggle.addEventListener('click',()=>{if(!desktop.matches)return;collapsed=!collapsed;save();apply();});
 handle.addEventListener('pointerdown',event=>{if(!desktop.matches||collapsed||event.button!==0)return;event.preventDefault();drag={id:event.pointerId,x:event.clientX,width,startWidth:clamp(width)};handle.focus();handle.setPointerCapture(event.pointerId);document.body.classList.add('sidebar-resizing');});
 handle.addEventListener('pointermove',event=>{if(!drag||event.pointerId!==drag.id)return;width=clamp(drag.startWidth+event.clientX-drag.x);apply();});
 handle.addEventListener('pointerup',event=>{if(drag&&event.pointerId===drag.id)finish();});
 handle.addEventListener('pointercancel',()=>finish(true));handle.addEventListener('lostpointercapture',()=>finish(true));
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&drag){event.preventDefault();finish(true);}});
 handle.addEventListener('keydown',event=>{if(!desktop.matches||collapsed)return;const step=event.shiftKey?50:10;let next;if(event.key==='ArrowLeft')next=clamp(width)-step;else if(event.key==='ArrowRight')next=clamp(width)+step;else if(event.key==='Home')next=220;else if(event.key==='End')next=maximum();else return;event.preventDefault();width=clamp(next);save();apply();});
 handle.addEventListener('dblclick',()=>{if(!desktop.matches||collapsed)return;width=256;save();apply();});
 desktop.addEventListener('change',()=>{finish(true);apply();});window.addEventListener('resize',()=>{finish(true);apply();});
 window.addEventListener('storage',event=>{if(event.key!==storageKey||drag)return;try{const value=JSON.parse(event.newValue);if(!value){width=256;collapsed=false;}else if(Number.isFinite(value.width)&&value.width>=220&&value.width<=480&&typeof value.collapsed==='boolean'){width=value.width;collapsed=value.collapsed;}else return;apply();}catch(_){}});
 apply();
})();
