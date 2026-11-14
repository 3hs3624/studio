'use strict';
(()=>{
 for(const layout of document.querySelectorAll('[data-screen-layout][data-layout-mode="tabs"]')){
  const tabs=[...layout.querySelectorAll('[data-group-tabs]>button')];
  const activate=(tab,focus=false)=>{for(const t of tabs){const selected=t===tab;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!selected;}if(focus)tab.focus();};
  for(const tab of tabs){tab.addEventListener('click',()=>activate(tab));tab.addEventListener('keydown',e=>{let i=tabs.indexOf(tab);if(e.key==='ArrowRight')i=(i+1)%tabs.length;else if(e.key==='ArrowLeft')i=(i+tabs.length-1)%tabs.length;else if(e.key==='Home')i=0;else if(e.key==='End')i=tabs.length-1;else return;e.preventDefault();activate(tabs[i],true);});}
  if(tabs.length)activate(tabs[0]);
  // Native required validation must reveal a field in an inactive tab.
  let revealing=false;
  layout.addEventListener('invalid',e=>{if(revealing)return;revealing=true;setTimeout(()=>revealing=false,0);const panel=e.target.closest('[role=tabpanel]');const tab=tabs.find(t=>t.getAttribute('aria-controls')===panel?.id);if(tab)activate(tab);},true);
 }
})();
