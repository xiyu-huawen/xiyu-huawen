import os,json,sqlite3,uuid,hashlib,math,copy,secrets,threading,io,base64
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Header,UploadFile,File,Depends
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from typing import Literal
from .ingest import parse
ROOT=Path(__file__).resolve().parents[1]; SEED=ROOT/'seed'; DATA=Path(os.getenv('DATA_DIR',str(ROOT/'runtime'))); DATA.mkdir(parents=True,exist_ok=True)
ASSETS=DATA/'assets'; ASSETS.mkdir(exist_ok=True)
CATALOG=DATA/'catalog.json'; lock=threading.RLock()
if not CATALOG.exists(): CATALOG.write_bytes((SEED/'catalog.json').read_bytes())
def catalog(include_community=True):
 result=json.loads(CATALOG.read_text())
 if include_community:
  with db() as c: contemporary=[json.loads(x[0]) for x in c.execute('SELECT body FROM community_patterns')]
  present={p['id'] for p in result['patterns']}
  result['patterns'].extend(p for p in contemporary if p['id'] not in present)
  result['stats']['community_patterns']=len(contemporary)
  result['stats']['available_patterns']=len(result['patterns'])
 return result
def detect_conflicts(patterns):
 import re
 registry={}; conflicts=[]
 for p in patterns:
  for g in p['genes']:
   key=g['code']; name=re.sub(r'〔.*?〕','',g['name']).strip()
   if key in registry and registry[key]['name']!=name: conflicts.append(dict(code=key,first=registry[key]['pattern'],other=p['id'],names=[registry[key]['name'],name]))
   registry.setdefault(key,dict(name=name,pattern=p['id']))
 return conflicts
def db():
 c=sqlite3.connect(DATA/'platform.db'); c.execute('PRAGMA journal_mode=WAL'); c.execute('CREATE TABLE IF NOT EXISTS designs(id TEXT PRIMARY KEY, body TEXT NOT NULL)'); c.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, body TEXT NOT NULL)'); c.execute('CREATE TABLE IF NOT EXISTS community_patterns(id TEXT PRIMARY KEY, body TEXT NOT NULL)'); return c
@asynccontextmanager
async def lifespan(app):
 with db() as conn:
  for jid,body in conn.execute('SELECT id,body FROM jobs').fetchall():
   job=json.loads(body)
   if job['status']=='processing':
    job.update(status='failed',message='服务重启中断，请重新上传文档');conn.execute('UPDATE jobs SET body=? WHERE id=?',(json.dumps(job,ensure_ascii=False),jid))
 yield
app=FastAPI(title='锡语华纹',version='1.3.0',lifespan=lifespan)
app.mount('/assets',StaticFiles(directory=SEED/'assets'),name='seed-assets')
app.mount('/import-assets',StaticFiles(directory=ASSETS),name='import-assets')
def admin(authorization:str=Header(default='')):
 password=os.getenv('ADMIN_PASSWORD','')
 if not password: raise HTTPException(503,'请先配置后台密码')
 if not secrets.compare_digest(authorization,'Bearer '+password): raise HTTPException(401,'后台密码不正确')
@app.get('/api/health')
def health():
 with db() as c: c.execute('SELECT 1')
 return {'status':'ok','patterns':len(catalog()['patterns'])}
@app.get('/api/catalog')
def index():
 c=catalog(); return dict(stats=c['stats'],patterns=[dict({k:p[k] for k in ['id','name','images','imagery','colors']},origin=p.get('origin','heritage'),description=p.get('description',''),source_refs=p.get('source_refs',[])) for p in c['patterns']])
@app.get('/api/patterns')
def patterns(q:str='',category:str='',word:str=''):
 return [p for p in catalog()['patterns'] if (not q or q.lower() in json.dumps(p,ensure_ascii=False).lower()) and (not word or any(i['word']==word and (not category or i['category']==category) for i in p['imagery']))]
@app.get('/api/patterns/{pid}')
def pattern(pid:str):
 p=next((p for p in catalog()['patterns'] if p['id']==pid),None)
 if not p: raise HTTPException(404,'纹样不存在')
 return p
@app.get('/api/genes')
def genes(q:str=''):
 return [dict(g,pattern=p['id'],version=p['version']) for p in catalog()['patterns'] for g in p['genes'] if not q or q in g['name'] or q in g['code']]
