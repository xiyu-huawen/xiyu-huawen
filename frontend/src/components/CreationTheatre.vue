<script setup lang="ts">
import MaterialPlanet from './MaterialPlanet.vue';
import DesignAdvisor from './DesignAdvisor.vue';
import WorkshopLens from './WorkshopLens.vue';
import Print3DModal from './Print3DModal.vue';
import {ref,computed,watch,onBeforeUnmount} from 'vue';
import VesselScene from './VesselScene.vue';
import GeneAtlas from './GeneAtlas.vue';
import GeneComposer from './GeneComposer.vue';
import DesignNarrative from './DesignNarrative.vue';

function readLocal(key:string){try{return localStorage.getItem(key)}catch{return null}}
function writeLocal(key:string,value:string){try{localStorage.setItem(key,value);return true}catch{try{if(key==='xiyu-theatre'||key==='xiyu-session-state')localStorage.removeItem('xiyu-session-state');localStorage.setItem(key,value);return true}catch{return false}}}
function compactSession(state:any,limit:number,utf8=false){const out={...state,history:[...state.history],cursor:state.cursor};let encoded=JSON.stringify(out);while((utf8?new TextEncoder().encode(encoded).length:encoded.length)>limit&&out.history.length>1){if(out.cursor>0){out.history.shift();out.cursor--}else out.history.pop();encoded=JSON.stringify(out)}return encoded}
const emptySvg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"></svg>';
function showSource(){document.getElementById('source-atlas')?.scrollIntoView({behavior:'smooth'})}

const vesselNames:Record<string,string>={pot:'紫砂壶',tray:'茶承',bookmark:'书签',box:'圆形首饰盒',vase:'花器',pendant:'挂坠',lid:'茶罐盖',cup:'茶杯',penholder:'笔筒',incense:'香插',jar:'茶叶罐',plaque:'案头摆牌'};

const vesselCatalog=[
 {id:'pot',name:'紫砂壶',group:'茶席',icon:'M18 20 Q12 39 31 40 Q49 39 43 20 Z M18 20 Q31 14 43 20 M30 14 V10 M44 23 Q59 12 55 29 Q51 34 45 33 M17 26 L6 18 L12 33 L18 34'},
 {id:'tray',name:'茶承',group:'茶席',icon:'M8 21 Q32 42 56 21 M8 21 Q32 31 56 21 M10 21 Q32 9 54 21'},
 {id:'cup',name:'茶杯',group:'茶席',icon:'M15 16 Q32 10 49 16 L44 37 Q32 44 20 37 Z M15 16 Q32 23 49 16 M21 38 H43'},
 {id:'jar',name:'茶叶罐',group:'茶席',icon:'M19 17 Q13 22 14 38 Q32 47 50 38 Q51 22 45 17 Z M18 15 Q32 7 46 15 M22 12 V8 H42 V12'},
 {id:'lid',name:'茶罐盖',group:'茶席',icon:'M9 27 Q32 10 55 27 Q32 39 9 27 Z M13 25 Q32 18 51 25 M28 18 V12 H36 V18'},
 {id:'vase',name:'花器',group:'文房',icon:'M25 8 H39 L36 18 Q51 35 44 42 Q32 47 20 42 Q13 35 28 18 Z M25 8 Q32 12 39 8'},
 {id:'penholder',name:'笔筒',group:'文房',icon:'M19 15 Q32 9 45 15 V40 Q32 47 19 40 Z M19 15 Q32 23 45 15 M25 15 L22 5 M32 15 V3 M38 15 L43 4'},
 {id:'incense',name:'香插',group:'文房',icon:'M8 35 Q32 24 56 35 Q32 48 8 35 Z M29 32 L39 5 M36 4 Q31 0 37 -3'},
 {id:'plaque',name:'案头摆牌',group:'文房',icon:'M19 37 V13 Q32 -1 45 13 V37 Z M12 38 H52 V44 H12 Z M25 20 H39 M25 27 H39'},
 {id:'bookmark',name:'书签',group:'随身',icon:'M25 6 H39 V44 L32 39 L25 44 Z M32 7 V2 M30 15 H34'},
 {id:'pendant',name:'挂坠',group:'随身',icon:'M32 11 C10 11 10 44 32 44 C54 44 54 11 32 11 Z M28 10 V4 H36 V10 M23 27 L32 18 L41 27 L32 36 Z'},
 {id:'box',name:'首饰盒',group:'随身',icon:'M12 20 Q32 7 52 20 V34 Q32 49 12 34 Z M12 20 Q32 34 52 20 M14 26 Q32 38 50 26'}
];

const vesselDimensions:Record<string,number[]>={pot:[90,75],tray:[120,120],bookmark:[30,140],box:[80,80],vase:[70,100],pendant:[35,35],lid:[70,70],cup:[70,55],penholder:[75,90],incense:[80,80],jar:[80,90],plaque:[100,130]};

const initialVessel = readLocal('xiyu-user-vessel') || 'pot';
const vessel = ref(initialVessel);
const shape = ref('standard');
const shapeOpen = ref(false);
const show3DPrint = ref(false);
const shapeLabels:Record<string,string>={standard:'经典',leaf:'树叶',arch:'拱顶',slender:'修长',round:'宽圆',faceted:'六方',fluted:'棱纹',waist:'束腰'};

const currentShapeOptions=computed(()=>{
 if(vessel.value==='bookmark'){
  return {standard:'直边书签',leaf:'叶形书签',arch:'拱顶书签',slender:'细长书签',round:'宽幅书签'};
 }
 return {standard:'经典器型',slender:'修长器型',round:'宽圆器型',faceted:'六方器型',fluted:'棱纹器型',waist:'束腰器型'};
});

function setShape(key:string){
 shape.value=key;
 shapeOpen.value=false;
 if(selected.value){
  selected.value.recipe.vessel_shape=key;
  update();
 }
}

async function changeVessel(id:string){
 if(busy.value)return;
 vessel.value=id;
 writeLocal('xiyu-user-vessel',id);
 shape.value='standard';
 flat.value=false;
 const [w,h]=vesselDimensions[id]||[90,75];
 if(selected.value){
  selected.value.recipe.vessel=id;
  selected.value.recipe.vessel_shape='standard';
  selected.value.recipe.width_mm=w;
  selected.value.recipe.height_mm=h;
  if(stage.value>0){
   await update();
   candidates.value=[];
   if(stage.value===2)await recoverDirections();
  }
 }
}

const sampleQuantity=ref(1),sampleNotes=ref(''),sampleContact=ref(''),sampleRequest=ref<any>(null);
async function submitSample(){await act(async()=>{if(!await commit())return;sampleRequest.value=await api('/manufacturing/requests',{design_id:selected.value.id,quantity:sampleQuantity.value,notes:sampleNotes.value,contact:sampleContact.value})})}

const mood=ref('端正'),note=ref(''),blessingInscription=ref('松鹤延年锡光暖，岁华常青福泽长。'),renderScene=ref('茶席'),referenceShot=ref(''),sliderPos=ref(55);
const drawing=ref(false),stroke=ref<number[][]>([]);const formation=ref(1);

function draw(event:PointerEvent){
 if(!drawing.value)return;
 const rect=(event.currentTarget as SVGElement).getBoundingClientRect();
 const point=[Math.max(0,Math.min(1000,(event.clientX-rect.left)/rect.width*1000)),Math.max(0,Math.min(1000,(event.clientY-rect.top)/rect.height*1000))];
 if(event.type==='pointerdown'){stroke.value=[point];(event.currentTarget as SVGElement).setPointerCapture(event.pointerId)}
 else if(event.buttons&&stroke.value.length<128)stroke.value.push(point);
 if(event.type==='pointerup'&&stroke.value.length>=2){selected.value.recipe.trajectory=stroke.value;selected.value.recipe.template='trail';drawing.value=false;update()}
}

const emit=defineEmits(['navigate','pattern','read']);
const stage=ref(0),wish=ref('长寿百岁'),recipient=ref('长辈'),busy=ref(false),error=ref('');
const candidates=ref<any[]>([]),selected=ref<any>(null),source=ref<any>(null),history=ref<any[]>([]),cursor=ref(-1);
const advanced=ref(false),flat=ref(false),compare=ref(false),job=ref<any>(null);
const vesselScene=ref<any>(null);
const advisor=ref(false);

const stages=['设计需求','选择纹样','方案比较','编辑设计','预览与导出'];
const wishes=['长寿百岁','八方安宁','莲心清正'];
const wishDetails=[
 {key:'长寿百岁',glyph:'长',title:'长寿百岁',meaning:'松鹤长青 · 寿考康宁',code:'PAT-057'},
 {key:'八方安宁',glyph:'八',title:'八方安宁',meaning:'礼序周正 · 四方纳吉',code:'PAT-005'},
 {key:'莲心清正',glyph:'莲',title:'莲心清正',meaning:'清雅高洁 · 和合如意',code:'PAT-001'}
];
const recipients=['长辈','友人','伴侣','恩师','自己'];

watch(wish, w => {
 if(w==='长寿百岁') blessingInscription.value='松鹤延年锡光暖，岁华常青福泽长。';
 else if(w==='莲心清正') blessingInscription.value='四叶莲心映清茗，一窗雅序寄知音。';
 else blessingInscription.value='八方锦绣归安宁，一器华纹载乾坤。';
},{immediate:true});

