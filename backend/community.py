"""Immutable contemporary assets: safe vector geometry, editable recipes, and provenance."""
import copy,datetime,hashlib,io,json,math,re,uuid
from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel,Field
from defusedxml import ElementTree as SafeET
from svgelements import SVG,Path as SVGPath,Shape,Color
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union,polygonize
from shapely.strtree import STRtree
import numpy as np
from shapely import make_valid
router=APIRouter(prefix='/api/community')
class Contribution(BaseModel):
 name:str=Field(min_length=2,max_length=60)
 description:str=Field(default='',max_length=1600)
 svg:str=Field(min_length=20,max_length=1_200_000)
 source_design_id:str|None=None
 source_pattern_id:str|None=None
 rights_confirmed:bool=False
 creation_method:str=Field(default='freehand',max_length=30)
 editor_state:dict|None=None

def filled_geometry(path,rule):
 from .geometry import read_geometry
 if rule=='evenodd':return read_geometry('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000"><path d="'+path.d()+'"/></svg>')[0]
 rings=[];lines=[]
 for sub in path.as_subpaths():
  pts=[]
  for seg in sub:
   if seg.__class__.__name__=='Move':continue
   steps=1 if seg.__class__.__name__ in ('Line','Close') else 12
   pts.extend((seg.point(i/steps).x,seg.point(i/steps).y) for i in range(steps+1))
  if len(pts)<3:continue
  if pts[-1]!=pts[0]:pts.append(pts[0])
  arr=np.asarray(pts,dtype=float)
  if not np.isfinite(arr).all():raise ValueError('路径坐标不正确')
  rings.append(arr);lines.append(LineString(pts))
 if not lines:raise ValueError('没有可填充的轮廓')
 if len(lines)==1 and lines[0].is_simple:return make_valid(Polygon(rings[0]))
 # Partition intersections, then evaluate SVG's nonzero winding rule on every face.
 tree=STRtree(lines);kept=[]
 for face in polygonize(unary_union(lines)):
  q=face.representative_point();winding=0
  for index in tree.query(q):
   arr=rings[int(index)];a,b=arr[:-1],arr[1:]
   cross=(b[:,0]-a[:,0])*(q.y-a[:,1])-(q.x-a[:,0])*(b[:,1]-a[:,1])
   winding+=int(np.count_nonzero((a[:,1]<=q.y)&(b[:,1]>q.y)&(cross>0)))-int(np.count_nonzero((a[:,1]>q.y)&(b[:,1]<=q.y)&(cross<0)))
  if winding:kept.append(face)
 return unary_union(kept)

