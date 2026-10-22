(() => {
  'use strict';
  const {deck,sources}=JSON.parse(document.getElementById('deck-data').textContent);
  const slides=[...document.querySelectorAll('.slide')];
  const select=document.getElementById('page-select');
  const mounted=new Map();
  let index=Math.max(0,deck.slides.findIndex(s=>s.id===location.hash.slice(1)));
  let reading=false;
  function mount(i){
    if(mounted.has(i))return;
    const container=slides[i].querySelector('.diagram-mount');
    if(!window.ConceptCanvas){container.textContent='画布模块加载失败，请刷新页面。';container.classList.add('diagram-error');return;}
    mounted.set(i,window.ConceptCanvas.mount(container,deck.slides[i].graph,sources));
  }
  function show(next,updateHash=true){
    index=Math.min(slides.length-1,Math.max(0,next));
    slides.forEach((s,i)=>{s.classList.toggle('active',i===index);s.setAttribute('aria-hidden',String(!reading&&i!==index));});
    select.value=String(index);
    document.getElementById('previous').disabled=index===0;
    document.getElementById('next').disabled=index===slides.length-1;
    document.getElementById('progress').style.width=`${(index+1)/slides.length*100}%`;
    if(updateHash)history.replaceState(null,'','#'+deck.slides[index].id);
    requestAnimationFrame(()=>{mount(index);if(reading)slides[index].scrollIntoView({block:'start'});});
    document.title=`${index+1}. ${deck.slides[index].title} · vLLM PCP & DCP`;
  }
  document.getElementById('previous').addEventListener('click',()=>show(index-1));
  document.getElementById('next').addEventListener('click',()=>show(index+1));
  select.addEventListener('change',()=>show(Number(select.value)));
  document.getElementById('reading').addEventListener('click',event=>{
    reading=!reading;document.body.classList.toggle('reading',reading);event.currentTarget.setAttribute('aria-pressed',String(reading));event.currentTarget.textContent=reading?'逐页演示':'连续阅读';
    slides.forEach((s,i)=>{s.setAttribute('aria-hidden',String(!reading&&i!==index));if(reading)mount(i);});show(index);
  });
  const dialog=document.getElementById('source-dialog');
  document.getElementById('sources-button').addEventListener('click',()=>dialog.showModal());
  document.getElementById('close-sources').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  document.getElementById('fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{document.getElementById('fullscreen').textContent='请按 F11';}});
  window.addEventListener('hashchange',()=>{const i=deck.slides.findIndex(s=>s.id===location.hash.slice(1));if(i>=0)show(i,false);});
  document.addEventListener('keydown',event=>{
    if(dialog.open||event.altKey||event.ctrlKey||event.metaKey||event.target.closest('input,select,textarea,button,a,[contenteditable=true]'))return;
    if(event.key==='ArrowRight'||event.key==='PageDown'){event.preventDefault();show(index+1);}
    if(event.key==='ArrowLeft'||event.key==='PageUp'){event.preventDefault();show(index-1);}
    if(event.key==='Home'){event.preventDefault();show(0);}
    if(event.key==='End'){event.preventDefault();show(slides.length-1);}
  });
  show(index,false);
})();