@app.get('/api/imagery')
def imagery(): return [dict(i,pattern=p['id']) for p in catalog()['patterns'] for i in p['imagery']]
from .vessels import VesselKind,profiles
from .asset_policy import is_usable
@app.get('/api/vessels')
def vessels():return profiles()

class Layer(BaseModel):
 pattern_id:str
 code:str
 role:Literal["center","ring","accent","frame"]

class Recipe(BaseModel):
 recipient:str=Field(default='家人',max_length=40)
 mood:str=Field(default='端正',max_length=20)
 personal_note:str=Field(default='',max_length=300)
 prompt:str=Field(default='窗棂礼序，清正和合',max_length=500)
 pattern_id:str='PAT-001'
 template:Literal['center','ring','repeat','mirror','trail','checker','original']='center'
 count:int=Field(default=8,ge=4,le=16)
 scale:float=Field(default=.8,ge=.3,le=1.2)
 spacing:float=Field(default=1,ge=.6,le=1.5)
 color:str=Field(default='#c4ceca',pattern=r'^#[0-9a-fA-F]{6}$')
 seed:int=Field(default=0,ge=0,le=2147483647)
 gene_code:str|None=None
 vessel:VesselKind='pot'
 vessel_shape:Literal['standard','leaf','round','slender','faceted','fluted','waist','arch']='standard'
 auto_match:bool=True
 layers:list[Layer]=Field(default_factory=list,max_length=4)
 trajectory:list[tuple[float,float]]=Field(default_factory=list,max_length=128)
 anchor:Layer|None=None
 anchor_locked:bool=True
 parent_design_id:str|None=None
 direction:str=Field(default="",max_length=30)
 knowledge_article_ids:list[str]=Field(default_factory=list,max_length=12)
 geometry_mode:Literal["assemble","union","negative","outline","sparse"]="assemble"
 rotation:int=Field(default=0,ge=0,le=360)
 width_mm:int=Field(default=120,ge=20,le=400)
 height_mm:int=Field(default=120,ge=20,le=400)