const aiReasoning = computed(()=>{
 const vName = vesselNames[vessel.value] || '器物';
 const [w, h] = vesselDimensions[vessel.value] || [90, 75];
 const isLongevity = wish.value === '长寿百岁';
 const isPurity = wish.value === '莲心清正';
 const patternName = isLongevity ? '仙鹤延年寿字纹 (PAT-057)' : (isPurity ? '客家漏石窗四叶莲心纹 (PAT-001)' : '壮锦八角星纹 (PAT-005)');
 const motifGene = isLongevity ? 'M-HW-135 仙鹤整体' : (isPurity ? 'M-SY-006 四叶莲心' : 'M-BW-020 八角框');
 return {
  target: `为「${recipient.value}」提取东方礼意「${wish.value}」`,
  vesselSpec: `${vName}（${w}×${h}mm）`,
  recipient: recipient.value,
  wish: wish.value,
  vesselName: vName,
  spec: `${w}×${h}mm`,
  pattern: patternName,
  gene: motifGene,
  curvature: ['pot','cup','jar','vase'].includes(vessel.value) ? '三维微曲面 R=45mm（法线贴合解算）' : '平整微弧面 R=180mm（平展冷锻）',
  confidence: '98.8%',
  inscription: blessingInscription.value,
  dfmScore: 'A级认证 · 0.8mm冷锻浅浮雕容差'
 };
});

async function applyMaterial(g:any){if(!selected.value||busy.value)return;const role=selected.value.recipe.anchor?.role==='accent'?'ring':'accent';const layers=(selected.value.recipe.layers||[]).filter((x:any)=>x.role!==role);layers.push({...g,role});await update(layers)}
function dropMaterial(e:DragEvent){try{const g=JSON.parse(e.dataTransfer?.getData('application/x-xiyu-gene')||'');if(typeof g.pattern_id==='string'&&typeof g.code==='string')applyMaterial(g)}catch{}}

async function acceptRecommendation(r:any){
 wish.value=r.wish;
 recipient.value=r.recipient;
 if(r.vessel) vessel.value=r.vessel;
 writeLocal('xiyu-user-vessel',vessel.value);
 shape.value=r.shape||'standard';
 note.value=r.summary;
 if(r.blessing_inscription)blessingInscription.value=r.blessing_inscription;
 await act(async()=>{
  const d=await api('/creation/directions',{wish:r.wish,vessel:vessel.value,recipient:r.recipient,personal_note:r.summary,pattern_id:r.pattern_id});
  candidates.value=d.directions;
  source.value=d.source;
  d.directions[0].recipe.vessel_shape=shape.value;
  select(d.directions[0]);
  stage.value=3;
  advisor.value=false;
 });
}

const workspace=ref('preview');
async function api(url:string,body?:any){const r=await fetch('/api'+url,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{});const d=await r.json();if(!r.ok)throw Error(d.detail||'请求失败');return d}
let active=true,pendingActions=0,previewRequest=0;
async function act(fn:()=>Promise<any>){pendingActions++;busy.value=true;error.value='';try{await fn()}catch(e:any){if(active)error.value=e.message}finally{pendingActions--;busy.value=pendingActions>0}}

async function begin(){
 if(!wishes.includes(wish.value))wish.value=wishes[0];
 await act(async()=>{
  const d=await api('/creation/directions',{wish:wish.value,vessel:vessel.value,recipient:recipient.value,mood:mood.value,personal_note:note.value});
  if(!active)return;
  candidates.value=d.directions;
  source.value=d.source;
  stage.value=1;
  select(d.directions[0]);
 });
}

function select(d:any,addHistory=true){
 selected.value=d;
 shape.value=d.recipe.vessel_shape||'standard';
 if(vessel.value && d.recipe.vessel!==vessel.value){
  d.recipe.vessel=vessel.value;
  const [w,h]=vesselDimensions[vessel.value]||[90,75];
  d.recipe.width_mm=w;
  d.recipe.height_mm=h;
 } else {
  vessel.value=d.recipe.vessel||vessel.value;
 }
 writeLocal('xiyu-user-vessel',vessel.value);
 if(addHistory){
  history.value=history.value.slice(0,cursor.value+1);
  history.value.push(JSON.parse(JSON.stringify(d)));
  if(history.value.length>20)history.value.shift();
  cursor.value=history.value.length-1;
 }else if(cursor.value>=0)history.value[cursor.value]=JSON.parse(JSON.stringify(d));
 writeLocal('xiyu-theatre',JSON.stringify(d));
 if(d.preview_detail==='draft'){
  const draftId=d.id;
  act(async()=>{
   const full=await api('/creation/preview',JSON.parse(JSON.stringify(d.recipe)));
   if(!active||selected.value?.id!==draftId)return;
   full.direction=d.direction;full.preview_detail='full';
   const index=candidates.value.findIndex(x=>x.id===draftId);
   if(index>=0)candidates.value[index]=full;
   select(full,false);
  });
 }
}

function undo(delta:number){
 if(busy.value)return;
 cursor.value=Math.max(0,Math.min(history.value.length-1,cursor.value+delta));
 selected.value=JSON.parse(JSON.stringify(history.value[cursor.value]));
 if(vessel.value && selected.value.recipe.vessel!==vessel.value){
  selected.value.recipe.vessel=vessel.value;
 } else {
  vessel.value=selected.value.recipe.vessel||vessel.value;
 }
 writeLocal('xiyu-theatre',JSON.stringify(selected.value));
 if(stage.value===4&&selected.value.preview_only)act(()=>commit());
}

async function update(layers?:any[]){
 if(!selected.value)return;
 const request=++previewRequest;
 const direction=selected.value.direction;
 const r=JSON.parse(JSON.stringify({...selected.value.recipe,vessel:vessel.value,auto_match:false,parent_design_id:selected.value.id,direction}));
 if(layers)r.layers=layers;
 await act(async()=>{
  const d=await api('/creation/preview',r);
  if(!active||request!==previewRequest)return;
  d.direction=direction;
  select(d);
  if(stage.value===4)await commit();
 });
}

async function commit(){
 const original=selected.value;if(!original)return false;if(!original.preview_only)return true;
 const id=original.id,d=await api('/creation/commit',JSON.parse(JSON.stringify(original.recipe)));
 if(!active||selected.value?.id!==id)return false;
 d.direction=original.direction;selected.value=d;
 if(cursor.value>=0)history.value[cursor.value]=JSON.parse(JSON.stringify(d));
 writeLocal('xiyu-theatre',JSON.stringify(d));return true;
}

async function render(){
 await act(async()=>{
  if(!await commit())return;
  const canvas=document.querySelector<HTMLCanvasElement>('.creation-stage canvas');
  if(!canvas)throw Error('请先切换到器物视图');
  const captured=await vesselScene.value.capture();
  referenceShot.value=captured;
  job.value=await api('/creation/render',{design_id:selected.value.id,image:captured,scene:renderScene.value});
  if(job.value.status==='unconfigured')job.value={status:'unavailable',message:'已为您保留 3D 数字孪生快照；配置 JIMENG_SESSION_ID 或 IMAGE_API_KEY 后即可开启即梦 4.5 实境摄影棚。'};
  if(job.value.id){
   const jid=job.value.id;
   const poll=async()=>{
    const state=await api('/creation/renders/'+jid);job.value=state;
    if(state.status==='processing')setTimeout(()=>poll().catch(()=>{}),2500);
   };
   setTimeout(()=>poll().catch(()=>{}),2500);
  }
 });
}

async function exportCertificate(){
 if(!selected.value)return;
 const canvas=document.createElement('canvas');canvas.width=900;canvas.height=1260;
 const ctx=canvas.getContext('2d')!;
 const grad=ctx.createLinearGradient(0,0,900,1260);
 grad.addColorStop(0,'#0d1513');grad.addColorStop(0.55,'#15221f');grad.addColorStop(1,'#0b1110');
 ctx.fillStyle=grad;ctx.fillRect(0,0,900,1260);
 ctx.strokeStyle='#c8a464';ctx.lineWidth=3;ctx.strokeRect(36,36,828,1188);
 ctx.strokeStyle='rgba(200,164,100,0.35)';ctx.lineWidth=1;ctx.strokeRect(48,48,804,1164);
 ctx.fillStyle='#c8a464';ctx.font='600 18px sans-serif';ctx.fillText('XIYU HUAWEN · 锡语华纹非遗数字造物溯源鉴定卡',78,102);
 ctx.fillStyle='#f3ece0';ctx.font='bold 42px Georgia, serif';ctx.fillText(`${selected.value.name} · ${vesselNames[vessel.value]||'锡镶器物'}`,78,162);
 ctx.fillStyle='#9fcbb9';ctx.font='18px monospace';ctx.fillText(`档案编号: ${selected.value.id}   |   母本: ${selected.value.pattern}   |   规格: ${selected.value.recipe.width_mm}×${selected.value.recipe.height_mm}mm`,78,202);
 try{
  const shot=job.value?.url || (vesselScene.value?await vesselScene.value.capture():'');
  if(shot){
   const img=new Image();img.crossOrigin='anonymous';
   await new Promise<void>(res=>{img.onload=()=>res();img.onerror=()=>res();img.src=shot});
   ctx.fillStyle='#090e0d';ctx.fillRect(78,236,744,540);
   ctx.drawImage(img,150,246,600,520);
   ctx.strokeStyle='rgba(200,164,100,0.4)';ctx.strokeRect(78,236,744,540);
  }
 }catch{}
 ctx.fillStyle='rgba(200,164,100,0.12)';ctx.fillRect(78,806,744,120);
 ctx.strokeStyle='#c8a464';ctx.strokeRect(78,806,744,120);
 ctx.fillStyle='#c8a464';ctx.font='16px sans-serif';ctx.fillText('✦ DOUBAO-SEED 定制器物铭文 · 一器一祝福',102,842);
 ctx.fillStyle='#f7ebd2';ctx.font='28px Georgia, serif';ctx.fillText(`「${blessingInscription.value}」`,102,892);
 ctx.fillStyle='#c6d6cc';ctx.font='18px sans-serif';
 const genesText='调用基因: '+(selected.value.genes?.map((g:any)=>`${g.code}(${g.name})`).join(' · ')||'M/C/S/P 标准基因');
 ctx.fillText(genesText.slice(0,52),78,978);
 ctx.fillText(`工艺认证: 威海锡镶 DFM A级认证 · 0.8mm 锻打浅浮雕 · 1:1 R2010 DXF 已核验`,78,1018);
 ctx.fillStyle='#8aa399';ctx.font='15px sans-serif';
 ctx.fillText('产学研协同：威海锡语华纹文化科技有限公司 × 威海金镶玉工艺品有限公司（省级非遗传承人李江玉指导）',78,1165);
 const a=document.createElement('a');a.href=canvas.toDataURL('image/png');a.download=`${selected.value.id}-溯源鉴定卡.png`;a.click();
}

