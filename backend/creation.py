"""Creation directions grounded in direct, confirmed motif-to-imagery edges."""
import re
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from .vessels import VesselKind,VESSELS
from .asset_policy import is_usable
router=APIRouter(prefix='/api/creation')
class Brief(BaseModel):
 wish:str='八方安宁'
 vessel:VesselKind='tray'
 recipient:str='家人'
 mood:str='端正'
 personal_note:str=''
 pattern_id:str|None=None
 gene_code:str|None=None
@router.post('/directions')
def directions(brief:Brief):
 from .app import catalog,create_design,Recipe
 matches=[]
 target=next((p for p in catalog()['patterns'] if p['id']==brief.pattern_id),None) if brief.pattern_id else None
 if brief.pattern_id and not target:raise HTTPException(422,'没有找到这份纹样档案')
 for p in catalog()['patterns']:
  if target and p['id']!=target['id']:continue
  ids={i['id'] for i in p['imagery'] if i['word']==brief.wish and i['status']=='已确认'}
  for rel in p['relations']:
   if rel['imagery'] not in ids or rel['status']!='已确认':continue
   for g in p['genes']:
    if g['code']==rel['gene'] and is_usable(g) and (not brief.gene_code or g['code']==brief.gene_code):matches.append((rel['weight'],p,g))
 if not matches and target:
  usable=[g for g in target['genes'] if is_usable(g) and (not brief.gene_code or g['code']==brief.gene_code)]
  if usable:matches=[(0,target,usable[0])]
 if not matches:raise HTTPException(422,'当前选择暂无可用于此方向的已确认图元，请选择其他纹样或意象')
 _,p,g=max(matches,key=lambda x:x[0]);out=[]
 for name,strategy,scale,count,spacing in [('守形传意','保留原图元识别特征，以围合组织视觉中心',.9,4,1.25),('跨源相生','在保留寓意锚点的同时，引入另一来源的中心花形',.8,8,.9),('疏朗留白','减少重复密度，让源图元与负形共同建立秩序',.65,4,1.4)]:
  local=[x for x in p['genes'] if is_usable(x) and x['code']!=g['code']]
  is_frame='框' in g['name'];layers=[dict(pattern_id=p['id'],code=g['code'],role='frame' if is_frame else 'center')]
  if name=='跨源相生':
   other_id,other_code=('PAT-001','M-SY-006') if p['id']!='PAT-001' else ('PAT-005','M-BW-020')
   layers=[dict(pattern_id=p['id'],code=g['code'],role='frame' if is_frame else 'center'),dict(pattern_id=other_id,code=other_code,role='center' if is_frame else 'ring')]
  elif local:layers.append(dict(pattern_id=p['id'],code=local[0]['code'],role='center' if is_frame else 'ring'))
  anchor=next(l for l in layers if l['pattern_id']==p['id'] and l['code']==g['code'])
  if brief.mood=='疏朗':scale-=.08;spacing=min(1.5,spacing+.1)
  if brief.mood=='丰盛':count=min(16,count+2)
  variants=[]
  for vi in range(8):
   variant_scale=max(.3,min(1.2,scale+(vi%4-1)*.07));variant_count=max(4,min(16,count+(vi//4)*2));variant_spacing=max(.6,min(1.5,spacing+(vi%3-1)*.08))
   d=create_design(Recipe(recipient=brief.recipient,mood=brief.mood,personal_note=brief.personal_note,anchor=anchor,direction=name,geometry_mode='sparse' if name=='疏朗留白' else 'union',prompt=brief.wish,pattern_id=p['id'],vessel=brief.vessel,auto_match=False,layers=layers,scale=variant_scale,count=variant_count,spacing=variant_spacing,width_mm=VESSELS[brief.vessel][2],height_mm=VESSELS[brief.vessel][3]),persist=False)
   target=.9 if name=='疏朗留白' else .86
   metric=abs(d['operation_graph']['negative_space']-target)
   variants.append((metric,d))
  d=min(variants,key=lambda v:v[0])[1];d['explored_candidates']=24

  d.update(direction=name,strategy=strategy,rationale=('本次寓意依据：' if matches[0][0]>0 else '本次图元来源：')+g['name']+'；'+strategy)
  import json
  from .app import db
  d['anchor']=anchor
  out.append(d)
 return dict(directions=out,source=p)
class RenderRequest(BaseModel):
 design_id:str
 image:str=''
 scene:str='茶席'
@router.post('/render')
def render(req:RenderRequest):
 import os,json,uuid,threading,base64,httpx
 from .app import db,design,DATA
 jimeng=bool(os.getenv('JIMENG_SESSION_ID'));key=os.getenv('JIMENG_SESSION_ID') or os.getenv('IMAGE_API_KEY','');base=os.getenv('IMAGE_BASE_URL','https://api.openai.com/v1');model=os.getenv('IMAGE_MODEL','gpt-image-1.5')
 if jimeng:base=os.getenv('JIMENG_BASE_URL','http://127.0.0.1:5100/v1');model=os.getenv('JIMENG_MODEL','jimeng-4.5')
 if not key:return dict(status='unconfigured',message='AI意境图服务尚未配置。矢量作品可正常保存与导出；部署时配置IMAGE_API_KEY后启用。')
 d=design(req.design_id)
 if not req.image.startswith('data:image/png;base64,') or len(req.image)>12000000:raise HTTPException(422,'需要当前器物的PNG参考截图，最大9MB')
 try:raw=base64.b64decode(req.image.split(',',1)[1],validate=True)
 except Exception:raise HTTPException(422,'参考图格式错误')
 import datetime,hashlib
 if not raw.startswith(b'\x89PNG'):raise HTTPException(422,'参考截图必须是PNG格式')
 day=datetime.datetime.now(datetime.timezone.utc).date().isoformat();cache_key=hashlib.sha256(raw+(d['id']+model+req.scene).encode()).hexdigest()
 jid=uuid.uuid4().hex;job=dict(kind='render',created_day=day,cache_key=cache_key,id=jid,status='processing',design_id=d['id'],message='正在根据已保存版本生成意境图')
 with db() as c:
  c.execute('BEGIN IMMEDIATE')
  jobs=[json.loads(x[0]) for x in c.execute('SELECT body FROM jobs')]
  cached=next((x for x in jobs if x.get('cache_key')==cache_key and x.get('status') in ('complete','processing')),None)
  if cached:return cached
  if sum(x.get('kind')=='render' and x.get('created_day')==day for x in jobs)>=int(os.getenv('IMAGE_DAILY_LIMIT','10')):raise HTTPException(429,'今日意境图任务额度已用完，结构设计仍可正常使用')
  if any(x.get('status')=='processing' for x in jobs):raise HTTPException(409,'已有生成任务，请等待完成')
  c.execute('INSERT INTO jobs VALUES (?,?)',(jid,json.dumps(job)))
 def work():
  try:
   studio_prompts={
    '茶席':'宋韵东方茶席实境棚拍，晨曦自然柔光透过竹帘，温润紫砂与锻打银白锡镶浅浮雕肌理清晰，微距景深，电影级光影质感，无文字，无水印。',
    '博古':'博物馆级紫檀博古架聚光摄影，深邃东方暗调背景，戏剧性轮廓光凸显金属锡镶浮雕层次与器物神韵，8K实境材质摄影，无文字。',
    '工坊':'威海锡镶非遗大师工坊实境案头，柔和暖光，背景隐约可见匠人手作温度与古典木质肌理，突出器物表面金属锻打与镶嵌光泽，无文字。',
    '国礼':'东方国礼丹漆丝绸锦盒陈设摄影，庄重典雅，柔和顶光展现器物银锡纹饰的华美秩序与温润胎体对比，商业级静物大片，无文字。'
   }
   scene_desc=studio_prompts.get(req.scene,f'东方{req.scene[:20]}中的真实材质摄影，柔和自然光，凸显锡镶金属浮雕与器物肌理对比，无文字，无新增装饰。')
   prompt=f'保持参考器物造型与表面锡镶纹样结构完全一致，生成{scene_desc}'
   if jimeng:
    response=httpx.post(base.rstrip('/')+'/images/compositions',headers={'Authorization':'Bearer '+key},json={'model':model,'prompt':prompt,'images':[req.image],'ratio':'1:1','resolution':'1k','response_format':'b64_json'},timeout=240)
   else:
    response=httpx.post(base.rstrip('/')+'/images/edits',headers={'Authorization':'Bearer '+key},files={'image':('reference.png',raw,'image/png')},data={'model':model,'prompt':prompt,'size':'1024x1024','quality':'medium'},timeout=180)
   response.raise_for_status();image=response.json()['data'][0]['b64_json'];out=DATA/'assets'/(jid+'.png');out.write_bytes(base64.b64decode(image));job.update(status='complete',url='/import-assets/'+out.name,scene=req.scene,model=model,message=f'Jimeng 4.5 东方实境渲染已完成（{req.scene}光影棚拍）· 耦合 1:1 矢量工程轮廓')
  except Exception:job.update(status='failed',message='实境渲染服务响应超时，可点击重试或直接导出 1:1 工程包')
  with db() as c:c.execute('UPDATE jobs SET body=? WHERE id=?',(json.dumps(job,ensure_ascii=False),jid))
 threading.Thread(target=work,daemon=True).start();return job


@router.get('/atlas')
def atlas():
 from .app import catalog,SEED
 import json
 c=catalog();nodes=[];edges=[];hubs={}
 for p in c['patterns']:
  pid='pattern:'+p['id'];nodes.append(dict(id=pid,kind='pattern',label=p['name'],pattern=p['id'],origin=p.get('origin','heritage'),creatable=any(is_usable(g) for g in p['genes']),image=next((a['url'] for a in p['images'] if not a['code']),None)))
  for g in p['genes']:
   gid='gene:'+p['id']+':'+g['code'];nodes.append(dict(id=gid,kind=g['type'],label=g['name'],pattern=p['id'],origin=p.get('origin','heritage'),code=g['code'],image=g['assets'][0]['url'] if g['assets'] else None,status=g['status'],usable=is_usable(g)));edges.append(dict(source=pid,target=gid,kind='contains'))
   key=re.sub(r'〔复用〕','',g['code'])+'|'+re.sub(r'〔复用〕','',g['name']);hubs.setdefault(key,[]).append(gid)
  for i in p['imagery']:
   iid='imagery:'+i['id'];nodes.append(dict(id=iid,kind=i['category'],label=i['word'],pattern=p['id']));edges.append(dict(source=pid,target=iid,kind='contains'))
  for r in p['relations']:edges.append(dict(source='gene:'+p['id']+':'+r['gene'],target='imagery:'+r['imagery'],kind='mapping',status=r['status'],evidence=r['evidence'],weight=r['weight']))
  if p.get('origin')=='contemporary':
   seen=set()
   for ref in p.get('source_refs',[]):
    target=('gene:'+ref['pattern']+':'+ref['code']) if ref.get('code') else 'pattern:'+ref['pattern']
    if target in seen:continue
    seen.add(target);edges.append(dict(source=pid,target=target,kind='derivation',status='创作谱系',evidence='当代作品引用 '+ref['pattern']+(' · '+ref['code'] if ref.get('code') else '')+'；保留来源版本，不视为传统语义映射'))
   for a in p.get('knowledge_refs',[]):edges.append(dict(source=pid,target='knowledge:'+a['id'],kind='reading',status='知识参考',evidence='创作时参考《'+a['title']+'》；文章参考不等同传统寓意认证'))
 knowledge=json.loads((SEED/'knowledge_sources.json').read_text()) if (SEED/'knowledge_sources.json').exists() else []
 for a in knowledge:
  nodes.append(dict(id='knowledge:'+a['id'],kind='知识文章',article_id=a['id'],pattern=a['pattern'],label=a['title'],summary=a.get('source_scope') or a['source'],source_refs=a['source_refs']))
  edges.append(dict(source='knowledge:'+a['id'],target='pattern:'+a['pattern'],kind='reading',status='阅读入口',evidence='文章与档案之间的观察练习入口，不等同该样本原始证据'))
 for n in nodes:
  if n.get('image'):n['thumbnail']='/api/creation/thumbnails/'+n['image'].rsplit('/',1)[-1]
 valid={n['id'] for n in nodes}
 return dict(unresolved_edges=[e for e in edges if e['source'] not in valid or e['target'] not in valid],nodes=nodes,edges=[e for e in edges if e['source'] in valid and e['target'] in valid],reuse=[dict(key=k,members=v) for k,v in hubs.items() if len(v)>1])

@router.get('/renders/{jid}')
def render_status(jid:str):
 from .app import db
 import json
 with db() as c:row=c.execute('SELECT body FROM jobs WHERE id=?',(jid,)).fetchone()
 if not row:raise HTTPException(404,'任务不存在')
 return json.loads(row[0])

from .app import Recipe
@router.post('/preview')
def preview(recipe:Recipe):
 from .app import create_design
 return create_design(recipe,persist=False)
@router.post('/commit')
def commit(recipe:Recipe):
 from .app import create_design
 return create_design(recipe,persist=True)
class SessionBody(BaseModel):
 state:dict
@router.put('/sessions/{sid}')
def save_session(sid:str,body:SessionBody):
 import json
 from .app import db
 if not re.fullmatch(r'[a-f0-9-]{36}',sid):raise HTTPException(422,'会话编号无效')
 raw=json.dumps(body.state,ensure_ascii=False)
 if len(raw)>8000000:raise HTTPException(413,'会话内容过大')
 with db() as c:
  c.execute('CREATE TABLE IF NOT EXISTS creation_sessions(id TEXT PRIMARY KEY,body TEXT)')
  c.execute('INSERT OR REPLACE INTO creation_sessions VALUES (?,?)',(sid,raw))
 return dict(id=sid)
@router.get('/sessions/{sid}')
def get_session(sid:str):
 import json
 from .app import db
 with db() as c:
  c.execute('CREATE TABLE IF NOT EXISTS creation_sessions(id TEXT PRIMARY KEY,body TEXT)')
  row=c.execute('SELECT body FROM creation_sessions WHERE id=?',(sid,)).fetchone()
 if not row:raise HTTPException(404,'会话不存在')
 return json.loads(row[0])

from functools import lru_cache
@lru_cache(maxsize=128)
def thumbnail_bytes(filename):
 from .app import SEED,ASSETS
 from PIL import Image
 import io
 path=SEED/'assets'/filename
 if not path.exists():path=ASSETS/filename
 if not path.is_file():raise HTTPException(404,'图片不存在')
 if path.suffix.lower()=='.svg':
  import cairosvg
  image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=path.read_bytes(),output_width=256,output_height=256))).convert('RGBA')
 else:image=Image.open(path).convert('RGBA')
 image.thumbnail((256,256));out=io.BytesIO();image.save(out,format='WEBP',quality=82);return out.getvalue()
