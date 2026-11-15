<script setup lang="ts">
import { ref, computed } from 'vue';
import * as T from 'three';
import { createReliefGeometries, parseMotifSvg } from '../three/motifGeometry.js';
import { STLExporter } from 'three/addons/exporters/STLExporter.js';

const props = withDefaults(defineProps<{
  modelValue: boolean;
  design: any;
  width?: number;
  height?: number;
}>(), {
  width: 120,
  height: 120
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();

const materials = [
  {
    code: 'pla',
    name: 'PLA',
    label: '聚乳酸 · 常见通用',
    badge: '首选入门 ★☆☆☆☆',
    desc: '最常见易打的环保耗材，收缩率极低、不易翘边，非常适合快速手板与非遗纹样视觉打样。',
    nozzle: '200 - 215 ℃',
    bed: '50 - 60 ℃',
    layer: '0.12 - 0.20 mm',
    infill: '15% - 20%',
    speed: '50 - 80 mm/s',
    cooling: '100% 强风',
    enclosure: '无需封箱',
    density: 1.24
  },
  {
    code: 'petg',
    name: 'PETG',
    label: '高韧聚酯 · 耐温防水',
    badge: '简单易打 ★★☆☆☆',
    desc: '高韧性抗冲击、耐湿热耐老化，适合茶承托盘底座、日用器物配件等具有功能承载要求的打样。',
    nozzle: '230 - 245 ℃',
    bed: '70 - 80 ℃',
    layer: '0.16 - 0.20 mm',
    infill: '20% - 30%',
    speed: '40 - 60 mm/s',
    cooling: '30% - 50% 微风',
    enclosure: '无需封箱',
    density: 1.27
  },
  {
    code: 'abs',
    name: 'ABS',
    label: '工程刚性 · 耐温可抛光',
    badge: '工业进阶 ★★★☆☆',
    desc: '工业级高刚度抗冲击，耐热达100℃以上，支持丙酮蒸汽熏蒸镜面抛光，消除层纹达到注塑光洁度。',
    nozzle: '245 - 255 ℃',
    bed: '95 - 105 ℃',
    layer: '0.12 - 0.20 mm',
    infill: '20% - 35%',
    speed: '40 - 60 mm/s',
    cooling: '0% - 20% (微风)',
    enclosure: '建议保温封箱',
    density: 1.04
  },
  {
    code: 'resin',
    name: '光敏树脂',
    label: 'SLA/LCD · 超高精微雕',
    badge: '微雕光固化 ★★☆☆☆',
    desc: '微米级超高分辨率与光滑表面，完美还原非遗细金微雕、浅浮雕与镂空花纹细节，失蜡精密铸造首选。',
    nozzle: '常温光固化 (25 ℃)',
    bed: '室温成型平台',
    layer: '0.03 - 0.05 mm',
    infill: '100% (实心微雕)',
    speed: '单层曝光 2.2 - 3.2s',
    cooling: 'IPA清洗 + UV二次固化',
    enclosure: '避光罩',
    density: 1.15
  },
  {
    code: 'tpu',
    name: 'TPU',
    label: '热塑弹性体 · 减震防滑',
    badge: '柔性软胶 ★★★☆☆',
    desc: '高弹性柔韧耐磨，适合器物防滑底垫、减震脚托和柔性保护套件打印。',
    nozzle: '215 - 230 ℃',
    bed: '40 - 50 ℃',
    layer: '0.16 - 0.24 mm',
    infill: '15% - 25%',
    speed: '20 - 30 mm/s (慢速直驱)',
    cooling: '50% - 100%',
    enclosure: '无需封箱',
    density: 1.21
  }
];

const selectedMaterial = ref('pla');
const thickness = ref<number>(1.2);
const withBase = ref(true);
const isExporting = ref(false);

const curMat = computed(() => materials.find(m => m.code === selectedMaterial.value) || materials[0]);

const effWidth = computed(() => Number(props.width || props.design?.recipe?.width_mm) || 120);
const effHeight = computed(() => Number(props.height || props.design?.recipe?.height_mm) || 120);
const totalThickness = computed(() => Number((thickness.value + (withBase.value ? 1.0 : 0.0)).toFixed(2)));

const estVolumeCm3 = computed(() => {
  const areaRatio = 0.35;
  const volMm3 = effWidth.value * effHeight.value * areaRatio * thickness.value + (withBase.value ? effWidth.value * effHeight.value * 1.0 : 0);
  return Number((volMm3 / 1000).toFixed(2));
});

const estWeightG = computed(() => {
  return Number((estVolumeCm3.value * curMat.value.density).toFixed(1));
});

function close() {
  emit('update:modelValue', false);
}

function generateLocalStlBlob(): Blob | null {
  const svgStr = props.design?.svg;
  if (!svgStr) return null;

  try {
    const group = new T.Group();
    const parsed = parseMotifSvg(svgStr);
    const w = effWidth.value;
    const h = effHeight.value;
    const factor = Math.min(w, h) / 1000;
    const t = thickness.value;

    for (const path of parsed.paths) {
      for (const geo of createReliefGeometries(path, {
        depth: t,
        bevelEnabled: false
      })) {
        const pos = geo.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          const x = (pos.getX(i) - 500) * factor + w / 2;
          const y = -(pos.getY(i) - 500) * factor + h / 2;
          const z = pos.getZ(i);
          pos.setXYZ(i, x, y, z);
        }
        geo.computeVertexNormals();
        const mesh = new T.Mesh(geo);
        group.add(mesh);
      }
    }

    if (withBase.value) {
      const baseGeo = new T.BoxGeometry(w, h, 1.0);
      baseGeo.translate(w / 2, h / 2, -0.5);
      const baseMesh = new T.Mesh(baseGeo);
      group.add(baseMesh);
    }

    const exporter = new STLExporter();
    const stlData = exporter.parse(group, { binary: true }) as DataView;
    return new Blob([stlData.buffer], { type: 'application/octet-stream' });
  } catch (err) {
    console.error('Three.js STL generation error:', err);
    return null;
  }
}

async function exportStlDirect() {
  isExporting.value = true;
  try {
    let blob = generateLocalStlBlob();
    const did = props.design?.id || 'model';
    const filename = `${did}-3dprint-${selectedMaterial.value}-${effWidth.value}x${effHeight.value}mm.stl`;

    if (!blob) {
      const res = await fetch('/api/manufacturing/export-stl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          svg: props.design?.svg,
          width_mm: effWidth.value,
          height_mm: effHeight.value,
          material: selectedMaterial.value,
          thickness_mm: thickness.value,
          with_base: withBase.value
        })
      });
      if (!res.ok) throw new Error('导出 STL 模型失败');
      blob = await res.blob();
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (e: any) {
    alert(e.message || '导出 3D 打印模型失败，请检查网络或设计轮廓');
  } finally {
    isExporting.value = false;
  }
}

