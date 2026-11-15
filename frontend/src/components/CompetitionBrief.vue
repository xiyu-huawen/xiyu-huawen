<script setup lang="ts">
defineProps<{stats:any}>();const emit=defineEmits(['navigate']);
</script>
<template>
<main class="competition-brief">
 <section class="competition-intro">
  <div class="intro-badge-row">
   <span class="pulse-badge"><i></i>AI 双擎驱动 × 省级非遗威海锡镶 × 产学研实证闭环</span>
   <span class="version-pill">FLAGSHIP v2.0 · 参赛路演全景展板</span>
  </div>
  <p class="kicker">XIYU HUAWEN / 以基因库守住纹样之根 · 以锡镶拓展纹样之用</p>
  <h1>每一件器物，<br>都藏着一句<em>中国祝福。</em></h1>
  <p class="intro-lead">
   「锡语华纹」以<strong>中国传统纹样四维文化基因库（M/C/S/P）</strong>为数据底座，融合 <strong>Doubao-Seed 文化基因推理大模型</strong>、<strong>Jimeng 4.5 东方器物实境渲染引擎</strong>与 <strong>Shapely 毫米级锡镶 DFM 工艺校验算法</strong>，打通从“文化溯源、AI 灵犀共创、三维曲面凝锡、自动工艺预检”到“1:1 DXF 工坊制版与非遗传承人手作精制”的完整数字化造物闭环。
  </p>
  <div class="hero-metrics-grid">
   <article><strong>{{stats.patterns||60}}<span>篇</span></strong><small>结构化考据纹样档案</small></article>
   <article><strong>402<span>条</span></strong><small>M/C/S/P 四维基因记录</small></article>
   <article><strong>12<span>类</span></strong><small>程序化三维锡镶器型</small></article>
   <article><strong>1 : 1<span>mm</span></strong><small>R2010 DXF 激光制版工程包</small></article>
  </div>
  <div class="competition-actions">
   <button class="primary" @click="emit('navigate','studio')">✦ 立即开启 AI 灵犀造物 →</button>
   <button @click="emit('navigate','atlas')">探索三维纹样星球 ↗</button>
   <button @click="emit('navigate','knowledge')">步入纹样书房 ↗</button>
  </div>
 </section>

 <section class="innovation-columns">
  <article>
   <span>核心壁垒 01 · 文化基因编码工程</span>
   <h2>一基因一编码，<br>让千年纹脉可溯可算。</h2>
   <p>严格遵循文化和旅游部非遗数字资源著录标准，将传统纹样拆解为图元（M）、构图（C）、语义（S）与工艺适配（P）四维基因，建立“意象词—基因—文献出处”多对多有向证据图谱，彻底告别无据拼贴与文化失真。</p>
   <strong>{{stats.genes||238}}<small>独立编码基因 · 100% 证据链闭环</small></strong>
  </article>
  <article>
   <span>核心壁垒 02 · Seed × Jimeng 双擎协同</span>
   <h2>听懂人间心意，<br>渲染东方实境大片。</h2>
   <p>由 Doubao-Seed 认知大模型解构赠礼语境、召回白名单基因并创作专属「一器一祝福」藏头吉言；联袂 Jimeng 4.5 视觉大模型提供宋韵茶席、紫檀博古、非遗案头、东方国礼四大光影棚拍，一键跨越三维白模与实境大片。</p>
   <strong>4<small>大东方实境摄影棚 · 实时思维链推演</small></strong>
  </article>
  <article>
   <span>核心壁垒 03 · 毫米级锡镶 DFM 校验</span>
   <h2>从三维流光凝锡，<br>直抵工坊 1:1 制版。</h2>
   <p>首创面向威海锡镶的 Shapely 几何拓扑 DFM 校验舱，实时扫描最细锡线宽度（≥1.0mm）、虚实镂空率、闭合连通域与器面曲率贴合度，自动标定 4 处隐蔽承力焊点坐标，一键输出 1:1 毫米制 DXF 工程包。</p>
   <strong>A 级<small>四阶制造可行性认证 · 零误差交接</small></strong>
  </article>
 </section>

 <section class="value-path">
  <p class="kicker">END-TO-END DIGITAL HERITAGE PIPELINE / 八步数字化活态传承闭环</p>
  <h2>不止让纹样被看见，<em>更让它在当代器物上重获新生。</em></h2>
  <div>
   <span>文献与实地采集</span><i>→</i>
   <span>M/C/S/P 基因编码</span><i>→</i>
   <span>Seed 语义推演</span><i>→</i>
   <span>参数化结构共创</span><i>→</i>
   <span>三维曲面凝锡</span><i>→</i>
   <span>DFM 激光校验</span><i>→</i>
   <span>Jimeng 实境棚拍</span><i>→</i>
   <span>1:1 工坊制版交付</span>
  </div>
  <p>每一次创作均同步生成 SVG 矢量快照、R2010 闭合轮廓 DXF、DFM 工艺诊断报告、Seed 吉言铭文与文化溯源档案，实现数字创意与非遗手作的无缝衔接。</p>
 </section>

 <section class="business-paths">
  <div>
   <p class="kicker">INDUSTRY-ACADEMIA-RESEARCH SYNERGY / 产学研用全方位落地验证</p>
   <h2>名师学术把关，<br>非遗工坊实证转化。</h2>
  </div>
  <article>
   <small>非遗传承人深度共创</small>
   <h3>威海金镶玉工艺品有限公司 × 李江玉老师</h3>
   <p>团队已与威海本地龙头锡镶企业「威海金镶玉工艺品有限公司」建立深度合作，由山东省省级非物质文化遗产（威海锡镶技艺）代表性传承人、技术总监<strong>李江玉老师</strong>担任首席工艺指导，共同制定锡镶工艺适配层规则并完成首批实物产品打样生产。</p>
   <span>产学研实证 · 传承人终审精制</span>
  </article>
  <article>
   <small>学术指导与实体公司运营</small>
   <h3>清华美院专家指导 × 200万注册资本主体</h3>
   <p>团队已对接清华大学美术学院<strong>张夫也教授</strong>推进艺术方向与纹样当代表达指导；并正式注册成立<strong>「威海锡语华纹文化科技有限公司」</strong>（注册资本 200 万元），构建完善的知识产权管理、成本核算与定制交付体系。</p>
   <span>公司化运作 · 权威学术赋能</span>
  </article>
  <article>
   <small>商业快闪验证与多场景拓展</small>
   <h3>2026 威海半马快闪首秀即实现备货全售罄</h3>
   <p>在 2026 威海半程马拉松期间开展线下快闪试运营，单日即实现销售额 <strong>2710 元</strong>、首批备货 <strong>100% 售罄</strong>，有力验证了“标准文创 + AI 个性定制 + 研学美育体验”三轨商业模式的市场吸引力。</p>
   <span>真实商业闭环 · 首批备货售罄</span>
  </article>
 </section>

 <section class="business-paths">
  <div>
   <p class="kicker">SCENARIO MATRIX / 三大核心赋能场域</p>
   <h2>同一份文化基因资产，<br>激活多元消费与美育生态。</h2>
  </div>
  <article>
   <small>01 · 高定个人礼赠</small>
   <h3>把心意锻造成独一无二的东方器物</h3>
   <p>围绕祝寿、乔迁、婚嫁、知音赠礼等场景，用户通过 AI 灵犀定制舱 30 秒生成有据可查的纹样配方与吉言铭文，实时预览三维紫砂锡器并一键提交工坊定制。</p>
   <button @click="emit('navigate','studio')">体验高定礼赠设计 →</button>
  </article>
  <article>
   <small>02 · 城市国礼与机构文创</small>
   <h3>可复用基因配方支撑系列化敏捷开发</h3>
   <p>面向高校纪念、文旅城市伴手礼与政企机构定制，依托十二类标准化器型与参数化母版，大幅缩短传统锡镶从纹样构思到工程制版的设计周期。</p>
   <button @click="emit('navigate','original')">进入活态共创工坊 →</button>
  </article>
  <article>
   <small>03 · 高校与非遗美育研学</small>
   <h3>在交互式探索中读懂中华造物智慧</h3>
   <p>连接三维纹样星球、17 篇故宫及权威机构考据读本、对称实验室与自由手绘工坊，让青年学子在亲手拆解与重组纹样中完成有深度的文化美育实践。</p>
   <button @click="emit('navigate','knowledge')">走进纹样书房 →</button>
  </article>
 </section>

 <section class="value-path">
  <p class="kicker">STRATEGIC ROADMAP / 阶段建设路线图</p>
  <h2>先跑通数字智造闭环，<em>再铸就国家级纹样基因底座。</em></h2>
  <p><strong>第一阶段（已完成闭环验证）</strong>：建成 60 篇深度考据纹样样本、238 个独立编码、402 条基因记录与 145 份高精度矢量图元；上线三维纹样星球、十二器型实时 PBR 孪生剧场、Doubao-Seed × Jimeng 4.5 双擎协同与 1:1 毫米级 DXF 工程包交付系统，完成威海半马快闪商业首秀。</p>
  <p><strong>第二阶段（2026.11—2027.06 区域深采与产线联调）</strong>：推进苏州、北京、广州、深圳/香港及华北、华东、西南五大片区博物馆与传统村落实地采集；联合李江玉老师工坊深化曲面展开与激光下料参数库，拓展高校美育课程与城市礼物合作。</p>
  <p><strong>第三阶段（2027.07—2027.12 规模化生态成型）</strong>：达成累计 <strong>500+ 篇传统纹样档案、2000+ 个可计算文化基因</strong>的阶段建设目标，沉淀行业领先的非遗纹样数字化提取、语义编码与金属工艺转译标准体系。</p>
 </section>

 <section class="competition-proof">
  <h2>以基因库守住纹样之根，以锡镶拓展纹样之用。</h2>
  <p>现在，选一份心意，启动 AI 双擎推演，亲手锻造您的第一件数字非遗器物。</p>
  <button class="primary" @click="emit('navigate','studio')">✦ 立即进入 AI 造物台 →</button>
 </section>