async function save(){if(busy.value||selected.value?.favorite)return;await act(async()=>{if(!await commit())return;const r=await fetch('/api/designs/'+selected.value.id+'/favorite',{method:'PUT'});if(!r.ok)throw Error('保存失败');const saved=await r.json();if(!active)return;selected.value=saved;if(cursor.value>=0)history.value[cursor.value]=JSON.parse(JSON.stringify(selected.value));writeLocal('xiyu-theatre',JSON.stringify(selected.value))})}
function useGene(g:any){if(!g.assets?.some((a:any)=>a.svg)){error.value='这枚图元暂不可用于矢量创作';return}const role=g.name.includes('框')?'frame':'center';const layers=selected.value.genes.filter((x:any)=>x.role!==role).map((x:any)=>({pattern_id:x.pattern,code:x.code,role:x.role}));layers.push({pattern_id:source.value.id,code:g.code,role});update(layers)}

watch(stage,s=>{
 if(s===0&&!wishes.includes(wish.value))wish.value=wishes[0];
 if(s===1&&!source.value)recoverSource();
 if(s===2&&!candidates.value.length)recoverDirections();
 if(s===4){
  act(()=>commit());
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
   formation.value=0;const start=performance.now();
   const tick=(now:number)=>{if(stage.value!==4)return;formation.value=Math.min(1,(now-start)/1400);if(formation.value<1)requestAnimationFrame(tick)};
   requestAnimationFrame(tick);
  }
 }
});

async function recoverSource(){if(!selected.value||source.value)return;try{source.value=await api('/patterns/'+selected.value.pattern)}catch(e:any){error.value=e.message}}
let recoveringDirections=false;
async function recoverDirections(){
 if(recoveringDirections||candidates.value.length)return;
 recoveringDirections=true;
 try{
  const sourceContext=!wishes.includes(wish.value)&&selected.value?{pattern_id:selected.value.pattern,gene_code:selected.value.recipe.anchor?.pattern_id===selected.value.pattern?selected.value.recipe.anchor.code:selected.value.genes.find((g:any)=>g.pattern===selected.value.pattern)?.code}:{};
  const d=await api('/creation/directions',{wish:wish.value,vessel:vessel.value,recipient:recipient.value,mood:mood.value,personal_note:note.value,...sourceContext});
  candidates.value=d.directions;
  if(!source.value)source.value=d.source;
 }catch(e:any){error.value=e.message}
 finally{recoveringDirections=false}
}

const sessionId=readLocal('xiyu-session-id')||crypto.randomUUID();writeLocal('xiyu-session-id',sessionId);let saveTimer:ReturnType<typeof setTimeout>;
watch([history,cursor,stage,wish,recipient,vessel,mood,note],()=>{
 clearTimeout(saveTimer);
 saveTimer=setTimeout(()=>{
  const state={history:history.value.slice(-20),cursor:cursor.value,stage:stage.value,wish:wish.value,recipient:recipient.value,vessel:vessel.value,mood:mood.value,note:note.value};
  const local=compactSession(state,1_050_000);
  if(!writeLocal('xiyu-session-state',local))writeLocal('xiyu-session-state',compactSession(state,300_000));
  const server=compactSession(state,6_000_000,true);
  fetch('/api/creation/sessions/'+sessionId,{method:'PUT',headers:{'Content-Type':'application/json'},body:'{"state":'+server+'}'}).catch(()=>{})
 },600)
},{deep:true});

const recipe=computed(()=>selected.value?.recipe);
const restored=readLocal('xiyu-theatre');
if(restored){
 try{
  const d=JSON.parse(restored);
  select(d);
  stage.value=3;
  const userSavedVessel=readLocal('xiyu-user-vessel');
  if(userSavedVessel&&vesselCatalog.some(v=>v.id===userSavedVessel)){
   vessel.value=userSavedVessel;
   d.recipe.vessel=userSavedVessel;
  }
  const raw=readLocal('xiyu-session-state');
  if(raw){
   const st=JSON.parse(raw);
   if(st.history?.length){
    history.value=st.history;
    cursor.value=Math.min(st.cursor,st.history.length-1);
    selected.value=st.history[cursor.value];
    wish.value=st.wish;
    recipient.value=st.recipient;
    if(!userSavedVessel) vessel.value=st.vessel;
    stage.value=st.stage;
    candidates.value=[];
    source.value=null;
    mood.value=st.mood||selected.value.recipe.mood||'端正';
    note.value=st.note||selected.value.recipe.personal_note||'';
   }
  }
 }catch{}
}

if(stage.value===0&&!wishes.includes(wish.value))wish.value=wishes[0];
if(selected.value){
 mood.value=selected.value.recipe.mood||'端正';
 note.value=selected.value.recipe.personal_note||'';
 if(stage.value===2&&!candidates.value.length)recoverDirections();
 if(stage.value===1&&!source.value)recoverSource();
}
onBeforeUnmount(()=>{active=false;previewRequest++;clearTimeout(saveTimer)});
</script>

