import * as T from 'three';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';

const DUPLICATE_TOLERANCE = 1e-4;
const AREA_TOLERANCE = 0.025;

export function parseMotifSvg(text) {
  const normalized = text.replace(/<(\/?)(?:[A-Za-z_][\w.-]*):(?=(?:svg|g|path|rect|circle|ellipse|polygon|polyline|line|defs|use|style)\b)/g, '<$1');
  return new SVGLoader().parse(normalized);
}

function cleanPoints(points) {
  const cleaned = [];
  for (const point of points) {
    if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) continue;
    const previous = cleaned[cleaned.length - 1];
    if (previous && Math.hypot(point.x - previous.x, point.y - previous.y) < DUPLICATE_TOLERANCE) continue;
    cleaned.push(new T.Vector2(point.x, point.y));
  }
  if (cleaned.length > 2 && Math.hypot(cleaned[0].x - cleaned.at(-1).x, cleaned[0].y - cleaned.at(-1).y) < DUPLICATE_TOLERANCE) cleaned.pop();
  return cleaned;
}

function segmentsIntersect(a, b, c, d) {
  const cross = (p, q, r) => (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x);
  const abC = cross(a, b, c);
  const abD = cross(a, b, d);
  const cdA = cross(c, d, a);
  const cdB = cross(c, d, b);
  return abC * abD < 0 && cdA * cdB < 0;
}

function hasSelfIntersection(points) {
  const count = points.length;
  if (count < 4 || count > 1600) return false;
  for (let i = 0; i < count; i++) {
    const a = points[i];
    const b = points[(i + 1) % count];
    for (let j = i + 2; j < count; j++) {
      if (i === 0 && j === count - 1) continue;
      const c = points[j];
      const d = points[(j + 1) % count];
      if (segmentsIntersect(a, b, c, d)) return true;
    }
  }
  return false;
}

function normalizeShape(source) {
  const outer = cleanPoints(source.getPoints());
  if (outer.length < 3) throw new Error('外轮廓不足三个有效顶点');
  if (!T.ShapeUtils.isClockWise(outer)) outer.reverse();
  const shape = new T.Shape(outer);
  const holes = [];
  for (const sourceHole of source.holes) {
    const points = cleanPoints(sourceHole.getPoints());
    if (points.length < 3) continue;
    if (T.ShapeUtils.isClockWise(points)) points.reverse();
    holes.push(new T.Path(points));
  }
  shape.holes = holes;
  return { shape, selfIntersecting: hasSelfIntersection(outer) || holes.some(hole => hasSelfIntersection(hole.getPoints())) };
}

function trianglesArea2D(geometry) {
  const positions = geometry.attributes.position;
  const indices = geometry.index;
  const a = new T.Vector3();
  const b = new T.Vector3();
  const c = new T.Vector3();
  let area = 0;
  const count = indices ? indices.count : positions.count;
  for (let i = 0; i < count; i += 3) {
    a.fromBufferAttribute(positions, indices ? indices.getX(i) : i);
    b.fromBufferAttribute(positions, indices ? indices.getX(i + 1) : i + 1);
    c.fromBufferAttribute(positions, indices ? indices.getX(i + 2) : i + 2);
    area += b.clone().sub(a).cross(c.clone().sub(a)).z / 2;
  }
  return Math.abs(area);
}

function validateGeometry(geometry, expectedArea) {
  const positions = geometry.attributes.position;
  if (!positions || positions.count === 0) return false;
  for (let i = 0; i < positions.array.length; i++) {
    if (!Number.isFinite(positions.array[i])) return false;
  }
  if (expectedArea <= 0) return false;
  const actualArea = trianglesArea2D(geometry);
  return Math.abs(actualArea - expectedArea) / expectedArea <= AREA_TOLERANCE;
}