</main>
</template>
<style scoped>
.intro-badge-row { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:14px; }
.pulse-badge { display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:999px; background:rgba(212,175,106,0.12); border:1px solid rgba(212,175,106,0.38); color:var(--accent-gold); font-size:12px; letter-spacing:1px; }
.pulse-badge i { width:8px; height:8px; border-radius:50%; background:#34d399; box-shadow:0 0 10px #34d399; }
.version-pill { padding:5px 12px; border-radius:999px; background:rgba(159,203,185,0.12); border:1px solid rgba(159,203,185,0.3); color:#9fcbb9; font-size:11px; letter-spacing:1.5px; }
.intro-lead { font-size:16px; line-height:1.95; max-width:920px; }
.intro-lead strong { color:var(--accent-gold); font-weight:600; }
.hero-metrics-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:26px 0; max-width:920px; }
.hero-metrics-grid article { padding:18px 16px; background:linear-gradient(145deg, rgba(255,255,255,0.04), rgba(212,175,106,0.05)); border:1px solid rgba(212,175,106,0.25); border-radius:10px; }
.hero-metrics-grid strong { display:block; font:32px/1.2 var(--font-serif, Georgia, serif); color:var(--accent-gold); }
.hero-metrics-grid strong span { font-size:14px; margin-left:4px; color:var(--text-secondary); }
.hero-metrics-grid small { display:block; margin-top:6px; font-size:12px; color:var(--text-secondary); }
@media(max-width:760px){ .hero-metrics-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
</style>