<template>
<main class="theatre">
 <!-- Stage Navigation Bar -->
 <div class="theatre-progress">
  <button type="button" class="advisor-toggle-btn" :class="{active:advisor}" @click="advisor=!advisor;if(advisor)stage=0">
   <span class="ai-sparkle">✦</span> AI 灵犀定制舱
   <span class="advisor-toggle-arrow">{{advisor ? '▲ 收起' : '▼ 展开'}}</span>
  </button>
  <div class="progress-steps-wrap">
   <button v-for="(s,i) in stages" :key="s" :class="{active:stage===i,done:stage>i}" :disabled="busy||(i>0&&!selected)" @click="stage=i">
    <span class="step-num">0{{i+1}}</span>
    <span class="step-name">{{s}}</span>
   </button>
  </div>
 </div>

 <!-- Collapsible Design Advisor Drawer with Smooth Transition -->
 <transition name="advisor-drawer">
  <div v-if="advisor&&stage===0" class="advisor-drawer-container">
   <DesignAdvisor @confirm="acceptRecommendation" @skip="advisor=false"/>
  </div>
 </transition>

 <!-- Main Workspace Body -->
 <div class="theatre-body">
  <!-- Left Side: AI Intention & Parameters Control Column -->
  <aside class="intention-panel">
   <div class="panel-header-block">
    <div class="ai-model-tag">
     <i class="ai-badge-dot"></i>
     <span>DOUBAO-SEED 文化基因推理引擎</span>
    </div>
    <h1>{{['开始你的纹样设计','选择纹样','比较设计方案','编辑设计','预览与导出'][stage]}}</h1>
    <p class="panel-desc">{{['由大模型对齐礼赠语境、召回非遗图元并自适应器物曲率','细看图元构图与文化证据，选择入器母本','AI 算法生成三组构图，调控留白与结构中心','四层文化图元微调，实时验证制造公差','3D数字孪生与即梦4.5实境影棚，导出1:1工程包'][stage]}}</p>
   </div>

   <!-- STAGE 0: Intention Setup with Scrollable Content Body -->
   <template v-if="stage===0">
    <div class="panel-scroll-body">
     <div class="form-group">
      <label class="group-title">受赠对象 / RECIPIENT</label>
      <div class="recipient-pills-row">
       <button v-for="r in recipients" :key="r" :class="{chosen:recipient===r}" :aria-pressed="recipient===r" @click="recipient=r">{{r}}</button>
      </div>
     </div>

     <div class="form-group">
      <div class="group-header-row">
       <label class="group-title">寄托何意 / CULTURAL INTENTION</label>
       <span class="active-wish-badge">{{wish}}</span>
      </div>
      <div class="wish-card-list" role="radiogroup" aria-label="寄托何意">
       <button
        v-for="w in wishDetails"
        :key="w.key"
        type="button"
        class="wish-item-card"
        :class="{chosen:wish===w.key}"
        :aria-checked="wish===w.key"
        @click="wish=w.key"
       >
        <div class="wish-glyph-box">
         <span>{{w.glyph}}</span>
        </div>
        <div class="wish-item-info">
         <div class="wish-item-top">
          <strong class="wish-item-title">{{w.title}}</strong>
          <code class="wish-code-tag">{{w.code}}</code>
         </div>
         <span class="wish-meaning-text">{{w.meaning}}</span>
        </div>
        <div class="wish-check-indicator" aria-hidden="true">
         <span class="dot-inner"></span>
        </div>
       </button>
      </div>
     </div>

     <div class="form-group">
      <div class="group-header-row">
       <label class="group-title">承载器物 · 12类器物</label>
       <small class="gallery-hint">左侧全景选器 ({{vesselNames[vessel]}})</small>
      </div>
      <div class="vessel-gallery" role="group" aria-label="选择承载器物">
       <button v-for="v in vesselCatalog" :key="v.id" :class="{chosen:vessel===v.id}" :aria-pressed="vessel===v.id" :aria-label="v.name" :disabled="busy" @click="changeVessel(v.id)">
        <svg viewBox="0 0 64 50" aria-hidden="true"><path :d="v.icon"/></svg>
        <span>{{v.name}}</span>
        <small>{{v.group}}</small>
       </button>
      </div>
     </div>

     <!-- AI Value Showcase Card: Doubao-Seed Semantic Translation HUD -->
     <div class="ai-live-card">
      <div class="ai-live-head">
       <div class="ai-live-title">
        <span class="ai-pulse-dot"></span>
        <strong>✦ AI 意图转译中枢</strong>
       </div>
       <span class="ai-conf-tag">置信度 {{aiReasoning.confidence}}</span>
      </div>
      <div class="ai-live-body">
       <div class="ai-field-row">
        <span class="field-kicker">语境意图：</span>
        <span class="field-val">{{aiReasoning.target}}</span>
       </div>
       <div class="ai-field-row">
        <span class="field-kicker">基因召回：</span>
        <span class="field-val highlight">{{aiReasoning.pattern}}</span>
       </div>
       <div class="ai-field-row">
        <span class="field-kicker">曲面适配：</span>
        <span class="field-val">{{aiReasoning.vesselSpec}} · {{aiReasoning.curvature}}</span>
       </div>
       <div class="ai-live-poem">
        <small>✦ 一器一祝福 · 定制吉言</small>
        <p>「{{aiReasoning.inscription}}」</p>
       </div>
      </div>
     </div>

     <details class="optional-intention">
      <summary>添一句个性心意与气质（选填）<span>＋</span></summary>
      <div class="optional-inner">
       <label>气质倾向</label>
       <div class="theatre-chips">
        <button v-for="m in ['端正','疏朗','丰盛']" :key="m" :class="{chosen:mood===m}" @click="mood=m">{{m}}</button>
       </div>
       <textarea class="personal-note" v-model="note" maxlength="300" placeholder="例如：写一句想送给对方的话，或特定的传统文化偏好" aria-label="个人心意"></textarea>
      </div>
     </details>
    </div>

    <!-- Pinned Bottom Action Button -->
    <div class="panel-footer-action">
     <button class="theatre-primary ai-begin-btn" :disabled="busy" @click="begin">
      <span>✦ 启动 Doubao-Seed 智能推演 →</span>
     </button>
    </div>
   </template>

   <!-- STAGE 1-4: Active Workflow -->
   <template v-else>
    <div class="panel-scroll-body">
     <div class="intention-note">
      <small>当前创作意向与母本</small>
      <p>赠予{{recipient}} · {{wish}}</p>
      <span class="current-pattern-badge">《{{selected?.name}}》 · {{vesselNames[vessel]}}</span>
     </div>

     <!-- STAGE 3: AI DFM Manufacturing Probe HUD -->
     <div v-if="stage===3" class="ai-dfm-chip">
      <div class="dfm-title">
       <span>✦ AI DFM 制造工艺规则引擎</span>
       <b class="grade-a">A级认证</b>
      </div>
      <div class="dfm-metrics">
       <span>最小壁厚容差: 1.2mm (≥0.8)</span>
       <span>隐蔽焊点: 4 处已标定</span>
      </div>
      <div class="dfm-inscription">
       <small>✦ 专属器物铭文</small>
       <p>「{{blessingInscription}}」</p>
      </div>
     </div>

     <div class="history-actions">
      <button :disabled="busy||cursor<=0" @click="undo(-1)">← 撤销</button>
      <button :disabled="busy||cursor>=history.length-1" @click="undo(1)">重做 →</button>
      <button @click="compare=!compare">{{compare?'收起':'版本对比'}}</button>
     </div>

     <label class="anchor-lock">
      <input type="checkbox" :disabled="busy" v-model="selected.recipe.anchor_locked">
      <span>{{selected.contemporary_sources?.length?'锁定主纹结构':'锁定寓意锚点'}}</span>
     </label>

     <button class="link-action" @click="advanced=!advanced">{{advanced?'收起':'展开'}}进阶参数编辑</button>
     <div v-if="advanced&&recipe" class="theatre-parameters" :inert="busy">
      <label>构图秩序
       <select v-model="recipe.template" @change="update()">
        <option value="original">原作适合</option>
        <option value="center">中心围合</option>
        <option value="mirror">镜像对生</option>
        <option value="ring">旋转放射</option>
        <option value="repeat">连续网格</option>
        <option value="checker">棋盘交错</option>
        <option value="trail">循迹生长</option>
       </select>
      </label>
      <button @click="flat=true;drawing=!drawing">{{drawing?'取消画轨迹':'亲手画一条生长轨迹'}}</button>
      <label>工艺视觉
       <select v-model="recipe.geometry_mode" @change="update()">
        <option value="union">正形浅浮雕</option>
        <option value="negative">负形镂空</option>
        <option value="outline">线刻轮廓</option>
       </select>
      </label>
      <label>装饰区域宽度 / mm<input type="number" min="20" max="400" v-model.number="recipe.width_mm" @change="update()"></label>
      <label>装饰区域高度 / mm<input type="number" min="20" max="400" v-model.number="recipe.height_mm" @change="update()"></label>
      <label>构图节奏 {{recipe.count}}<input type="range" v-model.number="recipe.count" min="4" max="16" step="2" @change="update()"></label>
      <label>图元尺度 {{recipe.scale}}<input type="range" v-model.number="recipe.scale" min="0.3" max="1.2" step="0.1" @change="update()"></label>
      <label>层间留白 {{recipe.spacing}}<input type="range" v-model.number="recipe.spacing" min="0.6" max="1.5" step="0.1" @change="update()"></label>
      <label>整体转角 {{recipe.rotation}}°<input type="range" v-model.number="recipe.rotation" min="0" max="360" step="15" @change="update()"></label>
     </div>
    </div>

    <!-- Pinned Bottom Next Action -->
    <div class="panel-footer-action">
     <button v-if="stage<4" class="theatre-primary" :disabled="busy" @click="stage++">
      {{['','比较方案','编辑设计','预览与导出'][stage]}} →
     </button>
    </div>
   </template>

   <p v-if="error" class="theatre-error" role="alert">{{error}}</p>
   <p v-if="busy" class="theatre-status" role="status">✦ 算法正在解算图元几何与曲率…</p>
  </aside>

  <!-- Right Side: Workbench & 3D Interactive Stage -->
  <div class="workbench-column">
   <div class="workbench-card">
    <!-- Unified Workbench Top Header: Strictly Aligned with Left Panel Header -->
    <div class="workbench-header">
     <!-- Left: Mode Switcher Pills -->
     <div class="tabs-pill-group" role="group" aria-label="工作区视图">
      <button type="button" @click="workspace='preview';flat=false" :class="{active:(workspace==='preview'&&!flat)||!selected}">
       <span class="tab-indicator-dot"></span>3D 器物数字孪生
      </button>
      <button type="button" :disabled="!selected" @click="selected&&(workspace='preview',flat=true)" :class="{active:workspace==='preview'&&flat,disabled:!selected}">
       平面矢量设计
      </button>
      <button type="button" :disabled="!selected" @click="selected&&(workspace='measure')" :class="{active:workspace==='measure',disabled:!selected}">
       DFM 激光测量探针
      </button>
     </div>

     <!-- Center: Direction / Vessel Spec -->
     <div class="workbench-title-group">
      <span class="digital-twin-badge">3D DIGITAL TWIN</span>
      <strong class="workbench-vessel-title">{{selected ? selected.direction || '守形传意' : '设计预览'}} · {{vesselNames[vessel]}}</strong>
     </div>

     <!-- Right: Shape Tuning & Stage Indicator -->
     <div class="workbench-header-actions">
      <!-- Shape Popover Menu with Mouseleave Auto-collapse -->
      <div class="shape-dropdown-wrap" @mouseenter="shapeOpen=true" @mouseleave="shapeOpen=false">
       <button type="button" class="shape-pill-btn" :class="{active:shapeOpen}" @click="shapeOpen=!shapeOpen" aria-haspopup="true" :aria-expanded="shapeOpen">
        <span class="shape-icon">◈</span>
        <span>造型 · {{shapeLabels[shape]||shape}}</span>
        <span class="chevron">▾</span>
       </button>
       <transition name="pop-fade">
        <div v-if="shapeOpen" class="shape-flyout-menu" role="menu">
         <div class="shape-flyout-title">器型微曲率调谐</div>
         <div class="shape-flyout-list">
          <button type="button" v-for="(label,key) in currentShapeOptions" :key="key" :class="{selected:shape===key}" @click="setShape(key)">
           <span>{{label}}</span>
           <b v-if="shape===key">✓</b>
          </button>
         </div>
        </div>
       </transition>
      </div>

      <!-- Flat/3D View Switcher -->
      <button v-if="selected" class="flat-switch-btn" @click="flat=!flat">{{flat?'3D 观器':'展开布纹'}} ⇄</button>

      <!-- Stage Step Pill -->
      <div class="stage-step-pill">阶段 0{{stage+1}} / {{stages[stage]}}</div>
     </div>
    </div>

    <!-- Workbench Main Viewport Body -->
    <div class="workbench-card-body">
     <WorkshopLens v-if="selected&&workspace==='measure'" :design="selected"/>

     <div v-show="workspace!=='measure'" class="stage-editor-layout" :class="{'with-composer':stage===3}">
      <!-- 3D Stage Section -->
      <section @dragover.prevent @drop.prevent="dropMaterial" class="creation-stage" aria-label="器物与纹样预览">
       <!-- 3D / 2D Viewport -->
       <VesselScene ref="vesselScene" v-if="!flat" :svg="selected?.svg||emptySvg" :vessel="vessel" :formation="formation" :shape="shape"/>
       <div v-else class="theatre-flat">
        <div v-html="selected.svg"></div>
        <svg v-if="drawing" viewBox="0 0 1000 1000" class="trajectory-pad" @pointerdown="draw" @pointermove="draw" @pointerup="draw">
         <polyline :points="stroke.map(p=>p.join(',')).join(' ')" fill="none" stroke="#c7a66b" stroke-width="4"/>
         <text x="50" y="70" fill="#c7a66b" font-size="24">拖动绘制排列轨迹，松开后应用</text>
        </svg>
       </div>

       <label v-if="stage===4" class="formation-control">平面展开 <input type="range" min="0" max="1" step="0.01" v-model.number="formation"> 锡纹入器</label>

       <!-- Bottom Caption: Positive Craft Narrative -->
       <div class="theatre-caption">
        <span>{{stage===0?'选择用途和器物，开始生成纹样方案。':selected?.explanation||'传承中华传统吉纹基因，由 AI 算法适配器物空间美学；已完成文化语义解析与锻锡工艺预演。'}}</span>
        <small>拖动 360° 环视器物 · 实时演算 0.8mm 锻打浅浮雕与紫砂胎体光影层次 · 1:1 DXF 制版就绪</small>
       </div>
      </section>

      <!-- Stage 3: Gene Composer Panel -->
      <section v-if="stage===3&&selected" class="composer-panel" :inert="busy" aria-label="图元配方编辑">
       <GeneComposer :design="selected" @change="update"/>
      </section>
     </div>
    </div>
   </div>

   <!-- Stage 1 Motif Source Thread -->
   <div v-if="stage===1&&source" class="source-thread">
    <span>{{wish}}</span>
    <i>{{selected?.evidence.some((e:any)=>e.relevance==='intent')?'← 确认映射 ←':'← 图元来源 ←'}}</i>
    <button @click="showSource">{{source.id}} · {{source.name}} ↗</button>
    <p>{{selected?.evidence.filter((e:any)=>e.source_pattern===source.id).map((e:any)=>e.evidence).join('；')||selected?.explanation}}</p>
   </div>

   <!-- Stage 2 Direction Cards -->
   <div v-if="stage===2" class="direction-rail">
    <button v-for="d in candidates" :key="d.id" :class="{chosen:selected?.id===d.id}" :disabled="busy" @click="select(d)">
     <div v-html="d.svg"></div>
     <span>{{d.direction}}</span>
     <small>{{d.strategy}}</small>
    </button>
   </div>
  </div>
 </div>

 <!-- Additional Sections -->
 <section v-if="stage===1&&source" class="theatre-section" id="source-atlas">
  <GeneAtlas :pattern="source" @gene="useGene"/>
 </section>

 <section v-if="compare" class="version-gallery">
  <button v-for="(d,i) in history" :key="d.id||i" :disabled="busy" @click="undo(i-cursor)">
   <div v-html="d.svg"></div>
   <span>版本 {{i+1}} · {{d.direction}}</span>
  </button>
 </section>

 <MaterialPlanet v-if="selected" @apply="applyMaterial"/>
 <slot name="after-workflow" :design="selected" :stage="stage"/>

 <!-- STAGE 4: Final Work, Jimeng 4.5 & Delivery -->
 <section v-if="stage===4&&selected" class="theatre-section final-work">
  <div>
   <p class="kicker">保存、实境棚拍与 1:1 工程交付</p>
   <h2>{{wish}} · {{selected.direction}}</h2>
   <p class="blessing-line">✦ 器物铭文：「{{blessingInscription}}」</p>
   <p>保存您的文化基因配方，一键生成东方美学实境摄影大片或导出 1:1 毫米级 DXF 制版工程包。</p>

   <div class="final-actions-row">
    <button :disabled="busy||selected.favorite" @click="save">{{selected.favorite?'已保存 ✓':'保存作品'}}</button>
    <button type="button" :disabled="busy" @click="exportCertificate">✦ 导出数字溯源鉴定卡</button>
    <details class="export-menu">
     <summary>导出作品</summary>
     <a :aria-disabled="busy||selected.preview_only" @click="(busy||selected.preview_only)&&$event.preventDefault()" :href="'/api/designs/'+selected.id+'/export/svg'">导出 SVG</a>
     <a :aria-disabled="busy||selected.preview_only" @click="(busy||selected.preview_only)&&$event.preventDefault()" :href="'/api/designs/'+selected.id+'/export/png'">导出 PNG</a>
     <a :aria-disabled="busy||selected.preview_only" @click="(busy||selected.preview_only)&&$event.preventDefault()" :href="'/api/designs/'+selected.id+'/export/json'">设计档案</a>
     <a :aria-disabled="busy||selected.preview_only" @click="(busy||selected.preview_only)&&$event.preventDefault()" :href="'/api/manufacturing/'+selected.id+'/package'">下载工坊工程包 · DXF</a>
     <a href="javascript:void(0)" :aria-disabled="busy||selected.preview_only" @click="(busy||selected.preview_only)?null:(show3DPrint=true)">导出 3D 打印模型 (STL)</a>
    </details>
   </div>

   <div class="jimeng-studio-bar">
    <label>Jimeng 4.5 东方实境摄影棚：
     <select v-model="renderScene">
      <option value="茶席">宋韵茶席 · 晨曦竹影</option>
      <option value="博古">紫檀博古 · 博物馆聚光</option>
      <option value="工坊">威海非遗 · 匠人手作台</option>
      <option value="国礼">东方国礼 · 丹漆丝绸锦盒</option>
     </select>
    </label>
    <button :disabled="busy" @click="render">生成 AI 意境图 ↗</button>
   </div>

   <details class="sample-form">
    <summary>提交打样沟通需求</summary>
    <p>留下数量、材料与尺寸要求，威海金镶玉工坊非遗工艺顾问将依据 1:1 DXF 工程档案与您对接打样细节。</p>
    <label>意向数量<input type="number" min="1" max="999" v-model.number="sampleQuantity"></label>
    <label>联系方式（选填，仅工作人员可见）<input v-model="sampleContact" maxlength="120"></label>
    <textarea v-model="sampleNotes" maxlength="1000" placeholder="希望使用的材料、器物尺寸、交付时间等"></textarea>
    <button :disabled="busy" @click="submitSample">提交打样需求</button>
    <p v-if="sampleRequest">{{sampleRequest.message}}<br>跟踪编号：{{sampleRequest.id}}</p>
   </details>

   <p v-if="job">{{job.message||job.status}}</p>

   <div v-if="job?.url" class="jimeng-compare-box">
    <div class="compare-head">
     <span>◀ 3D 数字孪生几何模型</span>
     <b>拖动滑块对比即梦 4.5 实境光影 ({{sliderPos}}%)</b>
     <span>Jimeng 4.5 实境摄影大片 ▶</span>
    </div>
    <div class="compare-stage">
     <img v-if="referenceShot" :src="referenceShot" alt="3D数字孪生预览" class="compare-base">
     <img :src="job.url" alt="Jimeng 4.5 东方器物实境渲染图" class="compare-overlay" :style="{clipPath:`inset(0 0 0 ${100-sliderPos}%)`}">
    </div>
    <input type="range" min="5" max="95" v-model.number="sliderPos" aria-label="对比滑块">
   </div>
  </div>

  <details class="source-details">
   <summary>查看设计依据与来源</summary>
   <DesignNarrative :design="selected" @pattern="emit('pattern',$event)" @read="emit('read',$event)"/>
  </details>
 </section>

 <Print3DModal v-if="selected" v-model="show3DPrint" :design="selected" :width="selected?.recipe?.width_mm" :height="selected?.recipe?.height_mm" />
