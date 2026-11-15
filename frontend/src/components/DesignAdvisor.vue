<script setup lang="ts">
import {ref,computed,watch} from 'vue';
const emit=defineEmits(['confirm','skip']);
const prompt=ref(''),busy=ref(false),error=ref(''),result=ref<any>(null),activeStep=ref(0);

const userSaved = (typeof localStorage!=='undefined' && localStorage.getItem('xiyu-user-vessel')) || 'pot';
const initialCarrier = userSaved==='pot'?'茶壶':userSaved==='tray'?'茶承':userSaved==='cup'?'茶杯':userSaved==='jar'?'茶叶罐':userSaved==='bookmark'?'书签':userSaved==='penholder'?'笔筒':userSaved==='incense'?'香插':userSaved==='box'?'首饰盒':userSaved==='pendant'?'挂坠':'茶壶';

const recipient=ref('长辈'),occasion=ref('生日祝寿'),carrier=ref(initialCarrier),style=ref('宋韵极简 · 疏朗留白'),baseMaterial=ref('宜兴紫泥 · 深褐温润'),tinFinish=ref('锻打素锡 · 浅浮雕'),vesselGroup=ref('全部');

const recipientOptions=[
 {value:'长辈',label:'长辈 · 家族尊长（祈愿松鹤康宁）',tag:'IMG-LONGEVITY'},
 {value:'朋友',label:'朋友 · 知音同道（寄意清正雅集）',tag:'IMG-PURITY'},
 {value:'伴侣',label:'伴侣 · 琴瑟佳偶（寓意和合双全）',tag:'IMG-HARMONY'},
 {value:'恩师',label:'恩师 · 杏坛学者（致敬文心兰韵）',tag:'IMG-NOBLE'},
 {value:'自己',label:'自己 · 案头清供（日常独处观心）',tag:'IMG-SERENE'},
 {value:'外宾',label:'外宾 · 城市国礼（威海非遗名片）',tag:'IMG-HERITAGE'}
];

const occasionOptions=[
 {value:'生日祝寿',label:'寿辰贺礼 · 福寿绵长（松鹤/寿字基因）',wish:'长寿百岁'},
 {value:'乔迁新居',label:'乔迁新居 · 八方安宁（八角/漏窗基因）',wish:'八方安宁'},
 {value:'节日祝福',label:'书房茶事 · 莲心清正（四叶莲心/宝相花）',wish:'莲心清正'},
 {value:'新婚嘉礼',label:'新婚嘉礼 · 琴瑟和鸣（团花/如意云头）',wish:'八方安宁'},
 {value:'日常自用',label:'日常清赏 · 顺遂安康（回纹/暗八仙）',wish:'莲心清正'}
];