function extrudeShape(source, options) {
  const baseline = new T.ShapeGeometry(source, options.curveSegments || 8);
  const expectedArea = trianglesArea2D(baseline);
  baseline.dispose();
  if (expectedArea < 1e-8) return null;
  try {
    const direct = new T.ExtrudeGeometry(source, options);
    if (direct.attributes.position.count && direct.attributes.position.array.every(Number.isFinite)) {
      direct.userData.expectedArea = expectedArea;
      direct.userData.curveSegments = options.curveSegments || 8;
      return direct;
    }
    direct.dispose();
  } catch {}
  const { shape, selfIntersecting } = normalizeShape(source);
  const segments = [...new Set([options.curveSegments || 8, 16, 24])];
  let lastError;
  for (const curveSegments of segments) {
    try {
      const flat = new T.ShapeGeometry(shape, curveSegments);
      if (!validateGeometry(flat, expectedArea)) {
        flat.dispose();
        lastError = new Error(selfIntersecting ? '轮廓自交导致三角化面积不一致' : '三角化面积不一致');
        continue;
      }
      flat.dispose();
      const geometry = new T.ExtrudeGeometry(shape, { ...options, curveSegments });
      if (!geometry.attributes.position?.count) {
        geometry.dispose();
        lastError = new Error('挤出结果为空');
        continue;
      }
      for (const value of geometry.attributes.position.array) {
        if (!Number.isFinite(value)) {
          geometry.dispose();
          lastError = new Error('挤出结果包含非有限坐标');
          break;
        }
      }
      if (lastError) continue;
      geometry.userData.expectedArea = expectedArea;
      geometry.userData.curveSegments = curveSegments;
      lastError = null;
      return geometry;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error('三角化失败');
}

function extrudeStrokeMesh(source, depth) {
  const positions = source.attributes.position;
  const edges = new Map();
  const vertices = [];
  const key = point => `${point.x.toFixed(5)},${point.y.toFixed(5)}`;
  const edgeKey = (a, b) => [key(a), key(b)].sort().join('|');
  const pushTriangle = (a, b, c, z) => vertices.push(a.x, a.y, z, b.x, b.y, z, c.x, c.y, z);
  const point = index => new T.Vector3().fromBufferAttribute(positions, index);
  for (let i = 0; i < positions.count; i += 3) {
    const a = point(i);
    const b = point(i + 1);
    const c = point(i + 2);
    pushTriangle(a, b, c, 0);
    pushTriangle(c, b, a, depth);
    for (const [start, end] of [[a, b], [b, c], [c, a]]) {
      const id = edgeKey(start, end);
      if (edges.has(id)) edges.get(id).count++;
      else edges.set(id, { start, end, count: 1 });
    }
  }
  for (const { start, end, count } of edges.values()) {
    if (count !== 1) continue;
    const a = start.clone();
    const b = end.clone();
    const c = end.clone();
    const d = start.clone();
    c.z = depth;
    d.z = depth;
    pushTriangle(a, b, c, 0);
    pushTriangle(a, c, d, 0);
  }
  const geometry = new T.BufferGeometry();
  geometry.setAttribute('position', new T.Float32BufferAttribute(vertices, 3));
  geometry.computeVertexNormals();
  if (!vertices.length || vertices.some(value => !Number.isFinite(value))) {
    geometry.dispose();
    throw new Error('描边轮廓化失败');
  }
  return geometry;
}

export function createReliefGeometries(shapePath, options = {}) {
  const style = shapePath.userData?.style || {};
  const geometries = [];
  const errors = [];
  if (style.fill && style.fill !== 'none') {
    for (const shape of SVGLoader.createShapes(shapePath)) {
      try {
        const geometry = extrudeShape(shape, options);
        if (geometry) geometries.push(geometry);
      } catch (error) {
        errors.push(error);
      }
    }
  }
  if (style.stroke && style.stroke !== 'none' && Number(style.strokeWidth) > 0) {
    for (const subPath of shapePath.subPaths) {
      try {
        const stroke = SVGLoader.pointsToStroke(subPath.getPoints(), style, 12, DUPLICATE_TOLERANCE);
        if (stroke) geometries.push(extrudeStrokeMesh(stroke, options.depth || 10));
      } catch (error) {
        errors.push(error);
      }
    }
  }
  if (errors.length && !geometries.length) {
    throw new AggregateError(errors, '没有可用的浮雕实体轮廓');
  }
  if (errors.length) {
    throw new AggregateError(errors, '部分轮廓未能生成浮雕实体');
  }
  return geometries.map(geometry => {
    const welded = mergeVertices(geometry, 0.001);
    geometry.dispose();
    return welded;
  });
}