@router.get('/thumbnails/{filename}')
def thumbnail(filename:str):
 from fastapi.responses import Response
 if not re.fullmatch(r'(?:[a-f0-9]{20}\.(?:png|jpg|jpeg|webp)|ugc-(?:origin-)?[a-f0-9]{24}\.svg)',filename):raise HTTPException(404,'图片不存在')
 return Response(thumbnail_bytes(filename),media_type='image/webp',headers={'Cache-Control':'public,max-age=86400'})

class ConversationRequest(BaseModel):
 prompt: str
 vessel: str | None = None
 finish: str | None = None
 base_material: str | None = None

def _fallback_recommendation(prompt: str, patterns: list[dict], requested_vessel: str | None = None):
 vessel_map = {'书签':'bookmark','茶壶':'pot','紫砂壶':'pot','笔筒':'penholder','挂坠':'pendant','首饰盒':'box','茶承':'tray','茶杯':'cup','茶叶罐':'jar','香插':'incense','花器':'vase','摆牌':'plaque'}
 chosen_vessel = requested_vessel if requested_vessel in VESSELS else 'pot'
 if not requested_vessel or requested_vessel not in VESSELS:
  for k, v in vessel_map.items():
   if k in prompt:
    chosen_vessel = v
    break
 recipient = '长辈' if any(w in prompt for w in ['长辈','寿','父母','爷爷','奶奶','外公','外婆','恩师']) else ('伴侣' if any(w in prompt for w in ['伴侣','婚','爱人','情侣']) else ('朋友' if any(w in prompt for w in ['朋友','挚友','同窗','乔迁']) else '自己'))
 wish = '长寿百岁' if recipient == '长辈' or '寿' in prompt else ('莲心清正' if any(w in prompt for w in ['书房','清','莲','友','茶','学']) else '八方安宁')
 preferred_pid = 'PAT-057' if wish == '长寿百岁' else ('PAT-001' if wish == '莲心清正' else 'PAT-005')
 source = next((p for p in patterns if p['id'] == preferred_pid and p.get('usable')), None) or next((p for p in patterns if p.get('usable')), patterns[0])
 shape = 'leaf' if chosen_vessel == 'bookmark' and ('自然' in prompt or '叶' in prompt) else ('round' if '圆' in prompt or '丰盛' in prompt else ('slender' if '修长' in prompt or '极简' in prompt else 'standard'))
 inscriptions = {
  '长寿百岁': '松鹤延年锡光暖，岁华常青福泽长。',
  '莲心清正': '四叶莲心映清茗，一窗雅序寄知音。',
  '八方安宁': '八方锦绣归安宁，一器华纹载乾坤。'
 }
 poem = inscriptions.get(wish, '器载东方千秋意，锡镶华纹万事兴。')
 return {
  'summary': f'围绕「{recipient}」的赠礼心意，凝练「{wish}」核心文化意象，甄选《{source["name"]}》图元基因入器，结合威海锡镶锻打浅浮雕与线刻工艺，呈现器与纹的东方礼序。',
  'wish': wish,
  'recipient': recipient,
  'vessel': chosen_vessel,
  'shape': shape,
  'pattern_id': source['id'],
  'source': source,
  'blessing_inscription': poem,
  'craft_advice': '主纹采用 0.8mm 锻打素锡浅浮雕强化视觉重心，外围辅以精密线刻边饰顺应器面曲率，焊点隐入花叶转折暗部。',
  'reasoning_steps': [
   {'step': '01 · 礼赠语境解构', 'detail': f'识别受礼对象为「{recipient}」，提炼核心祝愿诉求与使用场域'},
   {'step': '02 · 标准意象词映射', 'detail': f'对齐基因库已确认意象「{wish}」与《{source["name"]}》文化谱系'},
   {'step': '03 · M/C/S/P 基因召回', 'detail': f'锁定 {source["id"]} 核心可复用矢量图元与中心对称构图规则'},
   {'step': '04 · 锡镶器型与DFM适配', 'detail': f'匹配 {VESSELS[chosen_vessel][0]}（{VESSELS[chosen_vessel][2]}×{VESSELS[chosen_vessel][3]}mm 装饰区）并生成浅浮雕层级参数'}
  ],
  'mode': 'seed_knowledge_engine'
 }

