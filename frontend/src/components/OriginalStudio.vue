<script setup lang="ts">
import {computed,onBeforeUnmount,ref,watch} from 'vue';
type Shape={id:string;d:string;x:number;y:number;rotation:number;scale:number;stroke:string;fill:string;strokeWidth:number;bounds:{x:number;y:number;width:number;height:number}};
type Workspace={shapes:Shape[];symmetry:number;mirror:boolean;template:string;sourceDesign:string;sourcePattern:string};
const props=defineProps<{seedDesign?:any;seedPattern?:any}>();
const emit=defineEmits(['saved','navigate']);
const canvas=ref<SVGSVGElement>(),tool=ref('pen'),shapes=ref<Shape[]>([]),selected=ref(''),symmetry=ref(1),mirror=ref(false),stroke=ref('#d6e2df'),fill=ref('#e6bc77'),strokeWidth=ref(7),filled=ref(false),closed=ref(false),showGuides=ref(true),name=ref(''),description=ref(''),template=ref(''),sourceDesign=ref(''),sourcePattern=ref(''),rights=ref(false),busy=ref(false),message=ref(''),error=ref(''),savedPattern=ref<any>(null),draftNotice=ref('');
const draft=ref<Shape|null>(null),points=ref<{x:number;y:number}[]>([]),history=ref<string[]>([]),cursor=ref(-1);
let gesture:{type:'draw'|'move';start:{x:number;y:number};original?:Shape;copyAngle?:number;copyMirror?:boolean;pointer:number}|null=null;
const tools=[
  {id:'select',name:'选取',icon:'↖'},
  {id:'pen',name:'自由画笔',icon:'〰'},
  {id:'eraser',name:'橡皮擦',icon:'⌫'},
  {id:'line',name:'线段',icon:'／'},
  {id:'rect',name:'矩形',icon:'□'},
  {id:'diamond',name:'菱形',icon:'◇'},
  {id:'ellipse',name:'圆形',icon:'○'},
  {id:'petal',name:'花瓣',icon:'❧'},
  {id:'cloud',name:'如意云',icon:'☁'},
  {id:'arc',name:'弧线',icon:'⌒'}
];
const current=computed(()=>shapes.value.find(s=>s.id===selected.value));
const copies=computed(()=>Array.from({length:symmetry.value},(_,i)=>({angle:i*360/symmetry.value,reflected:false})).flatMap(c=>mirror.value?[c,{...c,reflected:true}]:[c]));
const hasArt=computed(()=>shapes.value.length>0||!!template.value);
const canSave=computed(()=>hasArt.value&&name.value.trim().length>=2&&rights.value&&!busy.value);
const isRemix=computed(()=>!!sourceDesign.value||!!sourcePattern.value);
const palette=['#d6e2df','#e6bc77','#efb3a1','#a6cfc2','#f5f0e5'];
function cleanTemplate(svg:string){
 if(!svg)return'';
 const doc=new DOMParser().parseFromString(svg,'image/svg+xml');if(doc.querySelector('parsererror')||doc.documentElement.localName!=='svg')return'';
 const allowed=new Set(['svg','g','path','rect','circle','ellipse','line','polyline','polygon','title','desc','defs','clippath','mask','lineargradient','radialgradient','stop']);
 const attrs=new Set(['id','d','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','width','height','viewbox','preserveaspectratio','points','transform','fill','fill-rule','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-miterlimit','stroke-dasharray','stroke-dashoffset','opacity','fill-opacity','stroke-opacity','clip-path','mask','offset','stop-color','stop-opacity','gradientunits','gradienttransform','spreadmethod','version','xmlns']);
 const root=doc.documentElement;for(const el of [root,...Array.from(root.querySelectorAll('*'))]){if(!allowed.has(el.localName.toLowerCase())){el.remove();continue}for(const a of Array.from(el.attributes)){if(!attrs.has(a.name.toLowerCase())||(/url\(/i.test(a.value)&&!/^url\(#[a-zA-Z0-9_-]+\)$/.test(a.value)))el.removeAttribute(a.name)}}
 root.setAttribute('x','0');root.setAttribute('y','0');root.setAttribute('width','1000');root.setAttribute('height','1000');return new XMLSerializer().serializeToString(root);
}
function workspace():Workspace{return{shapes:JSON.parse(JSON.stringify(shapes.value)),symmetry:symmetry.value,mirror:mirror.value,template:template.value,sourceDesign:sourceDesign.value,sourcePattern:sourcePattern.value}}
function restoreWorkspace(w:Workspace){shapes.value=w.shapes||[];symmetry.value=w.symmetry||1;mirror.value=!!w.mirror;template.value=cleanTemplate(w.template||'');sourceDesign.value=w.sourceDesign||'';sourcePattern.value=w.sourcePattern||'';selected.value='';draft.value=null;savedPattern.value=null;rights.value=false}
function checkpoint(){const json=JSON.stringify(workspace());if(history.value[cursor.value]===json)return;history.value=history.value.slice(0,cursor.value+1);history.value.push(json);if(history.value.length>35)history.value.shift();cursor.value=history.value.length-1;savedPattern.value=null}
function undo(delta:number){const next=cursor.value+delta;if(next<0||next>=history.value.length)return;cursor.value=next;restoreWorkspace(JSON.parse(history.value[next]));message.value=''}
function copyTransform(angle:number,reflected=false){return `translate(500 500) rotate(${angle}) scale(${reflected?-1:1} 1) translate(-500 -500)`}
function shapeTransform(s:Shape){return `translate(${s.x} ${s.y}) rotate(${s.rotation}) scale(${s.scale})`}
function point(e:PointerEvent){const matrix=canvas.value?.getScreenCTM();if(!matrix)return{x:500,y:500};const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(matrix.inverse());return{x:Math.max(0,Math.min(1000,p.x)),y:Math.max(0,Math.min(1000,p.y))}}
function sourcePoint(p:{x:number;y:number},angle=0,reflected=false){return new DOMPoint(p.x,p.y).matrixTransform(new DOMMatrix().translate(500,500).rotate(angle).scale(reflected?-1:1,1).translate(-500,-500).inverse())}
function makeShape(start:{x:number;y:number},end:{x:number;y:number}):Shape{
 const w=Math.max(4,Math.abs(end.x-start.x)),h=Math.max(4,Math.abs(end.y-start.y));
 let x=(start.x+end.x)/2,y=(start.y+end.y)/2,d='';
 let bounds={x:-w/2,y:-h/2,width:w,height:h};

 if(tool.value==='pen'){
  const xs=points.value.map(p=>p.x),ys=points.value.map(p=>p.y);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
  x=(minX+maxX)/2; y=(minY+maxY)/2;
  d=points.value.map((p,i)=>`${i?'L':'M'}${(p.x-x).toFixed(1)} ${(p.y-y).toFixed(1)}`).join(' ')+(closed.value?' Z':'');
  bounds={x:minX-x,y:minY-y,width:Math.max(4,maxX-minX),height:Math.max(4,maxY-minY)};
 }else if(tool.value==='line'){
  const dx=end.x-start.x, dy=end.y-start.y;
  d=`M ${(-dx/2).toFixed(1)} ${(-dy/2).toFixed(1)} L ${(dx/2).toFixed(1)} ${(dy/2).toFixed(1)}`;
  bounds={x:-w/2,y:-h/2,width:w,height:h};
 }else if(tool.value==='ellipse'){
  d=`M ${-w/2} 0 A ${w/2} ${h/2} 0 1 0 ${w/2} 0 A ${w/2} ${h/2} 0 1 0 ${-w/2} 0 Z`;
 }else if(tool.value==='rect'){
  d=`M ${-w/2} ${-h/2} H ${w/2} V ${h/2} H ${-w/2} Z`;
 }else if(tool.value==='diamond'){
  d=`M 0 ${(-h/2).toFixed(1)} L ${(w/2).toFixed(1)} 0 L 0 ${(h/2).toFixed(1)} L ${(-w/2).toFixed(1)} 0 Z`;
 }else if(tool.value==='petal'){
  d=`M 0 ${-h/2} C ${w*.7} ${-h*.15} ${w*.45} ${h*.4} 0 ${h/2} C ${-w*.45} ${h*.4} ${-w*.7} ${-h*.15} 0 ${-h/2} Z`;
 }else if(tool.value==='cloud'){
  // Traditional Chinese Ruyi Cloud motif
  d=`M 0 ${(-h*0.45).toFixed(1)} C ${(w*0.35).toFixed(1)} ${(-h*0.65).toFixed(1)} ${(w*0.55).toFixed(1)} ${(-h*0.25).toFixed(1)} ${(w*0.45).toFixed(1)} ${(h*0.05).toFixed(1)} C ${(w*0.5).toFixed(1)} ${(h*0.35).toFixed(1)} ${(w*0.2).toFixed(1)} ${(h*0.5).toFixed(1)} 0 ${(h*0.35).toFixed(1)} C ${(-w*0.2).toFixed(1)} ${(h*0.5).toFixed(1)} ${(-w*0.5).toFixed(1)} ${(h*0.35).toFixed(1)} ${(-w*0.45).toFixed(1)} ${(h*0.05).toFixed(1)} C ${(-w*0.55).toFixed(1)} ${(-h*0.25).toFixed(1)} ${(-w*0.35).toFixed(1)} ${(-h*0.65).toFixed(1)} 0 ${(-h*0.45).toFixed(1)} Z`;
 }else if(tool.value==='arc'){
  d=`M ${(-w/2).toFixed(1)} ${(h*0.3).toFixed(1)} Q 0 ${(-h/2).toFixed(1)} ${(w/2).toFixed(1)} ${(h*0.3).toFixed(1)}`;
 }else{
  d=`M 0 ${-h/2} C ${w*.7} ${-h*.15} ${w*.45} ${h*.4} 0 ${h/2} C ${-w*.45} ${h*.4} ${-w*.7} ${-h*.15} 0 ${-h/2} Z`;
 }
 return{id:crypto.randomUUID(),d,x,y,rotation:0,scale:1,stroke:stroke.value,fill:filled.value?fill.value:'none',strokeWidth:strokeWidth.value,bounds};
}
function eraseAt(p:{x:number;y:number}){
 const hitIndex=shapes.value.findIndex(s=>{
  const dx=p.x-s.x, dy=p.y-s.y;
  return Math.hypot(dx,dy) <= Math.max(30, s.bounds.width/2, s.bounds.height/2);
 });
 if(hitIndex>=0){
  shapes.value.splice(hitIndex,1);
  selected.value='';
  checkpoint();
 }
}
function startDraw(e:PointerEvent){
 if(e.button!==0||busy.value)return;
 if(tool.value==='eraser'){
  e.preventDefault();
  canvas.value?.setPointerCapture(e.pointerId);
  gesture={type:'draw',start:point(e),pointer:e.pointerId};
  eraseAt(point(e));
  return;
 }
 if(tool.value==='select'){selected.value='';return}
 if(shapes.value.length>=120){error.value='一份作品最多保留120个独立笔画，可先整理图层。';return}
 e.preventDefault();const p=point(e);canvas.value?.setPointerCapture(e.pointerId);
 gesture={type:'draw',start:p,pointer:e.pointerId};points.value=[p];draft.value=makeShape(p,p);error.value='';message.value='';
}
function startMove(e:PointerEvent,s:Shape,angle:number,reflected:boolean){
 if(tool.value==='eraser'){
  e.preventDefault();
  shapes.value=shapes.value.filter(item=>item.id!==s.id);
  selected.value='';
  checkpoint();
  return;
 }
 if(tool.value!=='select'){startDraw(e);return}
 if(e.button!==0||busy.value)return;
 e.preventDefault();selected.value=s.id;canvas.value?.setPointerCapture(e.pointerId);
 const p=sourcePoint(point(e),angle,reflected);
 gesture={type:'move',start:p,original:JSON.parse(JSON.stringify(s)),copyAngle:angle,copyMirror:reflected,pointer:e.pointerId};
}
function move(e:PointerEvent){
 if(!gesture||gesture.pointer!==e.pointerId)return;e.preventDefault();const p=point(e);
 if(tool.value==='eraser'){eraseAt(p);return}
 if(gesture.type==='draw'){if(points.value.length<256&&Math.hypot(p.x-points.value.at(-1)!.x,p.y-points.value.at(-1)!.y)>2)points.value.push(p);draft.value=makeShape(gesture.start,p)}
 else{const s=shapes.value.find(s=>s.id===gesture!.original!.id);if(s){const local=sourcePoint(p,gesture.copyAngle,gesture.copyMirror);s.x=Math.max(-200,Math.min(1200,gesture.original!.x+local.x-gesture.start.x));s.y=Math.max(-200,Math.min(1200,gesture.original!.y+local.y-gesture.start.y))}}
}
function finish(e:PointerEvent){if(!gesture||gesture.pointer!==e.pointerId)return;move(e);if(tool.value!=='eraser'&&gesture.type==='draw'&&draft.value&&Math.max(draft.value.bounds.width,draft.value.bounds.height)>4){shapes.value.push(draft.value);selected.value=draft.value.id;checkpoint()}gesture=null;draft.value=null;points.value=[];if(canvas.value?.hasPointerCapture(e.pointerId))canvas.value.releasePointerCapture(e.pointerId)}
function cancel(){if(gesture?.type==='move'&&gesture.original){const index=shapes.value.findIndex(s=>s.id===gesture!.original!.id);if(index>=0)shapes.value[index]=gesture.original}gesture=null;draft.value=null;points.value=[]}
function remove(){if(!selected.value)return;shapes.value=shapes.value.filter(s=>s.id!==selected.value);selected.value='';checkpoint()}
function duplicate(){if(!current.value||shapes.value.length>=120)return;const s=JSON.parse(JSON.stringify(current.value));s.id=crypto.randomUUID();s.x+=25;s.y+=25;shapes.value.push(s);selected.value=s.id;checkpoint()}
function newCanvas(){restoreWorkspace({shapes:[],symmetry:1,mirror:false,template:'',sourceDesign:'',sourcePattern:''});name.value='';description.value='';checkpoint();message.value='已打开空白画布，仍可撤销找回上一份草稿。'}
function keydown(e:KeyboardEvent){if((e.target as HTMLElement).closest('input,textarea,select'))return;if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();undo(e.shiftKey?1:-1)}else if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();remove()}}
function escape(value:string){return value.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;')}
function svgText(){const paths=copies.value.map(c=>`<g transform="${copyTransform(c.angle,c.reflected)}">${shapes.value.map(s=>`<path d="${escape(s.d)}" transform="${shapeTransform(s)}" fill="${s.fill}" stroke="${s.stroke}" stroke-width="${s.strokeWidth}" stroke-linecap="round" stroke-linejoin="round"/>`).join('')}</g>`).join('');return `<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="120mm" viewBox="0 0 1000 1000"><title>${escape(name.value.trim()||'我的当代纹样')}</title>${template.value}${paths}</svg>`}
function download(blob:Blob,extension:string){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=(name.value.trim()||'我的当代纹样')+'.'+extension;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function exportSvg(){download(new Blob([svgText()],{type:'image/svg+xml;charset=utf-8'}),'svg')}
async function exportPng(){try{const image=new Image(),url=URL.createObjectURL(new Blob([svgText()],{type:'image/svg+xml;charset=utf-8'}));await new Promise<void>((resolve,reject)=>{image.onload=()=>resolve();image.onerror=()=>reject(Error('图片导出失败，请重试'));image.src=url});const surface=document.createElement('canvas');surface.width=surface.height=2000;surface.getContext('2d')!.drawImage(image,0,0,2000,2000);URL.revokeObjectURL(url);const blob=await new Promise<Blob|null>(resolve=>surface.toBlob(resolve,'image/png'));if(blob)download(blob,'png')}catch(e:any){error.value=e.message}}
async function loadSeed(seed:any,isPattern=false){
 busy.value=true;error.value='';try{
  if(isPattern&&seed.editor_state?.version===1&&Array.isArray(seed.editor_state.shapes)){restoreWorkspace(seed.editor_state);sourcePattern.value=seed.id;name.value=(seed.name+' · 新作').slice(0,60);description.value=seed.description||'';checkpoint();message.value='已载入可编辑笔画。发布时会保留与原作的关系。';return}
  let svg=seed.svg||seed.images?.[0]?.svg;if(!svg)throw Error('这份作品尚无可读取的矢量底稿');if(!svg.trim().startsWith('<svg')){const r=await fetch(svg);if(!r.ok)throw Error('底稿读取失败，请稍后重试');svg=await r.text()}
  const doc=new DOMParser().parseFromString(svg,'image/svg+xml');if(doc.querySelector('parsererror')||doc.documentElement.localName!=='svg')throw Error('底稿不是有效的SVG图形');
  const root=doc.documentElement;root.setAttribute('x','0');root.setAttribute('y','0');root.setAttribute('width','1000');root.setAttribute('height','1000');root.querySelectorAll('script,foreignObject,iframe,style,image,use').forEach(n=>n.remove());[root,...Array.from(root.querySelectorAll('*'))].forEach(el=>Array.from(el.attributes).forEach(a=>{if(a.name.toLowerCase().startsWith('on')||a.name==='href'||a.name==='xlink:href'||a.name==='style')el.removeAttribute(a.name)}));
  restoreWorkspace({shapes:[],symmetry:1,mirror:false,template:new XMLSerializer().serializeToString(root),sourceDesign:isPattern?'':seed.id,sourcePattern:isPattern?seed.id:''});name.value=((seed.name||'底稿')+' · 新作').slice(0,60);description.value='';checkpoint();message.value='底稿已载入，新增笔画可独立编辑；原作来源将随新作品保留。';
 }catch(e:any){error.value=e.message}finally{busy.value=false}
}
async function save(){if(!canSave.value)return;busy.value=true;error.value='';try{const body={name:name.value.trim(),description:description.value.trim(),svg:svgText(),source_design_id:sourceDesign.value||undefined,source_pattern_id:sourcePattern.value||undefined,rights_confirmed:true,creation_method:isRemix.value?'remix':'freehand',editor_state:{...workspace(),version:1}};const r=await fetch('/api/community/patterns',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw Error(typeof d.detail==='string'?d.detail:'入库失败，请检查作品名称与图形后重试');savedPattern.value=d;message.value='作品已进入当代创作库，可以继续用于器物设计。';emit('saved',d)}catch(e:any){error.value=e.message}finally{busy.value=false}}
try{const local=JSON.parse(localStorage.getItem('xiyu-original-draft')||'null');if(!props.seedPattern&&!props.seedDesign&&local?.workspace){restoreWorkspace(local.workspace);name.value=local.name||'';description.value=local.description||''}}catch{}
checkpoint();
function saveDraft(){try{const value=JSON.stringify({workspace:workspace(),name:name.value,description:description.value});if(value.length>1_000_000){draftNotice.value='这份草稿较大，请先入库，避免刷新后丢失。';return}localStorage.setItem('xiyu-original-draft',value);draftNotice.value='草稿已保存在本机'}catch{draftNotice.value='本机草稿空间不足，请先入库，避免刷新后丢失。'}}
let draftTimer:ReturnType<typeof setTimeout>;watch([shapes,symmetry,mirror,template,sourceDesign,sourcePattern,name,description],()=>{clearTimeout(draftTimer);draftTimer=setTimeout(saveDraft,400)},{deep:true});
window.addEventListener('pagehide',saveDraft);
watch(()=>props.seedPattern,p=>{if(p)loadSeed(p,true)},{immediate:true});
watch(()=>props.seedDesign,d=>{if(d)loadSeed(d)},{immediate:true});
onBeforeUnmount(()=>{clearTimeout(draftTimer);saveDraft();window.removeEventListener('pagehide',saveDraft)});
</script>

<template>
<main class="original-studio" @keydown="keydown">
 <header class="original-heading"><div><p class="original-kicker">当代共创 / ORIGINAL PATTERN STUDIO</p><h1>这一笔，<em>由你落下。</em></h1><p>从空白画布自由创作，或沿一份有出处的底稿继续生长。作品入库后，可反复用于器物设计。</p></div><button class="original-library-link" @click="emit('navigate','community')">浏览当代创作库 ↗</button></header>
 <div class="original-layout">
  <aside class="original-tools"><section><p class="tool-label">落笔方式</p><div class="original-tool-grid"><button v-for="t in tools" :key="t.id" :class="{active:tool===t.id}" :aria-pressed="tool===t.id" :aria-label="t.name" @click="tool=t.id"><b aria-hidden="true">{{t.icon}}</b><span>{{t.name}}</span></button></div></section><section><p class="tool-label">生长秩序</p><div class="symmetry-options"><button v-for="n in [1,2,4,6,8]" :class="{active:symmetry===n}" @click="symmetry=n;checkpoint()">{{n===1?'单笔':n+'向'}}</button></div><label class="original-check"><input type="checkbox" v-model="mirror" @change="checkpoint()">同时镜像</label><p class="tool-hint">一笔会按所选秩序同步生长，所有副本保留真实矢量轮廓。</p></section><section><p class="tool-label">笔触与填色</p><label class="original-control">线宽 <strong>{{strokeWidth}}</strong><input type="range" min="1" max="28" v-model.number="strokeWidth" aria-label="新笔画线宽"></label><div class="original-colors"><button v-for="c in palette" :style="{background:c}" :class="{chosen:stroke===c}" :aria-label="'笔触颜色 '+c" @click="stroke=c"></button><input type="color" v-model="stroke" aria-label="自定义笔触颜色"></div><label class="original-check"><input type="checkbox" v-model="filled">填充图形 <input v-if="filled" type="color" v-model="fill" aria-label="新图形填充颜色"></label><label v-if="tool==='pen'" class="original-check"><input type="checkbox" v-model="closed">自由笔画闭合</label></section><section class="seed-section"><p class="tool-label">沿着旧作，再画一笔</p><button v-if="seedDesign" class="original-seed-button" :disabled="busy" @click="loadSeed(seedDesign)">以当前器物纹样为底稿 ↗</button><p v-else class="tool-hint">可先在造物中完成一份纹样，再带入这里继续创作。</p><p v-if="template" class="original-seed-note">当前底稿保持原貌，新增笔画可编辑。<button @click="template='';checkpoint()">移除底稿</button></p><button class="original-new" @click="newCanvas">打开空白画布</button></section></aside>
  <section class="original-board-column"><div class="original-board-bar"><div><span class="board-status-dot"></span>{{tool==='select'?'点击图形选取，拖动改变位置':tool==='eraser'?'点击或划过笔画以快速擦除':'按住并拖动，在画布上落笔'}}</div><div><button :disabled="cursor<=0" @click="undo(-1)" aria-label="撤销笔画">↶</button><button :disabled="cursor>=history.length-1" @click="undo(1)" aria-label="重做笔画">↷</button><button :class="{active:showGuides}" @click="showGuides=!showGuides">辅助线</button></div></div><div class="original-drawing-surface"><svg ref="canvas" viewBox="0 0 1000 1000" aria-label="自由纹样创作画布" role="img" @pointerdown="startDraw" @pointermove="move" @pointerup="finish" @pointercancel="cancel"><defs><pattern id="original-dot-grid" width="50" height="50" patternUnits="userSpaceOnUse"><circle cx="0" cy="0" r="1.5" fill="#80998d"/></pattern></defs><rect width="1000" height="1000" fill="#202c26"/><rect v-if="showGuides" width="1000" height="1000" fill="url(#original-dot-grid)" opacity=".55"/><g v-if="showGuides" class="original-guide-lines"><circle cx="500" cy="500" r="350"/><circle cx="500" cy="500" r="200"/><path v-for="c in copies" :d="'M500 500V20'" :transform="copyTransform(c.angle,c.reflected)"/><path d="M475 500H525M500 475V525"/></g><g class="original-template" v-html="template"></g><g v-for="(c,index) in copies" :key="index" :transform="copyTransform(c.angle,c.reflected)"><g v-for="s in shapes" :key="s.id" :transform="shapeTransform(s)" class="original-shape" :class="{selected:selected===s.id&&tool==='select'}" @pointerdown.stop="startMove($event,s,c.angle,c.reflected)"><path :d="s.d" :fill="s.fill" :stroke="s.stroke" :stroke-width="s.strokeWidth" stroke-linecap="round" stroke-linejoin="round"/><rect v-if="selected===s.id&&tool==='select'" :x="s.bounds.x-12" :y="s.bounds.y-12" :width="s.bounds.width+24" :height="s.bounds.height+24" class="original-selection"/></g><path v-if="draft" :d="draft.d" :transform="shapeTransform(draft)" :fill="draft.fill" :stroke="draft.stroke" :stroke-width="draft.strokeWidth" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/></g><text v-if="!hasArt&&!draft" x="500" y="510" text-anchor="middle" class="empty-board-poem">心意为引，落笔成纹。</text></svg></div><div class="original-board-foot"><span>{{shapes.length}} 个独立图形 · {{copies.length}} 重生长</span><span>1000 × 1000 矢量画布</span></div><div class="original-export"><button :disabled="!hasArt" @click="exportSvg">下载 SVG</button><button :disabled="!hasArt" @click="exportPng">下载透明 PNG</button><span>本地导出保留真实矢量与透明背景</span></div>
   <section v-if="current" class="original-selection-controls"><div><p class="tool-label">独立图形编辑</p><span>选取工具可拖动图形；参数调整会同步到所有对称副本。</span></div><label>转角 {{current.rotation}}°<input type="range" min="-180" max="180" step="1" v-model.number="current.rotation" @change="checkpoint()"></label><label>比例 {{current.scale.toFixed(2)}}×<input type="range" min="0.2" max="3" step="0.05" v-model.number="current.scale" @change="checkpoint()"></label><label>线宽 {{current.strokeWidth}}<input type="range" min="1" max="28" v-model.number="current.strokeWidth" @change="checkpoint()"></label><label class="selected-color">线色<input type="color" v-model="current.stroke" @change="checkpoint()"></label><label class="original-check"><input type="checkbox" :checked="current.fill!=='none'" @change="current.fill=($event.target as HTMLInputElement).checked?fill:'none';checkpoint()">填色</label><div class="selected-actions"><button @click="duplicate">复制</button><button @click="remove">删除图形</button></div></section>
  </section>
 </div>
 <p v-if="draftNotice" class="original-draft-notice" role="status">{{draftNotice}}</p><section class="original-publish"><div><p class="original-kicker">一笔成形，反复入器</p><h2>把你的创作，<em>留在纹样库。</em></h2><p>入库作品标注为“当代创作”，可用于后续造物。它与传统档案分开保留，来源关系随作品一起记录。</p><p v-if="isRemix" class="original-lineage">延续来源：{{sourceDesign||sourcePattern}}</p></div><form @submit.prevent="save"><label>作品名称<input v-model="name" minlength="2" maxlength="60" placeholder="给你的纹样起一个名字" required></label><label>创作说明<textarea v-model="description" rows="3" maxlength="1200" placeholder="记录灵感、构图想法或希望表达的当代寓意"></textarea></label><label class="original-rights"><input type="checkbox" v-model="rights">我确认拥有新增内容的使用权，并同意保留所用底稿的来源记录。</label><button class="original-publish-button" :disabled="!canSave">{{busy?'正在保存…':'入库为当代创作 →'}}</button><p v-if="savedPattern" class="original-saved">已入库 · {{savedPattern.name}} <button type="button" @click="emit('navigate','community')">到创作库查看 ↗</button></p></form></section>
 <p v-if="message" class="original-message" role="status">{{message}}</p><p v-if="error" class="original-error" role="alert">{{error}}</p>
</main>
</template>

<style scoped>
.original-studio{max-width:1680px;margin:0 auto;padding:38px 4% 70px;color:var(--text-primary)}.original-heading{display:flex;justify-content:space-between;align-items:center;gap:30px;margin-bottom:30px}.original-kicker{color:var(--accent-gold);font:11px/1.8 sans-serif;letter-spacing:2px;margin:0 0 10px}.original-heading h1{font:38px/1.5 var(--serif);margin:10px 0}.original-studio h1 em,.original-studio h2 em{font-style:normal;color:var(--accent-gold)}.original-heading>div>p:last-child{font-size:14px;color:var(--text-secondary);line-height:1.9;max-width:740px}.original-library-link{color:var(--accent-gold);background:none;border:0;border-bottom:1px solid var(--border-default);font-size:13px;white-space:nowrap;padding:12px 0}.original-layout{display:grid;grid-template-columns:215px minmax(0,1fr);gap:26px}.original-tools{background:var(--bg-elevated);border:1px solid var(--border-default);padding:21px 18px;align-self:start}.original-tools section+section{border-top:1px solid var(--border-default);margin-top:22px;padding-top:20px}.tool-label{font-size:12px;letter-spacing:1px;color:var(--accent-gold);margin:0 0 14px}.original-tool-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:7px}.original-tool-grid button{display:grid;justify-items:center;gap:4px;background:var(--bg-elevated);border:1px solid var(--border-default);padding:10px 5px;color:var(--text-secondary)}.original-tool-grid b{font:26px/1.3 Georgia,serif}.original-tool-grid span{font-size:11px}.original-tool-grid button.active,.symmetry-options button.active{color:var(--accent-gold-bright);background:var(--bg-active);border-color:var(--accent-gold)}.symmetry-options{display:flex;flex-wrap:wrap;gap:5px}.symmetry-options button{padding:7px 9px;font-size:12px;color:var(--text-secondary);background:var(--bg-elevated);border:1px solid var(--border-default)}.original-check{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text-secondary);margin:14px 0 0}.original-check input[type=checkbox]{accent-color:var(--accent-gold);width:15px;height:15px}.original-check input[type=color]{width:30px;height:25px;padding:0;border:0}.tool-hint{font-size:11px;line-height:1.9;color:var(--text-secondary);margin:12px 0 0}.original-control{display:flex;align-items:center;flex-wrap:wrap;justify-content:space-between;font-size:12px;color:var(--text-secondary)}.original-control input{width:100%;margin:12px 0;accent-color:var(--accent-gold)}.original-control strong{font:17px Georgia;color:var(--accent-gold)}.original-colors{display:flex;gap:8px;flex-wrap:wrap;margin:7px 0}.original-colors>button{height:22px;width:22px;border:2px solid transparent;padding:0;border-radius:50%}.original-colors>button.chosen{box-shadow:0 0 0 2px #F4F6F8,0 0 0 3px var(--accent-gold)}.original-colors>input{width:24px;height:24px;border:1px solid var(--border-default);padding:0}.original-seed-button,.original-new{display:block;width:100%;padding:11px 8px;color:var(--text-secondary);background:var(--bg-elevated);border:1px solid var(--border-default);font-size:11px;line-height:1.8}.original-new{margin-top:12px;background:transparent;color:var(--text-secondary)}.original-seed-note{font-size:11px;line-height:1.8;color:var(--text-secondary)}.original-seed-note button{font-size:11px;background:none;color:var(--accent-gold);border:0;padding:4px 0}.original-board-column{min-width:0}.original-board-bar{display:flex;justify-content:space-between;align-items:center;gap:15px;background:var(--bg-elevated);border:1px solid var(--border-default);border-bottom:0;padding:12px 18px;color:var(--text-secondary);font-size:12px}.original-board-bar>div{display:flex;gap:8px;align-items:center}.original-board-bar button{padding:6px 9px;font-size:12px;border:1px solid var(--border-default);background:none;color:var(--text-secondary)}.original-board-bar button.active{border-color:var(--accent-gold);color:var(--accent-gold-bright)}.board-status-dot{width:5px;height:5px;border-radius:50%;background:var(--accent-gold);box-shadow:0 0 10px color-mix(in srgb, var(--accent-gold) 33.3%, transparent);margin-right:4px}.original-drawing-surface{border:1px solid var(--border-default);background:var(--specimen-dark);display:flex;justify-content:center;max-height:690px;overflow:hidden}.original-drawing-surface>svg{width:100%;max-height:690px;display:block;aspect-ratio:1;touch-action:none;user-select:none;cursor:crosshair}.original-guide-lines{fill:none;stroke:var(--text-secondary);stroke-width:1;stroke-dasharray:3 8;opacity:.2;pointer-events:none}.original-template{pointer-events:none}.original-shape{cursor:move}.original-selection{fill:none;stroke:var(--text-secondary);stroke-width:2;stroke-dasharray:8 5;pointer-events:none}.empty-board-poem{font:32px var(--serif);letter-spacing:7px;fill:var(--text-secondary);opacity:.5;pointer-events:none}.original-board-foot{display:flex;justify-content:space-between;font-size:11px;color:var(--text-secondary);gap:12px;padding:12px 4px}.original-export{display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:10px 0 20px}.original-export button{padding:10px 16px;font-size:12px;color:var(--text-secondary);background:var(--bg-elevated);border:1px solid var(--border-default)}.original-export>span{color:var(--text-secondary);font-size:11px;margin-left:auto}.original-selection-controls{border:1px solid var(--border-default);padding:18px 20px;background:var(--bg-elevated);display:grid;grid-template-columns:repeat(3,1fr);gap:14px 22px}.original-selection-controls>div:first-child{grid-column:1/-1}.original-selection-controls .tool-label{margin:0 0 4px}.original-selection-controls>div>span{font-size:11px;color:var(--text-secondary)}.original-selection-controls>label{font-size:12px;color:var(--text-secondary)}.original-selection-controls input[type=range]{display:block;width:100%;margin-top:12px;accent-color:var(--accent-gold)}.original-selection-controls .selected-color{display:flex;align-items:center;gap:15px}.selected-color input{height:26px;width:40px;padding:1px}.original-selection-controls .original-check{margin:0}.selected-actions{display:flex;gap:10px;justify-content:end}.selected-actions button{padding:9px 13px;font-size:12px;background:var(--bg-elevated);border:1px solid var(--border-default);color:var(--text-secondary)}.original-publish{display:grid;grid-template-columns:1fr 1.1fr;gap:8%;margin-top:45px;padding:35px;background:var(--bg-elevated);border:1px solid var(--border-default)}.original-publish h2{font:29px/1.7 var(--serif);margin:12px 0}.original-publish p{font-size:13px;line-height:1.9;color:var(--text-secondary)}.original-publish .original-lineage{color:var(--accent-gold);font-size:11px;overflow-wrap:anywhere}.original-publish form>label:not(.original-rights){display:block;font-size:12px;color:var(--text-secondary);margin-bottom:17px}.original-publish input:not([type=checkbox]),.original-publish textarea{display:block;width:100%;box-sizing:border-box;margin-top:8px;background:var(--bg-elevated);border:1px solid var(--border-default);color:var(--text-primary);padding:12px;font-size:13px}.original-rights{display:flex;align-items:start;gap:9px;font-size:12px;line-height:1.9;color:var(--text-secondary)}.original-rights input{accent-color:var(--accent-gold);margin-top:5px;flex-shrink:0}.original-publish .original-publish-button{display:block;margin-top:20px;padding:14px 20px;width:100%;background:var(--accent-gold);border:1px solid var(--accent-gold);color:var(--text-primary);font-size:14px;font-weight:600}.original-publish .original-publish-button:disabled{background:var(--bg-elevated);color:var(--text-secondary);border-color:var(--border-default)}.original-publish .original-saved{color:var(--text-secondary)}.original-saved button{background:none;border:0;color:var(--accent-gold);padding:0 5px;font-size:12px}.original-message,.original-error{padding:15px 20px;margin-top:20px;color:var(--text-secondary);background:var(--bg-elevated);border:1px solid var(--border-default);font-size:13px;line-height:1.8}.original-error{background:var(--bg-panel);border-color:var(--border-default);color:var(--text-secondary)}.original-studio button:focus-visible,.original-studio input:focus-visible,.original-studio textarea:focus-visible{outline:2px solid var(--accent-gold);outline-offset:4px}@media(max-width:1000px){.original-layout{grid-template-columns:180px minmax(0,1fr);gap:16px}.original-tools{padding:18px 12px}.original-heading h1{font-size:33px}.original-selection-controls{grid-template-columns:1fr 1fr}.selected-actions{justify-content:start}.original-publish{padding:25px;gap:6%}}@media(max-width:700px){.original-studio{padding:26px 20px 45px}.original-heading{display:block;margin-bottom:22px}.original-heading h1{font-size:30px}.original-heading>div>p:last-child{font-size:13px}.original-library-link{padding-top:0}.original-layout{display:flex;flex-direction:column;gap:18px}.original-tools{width:100%;box-sizing:border-box;display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:16px}.original-tools section+section{margin:0;padding:0;border:0}.original-tools .seed-section{border-top:1px solid var(--border-default);padding-top:16px}.original-tool-grid{grid-template-columns:repeat(3,1fr);gap:5px}.original-tool-grid button{padding:7px 2px}.original-tool-grid b{font-size:21px}.original-tool-grid span{font-size:10px}.tool-label{font-size:11px;margin-bottom:12px}.symmetry-options button{font-size:10px;padding:7px}.tool-hint{font-size:10px}.original-check{font-size:11px;gap:6px}.original-board-bar{padding:10px;font-size:10px}.original-board-bar>div{gap:5px}.original-board-bar button{font-size:10px;padding:6px}.original-board-bar>div:first-child{max-width:150px;line-height:1.7}.original-board-foot{font-size:10px}.original-export>span{margin-left:0;width:100%;font-size:10px}.original-selection-controls{padding:16px 12px;gap:15px}.original-selection-controls>label{font-size:11px}.original-publish{display:block;margin-top:28px;padding:22px}.original-publish h2{font-size:26px}.original-publish form{margin-top:25px}.original-publish p{font-size:12px}.original-rights{font-size:11px}.original-seed-button,.original-new{font-size:10px}.empty-board-poem{font-size:32px}}
.original-draft-notice{color:var(--text-secondary);font-size:12px;line-height:1.9;margin:18px 0}
</style>