def normalize_svg(raw,preserve_source=False):
 if re.search(r'<!DOCTYPE|<!ENTITY',raw,re.I):raise ValueError('不支持外部实体或文档定义')
 root=SafeET.fromstring(raw)
 if root.tag.split('}')[-1]!='svg':raise ValueError('需要SVG画布')
 allowed={'svg','g','path','circle','ellipse','rect','line','polygon','polyline','title','desc'}
 attrs={'d','transform','fill','stroke','stroke-width','fill-rule','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','x','y','x1','x2','y1','y2','cx','cy','r','rx','ry','width','height','viewBox','points','version'}
 count=0
 for el in root.iter():
  count+=1
  if count>4500:raise ValueError('图层过多，请减少重复数量或笔画')
  tag=el.tag.split('}')[-1]
  if tag not in allowed:raise ValueError('仅支持本地矢量路径，不支持脚本、图片或外部引用')
  for key,value in list(el.attrib.items()):
   key=key.split('}')[-1]
   if key not in attrs:raise ValueError('SVG包含不支持的属性：'+key)
   if re.search(r'url\s*\(|javascript:|data:|https?:|[<>]',value,re.I):raise ValueError('SVG不允许外部内容')
   if key in ('fill','stroke') and not re.fullmatch(r'#[0-9a-fA-F]{3,8}|none|black|white|transparent',value):raise ValueError('请使用纯色填充与线条')
   if key=='d' and not re.fullmatch(r'[MmZzLlHhVvCcSsQqTtAa0-9eE.,+\-\s]*',value):raise ValueError('路径格式不正确')
   if key=='transform' and not re.fullmatch(r'(?:(?:matrix|translate|scale|rotate|skewX|skewY)\s*\([0-9eE.,+\-\s]+\)\s*)+',value):raise ValueError('变换格式不正确')
   if key in ('opacity','fill-opacity','stroke-opacity','stroke-width','x','y','x1','x2','y1','y2','cx','cy','r','rx','ry'):
    try:n=float(value)
    except ValueError:raise ValueError('坐标与线宽必须为数字')
    if not math.isfinite(n) or abs(n)>100000:raise ValueError('坐标超出可处理范围')
 root.set('width','1000');root.set('height','1000');root.set('viewBox','0 0 1000 1000')
 import xml.etree.ElementTree as ET
 parsed=SVG.parse(io.StringIO(ET.tostring(root,encoding='unicode')),reify=True)
 parts=[];segments=0
 from .geometry import read_geometry
 for el in parsed.elements():
  if not isinstance(el,Shape):continue
  path=SVGPath(el);path.reify();segments+=len(path)
  if segments>45000:raise ValueError('轮廓过于复杂，请减少笔画或重复数量')
  visible=float(getattr(el,'opacity',1) or 0)>0
  if not visible:continue
  if el.fill is not None and el.fill.value is not None and el.fill.alpha>0:
   try:
    geo=filled_geometry(path,el.values.get('fill-rule','nonzero'))
    parts.append(geo)
   except ValueError:pass
  if el.stroke is not None and el.stroke.value is not None and el.stroke.alpha>0 and float(el.stroke_width or 0)>0:
   width=min(100,float(el.stroke_width))
   for sub in path.as_subpaths():
    pts=[]
    for seg in sub:
     if seg.__class__.__name__=='Move':continue
     steps=1 if seg.__class__.__name__ in ('Line','Close') else 10
     pts.extend((seg.point(i/steps).x,seg.point(i/steps).y) for i in range(steps+1))
    if len(pts)>1:parts.append(LineString(pts).buffer(width/2,quad_segs=6))
 if not parts:raise ValueError('请至少画出一条可见轮廓')
 geo=make_valid(unary_union(parts)).intersection(box(0,0,1000,1000))
 if geo.is_empty or geo.area<1:raise ValueError('可用轮廓为空，请把笔画画在画布内')
 def ring(coords):return 'M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in coords)+' Z'
 paths=[ring(p.exterior.coords)+''.join(ring(h.coords) for h in p.interiors) for p in getattr(geo,'geoms',[geo]) if hasattr(p,'exterior')]
 if not paths:raise ValueError('无法生成封闭轮廓')
 result='<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000"><path fill="#d6e2df" fill-rule="evenodd" d="'+' '.join(paths)+'"/></svg>'
 return (result,ET.tostring(root,encoding='unicode')) if preserve_source else result

def entries():
 from .app import db
 with db() as c:return [json.loads(x[0]) for x in c.execute('SELECT body FROM community_patterns ORDER BY rowid DESC')]

def clean_editor(state):
 if not state:return None
 if len(json.dumps(state,ensure_ascii=False).encode())>3_000_000:raise ValueError('编辑记录过大，请减少笔画')
 if state.get('version')!=1:raise ValueError('不支持的编辑记录版本')
 out=copy.deepcopy(state)
 if out.get('template'):out['template']=normalize_svg(out['template'])
 if len(out.get('shapes',[]))>120:raise ValueError('独立笔画不可超过120条')
 for s in out.get('shapes',[]):
  if not isinstance(s,dict) or not re.fullmatch(r'[MmZzLlHhVvCcSsQqTtAa0-9eE.,+\-\s]*',str(s.get('d',''))):raise ValueError('编辑路径格式不正确')
  for k in ('fill','stroke'):
   if not re.fullmatch(r'#[0-9a-fA-F]{3,8}|none',str(s.get(k,'none'))):raise ValueError('编辑颜色格式不正确')
  for k in ('x','y','rotation','scale','strokeWidth'):
   n=s.get(k,0)
   if isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) or abs(n)>100000:raise ValueError('编辑参数不正确')
  bounds=s.get('bounds',{})
  if not isinstance(bounds,dict) or any(isinstance(bounds.get(k),bool) or not isinstance(bounds.get(k),(int,float)) or not math.isfinite(bounds[k]) or abs(bounds[k])>100000 for k in ('x','y','width','height')):raise ValueError('笔画边界参数不正确')
 if out.get('symmetry',1) not in (1,2,4,6,8):raise ValueError('重复数量不受支持')
 return out

