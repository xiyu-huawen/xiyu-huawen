import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { DOMParser } from '@xmldom/xmldom';
import * as T from 'three';
import { createReliefGeometries, parseMotifSvg } from '../src/three/motifGeometry.js';

globalThis.DOMParser = DOMParser;

function parse(svg) {
  return parseMotifSvg(svg);
}

function zRange(geometry) {
  const positions = geometry.attributes.position;
  const range = [Infinity, -Infinity];
  for (let i = 0; i < positions.count; i++) {
    range[0] = Math.min(range[0], positions.getZ(i));
    range[1] = Math.max(range[1], positions.getZ(i));
  }
  return range;
}

const options = { depth: 8, bevelEnabled: false };

test('粗 stroke 外框展开为连续实体并保留挤出厚度', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M100 100H900V900H100Z" fill="none" stroke="#d6e2df" stroke-width="40"/></svg>';
  const geometries = createReliefGeometries(parse(svg).paths[0], options);
  assert.equal(geometries.length, 1);
  assert.ok(geometries[0].attributes.position.count >= 24);
  assert.deepEqual(zRange(geometries[0]), [0, 8]);
});

test('evenodd 嵌套矩形只扣除真实内孔并保持外轮廓绕向', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0H1000V1000H0Z M200 200H800V800H200Z" fill-rule="evenodd"/></svg>';
  const geometries = createReliefGeometries(parse(svg).paths[0], options);
  assert.equal(geometries.length, 1);
  assert.ok(Math.abs(geometries[0].userData.expectedArea - 640000) < 1);
  assert.deepEqual(zRange(geometries[0]), [0, 8]);
});

test('细线描边只生成实际宽度，不扩张成实心区域', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M100 500L900 500" fill="none" stroke="#d6e2df" stroke-width="20"/></svg>';
  const geometries = createReliefGeometries(parse(svg).paths[0], options);
  const positions = geometries[0].attributes.position;
  let minY = Infinity;
  let maxY = -Infinity;
  for (let i = 0; i < positions.count; i++) {
    minY = Math.min(minY, positions.getY(i));
    maxY = Math.max(maxY, positions.getY(i));
  }
  assert.ok(Math.abs(minY - 490) < .001);
  assert.ok(Math.abs(maxY - 510) < .001);
});

test('fill 与 stroke 同时存在时分别保留，不互相覆盖', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M100 100H900V900H100Z" fill="#d6e2df" stroke="#d6e2df" stroke-width="20"/></svg>';
  assert.equal(createReliefGeometries(parse(svg).paths[0], options).length, 2);
});

test('重复点和零长度线段被清理，空路径不产生异常', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L0 0L1000 0L1000 1000L0 1000L0 1000Z" fill="#d6e2df"/><path d="M0 0" fill="none" stroke="none"/></svg>';
  const paths = parse(svg).paths;
  assert.equal(createReliefGeometries(paths[0], options).length, 1);
  assert.equal(createReliefGeometries(paths[1], options).length, 0);
});

test('自交轮廓使用原始三角化兜底并保持坐标有效', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L1000 1000L0 1000L1000 0Z" fill="#d6e2df"/></svg>';
  const geometries = createReliefGeometries(parse(svg).paths[0], options);
  assert.equal(geometries.length, 1);
  assert.ok(geometries[0].attributes.position.array.every(Number.isFinite));
});

test('寿字纹复杂嵌套轮廓保持实体面积且坐标有限', () => {
  const svg = fs.readFileSync(new URL('../../seed/assets/4cd45c87cb7b0b54b478.svg', import.meta.url), 'utf8');
  const paths = parse(svg).paths;
  const geometries = createReliefGeometries(paths[0], options);
  assert.equal(geometries.length, 1);
  assert.ok(geometries[0].userData.expectedArea > 120000);
  assert.ok(geometries[0].userData.expectedArea < 125000);
  assert.ok(geometries[0].attributes.position.array.every(Number.isFinite));
});

test('寿字描边不被意外填成实心', () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M100 100L900 100L900 900L100 900Z" fill="none" stroke="#d6e2df" stroke-width="4"/></svg>';
  const geometries = createReliefGeometries(parse(svg).paths[0], options);
  assert.equal(geometries.length, 1);
  assert.deepEqual(zRange(geometries[0]), [0, 8]);
});

