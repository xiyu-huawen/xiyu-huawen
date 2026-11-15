import type { BufferGeometry, ShapePath } from 'three';

export interface ReliefOptions {
  depth?: number;
  bevelEnabled?: boolean;
  bevelSize?: number;
  bevelThickness?: number;
  bevelSegments?: number;
  curveSegments?: number;
}

export declare function createReliefGeometries(shapePath: ShapePath, options?: ReliefOptions): BufferGeometry[];
export declare function parseMotifSvg(text: string): { paths: ShapePath[]; xml: string };
