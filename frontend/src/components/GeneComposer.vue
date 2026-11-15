<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';

const props = defineProps<{ design: any }>();
const emit = defineEmits(['change']);

const genes = ref<any[]>([]);
const search = ref('');
const role = ref('center');
const open = ref(false);
const origin = ref('all');

const roles = [
  { id: 'frame', name: '框架', codeNum: '01', note: '保留外缘识别', icon: '◰' },
  { id: 'center', name: '主纹', codeNum: '02', note: '留住视觉中心', icon: '✦' },
  { id: 'ring', name: '环饰', codeNum: '03', note: '组织环绕节奏', icon: '◎' },
  { id: 'accent', name: '点缀', codeNum: '04', note: '建立细部层次', icon: '❖' }
];

const pool = computed(() =>
  genes.value
    .filter(
      g =>
        g.type === '图元' &&
        (g.status === '已确认' || (g.origin === 'contemporary' && g.status === '可复用')) &&
        g.assets?.some((a: any) => a.svg) &&
        (origin.value === 'all' || (g.origin || 'heritage') === origin.value) &&
        (!search.value || (g.name + g.code + g.pattern).toLowerCase().includes(search.value.toLowerCase()))
    )
    .slice(0, 48)
);

const chosen = computed(() =>
  props.design.genes.map((g: any, i: number) => ({
    ...g,
    role: g.role || roles[i]?.id
  }))
);

function getGeneForRole(roleId: string) {
  return chosen.value.find((g: any) => g.role === roleId);
}

function isRoleLocked(roleId: string) {
  return !!(props.design.recipe?.anchor_locked && props.design.recipe?.anchor?.role === roleId);
}

async function openPicker(id: string) {
  role.value = id;
  open.value = true;
  await nextTick();
  const input = document.querySelector<HTMLInputElement>('.gene-picker input');
  input?.focus();
  try {
    if (!genes.value.length) {
      const response = await fetch('/api/genes');
      if (response.ok) genes.value = await response.json();
    }
  } catch {}
}

function pick(g: any) {
  const selections = chosen.value
    .filter((x: any) => x.role !== role.value)
    .map((x: any) => ({
      pattern_id: x.pattern,
      code: x.code,
      role: x.role
    }));
  selections.push({
    pattern_id: g.pattern,
    code: g.code,
    role: role.value
  });
  emit('change', selections);
  open.value = false;
}

onMounted(async () => {
  try {
    const r = await fetch('/api/genes');
    if (r.ok) genes.value = await r.json();
  } catch {}
});
</script>