@router.post('/patterns',status_code=201)
def contribute(req:Contribution):
 from .app import db,ASSETS,design,catalog
 if len(req.name.strip())<2:raise HTTPException(422,'作品名称至少需要两个字')
 if not req.rights_confirmed:raise HTTPException(422,'请先确认原创笔画与底稿的使用权')
 try:(svg,source_svg)=normalize_svg(req.svg,True);editor=clean_editor(req.editor_state)
 except Exception as e:raise HTTPException(422,'无法入库：'+str(e))
 sources=[];knowledge=[];parent=None
 if req.source_design_id:
  d=design(req.source_design_id)
  sources.extend(dict(pattern=g['pattern'],code=g['code'],version=g.get('document_version',d['version'])) for g in d['genes'])
  sources.extend(d.get('source_refs',[]));knowledge.extend(d.get('knowledge_refs',[]))
 if req.source_pattern_id:
  parent=next((p for p in catalog()['patterns'] if p['id']==req.source_pattern_id),None)
  if not parent:raise HTTPException(422,'底稿来源不存在')
  sources.append(dict(pattern=parent['id'],version=parent['version'],name=parent['name']))
  sources.extend(parent.get('source_refs',[]));knowledge.extend(parent.get('knowledge_refs',[]))
 # Editor metadata cannot silently introduce an unrecorded background lineage.
 if editor:
  if editor.get('template') and not(req.source_design_id or req.source_pattern_id):raise HTTPException(422,'带底稿的创作需要保留来源编号')
  editor['sourceDesign']=req.source_design_id or '';editor['sourcePattern']=req.source_pattern_id or ''
 refs=list({json.dumps(s,ensure_ascii=False,sort_keys=True):s for s in sources}.values())
 pid='UGC-'+uuid.uuid4().hex[:12].upper();version=hashlib.sha256(svg.encode()+source_svg.encode()).hexdigest();code='M-'+pid
 filename='ugc-'+version[:24]+'.svg';url='/import-assets/'+filename
 original_filename='ugc-origin-'+version[:24]+'.svg';original_url='/import-assets/'+original_filename
 asset=dict(url=original_url,svg=url,code='',version=version,source=dict(document='共创工坊',location=pid),quality='original_vector')
 g=dict(code=code,name=req.name.strip(),type='图元',status='可复用',origin='contemporary',structure=req.description.strip() or '用户在共创工坊绘制的当代图形',position='当代创作画布',assets=[asset])
 p=dict(id=pid,name=req.name.strip(),description=req.description.strip(),origin='contemporary',semantic_status='当代创作，未作传统寓意认定',created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),document='共创工坊 · '+req.name.strip(),version=version,images=[asset],genes=[g],imagery=[],relations=[],colors=[],issues=[],text='当代创作记录。来源编号：'+(req.source_design_id or req.source_pattern_id or '独立绘制')+'。\n'+req.description.strip(),source_design_id=req.source_design_id,source_pattern_id=req.source_pattern_id,source_refs=refs,knowledge_refs=list({a['id']:a for a in knowledge}.values()),creation_method='remix' if req.source_design_id or req.source_pattern_id else 'freehand',editor_state=editor,rights_statement='提交者已确认原创笔画与底稿使用权',asset_check='安全矢量与闭合轮廓校验通过；不等于传统文化语义认证')
 (ASSETS/filename).write_text(svg);(ASSETS/original_filename).write_text(source_svg)
 with db() as c:c.execute('INSERT INTO community_patterns VALUES(?,?)',(pid,json.dumps(p,ensure_ascii=False)))
 return p

@router.get('/patterns')
def listing():
 from .app import db
 records=entries()
 with db() as c:
  for p in records:
   p['reuse_count']=c.execute('SELECT COUNT(*) FROM designs WHERE body LIKE ?',('%'+p['id']+'%',)).fetchone()[0]
   p['derivatives']=sum(x.get('source_pattern_id')==p['id'] for x in records)
 return records

@router.get('/patterns/{pid}')
def entry(pid:str):
 p=next((p for p in entries() if p['id']==pid),None)
 if not p:raise HTTPException(404,'共创资产不存在')
 return p
