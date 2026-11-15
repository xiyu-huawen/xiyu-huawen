import fs from 'node:fs';
import path from 'node:path';
import { DOMParser } from '@xmldom/xmldom';
import { createReliefGeometries, parseMotifSvg } from '../src/three/motifGeometry.js';

globalThis.DOMParser = DOMParser;
const root = path.resolve(import.meta.dirname, '../..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'seed/catalog.json'), 'utf8'));
const assets = new Set();
for (const pattern of catalog.patterns) {
  for (const gene of pattern.genes) {
    for (const asset of gene.assets || []) {
      if (asset.svg) assets.add(asset.svg);
    }
  }
}

const options = { depth: 8, bevelEnabled: false };
const failures = [];
let pathCount = 0;
let meshCount = 0;
let finiteCount = 0;
for (const asset of [...assets].sort()) {
  const file = path.join(root, 'seed/assets', path.basename(asset));
  try {
    const parsed = parseMotifSvg(fs.readFileSync(file, 'utf8'));
    for (const shapePath of parsed.paths) {
      pathCount++;
      const geometries = createReliefGeometries(shapePath, options);
      for (const geometry of geometries) {
        meshCount++;
        if (!geometry.attributes.position.array.every(Number.isFinite)) throw new Error('包含非有限坐标');
        finiteCount++;
        geometry.dispose();
      }
    }
  } catch (error) {
    failures.push({ asset, error: error.message });
  }
}

console.log(JSON.stringify({ assets: assets.size, paths: pathCount, meshes: meshCount, finiteMeshes: finiteCount, failures }, null, 2));
if (failures.length) process.exitCode = 1;