async function exportFullPackage() {
  const did = props.design?.id;
  if (did) {
    const url = `/api/manufacturing/${did}/3dprint-package?material=${selectedMaterial.value}&thickness=${thickness.value}&with_base=${withBase.value}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `${did}-3dprint-${selectedMaterial.value}-bundle.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    exportStlDirect();
  }
}
</script>

<template>
  <div v-if="modelValue" class="modal-backdrop" @click.self="close" @keydown.esc="close">
    <div class="print-modal-container" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <header class="modal-header">
        <div>
          <span class="sub-kicker">3D PRINTING DFM &amp; SLICING SUITE</span>
          <h3 id="modal-title">导出 1:1 毫米级 3D 打印模型与材料工艺包</h3>
          <p class="modal-sub">支持常见 3D 打印材料快速打样与实物切片验证，直连 Bambu Studio、Cura、PrusaSlicer 等切片机。</p>
        </div>
        <button class="btn-close" @click="close" aria-label="关闭窗口">✕</button>
      </header>

      <div class="modal-body">
        <!-- Section 1: Material Selection Tabs -->
        <section class="section-block">
          <label class="section-title">01 · 选择 3D 打印材料</label>
          <div class="material-card-grid">
            <button
              v-for="mat in materials"
              :key="mat.code"
              type="button"
              class="mat-card"
              :class="{ active: selectedMaterial === mat.code }"
              @click="selectedMaterial = mat.code"
            >
              <div class="mat-card-head">
                <strong>{{ mat.name }}</strong>
                <span class="mat-badge">{{ mat.badge }}</span>
              </div>
              <span class="mat-label">{{ mat.label }}</span>
              <p class="mat-desc">{{ mat.desc }}</p>
            </button>
          </div>
        </section>

        <!-- Section 2: Form & Base Specifications -->
        <section class="section-block specs-row">
          <div class="specs-col">
            <label class="section-title">02 · 浮雕成型厚度</label>
            <div class="thickness-pills">
              <button
                v-for="th in [0.8, 1.2, 1.6, 2.0]"
                :key="th"
                type="button"
                :class="{ active: thickness === th }"
                @click="thickness = th"
              >
                {{ th }} mm <small v-if="th === 0.8">(传统锡片)</small><small v-else-if="th === 1.2">(推荐FDM)</small>
              </button>
            </div>
          </div>

          <div class="specs-col">
            <label class="section-title">03 · 工艺试打基底</label>
            <div class="base-toggle-box">
              <label class="radio-label">
                <input type="radio" :value="true" v-model="withBase" />
                <span><strong>附带 1.0mm 工艺测试底板</strong><small>推荐 · 保证微细孤岛线条在热床稳固附着，防脱落防翘边</small></span>
              </label>
              <label class="radio-label">
                <input type="radio" :value="false" v-model="withBase" />
                <span><strong>仅导出镂空纹样浮雕 (无底板)</strong><small>1:1 纯金属浮雕实体，适合直接嵌入紫砂/木器凹槽</small></span>
              </label>
            </div>
          </div>
        </section>

        <!-- Section 3: Material Slicing Guide & Estimated Volume Card -->
        <section class="section-block guide-panel">
          <div class="guide-header">
            <h4>✦ 当前材料【{{ curMat.name }}】切片与打印工艺指引</h4>
            <div class="est-tags">
              <span>实物尺寸：<b>{{ effWidth }} × {{ effHeight }} × {{ totalThickness }} mm</b></span>
              <span>预估体积：<b>约 {{ estVolumeCm3 }} cm³</b></span>
              <span>预估耗材：<b>约 {{ estWeightG }} g</b></span>
            </div>
          </div>

          <div class="guide-params-grid">
            <div class="param-box">
              <small>推荐喷嘴/挤出温度</small>
              <strong>{{ curMat.nozzle }}</strong>
            </div>
            <div class="param-box">
              <small>推荐热床底板温度</small>
              <strong>{{ curMat.bed }}</strong>
            </div>
            <div class="param-box">
              <small>推荐切片层高</small>
              <strong>{{ curMat.layer }}</strong>
            </div>
            <div class="param-box">
              <small>推荐内部填充率</small>
              <strong>{{ curMat.infill }}</strong>
            </div>
            <div class="param-box">
              <small>成型速度建议</small>
              <strong>{{ curMat.speed }}</strong>
            </div>
            <div class="param-box">
              <small>冷却与环境要求</small>
              <strong>{{ curMat.cooling }} · {{ curMat.enclosure }}</strong>
            </div>
          </div>

          <p class="guide-notice">
            💡 <b>非遗微雕打印技巧</b>：锡镶镂空线条较细，建议在切片软件中开启「薄壁检测 (Detect Thin Walls)」与「精确壁厚 (Arachne 壁生成引擎)」；若是光敏树脂打印，建议倾斜 35° 摆放并添加树状支撑，以获得最佳镜面质感。
          </p>
        </section>
      </div>

      <footer class="modal-footer">
        <div class="footer-left-info">
          <span>1:1 毫米工程 STL 格式 · 广泛兼容拓竹 Bambu Lab、创想三维、Anycubic、Prusa 等主流设备</span>
        </div>
        <div class="footer-actions">
          <button type="button" class="btn-secondary" @click="close">取消</button>
          <button type="button" class="btn-primary" :disabled="isExporting" @click="exportStlDirect">
            {{ isExporting ? '正在生成 3D 模型...' : '一键导出 .STL 3D打印模型' }}
          </button>
          <button type="button" class="btn-accent" :disabled="isExporting" @click="exportFullPackage">
            打包下载 3D 打印完整工程包 (.ZIP) ↗
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(8, 12, 11, 0.78);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.print-modal-container {
  background: var(--bg-elevated, #16201c);
  border: 1px solid var(--border-default, #2a3a33);
  border-radius: 14px;
  width: min(860px, 94vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(212, 175, 106, 0.2);
  color: var(--text-primary, #e6eee9);
  overflow: hidden;
  animation: modal-enter 0.25s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes modal-enter {
  from { opacity: 0; transform: scale(0.96) translateY(12px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border-default, #2a3a33);
}
.sub-kicker {
  display: block;
  font-size: 11px;
  letter-spacing: 2px;
  color: var(--accent-gold, #d4af6a);
  font-weight: 600;
  margin-bottom: 4px;
}
.modal-header h3 {
  font-size: 19px;
  margin: 0 0 6px;
  color: var(--text-primary, #e6eee9);
  font-weight: 600;
}
.modal-sub {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary, #94a39b);
  line-height: 1.6;
}
.btn-close {
  background: transparent;
  border: 1px solid var(--border-default, #2a3a33);
  color: var(--text-secondary, #94a39b);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s;
}
.btn-close:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary, #e6eee9);
}
.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(212, 175, 106, 0.3) transparent;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.section-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-gold, #d4af6a);
  letter-spacing: 1px;
}
.material-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}
.mat-card {
  background: var(--bg-canvas, #0f1614);
  border: 1px solid var(--border-default, #24342d);
  border-radius: 8px;
  padding: 12px 14px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 5px;
  transition: all 0.2s;
  color: inherit;
}
.mat-card:hover {
  border-color: rgba(212, 175, 106, 0.4);
  background: rgba(212, 175, 106, 0.04);
}
.mat-card.active {
  border-color: var(--accent-gold, #d4af6a);
  background: rgba(212, 175, 106, 0.12);
  box-shadow: 0 0 12px rgba(212, 175, 106, 0.16);
}
.mat-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mat-card-head strong {
  font-size: 15px;
  color: #fff;
}
.mat-badge {
  font-size: 10px;
  padding: 2px 5px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  color: var(--text-secondary, #94a39b);
}
.mat-card.active .mat-badge {
  background: rgba(212, 175, 106, 0.25);
  color: #f7dfa5;
}
.mat-label {
  font-size: 11px;
  color: var(--accent-gold, #d4af6a);
}
.mat-desc {
  margin: 0;
  font-size: 10.5px;
  line-height: 1.45;
  color: var(--text-secondary, #82928a);
}

.specs-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 680px) {
  .specs-row {
    grid-template-columns: 1fr;
  }
}
.specs-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.thickness-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.thickness-pills button {
  flex: 1;
  min-width: 80px;
  padding: 8px 10px;
  background: var(--bg-canvas, #0f1614);
  border: 1px solid var(--border-default, #24342d);
  border-radius: 6px;
  color: var(--text-secondary, #94a39b);
  cursor: pointer;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  transition: all 0.2s;
}
.thickness-pills button.active {
  border-color: var(--accent-gold, #d4af6a);
  background: rgba(212, 175, 106, 0.15);
  color: #fff;
}
.thickness-pills button small {
  font-size: 9.5px;
  opacity: 0.8;
}

.base-toggle-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.radio-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: var(--bg-canvas, #0f1614);
  border: 1px solid var(--border-default, #24342d);
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
}
.radio-label input {
  margin-top: 3px;
  accent-color: var(--accent-gold, #d4af6a);
}
.radio-label span {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.radio-label small {
  font-size: 10.5px;
  color: var(--text-secondary, #82928a);
}

.guide-panel {
  background: rgba(212, 175, 106, 0.05);
  border: 1px solid rgba(212, 175, 106, 0.25);
  border-radius: 10px;
  padding: 16px;
}
.guide-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}
.guide-header h4 {
  margin: 0;
  font-size: 13px;
  color: var(--accent-gold, #d4af6a);
}
.est-tags {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary, #94a39b);
}
.est-tags b {
  color: #6ee7b7;
}
.guide-params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}
.param-box {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid var(--border-default, #24342d);
  border-radius: 6px;
  padding: 8px 10px;
}
.param-box small {
  display: block;
  font-size: 10px;
  color: var(--text-secondary, #82928a);
  margin-bottom: 3px;
}
.param-box strong {
  display: block;
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.guide-notice {
  margin: 0;
  font-size: 11px;
  line-height: 1.6;
  color: var(--text-secondary, #94a39b);
  border-top: 1px dashed rgba(212, 175, 106, 0.2);
  padding-top: 10px;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid var(--border-default, #2a3a33);
  background: rgba(0, 0, 0, 0.2);
  gap: 16px;
  flex-wrap: wrap;
}
.footer-left-info {
  font-size: 11px;
  color: var(--text-secondary, #82928a);
}
.footer-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
.footer-actions button {
  padding: 9px 16px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-default, #2a3a33);
  color: var(--text-secondary, #94a39b);
}
.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}
.btn-primary {
  background: var(--bg-canvas, #101715);
  border: 1px solid var(--accent-gold, #d4af6a);
  color: var(--accent-gold, #d4af6a);
}
.btn-primary:hover {
  background: rgba(212, 175, 106, 0.15);
}
.btn-accent {
  background: var(--accent-gold, #d4af6a);
  border: 1px solid var(--accent-gold, #d4af6a);
  color: #101715;
  font-weight: 600;
}
.btn-accent:hover {
  background: #deb872;
}
</style>