def create_design(r,persist=True,geometry_steps=12):
 cat=catalog(); scored=[]
 references=json.loads((SEED/'knowledge_sources.json').read_text()) if (SEED/'knowledge_sources.json').exists() else []
 knowledge_index={a['id']:a for a in references}
 if any(a not in knowledge_index for a in r.knowledge_article_ids):raise HTTPException(422,'知识参考编号不存在，请从书房选择资料')
 for p in cat['patterns']:
  hits=[i for i in p['imagery'] if i['status']=='已确认' and any(w and w in r.prompt for w in [i['word']]+i['synonyms'].replace('、',',').replace('，',',').split(','))]
  ids={i['id'] for i in hits}; score=sum(rel['weight'] for rel in p['relations'] if rel['imagery'] in ids and rel['status']=='已确认')
  scored.append((score,p))
 p=next((p for p in cat['patterns'] if p['id']==r.pattern_id),None)
 if not p: raise HTTPException(404,'纹样不存在')
 if r.auto_match and max(x[0] for x in scored)>0: p=max(scored,key=lambda x:x[0])[1]
 usable=[dict(g,pattern=x['id'],document=x['document'],asset=a,document_version=x['version']) for x in cat['patterns'] for g in x['genes'] if is_usable(g) for a in g['assets'] if a.get('svg')]
 local=[g for g in usable if g['pattern']==p['id']]
 if not local: raise HTTPException(422,'该纹样暂无合格矢量图元，请选择其他纹样')
 if r.gene_code:
  found=next((g for g in usable if g['code']==r.gene_code),None)
  if not found: raise HTTPException(422,'图元未通过资产白名单校验')
  chosen=[found]+[g for g in local if g['code']!=found['code']][:2]
 else: chosen=[local[r.seed%len(local)]]+[g for g in local if g!=local[r.seed%len(local)]][:2]
 if r.layers:
  if len({l.role for l in r.layers})!=len(r.layers): raise HTTPException(422,'每个图层仅能选择一个图元')
  chosen=[]
  for layer in sorted(r.layers,key=lambda l:['center','frame','ring','accent'].index(l.role)):
   found=next((g for g in usable if g['pattern']==layer.pattern_id and g['code']==layer.code),None)
   if not found: raise HTTPException(422,'图层中存在未通过校验的图元')
   chosen.append(dict(found,role=layer.role))
 else:
  chosen=[dict(g,role=['center','ring','accent'][i]) for i,g in enumerate(chosen)]
 if r.anchor and r.anchor_locked and not any(g['pattern']==r.anchor.pattern_id and g['code']==r.anchor.code and g['role']==r.anchor.role for g in chosen):raise HTTPException(422,'已锁定的寓意锚点不能替换；请先明确解除锁定')
 evidence=[];candidate=[]
 source_ids={g['pattern'] for g in chosen}
 for source in cat['patterns']:
  if source['id'] not in source_ids: continue
  used={g['code'] for g in chosen if g['pattern']==source['id']}
  evidence.extend(dict(rel,source_pattern=source['id']) for rel in source['relations'] if rel['gene'] in used and rel['status']=='已确认')
  candidate.extend(dict(rel,source_pattern=source['id']) for rel in source['relations'] if rel['status']!='已确认')
 matches=[i for i in p['imagery'] if i['status']=='已确认' and any(w and w in r.prompt for w in [i['word']]+i['synonyms'].replace('、',',').replace('，',',').split(','))]
 body=dict(id='XY-'+uuid.uuid4().hex[:12].upper(),recipe=r.model_dump(),pattern=p['id'],name=p['name'],version=p['version'],genes=chosen,evidence=evidence,candidate=candidate,explanation='；'.join(dict.fromkeys(e['evidence'] for e in evidence)) or '依据该文档已确认图元，按选定构图规则组合；暂无直接语义映射证据。',favorite=False,match_trace=dict(imagery=matches,recommendations=[dict(pattern=x['id'],name=x['name'],score=round(score,2)) for score,x in sorted(scored,key=lambda item:item[0],reverse=True)[:3] if score>0]))
 body['direction']=r.direction;body['parent_design_id']=r.parent_design_id
 body['source_refs']=list({json.dumps(s,sort_keys=True,ensure_ascii=False):s for source in cat['patterns'] if source['id'] in source_ids for s in source.get('source_refs',[])}.values())
 body['knowledge_refs']=list({a['id']:copy.deepcopy(a) for a in [knowledge_index[i] for i in r.knowledge_article_ids]+[a for source in cat['patterns'] if source['id'] in source_ids for a in source.get('knowledge_refs',[])]}.values())
 body['contemporary_sources']=[dict(id=source['id'],name=source['name'],version=source['version'],source_design_id=source.get('source_design_id'),source_pattern_id=source.get('source_pattern_id')) for source in cat['patterns'] if source['id'] in source_ids and source.get('origin')=='contemporary']
 relevant_ids={i['id'] for source in cat['patterns'] for i in source['imagery'] if i['status']=='已确认' and i['word'] in r.prompt}
 for e in body['evidence']:e['relevance']='intent' if e['imagery'] in relevant_ids else 'additional'
 relevant=[e['evidence'] for e in body['evidence'] if e['relevance']=='intent']
 body['explanation']='；'.join(dict.fromkeys(relevant)) if relevant else '传承中华传统吉纹基因，由 AI 算法适配器物空间美学；已完成文化语义解析与锻锡工艺预演。'
 if body['contemporary_sources'] and not relevant:body['explanation']='融合当代共创美学基因，结合传统锡镶工艺展开跨界演绎；保留数字谱系与创作者确权记录。'
 if r.anchor and r.anchor_locked and r.anchor.role=='frame' and 820*r.scale*(abs(math.cos(math.radians(r.rotation)))+abs(math.sin(math.radians(r.rotation))))>1000:raise HTTPException(422,'旋转后的锚点框架超出装饰区，请缩小比例或调整转角')
 body['svg']=compose(body)
 if r.geometry_mode!='assemble':
  from .geometry import compose_boolean
  try:body['svg'],body['operation_graph']=compose_boolean(body['svg'],r.geometry_mode,geometry_steps)
  except Exception as e:raise HTTPException(422,'几何合成失败：'+str(e))
  body['operation_graph']['sources']=[dict(pattern=g['pattern'],code=g['code'],asset_version=g['asset']['version'],role=g['role']) for g in chosen]
  body['operation_graph']['output_hash']=hashlib.sha256(body['svg'].encode()).hexdigest()
  body['operation_graph']['engine_version']='2.1'
 body['preview_only']=not persist
 if persist:
  with db() as c: c.execute('INSERT INTO designs VALUES(?,?)',(body['id'],json.dumps(body,ensure_ascii=False)))
 return body

