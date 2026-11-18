"""Planar boolean artwork. Source SVG is retained; derived paths record their operation."""
import io
from svgelements import SVG,Path
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from shapely import make_valid

def read_geometry(svg,curve_steps=12):
 original_header=svg[:svg.index('>')+1]
 import re
 normalized=re.sub(r'width="[^"]+"','width="1000"',svg,count=1);normalized=re.sub(r'height="[^"]+"','height="1000"',normalized,count=1)
 parsed=SVG.parse(io.StringIO(normalized),reify=True);parts=[]
 for element in parsed.elements():
  if not isinstance(element,Path):continue
  shape=None
  for sub in element.as_subpaths():
   points=[]
   for seg in sub:
    if seg.__class__.__name__=='Move':continue
    steps=2 if seg.__class__.__name__ in ('Line','Close') else curve_steps
    points.extend((point[0],point[1]) for point in seg.npoint([i/steps for i in range(steps+1)]))
   if len(points)<3:continue
   poly=Polygon(points)
   if not poly.is_valid:poly=make_valid(poly)
   shape=poly if shape is None else shape.symmetric_difference(poly)
  if shape is not None and not shape.is_empty:parts.append(shape)
 if not parts:raise ValueError('没有可合成的闭合轮廓')
 geometry=unary_union(parts)
 if not geometry.is_valid:geometry=make_valid(geometry)
 return geometry,len(parts)

def compose_boolean(svg,mode,curve_steps=12):
 original_header=svg[:svg.index('>')+1]
 geometry,source_count=read_geometry(svg,curve_steps)
 detail=96
 if mode=='negative':
  envelope=Point(500,500).buffer(465,quad_segs=detail)
  if not envelope.covers(geometry):envelope=box(25,25,975,975).buffer(10)
  geometry=envelope.difference(geometry)
 if mode=='sparse':
  outer=Point(500,500).buffer(462,quad_segs=detail)
  inner=Point(500,500).buffer(444,quad_segs=detail)
  if outer.covers(geometry):
   support=outer.difference(inner)
  else:
   support=geometry.convex_hull.buffer(8,quad_segs=8).boundary.buffer(8,quad_segs=8)
  geometry=support.difference(geometry).union(geometry.boundary.buffer(2.5,quad_segs=8))
  parts=[part for part in getattr(geometry,'geoms',[geometry]) if part.area>=4]
  geometry=make_valid(unary_union(parts))
 if mode=='outline':geometry=geometry.boundary.buffer(3,quad_segs=8)
 geometry=geometry.intersection(box(0,0,1000,1000))
 if geometry.is_empty:raise ValueError('几何运算结果为空')
 def ring(coords):return 'M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in coords)+' Z'
 paths=[]
 for p in getattr(geometry,'geoms',[geometry]):
  if not hasattr(p,'exterior'):continue
  paths.append(ring(p.exterior.coords)+''.join(ring(r.coords) for r in p.interiors))
 start=original_header
 import re
 color=re.search(r'<g fill="(#[a-fA-F0-9]+)"',svg).group(1)
 output=start+'<path fill="'+color+'" fill-rule="evenodd" d="'+' '.join(paths)+'"/></svg>'
 return output,dict(operation=mode,area=round(geometry.area,2),negative_space=round(1-geometry.area/1000000,4),source_count=source_count)