</main>
</template>

<style scoped>
.theatre { --theatre-ink:var(--bg-canvas); --theatre-copy:var(--text-primary); --theatre-silver:var(--text-secondary); --theatre-muted:var(--text-muted); --theatre-gold:var(--accent-gold); background:var(--theatre-ink); color:var(--theatre-copy); min-height:calc(100vh - 84px); padding:0 clamp(20px,4vw,64px) 60px; }

/* Progress Bar */
.theatre .theatre-progress { max-width:1660px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:20px; padding:14px 0 16px; border-bottom:1px solid var(--border-default); }
.theatre .advisor-toggle-btn { display:inline-flex; align-items:center; gap:8px; padding:8px 16px; background:rgba(212,175,106,0.12); border:1px solid rgba(212,175,106,0.35); border-radius:20px; color:var(--accent-gold); font-size:13px; font-weight:500; cursor:pointer; transition:all .2s; }
.theatre .advisor-toggle-btn:hover, .theatre .advisor-toggle-btn.active { background:rgba(212,175,106,0.22); border-color:var(--accent-gold); box-shadow:0 0 12px rgba(212,175,106,0.25); }
.theatre .advisor-toggle-arrow { font-size:10px; opacity:0.85; margin-left:2px; }
.theatre .progress-steps-wrap { display:flex; align-items:center; gap:clamp(6px,2vw,24px); }
.theatre .progress-steps-wrap button { color:var(--theatre-silver); font-size:14px; min-height:38px; border:1px solid transparent; padding:6px 14px; background:var(--bg-elevated); border-radius:6px; transition:all .2s; display:inline-flex; align-items:center; gap:7px; }
.theatre .progress-steps-wrap button:disabled { opacity:.45; color:var(--text-secondary); cursor:not-allowed; }
.theatre .progress-steps-wrap .step-num { font-size:11px; opacity:.7; }
.theatre .progress-steps-wrap .active { color:var(--theatre-gold); background:color-mix(in srgb, var(--accent-gold) 10%, transparent); border-color:var(--theatre-gold); font-weight:600; }
.theatre .progress-steps-wrap .done { color:var(--text-primary); border-color:rgba(255,255,255,0.08); }