<template>
  <section class="gene-composer">
    <!-- Header -->
    <div class="composer-header">
      <div class="composer-header-top">
        <span class="seed-indicator"><i class="pulse-dot"></i>AI CULTURAL RECIPE</span>
        <span class="cross-badge">跨样本选配</span>
      </div>
      <h3>四层意象自由调谐</h3>
      <p class="composer-lead">按「框架 / 主纹 / 环饰 / 点缀」四层语法，AI 自适应解构并重组非遗意象。</p>
    </div>

    <!-- Vertical Stack of 4 Layer Cards -->
    <div class="layer-stack" role="group" aria-label="四层图元调谐">
      <div
        v-for="r in roles"
        :key="r.id"
        class="layer-row-card"
        :class="{
          active: open && role === r.id,
          locked: isRoleLocked(r.id),
          'has-art': !!getGeneForRole(r.id)
        }"
      >
        <!-- Left: Thumbnail Box -->
        <div class="thumb-box" @click="!isRoleLocked(r.id) && openPicker(r.id)">
          <img
            v-if="getGeneForRole(r.id)?.asset?.url"
            :src="getGeneForRole(r.id).asset.url"
            :alt="r.name"
            class="gene-thumb-img"
          />
          <div v-else class="thumb-empty">
            <span class="role-icon">{{ r.icon }}</span>
          </div>
        </div>

        <!-- Middle: Info Column -->
        <div class="layer-meta" @click="!isRoleLocked(r.id) && openPicker(r.id)">
          <div class="layer-tag-row">
            <span class="role-pill">{{ r.codeNum }} {{ r.name }}</span>
            <span v-if="isRoleLocked(r.id)" class="lock-pill">🔒 结构已锁定</span>
            <span v-else class="note-pill">{{ r.note }}</span>
          </div>
          <div class="gene-title-row">
            <strong v-if="getGeneForRole(r.id)" class="gene-name">
              {{ getGeneForRole(r.id).name.replace(/〔.*?〕/g, '') }}
            </strong>
            <span v-else class="gene-placeholder">选择一枚非遗图元</span>
          </div>
          <div v-if="getGeneForRole(r.id)" class="gene-code-row">
            <code>{{ getGeneForRole(r.id).pattern }} · {{ getGeneForRole(r.id).code }}</code>
          </div>
        </div>

        <!-- Right: Action Button -->
        <div class="layer-action-col">
          <button
            type="button"
            class="swap-btn"
            :disabled="isRoleLocked(r.id)"
            :title="isRoleLocked(r.id) ? '主纹结构已锁定' : '更换此层图元'"
            @click="openPicker(r.id)"
          >
            {{ isRoleLocked(r.id) ? '已锁定' : getGeneForRole(r.id) ? '更换 ↗' : '选择 ＋' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Gene Picker Drawer / Panel -->
    <transition name="picker-slide">
      <div v-if="open" class="gene-picker">
        <div class="picker-top">
          <div class="picker-title-group">
            <span class="picker-target-tag">选择「{{ roles.find(r => r.id === role)?.name }}」层图元</span>
            <small>AI 实时适配器面微曲率与浅浮雕公差</small>
          </div>
          <button type="button" class="close-picker-btn" @click="open = false" aria-label="关闭图元选择器">✕</button>
        </div>

        <div class="picker-search-bar">
          <input
            v-model="search"
            placeholder="搜索图元名称、编码或 PAT 编号…"
            aria-label="搜索可用图元"
          />
          <button v-if="search" type="button" class="clear-search" @click="search = ''">✕</button>
        </div>

        <div class="picker-filter-tabs">
          <button
            type="button"
            v-for="(label, key) in { all: '全部图元', heritage: '传统资料', contemporary: '当代共创' }"
            :key="key"
            :class="{ selected: origin === key }"
            @click="origin = key"
          >
            {{ label }}
          </button>
        </div>

        <div class="picker-grid-wrap">
          <div v-if="pool.length" class="picker-bento-grid">
            <button
              v-for="g in pool"
              :key="g.pattern + g.code"
              type="button"
              class="picker-gene-card"
              :class="{ 'is-contemporary': g.origin === 'contemporary' }"
              @click="pick(g)"
            >
              <div class="card-thumb">
                <img :src="g.assets[0].url" :alt="g.name" loading="lazy" />
              </div>
              <div class="card-text">
                <span class="card-name">{{ g.name.replace(/〔.*?〕/g, '') }}</span>
                <code class="card-code">{{ g.pattern }} · {{ g.code }}</code>
              </div>
            </button>
          </div>
          <div v-else class="picker-empty">
            <p>没有匹配的图元，请尝试输入“莲”、“星”或“PAT-005”。</p>
          </div>
        </div>
      </div>
    </transition>
  </section>
</template>

<style scoped>
.gene-composer {
  color: var(--text-primary);
  background: var(--bg-panel, #0f1615);
  border: 1px solid var(--border-default, rgba(212, 175, 106, 0.25));
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
  box-sizing: border-box;
}

/* Header */
.composer-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 10px;
}
.composer-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.seed-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  letter-spacing: 1.2px;
  color: var(--accent-gold, #d4af6a);
  font-weight: 600;
}
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px #34d399;
}
.cross-badge {
  font-size: 10px;
  color: var(--text-secondary, #9ca3af);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 2px 7px;
  border-radius: 12px;
}
.composer-header h3 {
  font-family: var(--font-serif, Georgia, serif);
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #f3ece0);
  margin: 2px 0 0;
  letter-spacing: 0.5px;
}
.composer-lead {
  font-size: 11px;
  color: var(--text-secondary, #9ca3af);
  margin: 0;
  line-height: 1.5;
}

/* Vertical Layer Cards */
.layer-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.layer-row-card {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-default, rgba(255, 255, 255, 0.08));
  border-radius: 8px;
  transition: all 0.2s ease;
}
.layer-row-card:hover {
  background: rgba(212, 175, 106, 0.04);
  border-color: rgba(212, 175, 106, 0.3);
}
.layer-row-card.active {
  background: rgba(212, 175, 106, 0.08);
  border-color: var(--accent-gold, #d4af6a);
  box-shadow: 0 0 12px rgba(212, 175, 106, 0.15);
}
.layer-row-card.locked {
  opacity: 0.7;
  background: rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.04);
}

/* Thumbnail Box */
.thumb-box {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  background: #141f1c;
  border: 1px solid rgba(212, 175, 106, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
}
.gene-thumb-img {
  width: 38px;
  height: 38px;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}
.thumb-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: rgba(212, 175, 106, 0.4);
}
.role-icon {
  font-size: 16px;
}

/* Metadata */
.layer-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  cursor: pointer;
}
.layer-tag-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.role-pill {
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-gold, #d4af6a);
  letter-spacing: 0.5px;
}
.note-pill {
  font-size: 10px;
  color: var(--text-secondary, #9ca3af);
  opacity: 0.8;
}
.lock-pill {
  font-size: 10px;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  padding: 1px 5px;
  border-radius: 3px;
}
.gene-title-row {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.gene-name {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.3px;
}
.gene-placeholder {
  font-size: 12px;
  color: var(--text-secondary, #9ca3af);
  font-style: italic;
}
.gene-code-row code {
  font-size: 10px;
  color: #a7b5b0;
  font-family: monospace;
  opacity: 0.85;
}

/* Action Button */
.layer-action-col {
  flex-shrink: 0;
}
.swap-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  padding: 0 10px;
  font-size: 11px;
  color: var(--accent-gold, #d4af6a);
  background: rgba(212, 175, 106, 0.08);
  border: 1px solid rgba(212, 175, 106, 0.3);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.18s ease;
  white-space: nowrap;
}
.swap-btn:hover:not(:disabled) {
  background: rgba(212, 175, 106, 0.2);
  border-color: var(--accent-gold, #d4af6a);
  transform: translateY(-1px);
}
.swap-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary, #9ca3af);
}

/* Gene Picker */
.gene-picker {
  background: #111a18;
  border: 1px solid rgba(212, 175, 106, 0.35);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
  margin-top: 4px;
}
.picker-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.picker-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.picker-target-tag {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-gold, #d4af6a);
}
.picker-title-group small {
  font-size: 10px;
  color: var(--text-secondary, #9ca3af);
}
.close-picker-btn {
  background: transparent;
  border: 0;
  color: var(--text-secondary, #9ca3af);
  font-size: 14px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}
.close-picker-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.picker-search-bar {
  position: relative;
  display: flex;
  align-items: center;
}
.picker-search-bar input {
  width: 100%;
  height: 32px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(212, 175, 106, 0.25);
  border-radius: 6px;
  padding: 0 28px 0 10px;
  color: #ffffff;
  font-size: 11px;
}
.picker-search-bar input:focus {
  outline: none;
  border-color: var(--accent-gold, #d4af6a);
}
.clear-search {
  position: absolute;
  right: 6px;
  background: none;
  border: 0;
  color: var(--text-secondary, #9ca3af);
  font-size: 11px;
  cursor: pointer;
}

.picker-filter-tabs {
  display: flex;
  gap: 4px;
}
.picker-filter-tabs button {
  flex: 1;
  height: 24px;
  font-size: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  color: var(--text-secondary, #9ca3af);
  cursor: pointer;
}
.picker-filter-tabs button.selected {
  background: rgba(212, 175, 106, 0.15);
  border-color: var(--accent-gold, #d4af6a);
  color: var(--accent-gold, #d4af6a);
  font-weight: 600;
}

.picker-grid-wrap {
  max-height: 240px;
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-width: thin;
  padding-right: 2px;
}
.picker-bento-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
}
.picker-gene-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}
.picker-gene-card:hover {
  background: rgba(212, 175, 106, 0.12);
  border-color: var(--accent-gold, #d4af6a);
  transform: translateY(-1px);
}
.card-thumb {
  width: 32px;
  height: 32px;
  background: #141f1c;
  border: 1px solid rgba(212, 175, 106, 0.2);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.card-thumb img {
  width: 26px;
  height: 26px;
  object-fit: contain;
}
.card-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.card-name {
  font-size: 11px;
  font-weight: 500;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-code {
  font-size: 9px;
  color: var(--text-secondary, #9ca3af);
  font-family: monospace;
}
.picker-empty {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary, #9ca3af);
  font-size: 11px;
}

/* Transitions */
.picker-slide-enter-active,
.picker-slide-leave-active {
  transition: all 0.25s ease;
}
.picker-slide-enter-from,
.picker-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
