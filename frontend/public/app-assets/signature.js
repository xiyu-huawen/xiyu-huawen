const inscriptions = {
  '守形传意': ['守形传意', '古纹新章'],
  '跨源相生': ['跨源相生', '合和共荣'],
  '疏朗留白': ['疏朗留白', '气韵自生'],
};
const numerals = ['壹', '贰', '叁', '肆', '伍', '陆'];

function currentDesign() {
  try {
    return JSON.parse(localStorage.getItem('xiyu-theatre') || '{}');
  } catch {
    return {};
  }
}

function colophon({ direction, index, id, stage = false }) {
  const [lineOne, lineTwo] = inscriptions[direction] || ['一意成纹', '一纹入器'];
  const number = Number.isInteger(index) ? `第${numerals[index] || index + 1}稿` : `编号 ${id || 'XY-DRAFT'}`;
  const element = document.createElement('span');
  element.className = stage ? 'xiyu-colophon xiyu-stage-colophon' : 'xiyu-colophon xiyu-direction-colophon';
  element.setAttribute('aria-label', `题跋：${lineOne}，${lineTwo}；${number}`);

  const copy = document.createElement('span');
  copy.className = 'xiyu-colophon-copy';
  const inscription = document.createElement('span');
  inscription.className = 'xiyu-colophon-inscription';
  inscription.textContent = `${lineOne} · ${lineTwo}`;
  const numberElement = document.createElement('small');
  numberElement.className = 'xiyu-colophon-number';
  numberElement.textContent = number;
  copy.append(inscription, numberElement);

  const seal = document.createElement('img');
  seal.className = 'xiyu-colophon-seal';
  seal.src = '/assets/brand-seal.png';
  seal.alt = '';
  seal.setAttribute('aria-hidden', 'true');
  element.append(copy, seal);
  return element;
}

function applySignatures() {
  const design = currentDesign();
  document.querySelectorAll('.direction-rail > button').forEach((card, index) => {
    const direction = card.querySelector(':scope > span')?.textContent?.trim() || '';
    const key = `${design.id || 'draft'}-${direction}-${index}`;
    if (card.dataset.signatureKey === key) return;
    card.querySelector(':scope > .xiyu-direction-colophon')?.remove();
    card.append(colophon({ direction, index, id: design.id }));
    card.dataset.signatureKey = key;
  });

  document.querySelectorAll('.creation-stage').forEach(stage => {
    const direction = design.direction || '守形传意';
    const key = `${design.id || 'draft'}-${direction}`;
    if (stage.dataset.signatureKey === key) return;
    stage.querySelector(':scope > .xiyu-stage-colophon')?.remove();
    if (!design.id) {
      stage.dataset.signatureKey = '';
      return;
    }
    stage.append(colophon({ direction, id: design.id, stage: true }));
    stage.dataset.signatureKey = key;
  });
}

let scheduled = false;
function schedule() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    scheduled = false;
    applySignatures();
  });
}

new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true });
window.addEventListener('storage', schedule);
window.addEventListener('hashchange', schedule);
applySignatures();