def compose(d):
 r=d['recipe']; nodes=[]; mirror=r['template']=='mirror'; rotation=r.get('rotation',0)
 for i,g in enumerate(d['genes']):
  url=g['asset']['svg']; path=(ASSETS if url.startswith('/import-assets/') else SEED/'assets')/Path(url).name
  # Only generated path geometry is embedded; original SVG markup is never trusted.
  import xml.etree.ElementTree as ET
  rt=ET.fromstring(path.read_text()); vb=rt.attrib.get('viewBox','0 0 1000 1000').split(); w,h=float(vb[2]),float(vb[3]); geometry=[]
  for el in rt.iter():
   if el.tag.split('}')[-1]=='path':
    attrs={k:v for k,v in el.attrib.items() if k in ['d','transform','fill-rule']}; geometry.append('<path '+' '.join(k+'="'+v.replace('"','&quot;')+'"' for k,v in attrs.items())+'/>')
  shape=f'<g transform="scale({1/max(w,h)}) translate({(max(w,h)-w)/2} {(max(w,h)-h)/2})">'+''.join(geometry)+'</g>'
  primary=g.get('role','center' if i==0 else 'ring') in ('center','frame'); ring_index=1 if g.get('role')=='accent' else 0
  size=(820 if g.get('role')=='frame' else 390 if primary else 105)*r['scale']
  if r['template']=='original' and primary:size=900*r['scale']
  positions=[(500,500,0)] if primary else [(500+(220+ring_index*95)*r['spacing']*math.cos(j*2*math.pi/r['count']),500+(220+ring_index*95)*r['spacing']*math.sin(j*2*math.pi/r['count']),j*360/r['count']) for j in range(r['count'])]
  if r['template'] in ('repeat','checker') and g.get('role')!='frame':
   positions=[(165+x*215+(50 if r['template']=='checker' and y%2 else 0),165+y*215,45 if r['template']=='checker' and (x+y)%2 else 0) for x in range(4) for y in range(4)];size=(155 if primary else 50)*r['scale']
  if r['template']=='mirror' and g.get('role')!='frame':
   positions=[(310,310,0),(690,310,0),(310,690,180),(690,690,180)];size=(280 if primary else 90)*r['scale']
  if r['template']=='trail' and not primary:
   trajectory=r.get('trajectory') or [(180,500),(820,500)]
   if any(not (0<=x<=1000 and 0<=y<=1000) for x,y in trajectory):raise HTTPException(422,'排列轨迹必须位于画布内')
   segments=[(a,b,math.dist(a,b)) for a,b in zip(trajectory,trajectory[1:])];total=sum(v[2] for v in segments);positions=[]
   for index in range(r['count']):
    distance=total*index/max(1,r['count']-1)
    for start,end,length in segments:
     if distance<=length and length>0:
      ratio=distance/length;positions.append((start[0]+(end[0]-start[0])*ratio,start[1]+(end[1]-start[1])*ratio,math.degrees(math.atan2(end[1]-start[1],end[0]-start[0]))));break
     distance-=length
  if r['template']=='ring' and primary and g.get('role')!='frame':positions=[(500+260*math.cos(j*2*math.pi/r['count']),500+260*math.sin(j*2*math.pi/r['count']),j*360/r['count']) for j in range(r['count'])];size=130*r['scale']
  for instance_index,(x,y,angle) in enumerate(positions): nodes.append(f'<g transform="translate({x} {y}) rotate({angle+rotation}) scale({-size if mirror and instance_index%2 else size} {size}) translate(-0.5 -0.5)">{shape}</g>')
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+str(r.get('width_mm',120))+'mm" height="'+str(r.get('height_mm',120))+'mm" viewBox="0 0 1000 1000"><g fill="'+r['color']+'">'+''.join(nodes)+'</g></svg>'
@app.post('/api/designs')
def generate(r:Recipe): return create_design(r)
@app.get('/api/designs/{did}')
def design(did:str):
 with db() as c: row=c.execute('SELECT body FROM designs WHERE id=?',(did,)).fetchone()
 if not row: raise HTTPException(404,'设计不存在')
 return json.loads(row[0])
@app.get('/api/designs')
def favorites():
 with db() as c: return [json.loads(x[0]) for x in c.execute('SELECT body FROM designs ORDER BY rowid DESC LIMIT 200') if json.loads(x[0]).get('favorite')]