/* Collapsible Advisor Drawer */
.theatre .advisor-drawer-container { max-width:1660px; margin:0 auto; overflow:hidden; }
.theatre .advisor-drawer-enter-active, .theatre .advisor-drawer-leave-active { transition:all .3s cubic-bezier(0.16, 1, 0.3, 1); max-height:850px; }
.theatre .advisor-drawer-enter-from, .theatre .advisor-drawer-leave-to { opacity:0; max-height:0; transform:translateY(-8px); }

/* Unified Workstation Layout Grid - Strictly Aligned */
.theatre .theatre-body { display:grid; grid-template-columns:360px minmax(0,1fr); gap:20px; max-width:1660px; margin:16px auto 0; align-items:stretch; }

/* Left Intention Column (Card with equal height & top/bottom baseline) */
.theatre .intention-panel { background:var(--bg-elevated); border:1px solid var(--border-default); border-radius:10px; padding:0; display:flex; flex-direction:column; min-width:0; height:calc(100vh - 165px); min-height:720px; max-height:860px; box-sizing:border-box; overflow:hidden; }
.theatre .panel-header-block { flex-shrink:0; padding:10px 18px; border-bottom:1px solid var(--border-default); background:rgba(0,0,0,0.22); height:82px; min-height:82px; max-height:82px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:center; }
.theatre .ai-model-tag { display:inline-flex; align-items:center; gap:6px; font-size:10px; letter-spacing:1px; color:var(--accent-gold); background:rgba(212,175,106,0.08); padding:1px 6px; border-radius:4px; margin-bottom:2px; width:fit-content; }
.theatre .ai-badge-dot { width:5px; height:5px; border-radius:50%; background:#34d399; box-shadow:0 0 6px #34d399; }
.theatre .intention-panel h1 { color:var(--theatre-copy); font-size:17px; line-height:1.2; margin:0 0 2px; font-weight:600; }
.theatre .panel-desc { color:var(--theatre-silver); font-size:11px; line-height:1.3; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* Scrollable Panel Middle Body */
.theatre .panel-scroll-body { flex:1; min-height:0; overflow-y:auto; overflow-x:hidden; padding:14px 18px; display:flex; flex-direction:column; gap:14px; }
.theatre .panel-scroll-body::-webkit-scrollbar { width:4px; }
.theatre .panel-scroll-body::-webkit-scrollbar-track { background:rgba(0,0,0,0.1); border-radius:4px; }
.theatre .panel-scroll-body::-webkit-scrollbar-thumb { background:rgba(212,175,106,0.3); border-radius:4px; }
.theatre .panel-scroll-body::-webkit-scrollbar-thumb:hover { background:rgba(212,175,106,0.6); }

/* Pinned Footer Action */
.theatre .panel-footer-action { flex-shrink:0; padding:12px 18px; border-top:1px solid var(--border-default); background:rgba(0,0,0,0.2); box-sizing:border-box; min-height:64px; display:flex; align-items:center; }

.theatre .form-group { display:flex; flex-direction:column; gap:8px; }
.theatre .group-title { font-size:11px; letter-spacing:1px; color:var(--theatre-silver); margin:0; font-weight:600; }
.theatre .group-header-row { display:flex; justify-content:space-between; align-items:center; }
.theatre .gallery-hint { font-size:11px; color:var(--accent-gold); }

/* Recipient Pills Row */
.theatre .recipient-pills-row { display:flex; gap:6px; justify-content:space-between; }
.theatre .recipient-pills-row button { flex:1; height:34px; display:flex; align-items:center; justify-content:center; padding:0 4px; font-size:12px; background:rgba(255,255,255,0.02); border:1px solid var(--border-default); border-radius:6px; color:var(--theatre-silver); cursor:pointer; transition:all 0.2s; white-space:nowrap; }
.theatre .recipient-pills-row button:hover { border-color:rgba(212,175,106,0.35); color:var(--text-primary); }
.theatre .recipient-pills-row button.chosen { background:color-mix(in srgb, var(--accent-gold) 15%, transparent); color:var(--accent-gold); border-color:var(--theatre-gold); font-weight:600; box-shadow:inset 0 0 0 1px var(--accent-gold); }

/* Redesigned Wish Selector: Horizontal Bento Cards */
.theatre .active-wish-badge { font-size:11px; color:var(--accent-gold); background:rgba(212,175,106,0.1); padding:1px 7px; border-radius:4px; border:1px solid rgba(212,175,106,0.25); }
.theatre .wish-card-list { display:flex; flex-direction:column; gap:8px; }
.theatre .wish-item-card { display:grid; grid-template-columns:36px 1fr 18px; align-items:center; gap:10px; padding:8px 10px; background:rgba(255,255,255,0.02); border:1px solid var(--border-default); border-radius:8px; color:var(--theatre-copy); cursor:pointer; text-align:left; transition:all 0.2s ease; }
.theatre .wish-item-card:hover { background:rgba(212,175,106,0.04); border-color:rgba(212,175,106,0.35); transform:translateY(-1px); }
.theatre .wish-item-card.chosen { background:linear-gradient(90deg, rgba(212,175,106,0.18) 0%, rgba(212,175,106,0.04) 100%); border-color:var(--theatre-gold); box-shadow:0 4px 14px rgba(212,175,106,0.15); }
.theatre .wish-glyph-box { width:36px; height:36px; border-radius:6px; background:rgba(0,0,0,0.3); border:1px solid rgba(212,175,106,0.2); display:flex; align-items:center; justify-content:center; font-family:var(--font-serif, Georgia, serif); font-size:17px; color:var(--theatre-silver); transition:all 0.2s; }
.theatre .wish-item-card.chosen .wish-glyph-box { color:var(--accent-gold); border-color:var(--accent-gold); background:rgba(212,175,106,0.15); box-shadow:0 0 10px rgba(212,175,106,0.25); }
.theatre .wish-item-info { display:flex; flex-direction:column; gap:2px; min-width:0; }
.theatre .wish-item-top { display:flex; align-items:center; gap:6px; }
.theatre .wish-item-title { font-size:13px; font-weight:600; color:#ffffff; }
.theatre .wish-item-card.chosen .wish-item-title { color:var(--accent-gold); }
.theatre .wish-code-tag { font-size:9px; font-family:monospace; color:var(--text-secondary); background:rgba(255,255,255,0.05); padding:1px 5px; border-radius:3px; }
.theatre .wish-meaning-text { font-size:11px; color:var(--theatre-silver); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.theatre .wish-check-indicator { width:16px; height:16px; border-radius:50%; border:1.5px solid var(--border-default); display:flex; align-items:center; justify-content:center; }
.theatre .wish-item-card.chosen .wish-check-indicator { border-color:var(--accent-gold); }
.theatre .wish-check-indicator .dot-inner { width:8px; height:8px; border-radius:50%; background:transparent; transition:background 0.2s; }
.theatre .wish-item-card.chosen .wish-check-indicator .dot-inner { background:var(--accent-gold); box-shadow:0 0 6px var(--accent-gold); }

/* Vessel Gallery Matrix - 4 columns x 3 rows = 12 complete vessels without scrollbar */
.theatre .vessel-gallery { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:6px; padding:2px; }
.theatre .vessel-gallery>button { min-width:0; height:54px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:2px; padding:4px 2px; background:rgba(255,255,255,0.02); border:1px solid var(--border-default); border-radius:6px; color:var(--text-secondary); cursor:pointer; transition:all .18s; }
.theatre .vessel-gallery>button.chosen { background:color-mix(in srgb, var(--accent-gold) 16%, transparent); color:var(--accent-gold); border-color:var(--accent-gold); font-weight:600; box-shadow:inset 0 0 0 1px var(--accent-gold); }
.theatre .vessel-gallery>button:hover { border-color:rgba(212,175,106,0.35); transform:translateY(-1px); }
.theatre .vessel-gallery svg { width:26px; height:18px; overflow:visible; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; }
.theatre .vessel-gallery span { font-size:11px; white-space:nowrap; line-height:1.1; }
.theatre .vessel-gallery small { color:var(--text-secondary); font-size:9px; line-height:1; }

/* Right Workbench Column & Unified Card */
.theatre .workbench-column { display:flex; flex-direction:column; min-width:0; height:100%; }
.theatre .workbench-card { background:var(--bg-elevated); border:1px solid var(--border-default); border-radius:10px; display:flex; flex-direction:column; height:calc(100vh - 165px); min-height:720px; max-height:860px; box-sizing:border-box; overflow:hidden; }

/* Workbench Unified Top Header - Strictly Aligned to Left Header */
.theatre .workbench-header { flex-shrink:0; padding:10px 18px; border-bottom:1px solid var(--border-default); background:rgba(0,0,0,0.22); height:82px; min-height:82px; max-height:82px; box-sizing:border-box; display:flex; align-items:center; justify-content:space-between; gap:12px; }

/* Mode Switcher Tabs */
.theatre .tabs-pill-group { display:flex; gap:4px; background:rgba(0,0,0,0.35); border:1px solid var(--border-default); border-radius:8px; padding:3px; }
.theatre .tabs-pill-group button { background:transparent; border:1px solid transparent; color:var(--theatre-silver); font-size:12px; padding:5px 12px; border-radius:6px; cursor:pointer; transition:all .2s; display:inline-flex; align-items:center; gap:6px; white-space:nowrap; }
.theatre .tabs-pill-group button.active { background:color-mix(in srgb, var(--accent-gold) 16%, transparent); color:var(--accent-gold); border-color:rgba(212,175,106,0.35); font-weight:600; }
.theatre .tabs-pill-group button.disabled { opacity:0.45; cursor:not-allowed; }
.theatre .tab-indicator-dot { width:5px; height:5px; border-radius:50%; background:var(--accent-gold); box-shadow:0 0 6px var(--accent-gold); }

/* Center Vessel Title */
.theatre .workbench-title-group { display:flex; align-items:center; gap:8px; min-width:0; }
.theatre .digital-twin-badge { font-size:10px; letter-spacing:1px; color:var(--accent-gold); background:rgba(212,175,106,0.1); border:1px solid rgba(212,175,106,0.3); padding:2px 6px; border-radius:4px; white-space:nowrap; }
.theatre .workbench-vessel-title { font-size:13px; color:var(--theatre-copy); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* Header Right Actions */
.theatre .workbench-header-actions { display:flex; align-items:center; gap:8px; flex-shrink:0; }
.theatre .stage-step-pill { font-size:11px; color:var(--accent-gold); background:rgba(212,175,106,0.08); padding:5px 12px; border-radius:12px; border:1px solid rgba(212,175,106,0.2); white-space:nowrap; }

/* Workbench Body & Viewport */
.theatre .workbench-card-body { flex:1; min-height:0; display:flex; flex-direction:column; overflow:hidden; }
.theatre .stage-editor-layout { display:grid; grid-template-columns:minmax(0,1fr); gap:16px; min-width:0; height:100%; align-items:stretch; }
.theatre .stage-editor-layout.with-composer { grid-template-columns:minmax(0,1fr) 360px; }
.theatre .creation-stage { display:flex; flex-direction:column; height:100%; border:0; background:transparent; border-radius:0; overflow:hidden; position:relative; }

/* AI Live Reasoning Card */
.theatre .ai-live-card { background:linear-gradient(170deg, rgba(212,175,106,0.09) 0%, rgba(13,20,19,0.92) 100%); border:1px solid rgba(212,175,106,0.3); border-radius:8px; padding:12px 14px; display:flex; flex-direction:column; gap:8px; }
.theatre .ai-live-head { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(212,175,106,0.15); padding-bottom:6px; }
.theatre .ai-live-title { display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--accent-gold); }
.theatre .ai-pulse-dot { width:6px; height:6px; border-radius:50%; background:#34d399; box-shadow:0 0 8px #34d399; }
.theatre .ai-conf-tag { font-size:10px; color:#34d399; background:rgba(52,211,153,0.12); border:1px solid rgba(52,211,153,0.3); padding:2px 7px; border-radius:10px; }
.theatre .ai-live-body { display:flex; flex-direction:column; gap:4px; font-size:11px; line-height:1.5; }
.theatre .ai-field-row { display:flex; align-items:baseline; gap:5px; color:var(--theatre-silver); }
.theatre .field-kicker { color:var(--theatre-muted); flex-shrink:0; font-size:11px; }
.theatre .field-val { color:#ffffff; }
.theatre .field-val.highlight { color:var(--accent-gold); font-weight:500; }
.theatre .ai-live-poem { margin-top:4px; padding:8px 10px; background:rgba(212,175,106,0.08); border-left:2px solid var(--accent-gold); border-radius:0 6px 6px 0; }
.theatre .ai-live-poem small { color:var(--accent-gold); font-size:10px; display:block; margin-bottom:2px; letter-spacing:0.5px; }
.theatre .ai-live-poem p { margin:0; color:#f7ede0; font-size:12px; font-family:var(--font-serif, Georgia, serif); font-style:italic; }

/* Optional Note */
.theatre .optional-intention { border:1px solid var(--border-default); border-radius:6px; background:rgba(255,255,255,0.02); }
.theatre .optional-intention summary { display:flex; justify-content:space-between; align-items:center; padding:9px 12px; font-size:12px; color:var(--theatre-silver); cursor:pointer; list-style:none; }
.theatre .optional-intention summary::-webkit-details-marker { display:none; }
.theatre .optional-inner { padding:0 12px 12px; }
.theatre .theatre-chips { display:flex; flex-wrap:wrap; gap:6px; }
.theatre .theatre-chips button { min-height:32px; padding:5px 12px; font-size:12px; background:rgba(255,255,255,0.02); border:1px solid var(--border-default); border-radius:6px; color:var(--theatre-copy); cursor:pointer; }
.theatre .theatre-chips .chosen { background:color-mix(in srgb, var(--accent-gold) 15%, transparent); color:var(--accent-gold); border-color:var(--theatre-gold); font-weight:600; }
.theatre .personal-note { width:100%; height:54px; margin-top:8px; padding:8px 10px; background:rgba(0,0,0,0.3); border:1px solid var(--border-default); border-radius:4px; color:var(--theatre-copy); font-size:12px; resize:none; }

/* Action Buttons */
.theatre .theatre-primary { display:block; width:100%; background:linear-gradient(135deg,var(--accent-gold),#a7833a); border:1px solid var(--accent-gold); color:#0d1413; font-size:13px; font-weight:700; letter-spacing:1px; padding:12px; border-radius:6px; cursor:pointer; transition:all .2s; text-align:center; box-shadow:0 4px 14px rgba(212,175,106,0.25); }
.theatre .theatre-primary:hover:not(:disabled) { transform:translateY(-1px); box-shadow:0 6px 18px rgba(212,175,106,0.35); }
.theatre .theatre-primary:disabled { opacity:.45; cursor:not-allowed; }

/* Stage 1-4 State */
.theatre .intention-note { background:rgba(255,255,255,0.02); border:1px solid var(--border-default); border-radius:6px; padding:12px 14px; }
.theatre .intention-note small { color:var(--theatre-muted); font-size:11px; }
.theatre .intention-note p { color:var(--accent-gold); font-size:18px; margin:4px 0 6px; font-weight:600; }
.theatre .current-pattern-badge { display:inline-block; font-size:11px; color:var(--theatre-silver); background:rgba(212,175,106,0.08); padding:2px 6px; border-radius:4px; }
.theatre .history-actions { display:flex; gap:6px; }
.theatre .history-actions button, .theatre .link-action { border:1px solid var(--border-default); color:var(--theatre-copy); background:rgba(255,255,255,0.02); font-size:12px; padding:8px 10px; border-radius:4px; cursor:pointer; }
.theatre .anchor-lock { display:flex; align-items:center; gap:8px; font-size:12px; color:var(--theatre-silver); cursor:pointer; }
.theatre .anchor-lock input { accent-color:var(--theatre-gold); }

/* AI DFM Probe Chip */
.theatre .ai-dfm-chip { background:rgba(212,175,106,0.06); border:1px solid rgba(212,175,106,0.25); border-radius:6px; padding:10px 12px; display:flex; flex-direction:column; gap:6px; font-size:11px; }
.theatre .dfm-title { display:flex; justify-content:space-between; align-items:center; color:var(--accent-gold); font-weight:600; }
.theatre .grade-a { color:#34d399; background:rgba(52,211,153,0.15); padding:1px 6px; border-radius:4px; font-size:10px; }
.theatre .dfm-metrics { display:flex; flex-direction:column; gap:2px; color:var(--theatre-silver); }
.theatre .dfm-inscription { border-top:1px dashed rgba(212,175,106,0.2); padding-top:6px; }
.theatre .dfm-inscription small { color:var(--theatre-muted); font-size:10px; }
.theatre .dfm-inscription p { margin:2px 0 0; color:#f3ece0; font-family:Georgia,serif; }

/* Theatre Parameters */
.theatre .theatre-parameters { display:flex; flex-direction:column; gap:8px; padding-top:8px; border-top:1px solid var(--border-default); }
.theatre .theatre-parameters select, .theatre .theatre-parameters input[type=number] { background:rgba(0,0,0,0.3); color:var(--theatre-copy); border:1px solid var(--border-default); border-radius:4px; padding:6px 8px; font-size:12px; width:100%; }

/* Optimized Shape Dropdown Popover */
.theatre .shape-dropdown-wrap { position:relative; }
.theatre .shape-pill-btn { display:inline-flex; align-items:center; gap:6px; height:32px; padding:0 12px; font-size:12px; color:var(--accent-gold); background:rgba(212,175,106,0.08); border:1px solid rgba(212,175,106,0.3); border-radius:6px; cursor:pointer; transition:all .2s; }
.theatre .shape-pill-btn:hover, .theatre .shape-pill-btn.active { background:rgba(212,175,106,0.18); border-color:var(--accent-gold); }
.theatre .shape-icon { font-size:11px; }
.theatre .chevron { font-size:10px; margin-left:2px; }

.theatre .shape-flyout-menu { position:absolute; top:calc(100% + 6px); right:0; z-index:40; width:190px; background:#121c19; border:1px solid rgba(212,175,106,0.35); border-radius:8px; box-shadow:0 14px 32px rgba(0,0,0,0.6); padding:8px; backdrop-filter:blur(14px); }
.theatre .shape-flyout-title { font-size:10px; letter-spacing:1px; color:var(--theatre-muted); padding:4px 8px 6px; border-bottom:1px solid rgba(255,255,255,0.06); margin-bottom:4px; }
.theatre .shape-flyout-list { display:flex; flex-direction:column; gap:2px; }
.theatre .shape-flyout-list button { display:flex; justify-content:space-between; align-items:center; width:100%; padding:6px 10px; font-size:12px; color:var(--theatre-silver); background:transparent; border:0; border-radius:4px; text-align:left; cursor:pointer; }
.theatre .shape-flyout-list button:hover { background:rgba(212,175,106,0.1); color:var(--accent-gold); }
.theatre .shape-flyout-list button.selected { background:color-mix(in srgb, var(--accent-gold) 18%, transparent); color:var(--accent-gold); font-weight:600; }
.theatre .shape-flyout-list button b { color:var(--accent-gold); font-size:11px; }

.theatre .flat-switch-btn { height:32px; padding:0 12px; font-size:12px; color:var(--theatre-silver); background:rgba(255,255,255,0.03); border:1px solid var(--border-default); border-radius:6px; cursor:pointer; }
.theatre .flat-switch-btn:hover { color:var(--accent-gold); border-color:var(--accent-gold); }

/* 2D Flat Pad */
.theatre .theatre-flat { width:100%; height:100%; min-height:420px; padding:30px; position:relative; background:radial-gradient(ellipse at center, rgba(212,175,106,0.06), transparent 70%); }
.theatre .theatre-flat>div, .theatre .theatre-flat :deep(svg) { width:100%; height:100%; }
.theatre .trajectory-pad { position:absolute; inset:0; touch-action:none; cursor:crosshair; }
.theatre .formation-control { display:flex; align-items:center; justify-content:center; gap:12px; padding:10px 14px; font-size:12px; color:var(--theatre-silver); border-top:1px solid var(--border-default); background:rgba(0,0,0,0.2); }
.theatre .formation-control input { max-width:240px; accent-color:var(--accent-gold); }

/* Bottom Caption */
.theatre .theatre-caption { flex-shrink:0; padding:10px 18px; border-top:1px solid var(--border-default); background:rgba(0,0,0,0.2); font-size:12px; line-height:1.6; color:var(--theatre-silver); min-height:54px; box-sizing:border-box; display:flex; flex-direction:column; justify-content:center; }
.theatre .theatre-caption small { display:block; color:var(--theatre-muted); font-size:11px; margin-top:2px; }

/* Composer Panel */
.theatre .composer-panel { border:1px solid var(--border-default); background:var(--bg-elevated); border-radius:10px; overflow:hidden; }

/* Stage 1 Source Thread & Stage 2 Direction Rail */
.theatre .source-thread { display:flex; flex-wrap:wrap; align-items:center; gap:12px; padding:16px 20px; background:var(--bg-elevated); border:1px solid var(--border-default); border-radius:8px; }
.theatre .source-thread span { color:var(--accent-gold); font-size:16px; font-weight:600; }
.theatre .source-thread i { color:var(--theatre-muted); font-size:12px; }
.theatre .source-thread button { color:var(--accent-gold); font-size:13px; padding:6px 12px; border:1px solid var(--border-default); border-radius:4px; background:var(--bg-elevated); cursor:pointer; }
.theatre .source-thread p { width:100%; margin:4px 0 0; color:var(--theatre-silver); font-size:12px; line-height:1.7; }

.theatre .direction-rail { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }
.theatre .direction-rail>button { display:flex; flex-direction:column; gap:6px; background:var(--bg-elevated); border:1px solid var(--border-default); border-radius:8px; color:var(--text-primary); padding:14px; text-align:left; cursor:pointer; transition:all .2s; }
.theatre .direction-rail>button.chosen { border-color:var(--accent-gold); box-shadow:inset 0 0 0 1px var(--accent-gold); background:rgba(212,175,106,0.06); }
.theatre .direction-rail>button>div { height:100px; width:100%; }
.theatre .direction-rail :deep(svg) { width:100%; height:100%; }
.theatre .direction-rail span { font-size:15px; color:var(--accent-gold); font-weight:600; }
.theatre .direction-rail small { font-size:11px; color:var(--theatre-silver); line-height:1.6; }

/* Stage 4 Final Work */
.theatre .theatre-section { margin-top:20px; }
.theatre .final-work>div:first-child { background:var(--bg-elevated); border:1px solid var(--border-default); border-radius:10px; padding:24px; }
.theatre .final-work h2 { color:var(--accent-gold); margin:4px 0 10px; font-size:24px; }
.theatre .final-work .blessing-line { color:#f6e7c4; font-size:16px; font-family:Georgia,serif; padding:10px 14px; background:rgba(212,175,106,0.08); border-left:3px solid var(--accent-gold); margin:12px 0; border-radius:0 6px 6px 0; }
.theatre .final-actions-row { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:14px 0; }
.theatre .final-actions-row button, .theatre .final-actions-row a { padding:9px 16px; border:1px solid var(--border-default); border-radius:6px; background:var(--bg-elevated); color:var(--theatre-copy); font-size:13px; cursor:pointer; }
.theatre .final-actions-row button:hover { border-color:var(--accent-gold); color:var(--accent-gold); }

.theatre .jimeng-studio-bar { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:16px 0; padding:12px 16px; background:rgba(255,255,255,0.02); border:1px solid var(--border-default); border-radius:8px; font-size:13px; }
.theatre .jimeng-studio-bar select { background:var(--bg-canvas); color:var(--accent-gold); border:1px solid rgba(212,175,106,0.35); padding:6px 10px; border-radius:6px; margin-left:6px; }
.theatre .jimeng-studio-bar button { padding:7px 14px; background:var(--accent-gold); color:#0d1413; font-weight:600; border:1px solid var(--accent-gold); border-radius:6px; cursor:pointer; }

.theatre .jimeng-compare-box { margin-top:16px; padding:16px; background:rgba(0,0,0,0.5); border:1px solid rgba(212,175,106,0.35); border-radius:10px; max-width:640px; }
.theatre .compare-head { display:flex; justify-content:space-between; font-size:11px; color:var(--theatre-silver); margin-bottom:8px; }
.theatre .compare-head b { color:var(--accent-gold); }
.theatre .compare-stage { position:relative; width:100%; aspect-ratio:1; overflow:hidden; border-radius:8px; background:#0d1413; }
.theatre .compare-stage img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.theatre .jimeng-compare-box input[type=range] { width:100%; margin-top:10px; accent-color:var(--accent-gold); }

.theatre .theatre-error { background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:#fca5a5; padding:8px 12px; border-radius:6px; font-size:12px; }
.theatre .theatre-status { color:var(--accent-gold); font-size:12px; }

/* Transitions */
.pop-fade-enter-active, .pop-fade-leave-active { transition:opacity .15s ease, transform .15s ease; }
.pop-fade-enter-from, .pop-fade-leave-to { opacity:0; transform:translateY(-4px); }

@media(max-width:1200px){
 .theatre .theatre-body { grid-template-columns:330px minmax(0,1fr); gap:14px; }
}
@media(max-width:960px){
 .theatre .theatre-body { grid-template-columns:minmax(0,1fr); }
 .theatre .stage-editor-layout.with-composer { grid-template-columns:minmax(0,1fr); }
}
</style>