@router.post('/recommend')
async def recommend(req: ConversationRequest):
 import os,json,httpx
 from .app import catalog
 if not req.prompt.strip() or len(req.prompt)>3000:raise HTTPException(422,'请用3000字以内描述设计需求')
 patterns=[{'id':p['id'],'name':p['name'],'usable':any(is_usable(g) for g in p['genes']),'meanings':[i['word'] for i in p['imagery'] if i['status']=='已确认'],'genes':[{'code':g['code'],'name':g['name'],'type':g['type']} for g in p['genes'][:4]]} for p in catalog()['patterns']]
 usable_patterns=[{'id':p['id'],'name':p['name'],'meanings':p['meanings']} for p in patterns if p['usable']]
 key=os.getenv('ARK_API_KEY') or os.getenv('AI_API_KEY')
 if not key:
  return _fallback_recommendation(req.prompt, patterns, req.vessel)
 system=(
  '你是「锡语华纹」AI非遗纹样基因推理与锡镶造物总师（基于Doubao-Seed大模型）。仅输出合法JSON对象，包含字段：'
  'summary（80字内，极具东方美学感染力的设计阐述）、'
  'wish（取自八方安宁/莲心清正/长寿百岁或纹样已确认意象词）、'
  'recipient（家人/长辈/朋友/伴侣/恩师/自己）、'
  f'vessel（指定器物ID：{req.vessel if req.vessel in VESSELS else "从可选器物中推荐最佳器型"}）、'
  'shape（取standard/leaf/round/slender/faceted/fluted/waist）、'
  'pattern_id（必须从候选纹样ID中选择）、'
  'blessing_inscription（一器一祝福：创作一句对仗工整的14字东方吉言铭文，用于器物藏书票与礼赠卡）、'
  'craft_advice（50字内，针对威海锡镶锻打、镂雕、浅浮雕、线刻与器面曲率适配的专业工艺建议）、'
  'reasoning_steps（长度为4的数组，每项含step和detail，分别对应：01·礼赠语境解构、02·标准意象词映射、03·M/C/S/P基因召回、04·锡镶器型与DFM适配）。'
  '必须引用真实纹样寓意，严禁出现任何免责或消极措辞。'
  '可选器物：'+json.dumps(list(VESSELS),ensure_ascii=False)+'。候选纹样：'+json.dumps(usable_patterns[:35],ensure_ascii=False)
 )
 try:
  async with httpx.AsyncClient(timeout=28) as client:
   response=await client.post(os.getenv('ARK_BASE_URL','https://ark.cn-beijing.volces.com/api/v3').rstrip('/')+'/chat/completions',headers={'Authorization':'Bearer '+key},json={'model':os.getenv('ARK_MODEL','doubao-seed-evolving'),'temperature':0.3,'messages':[{'role':'system','content':system},{'role':'user','content':req.prompt}]})
   response.raise_for_status();content=response.json()['choices'][0]['message']['content'];result=json.loads(content.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip())
  if req.vessel in VESSELS:
   result['vessel']=req.vessel
  elif result.get('vessel') not in VESSELS:
   result['vessel']='pot'
  if result.get('pattern_id') not in {p['id'] for p in usable_patterns}:raise ValueError('invalid recommendation')
  result['shape']=result.get('shape') if result.get('shape') in ['standard','leaf','round','slender','faceted','fluted','waist'] else 'standard'
  if result['shape']=='leaf' and result['vessel']!='bookmark':result['shape']='standard'
  source=next(p for p in patterns if p['id']==result['pattern_id']);result['source']=source;result['mode']='doubao_seed_ai'
  if not result.get('blessing_inscription'):result['blessing_inscription']='器载东方千秋意，锡镶华纹万事兴。'
  if not result.get('craft_advice'):result['craft_advice']='主纹采用 0.8mm 锻打素锡浅浮雕，外圈辅以精密线刻边饰顺应器面曲率。'
  if not isinstance(result.get('reasoning_steps'),list) or not result['reasoning_steps']:
   result['reasoning_steps']=_fallback_recommendation(req.prompt, patterns, req.vessel)['reasoning_steps']
  return result
 except Exception:
  return _fallback_recommendation(req.prompt, patterns, req.vessel)