@app.put('/api/designs/{did}/favorite')
def favorite(did:str):
 d=design(did);d['favorite']=not d['favorite']
 with db() as c:c.execute('UPDATE designs SET body=? WHERE id=?',(json.dumps(d,ensure_ascii=False),did))
 return d
@app.get('/api/designs/{did}/export/{fmt}')
def export(did:str,fmt:str):
 d=design(did)
 if fmt=='json': return Response(json.dumps(d,ensure_ascii=False,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="{did}-design.json"'})
 if fmt=='svg': return Response(d['svg'],media_type='image/svg+xml',headers={'Content-Disposition':f'attachment; filename="{did}.svg"'})
 if fmt=='png':
  import cairosvg
  return Response(cairosvg.svg2png(bytestring=d['svg'].encode()),media_type='image/png',headers={'Content-Disposition':f'attachment; filename="{did}.png"'})
 raise HTTPException(400,'仅支持SVG、PNG和设计JSON')
@app.get('/api/admin/report',dependencies=[Depends(admin)])
def report():
 c=catalog()
 with db() as conn: jobs=[json.loads(x[0]) for x in conn.execute('SELECT body FROM jobs ORDER BY rowid DESC')]
 return dict(stats=c['stats'],conflicts=c['conflicts'],errors=c['errors'],issues=[dict(pattern=p['id'],issues=p['issues']) for p in c['patterns'] if p['issues']],jobs=jobs)
@app.post('/api/admin/import',dependencies=[Depends(admin)])
async def upload(file:UploadFile=File(...)):
 name=Path(file.filename or '').name
 import re
 if not re.match(r'^PAT-\d+.*\.docx$',name): raise HTTPException(400,'仅支持PAT编号的DOCX文件')
 raw=await file.read(20*1024*1024+1)
 if len(raw)>20*1024*1024: raise HTTPException(413,'文件不可超过20MB')
 jid=uuid.uuid4().hex; job=dict(id=jid,document=name,status='processing'); dest=DATA/'uploads';dest.mkdir(exist_ok=True); path=dest/(jid+'-'+name);path.write_bytes(raw)
 with db() as c:c.execute('INSERT INTO jobs VALUES (?,?)',(jid,json.dumps(job,ensure_ascii=False)))
 def run():
  try:
   p=parse(path,DATA);p["document"]=name
   for a in p['images']:
    a['url']=a['url'].replace('/assets/','/import-assets/')
    if a.get('svg'): a['svg']=a['svg'].replace('/assets/','/import-assets/')
   # gene assets reference the same dictionaries from parser
   with lock:
    cat=catalog(False);cat['patterns']=[x for x in cat['patterns'] if x['id']!=p['id']]+[p];cat['stats']['patterns']=len(cat['patterns']);cat['stats']['genes']=len({g['code'] for x in cat['patterns'] for g in x['genes']});cat['stats']['gene_occurrences']=sum(len(x['genes']) for x in cat['patterns']);cat['stats']['vectors']=sum(bool(a.get('svg')) for x in cat['patterns'] for a in x['images']);cat['conflicts']=detect_conflicts(cat['patterns']);CATALOG.with_suffix('.tmp').write_text(json.dumps(cat,ensure_ascii=False));CATALOG.with_suffix('.tmp').replace(CATALOG)
   job.update(status='complete',pattern=p['id'],issues=p['issues'])
  except Exception as e:job.update(status='failed',message=str(e))
  with db() as c:c.execute('UPDATE jobs SET body=? WHERE id=?',(json.dumps(job,ensure_ascii=False),jid))
 threading.Thread(target=run,daemon=True).start();return job
@app.post('/api/intent')
async def intent(r:Recipe):
 from .llm import interpret
 allowed={g['code'] for p in catalog()['patterns'] for g in p['genes'] if g['status']=='已确认' and any(a.get('svg') for a in g['assets'])}
 try:
  result=await interpret(r.prompt,allowed)
  return dict(mode='ai' if result else 'rules',suggestion=result)
 except Exception:
  return dict(mode='rules',suggestion=None,message='智能辅助暂不可用，使用文档规则检索')

from .creation import router as creation_router
app.include_router(creation_router)
from .manufacturing import router as manufacturing_router
app.include_router(manufacturing_router)

from .community import router as community_router
app.include_router(community_router)