const vesselCatalog=[
 {id:'帮我选择',key:'pot',name:'AI 智能适器',group:'全部',spec:'自动匹配最佳器型',icon:'M32 8 L40 22 L56 25 L44 36 L47 52 L32 44 L17 52 L20 36 L8 25 L24 22 Z'},
 {id:'茶壶',key:'pot',name:'紫砂壶',group:'茶席',spec:'壶腹微曲 · 90×75mm',icon:'M18 20 Q12 39 31 40 Q49 39 43 20 Z M18 20 Q31 14 43 20 M30 14 V10 M44 23 Q59 12 55 29 Q51 34 45 33 M17 26 L6 18 L12 33 L18 34'},
 {id:'茶承',key:'tray',name:'圆形茶承',group:'茶席',spec:'盘心团窠 · 120×120mm',icon:'M8 21 Q32 42 56 21 M8 21 Q32 31 56 21 M10 21 Q32 9 54 21'},
 {id:'茶杯',key:'cup',name:'品茗杯',group:'茶席',spec:'杯壁环带 · 70×55mm',icon:'M15 16 Q32 10 49 16 L44 37 Q32 44 20 37 Z M15 16 Q32 23 49 16 M21 38 H43'},
 {id:'茶叶罐',key:'jar',name:'茶叶罐',group:'茶席',spec:'罐身对称 · 80×90mm',icon:'M19 17 Q13 22 14 38 Q32 47 50 38 Q51 22 45 17 Z M18 15 Q32 7 46 15 M22 12 V8 H42 V12'},
 {id:'笔筒',key:'penholder',name:'文房笔筒',group:'文房',spec:'筒身四方 · 75×90mm',icon:'M19 15 Q32 9 45 15 V40 Q32 47 19 40 Z M19 15 Q32 23 45 15 M25 15 L22 5 M32 15 V3 M38 15 L43 4'},
 {id:'香插',key:'incense',name:'禅意香插',group:'文房',spec:'盘面留白 · 80×80mm',icon:'M8 35 Q32 24 56 35 Q32 48 8 35 Z M29 32 L39 5'},
 {id:'书签',key:'bookmark',name:'金属书签',group:'随身',spec:'修长镂雕 · 30×140mm',icon:'M25 6 H39 V44 L32 39 L25 44 Z M32 7 V2 M30 15 H34'},
 {id:'首饰盒',key:'box',name:'圆形首饰盒',group:'随身',spec:'盒盖聚焦 · 80×80mm',icon:'M12 20 Q32 7 52 20 V34 Q32 49 12 34 Z M12 20 Q32 34 52 20'},
 {id:'挂坠',key:'pendant',name:'随身挂坠',group:'随身',spec:'双面精雕 · 35×35mm',icon:'M32 11 C10 11 10 44 32 44 C54 44 54 11 32 11 Z M28 10 V4 H36 V10'}
];

const filteredVessels=computed(()=>vesselGroup.value==='全部'?vesselCatalog:vesselCatalog.filter(v=>v.group===vesselGroup.value||v.id==='帮我选择'));
const activeVesselInfo=computed(()=>vesselCatalog.find(v=>v.id===carrier.value)||vesselCatalog[1]);

const presets=[
 {label:'✨ 寿辰松鹤紫砂壶',recipient:'长辈',occasion:'生日祝寿',carrier:'茶壶',style:'宫廷吉金 · 团窠对称',text:'爷爷八十寿辰，平日酷爱品饮普洱，希望设计一把端庄稳重的紫砂锡镶茶壶，寄托松鹤延年、福寿安康的心意。'},
 {label:'✨ 宋韵莲心文房书签',recipient:'朋友',occasion:'节日祝福',carrier:'书签',style:'宋韵极简 · 疏朗留白',text:'挚友新迁书房，钟爱宋代极简留白美学，希望以赣南客家漏石窗四叶莲心纹定制一枚清雅书签。'},
 {label:'✨ 乔迁八方安宁茶承',recipient:'伴侣',occasion:'乔迁新居',carrier:'茶承',style:'当代解构 · 几何虚实',text:'乔迁新居茶席陈设，希望将壮族八角星纹与回纹结合，祝愿小家八方安宁、万事顺遂。'}
];

function applyPreset(p:typeof presets[0]){
 recipient.value=p.recipient;
 occasion.value=p.occasion;
 carrier.value=p.carrier;
 style.value=p.style;
 prompt.value=p.text;
}

const livePreview=computed(()=>{
 const occ=occasionOptions.find(o=>o.value===occasion.value)||occasionOptions[0];
 const rec=recipientOptions.find(r=>r.value===recipient.value)||recipientOptions[0];
 const patternCode=occ.wish==='长寿百岁'?'PAT-057 鹤纹 × PAT-039 寿字纹':(occ.wish==='莲心清正'?'PAT-001 客家漏石窗 × M-SY-006 四叶莲心':'PAT-005 八角星纹 × M-BW-020 八角框');
 const poem=occ.wish==='长寿百岁'?'“松鹤延年锡光暖，岁华常青福泽长。”':(occ.wish==='莲心清正'?'“四叶莲心映清茗，一窗雅序寄知音。”':'“八方锦绣归安宁，一器华纹载乾坤。”');
 return {occ,rec,patternCode,poem};
});

const brief=computed(()=>`赠送对象：${recipient.value}；场合：${occasion.value}；器物：${carrier.value}；风格：${style.value}；胎体材质：${baseMaterial.value}；锡镶工艺：${tinFinish.value}。补充要求：${prompt.value}`);

async function recommend(){
 busy.value=true;error.value='';activeStep.value=1;
 const timer=setInterval(()=>{if(activeStep.value<4)activeStep.value++},380);
 try{
  const r=await fetch('/api/creation/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:brief.value,vessel:activeVesselInfo.value.key,finish:tinFinish.value,base_material:baseMaterial.value})});
  const d=await r.json();if(!r.ok)throw Error(d.detail);
  result.value=d;
 }catch(e:any){error.value=e.message}finally{clearInterval(timer);activeStep.value=4;busy.value=false}
}

watch(activeVesselInfo,(v)=>{
 if(v&&v.key!=='auto'&&typeof localStorage!=='undefined'){
  localStorage.setItem('xiyu-user-vessel',v.key);
 }
});

function confirmRecommendation(){
 if(!result.value)return;
 if(activeVesselInfo.value.key!=='auto'){
  result.value.vessel=activeVesselInfo.value.key;
 }
 if(typeof localStorage!=='undefined'){
  localStorage.setItem('xiyu-user-vessel',result.value.vessel);
 }
 emit('confirm',result.value);
}
</script>
<template>
<section class="design-advisor" aria-label="AI 灵犀定制舱">
 <!-- Left Column: Structured Dropdowns & Bento Grid -->
 <div class="advisor-controls">
  <header class="advisor-header">
   <div class="advisor-header-top">
    <div class="advisor-badge-row">
     <span class="seed-pill"><i></i>DOUBAO-SEED 文化基因推理引擎</span>
     <span class="craft-pill">M / C / S / P 四维编码驱动</span>
    </div>
    <button type="button" class="advisor-close-btn" @click="emit('skip')" title="收起定制舱">✕ 收起定制舱</button>
   </div>
   <h2>你想为谁锻造一件藏着中国祝福的器物？</h2>
   <p>通过下方高定下拉矩阵或自然语言描述心意，AI 将自动完成意象解构、基因召回与锡镶器型匹配。</p>
  </header>

  <!-- Row 1: Structured Custom Dropdowns for Recipient & Occasion -->
  <div class="advisor-select-grid">
   <div class="select-card">
    <label for="advisor-recipient">
     <span class="dot gold"></span>赠送对象 / RECIPIENT
     <small>高定下拉选单</small>
    </label>
    <div class="select-wrap">
     <select id="advisor-recipient" v-model="recipient" aria-label="赠送对象">
      <option v-for="opt in recipientOptions" :key="opt.value" :value="opt.value">{{opt.label}}</option>
     </select>
     <span class="select-chevron" aria-hidden="true">▾</span>
    </div>
    <div class="quick-pills" role="group" aria-label="快捷选择赠送对象">
     <button type="button" v-for="item in ['长辈','朋友','伴侣','恩师','自己']" :key="item" :aria-pressed="recipient===item" @click="recipient=item">{{item}}</button>
    </div>
   </div>

   <div class="select-card">
    <label for="advisor-occasion">
     <span class="dot jade"></span>礼仪场合 / OCCASION
     <small>场景意象映射</small>
    </label>
    <div class="select-wrap">
     <select id="advisor-occasion" v-model="occasion" aria-label="赠礼场合">
      <option v-for="opt in occasionOptions" :key="opt.value" :value="opt.value">{{opt.label}}</option>
     </select>
     <span class="select-chevron" aria-hidden="true">▾</span>
    </div>
    <div class="quick-pills" role="group" aria-label="快捷选择赠礼场合">
     <button type="button" v-for="item in ['生日祝寿','节日祝福','乔迁新居','日常自用']" :key="item" :aria-pressed="occasion===item" @click="occasion=item">{{item}}</button>
    </div>
   </div>
  </div>

  <!-- Row 2: Vessel Filter Dropdown + Visual Vessel Bento Cards -->
  <div class="vessel-bento-box">
   <div class="vessel-bento-head">
    <label for="advisor-vessel-group">
     <span class="dot sky"></span>承载器物与锡镶形制 / VESSEL CARRIER
    </label>
    <div class="group-filter-select">
     <span>场域筛选：</span>
     <select id="advisor-vessel-group" v-model="vesselGroup" aria-label="器物场域筛选">
      <option value="全部">全部场域（茶席 / 文房 / 随身）</option>
      <option value="茶席">东方茶席（茶壶 / 茶承 / 茶杯 / 茶罐）</option>
      <option value="文房">文房清供（笔筒 / 香插）</option>
      <option value="随身">随身雅物（书签 / 首饰盒 / 挂坠）</option>
     </select>
    </div>
   </div>
   <div class="vessel-mini-grid" role="group" aria-label="器物偏好">
    <button type="button" v-for="v in filteredVessels" :key="v.id" class="vessel-mini-card" :aria-pressed="carrier===v.id" @click="carrier=v.id">
     <svg viewBox="0 0 64 52" aria-hidden="true"><path :d="v.icon"/></svg>
     <div>
      <strong>{{v.name}}</strong>
      <small>{{v.spec}}</small>
     </div>
    </button>
   </div>
  </div>

  <!-- Row 3: Triple Dropdown Matrix for Style, Base Material, Tin Finish -->
  <div class="triple-dropdown-row">
   <div class="mini-select-card">
    <label for="advisor-style">设计风格与构图气韵</label>
    <div class="select-wrap">
     <select id="advisor-style" v-model="style" aria-label="设计风格">
      <option value="简洁现代">简洁现代 · 宋韵疏朗留白</option>
      <option value="传统雅致">传统雅致 · 宫廷团窠对称</option>
      <option value="自然有机">自然有机 · 缠枝循迹生长</option>
      <option value="精巧华丽">精巧华丽 · 宝相多层复瓣</option>
     </select>
     <span class="select-chevron" aria-hidden="true">▾</span>
    </div>
   </div>
   <div class="mini-select-card">
    <label for="advisor-base">器物胎体材质</label>
    <div class="select-wrap">
     <select id="advisor-base" v-model="baseMaterial" aria-label="器物胎体材质">
      <option value="宜兴紫泥 · 深褐温润">宜兴紫泥 · 深褐温润</option>
      <option value="玄墨黑陶 · 幽邃内敛">玄墨黑陶 · 幽邃内敛</option>
      <option value="汝窑素瓷 · 温润如玉">汝窑素瓷 · 温润如玉</option>
     </select>
     <span class="select-chevron" aria-hidden="true">▾</span>
    </div>
   </div>
   <div class="mini-select-card">
    <label for="advisor-finish">威海锡镶表面工艺</label>
    <div class="select-wrap">
     <select id="advisor-finish" v-model="tinFinish" aria-label="威海锡镶表面工艺">
      <option value="锻打素锡 · 浅浮雕">锻打素锡 · 0.8mm浅浮雕</option>
      <option value="镜面亮锡 · 精密镂雕">镜面亮锡 · 精密镂空</option>
      <option value="鎏金暖锡 · 双色嵌饰">鎏金暖锡 · 双色吉金</option>
     </select>
     <span class="select-chevron" aria-hidden="true">▾</span>
    </div>
   </div>
  </div>

  <!-- Row 4: Prompt Textarea + One-Click Inspiration Presets -->
  <div class="prompt-box">
   <div class="prompt-head">
    <span>自然语言心意描述（支持一键填入比赛路演典范案例）</span>
    <div class="preset-pills">
     <button type="button" v-for="p in presets" :key="p.label" @click="applyPreset(p)">{{p.label}}</button>
    </div>
   </div>
   <textarea v-model="prompt" maxlength="3000" placeholder="送给谁？想表达什么故事或祝愿？偏好怎样的器型与构图秩序？" aria-label="设计需求描述"/>
  </div>

  <div class="advisor-actions">
   <button type="button" class="ai-action" :disabled="busy" :aria-busy="busy" @click="recommend">
    <span>✦ {{busy?'Doubao-Seed 正在推演文化基因谱系…':result?'重新推演基因方案':'查看 AI 基因搭配方案'}}</span>
   </button>
   <button type="button" class="skip-action" @click="emit('skip')">直接进入造物台 →</button>
  </div>
  <p v-if="error" class="advisor-error" role="alert">{{error}}</p>
 </div>

 <!-- Right Column: Holographic Seed Preview & CoT HUD -->
 <article class="advisor-hologram">
  <div class="hologram-topbar">
   <span class="live-indicator"><i></i>{{result?'SEED 基因推演已完成':'全息配方实时预演舱'}}</span>
   <code>{{result?result.source.id:livePreview.patternCode}}</code>
  </div>

  <!-- Interactive Sacred Geometry & Motif Medallion -->
  <div class="hologram-stage">
   <svg class="sacred-orbit" viewBox="0 0 220 220" aria-hidden="true">
    <circle cx="110" cy="110" r="96" fill="none" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 6"/>
    <circle cx="110" cy="110" r="78" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.6"/>
    <polygon points="110,14 206,110 110,206 14,110" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.45"/>
    <rect x="42" y="42" width="136" height="136" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.35"/>
   </svg>
   <div class="medallion-core">
    <svg viewBox="0 0 64 52" class="medallion-vessel" aria-hidden="true">
     <path :d="activeVesselInfo.icon"/>
    </svg>
    <span class="medallion-badge">{{activeVesselInfo.name}} · {{tinFinish.split(' · ')[0]}}</span>
   </div>
  </div>

  <!-- If AI Recommendation Result is Ready -->
  <div v-if="result" class="hologram-result">
   <div class="result-title-bar">
    <div>
     <small>推荐纹样母本 · 已通过基因白名单核验</small>
     <h3>{{result.source.name}} <span>{{result.source.id}}</span></h3>
    </div>
    <span class="mode-tag">{{result.mode==='doubao_seed_ai'?'Doubao-Seed 实时推理':'Seed 知识图谱引擎'}}</span>
   </div>
   <p class="result-summary">{{result.summary}}</p>
   <div class="meaning-tags" v-if="result.source.meanings?.length">
    <span>确认文化意象：</span>
    <b v-for="m in result.source.meanings" :key="m">{{m}}</b>
   </div>

   <!-- 4-Step Chain of Thought -->
   <div class="cot-steps" v-if="result.reasoning_steps?.length">
    <div v-for="st in result.reasoning_steps" :key="st.step" class="cot-row">
     <strong>{{st.step}}</strong>
     <span>{{st.detail}}</span>
    </div>
   </div>

   <!-- Blessing Inscription -->
   <div class="inscription-card">
    <small>✦ 一器一祝福 · 专属器物吉言铭文</small>
    <p>「{{result.blessing_inscription||'器载东方千秋意，锡镶华纹万事兴。'}}」</p>
    <span>工艺建议：{{result.craft_advice||'主纹采用 0.8mm 锻打素锡浅浮雕，外圈辅以精密线刻顺应器面曲率。'}}</span>
   </div>

   <button type="button" class="confirm-btn" @click="confirmRecommendation">
    采用此基因配方，进入三维器物锻造 →
   </button>
  </div>

  <!-- Live Holographic Preview Before Clicking Recommend -->
  <div v-else class="hologram-live-summary">
   <div class="live-matrix-grid">
    <div class="matrix-cell">
     <dt>受礼对象与场合</dt>
     <dd>{{recipient}} · {{occasion}}</dd>
     <small>{{livePreview.rec.tag}} → {{livePreview.occ.wish}}</small>
    </div>
    <div class="matrix-cell">
     <dt>承载器物与规格</dt>
     <dd>{{activeVesselInfo.name}}</dd>
     <small>{{activeVesselInfo.spec}}</small>
    </div>
    <div class="matrix-cell">
     <dt>构图气韵与风格</dt>
     <dd>{{style.split(' · ')[0]}}</dd>
     <small>{{baseMaterial.split(' · ')[0]}}</small>
    </div>
    <div class="matrix-cell">
     <dt>锡镶表面工艺</dt>
     <dd>{{tinFinish.split(' · ')[0]}}</dd>
     <small>PBR 浅浮雕 + 1:1 DXF</small>
    </div>
   </div>

   <div class="inscription-card preview-poem">
    <small>✦ 实时意象吉言预演 · 每一件器物都藏着一句中国祝福</small>
    <p>{{livePreview.poem}}</p>
    <span>候选基因母本：{{livePreview.patternCode}}</span>
   </div>
  </div>
 </article>
</section>
</template>
<style scoped>
.design-advisor {
 display:grid;
 grid-template-columns:1.35fr 1fr;
 gap:28px;
 padding:28px 30px;
 margin:18px 0 26px;
 background:radial-gradient(circle at 18% 15%, rgba(212,175,106,0.11), transparent 52%),
            radial-gradient(circle at 85% 80%, rgba(159,203,185,0.09), transparent 55%),
            linear-gradient(160deg, var(--bg-panel) 0%, var(--bg-canvas) 100%);
 border:1px solid rgba(212,175,106,0.32);
 border-radius:16px;
 color:var(--text-primary);
 box-shadow:0 24px 60px rgba(0,0,0,0.45);
}
.advisor-controls { display:flex; flex-direction:column; gap:16px; min-width:0; }
.advisor-header-top { display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:6px; }
.advisor-close-btn { background:rgba(255,255,255,0.06); border:1px solid rgba(212,175,106,0.3); border-radius:6px; color:var(--text-secondary); font-size:12px; padding:4px 12px; cursor:pointer; transition:all .2s; }
.advisor-close-btn:hover { color:var(--accent-gold); border-color:var(--accent-gold); background:rgba(212,175,106,0.14); }
.advisor-badge-row { display:flex; flex-wrap:wrap; gap:8px; }
.seed-pill, .craft-pill {
 display:inline-flex; align-items:center; gap:6px;
 padding:4px 10px; border-radius:999px; font-size:11px; letter-spacing:1px;
}
.seed-pill { background:rgba(212,175,106,0.14); border:1px solid rgba(212,175,106,0.4); color:var(--accent-gold); }
.seed-pill i { width:6px; height:6px; border-radius:50%; background:#34d399; box-shadow:0 0 8px #34d399; }
.craft-pill { background:rgba(159,203,185,0.12); border:1px solid rgba(159,203,185,0.3); color:#9fcbb9; }
.advisor-header h2 { font:26px/1.35 var(--font-serif, Georgia, serif); margin:0 0 6px; color:var(--text-primary); }
.advisor-header p { margin:0; font-size:13px; color:var(--text-secondary); line-height:1.6; }

.advisor-select-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.select-card, .vessel-bento-box, .mini-select-card, .prompt-box {
 background:rgba(255,255,255,0.025);
 border:1px solid var(--border-default);
 border-radius:12px;
 padding:14px;
 transition:border-color .2s, background .2s;
}
.select-card:focus-within, .mini-select-card:focus-within, .prompt-box:focus-within {
 border-color:var(--accent-gold);
 background:rgba(212,175,106,0.04);
}
.select-card label, .vessel-bento-head label, .mini-select-card label {
 display:flex; align-items:center; gap:6px;
 font-size:12px; color:var(--text-secondary); margin-bottom:8px; letter-spacing:.5px;
}
.select-card label small { margin-left:auto; color:var(--accent-gold); font-size:11px; }
.dot { width:7px; height:7px; border-radius:50%; display:inline-block; }
.dot.gold { background:var(--accent-gold); }
.dot.jade { background:#34d399; }
.dot.sky { background:#38bdf8; }

.select-wrap { position:relative; }
.select-wrap select {
 width:100%; appearance:none; -webkit-appearance:none;
 background:var(--bg-canvas); color:var(--text-primary);
 border:1px solid rgba(212,175,106,0.28); border-radius:8px;
 padding:9px 32px 9px 12px; font-size:13px; font-weight:500;
 min-height:40px; cursor:pointer;
}
.select-wrap select:focus { outline:none; border-color:var(--accent-gold); }
.select-chevron {
 position:absolute; right:11px; top:50%; transform:translateY(-50%);
 color:var(--accent-gold); pointer-events:none; font-size:13px;
}

.quick-pills { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
.quick-pills button {
 padding:4px 10px; min-height:28px; font-size:12px; border-radius:6px;
 background:var(--bg-elevated); border:1px solid var(--border-default); color:var(--text-secondary);
}
.quick-pills button[aria-pressed=true] {
 background:rgba(212,175,106,0.18); color:var(--accent-gold); border-color:var(--accent-gold);
}

.vessel-bento-head { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; margin-bottom:10px; }
.vessel-bento-head label { margin-bottom:0; }
.group-filter-select { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--text-secondary); }
.group-filter-select select {
 background:var(--bg-canvas); color:var(--accent-gold);
 border:1px solid rgba(212,175,106,0.3); border-radius:6px; padding:4px 8px; font-size:12px;
}
.vessel-mini-grid { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:8px; }
.vessel-mini-card {
 display:flex; flex-direction:column; align-items:flex-start; justify-content:space-between;
 gap:6px; padding:9px 10px; border-radius:9px; text-align:left;
 background:var(--bg-canvas); border:1px solid var(--border-default); color:var(--text-primary);
 min-height:74px; transition:transform .15s, border-color .15s;
}
.vessel-mini-card:hover { transform:translateY(-2px); border-color:rgba(212,175,106,0.5); }
.vessel-mini-card[aria-pressed=true] {
 background:rgba(212,175,106,0.16); border-color:var(--accent-gold);
 box-shadow:inset 0 0 0 1px var(--accent-gold);
}
.vessel-mini-card svg { width:28px; height:22px; fill:none; stroke:var(--accent-gold); stroke-width:1.6; stroke-linecap:round; stroke-linejoin:round; }
.vessel-mini-card strong { display:block; font-size:12px; color:var(--text-primary); }
.vessel-mini-card small { display:block; font-size:10px; color:var(--text-secondary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%; }

.triple-dropdown-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }

.prompt-head { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px; font-size:12px; color:var(--text-secondary); }
.preset-pills { display:flex; flex-wrap:wrap; gap:6px; }
.preset-pills button {
 padding:3px 9px; font-size:11px; border-radius:999px;
 background:rgba(212,175,106,0.12); border:1px solid rgba(212,175,106,0.35); color:var(--accent-gold);
}
.preset-pills button:hover { background:rgba(212,175,106,0.24); }
.prompt-box textarea {
 width:100%; min-height:68px; height:68px; padding:10px 12px;
 background:var(--bg-canvas); border:1px solid var(--border-default); border-radius:8px;
 color:var(--text-primary); font-size:13px; margin:0;
}

.advisor-actions { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.ai-action {
 flex:1; min-height:46px; padding:12px 20px; border-radius:10px; font-size:14px; font-weight:600;
 background:linear-gradient(135deg, #d8b574 0%, #c49b50 100%);
 color:#101715; border:1px solid #e6c98f;
 box-shadow:0 8px 24px rgba(212,175,106,0.25);
}
.ai-action:hover:not(:disabled) { filter:brightness(1.08); }
.skip-action {
 min-height:46px; padding:12px 18px; border-radius:10px; font-size:13px;
 background:var(--bg-elevated); color:var(--text-primary); border:1px solid var(--border-default);
}
.advisor-error { color:#f87171; font-size:13px; margin:0; }

/* Right Column Hologram */
.advisor-hologram {
 background:rgba(9,14,13,0.72);
 border:1px solid rgba(212,175,106,0.28);
 border-radius:14px; padding:22px;
 display:flex; flex-direction:column; justify-content:space-between; gap:16px;
}
.hologram-topbar {
 display:flex; align-items:center; justify-content:space-between; gap:8px;
 padding-bottom:12px; border-bottom:1px solid var(--border-default); font-size:12px;
}
.live-indicator { display:inline-flex; align-items:center; gap:7px; color:var(--accent-gold); font-weight:600; letter-spacing:1px; }
.live-indicator i { width:7px; height:7px; border-radius:50%; background:var(--accent-gold); box-shadow:0 0 8px var(--accent-gold); }
.hologram-topbar code { font-size:11px; padding:3px 8px; border-radius:4px; background:rgba(255,255,255,0.05); color:#9fcbb9; }

.hologram-stage {
 position:relative; height:175px; display:flex; align-items:center; justify-content:center;
 background:radial-gradient(circle, rgba(212,175,106,0.12) 0%, transparent 68%);
 border:1px solid rgba(255,255,255,0.06); border-radius:12px; overflow:hidden;
}
.sacred-orbit {
 position:absolute; width:168px; height:168px; color:var(--accent-gold);
 animation:advisor-spin 32s linear infinite; pointer-events:none;
}
@keyframes advisor-spin { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
.medallion-core { position:relative; z-index:2; display:flex; flex-direction:column; align-items:center; gap:8px; }
.medallion-vessel { width:68px; height:56px; fill:none; stroke:#f3e3c3; stroke-width:1.8; filter:drop-shadow(0 0 10px rgba(212,175,106,0.45)); }
.medallion-badge {
 padding:3px 12px; border-radius:999px; font-size:11px; font-weight:600;
 background:rgba(212,175,106,0.2); border:1px solid var(--accent-gold); color:#f7e7c4;
}

.live-matrix-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.matrix-cell {
 padding:11px 12px; border-radius:10px;
 background:rgba(255,255,255,0.03); border:1px solid var(--border-default);
}
.matrix-cell dt { font-size:11px; color:var(--text-secondary); }
.matrix-cell dd { margin:4px 0 2px; font-size:15px; font-weight:600; color:var(--text-primary); }
.matrix-cell small { font-size:11px; color:var(--accent-gold); }

.inscription-card {
 margin-top:12px; padding:13px 15px; border-radius:10px;
 background:linear-gradient(135deg, rgba(212,175,106,0.14), rgba(159,203,185,0.08));
 border:1px solid rgba(212,175,106,0.35);
}
.inscription-card small { display:block; font-size:11px; color:var(--accent-gold); letter-spacing:1px; }
.inscription-card p { margin:6px 0; font:16px/1.5 var(--font-serif, Georgia, serif); color:#f8ebd0; }
.inscription-card span { display:block; font-size:11px; color:var(--text-secondary); line-height:1.5; }

.result-title-bar { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }
.result-title-bar h3 { margin:2px 0 6px; font:22px/1.3 var(--font-serif, Georgia, serif); color:var(--accent-gold); }
.result-title-bar h3 span { font-size:12px; color:var(--text-secondary); font-family:monospace; }
.mode-tag { padding:3px 8px; border-radius:4px; font-size:11px; background:rgba(52,211,153,0.15); color:#6ee7b7; border:1px solid rgba(52,211,153,0.35); }
.result-summary { font-size:13px; line-height:1.75; color:var(--text-primary); margin:4px 0 10px; }
.meaning-tags { display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12px; margin-bottom:10px; }
.meaning-tags b { padding:2px 8px; border-radius:4px; background:rgba(212,175,106,0.15); color:var(--accent-gold); font-weight:500; }

.cot-steps { display:grid; gap:6px; margin:10px 0; }
.cot-row {
 display:flex; justify-content:space-between; gap:10px; padding:7px 10px;
 border-radius:7px; background:rgba(255,255,255,0.03); border:1px solid var(--border-default); font-size:11px;
}
.cot-row strong { color:#9fcbb9; white-space:nowrap; }
.cot-row span { color:var(--text-secondary); text-align:right; }

.confirm-btn {
 width:100%; margin-top:12px; min-height:44px; padding:11px 16px;
 border-radius:9px; font-size:13px; font-weight:600;
 background:var(--accent-gold); color:#101715; border:1px solid var(--accent-gold);
}
@media(max-width:1050px){
 .design-advisor { grid-template-columns:1fr; padding:20px; }
 .vessel-mini-grid { grid-template-columns:repeat(3,minmax(0,1fr)); }
}
@media(max-width:640px){
 .advisor-select-grid, .triple-dropdown-row, .live-matrix-grid { grid-template-columns:1fr; }
 .vessel-mini-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
</style>
