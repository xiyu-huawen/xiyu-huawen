import os,tempfile,xml.etree.ElementTree as ET
os.environ['DATA_DIR']=tempfile.mkdtemp(prefix='xiyu-test-')
os.environ['ADMIN_PASSWORD']='test-password'
from fastapi.testclient import TestClient
from backend.app import app,catalog
client=TestClient(app)
def test_real_catalog_and_provenance():
 c=catalog();assert len(c['patterns'])==60
 p=client.get('/api/patterns/PAT-005').json()
 assert any(g['code']=='M-BW-020' for g in p['genes'])
 assert all(a['source'] and a['version'] for a in p['images'])
 assert all(i['id'].startswith('PAT-005:') for i in p['imagery'])
 assert all(r['id'].startswith('PAT-005:') for r in p['relations'])
 assert not c['errors']
def test_deterministic_generation_and_exports():
 req={'pattern_id':'PAT-005','auto_match':False,'seed':4,'color':'#bbccdd','template':'ring'}
 a=client.post('/api/designs',json=req).json();b=client.post('/api/designs',json=req).json()
 assert a['svg']==b['svg'];ET.fromstring(a['svg'])
 assert all(e['status']=='已确认' for e in a['evidence'])
 assert all(g['asset']['svg'] for g in a['genes'])
 assert client.get('/api/designs/'+a['id']).json()==a
 assert client.get('/api/designs/'+a['id']+'/export/svg').status_code==200
 png=client.get('/api/designs/'+a['id']+'/export/png');assert png.content.startswith(b'\x89PNG')
 assert client.put('/api/designs/'+a['id']+'/favorite').json()['favorite']
 assert any(x['id']==a['id'] for x in client.get('/api/designs').json())
def test_invalid_inputs_and_admin():
 assert client.post('/api/designs',json={'count':10000}).status_code==422
 assert client.post('/api/designs',json={'color':'<script>'}).status_code==422
 assert client.post('/api/designs',json={'gene_code':'NO-SUCH-GENE'}).status_code==422
 assert client.get('/api/admin/report').status_code==401
 assert client.get('/api/admin/report',headers={'Authorization':'Bearer test-password'}).status_code==200
 assert client.post('/api/admin/import',headers={'Authorization':'Bearer test-password'},files={'file':('bad.txt',b'bad')}).status_code==400

def test_all_patterns_can_generate():
 for p in catalog()['patterns']:
  response=client.post('/api/designs',json={'pattern_id':p['id'],'auto_match':False})
  if any(a.get('svg') for a in p['images']):
   assert response.status_code==200,(p['id'],response.text)
   assert response.json()['genes']
  else: assert response.status_code==422
def test_vector_keeps_negative_space():
 import cairosvg,io
 from PIL import Image
 from pathlib import Path
 # A double frame must retain its empty center after vectorization.
 path=Path(__file__).resolve().parents[1]/'seed/assets/38360dc3b8afe9a658f0.svg'
 image=Image.open(io.BytesIO(cairosvg.svg2png(url=str(path),output_width=200,output_height=200))).convert('RGBA')
 coverage=sum(a>128 for a in image.getchannel('A').getdata())/40000
 assert .10<coverage<.45
 assert image.getpixel((100,100))[3]==0
def test_cross_pattern_layers_and_provenance():
 req={'pattern_id':'PAT-005','auto_match':False,'layers':[{'pattern_id':'PAT-001','code':'M-SY-006','role':'center'},{'pattern_id':'PAT-005','code':'M-BW-020','role':'ring'}],'width_mm':90,'height_mm':90,'rotation':45}
 r=client.post('/api/designs',json=req);assert r.status_code==200,r.text
 d=r.json();assert {g['pattern'] for g in d['genes']}=={'PAT-001','PAT-005'}
 assert all(e['source_pattern'] in {'PAT-001','PAT-005'} for e in d['evidence'])
 assert 'width="90mm"' in d['svg']
 assert client.get('/api/designs/'+d['id']+'/export/json').json()['recipe']['layers']==req['layers']
 req['layers'][1]['role']='center'
 assert client.post('/api/designs',json=req).status_code==422
 req['layers'][1]['role']='ring';req['layers'][1]['code']='FAKE'
 assert client.post('/api/designs',json=req).status_code==422

def test_intent_is_explainable_without_provider():
 d=client.post('/api/designs',json={'prompt':'八方安宁，规整','auto_match':True}).json()
 assert d['match_trace']['imagery']
 assert all(i['status']=='已确认' for i in d['match_trace']['imagery'])
 assert d['match_trace']['recommendations']

def test_creation_directions_and_atlas():
 result=client.post('/api/creation/directions',json={'wish':'八方安宁','vessel':'tray'});assert result.status_code==200,result.text
 directions=result.json()['directions'];assert len(directions)==3
 assert len({x['svg'] for x in directions})==3
 assert all(x.get('operation_graph') for x in directions)
 assert all(any(e['evidence']=='八角象征八方' for e in x['evidence']) for x in directions)
 atlas=client.get('/api/creation/atlas').json();assert len([n for n in atlas['nodes'] if n['kind']!='知识文章'])==744
 assert len([n for n in atlas['nodes'] if n['kind']=='pattern'])==60
 assert client.post('/api/creation/directions',json={'wish':'无依据的寓意'}).status_code==422

def test_preview_commit_and_session():
 d=client.post('/api/creation/directions',json={'wish':'八方安宁'}).json()['directions'][0]
 assert d['preview_only']
 assert client.get('/api/designs/'+d['id']).status_code==404
 committed=client.post('/api/creation/commit',json=d['recipe']);assert committed.status_code==200
 assert client.get('/api/designs/'+committed.json()['id']).status_code==200
 r=d['recipe'];r['layers']=[x for x in r['layers'] if x['code']!=r['anchor']['code']]
 assert client.post('/api/creation/preview',json=r).status_code==422
 import uuid
 sid=str(uuid.uuid4());state={'stage':3,'wish':'八方安宁'}
 assert client.put('/api/creation/sessions/'+sid,json={'state':state}).status_code==200
 assert client.get('/api/creation/sessions/'+sid).json()==state

def test_extended_geometry_and_render_without_credentials():
 for template in ['mirror','checker','trail']:
  d=client.post('/api/creation/preview',json={'pattern_id':'PAT-005','auto_match':False,'template':template,'trajectory':[[150,200],[500,700],[850,400]],'geometry_mode':'outline'})
  assert d.status_code==200,(template,d.text)
  assert d.json()['operation_graph']['area']>0
 assert client.post('/api/creation/render',json={'design_id':'not-used'}).json()['status']=='unconfigured'

def test_manufacturing_package_and_request_queue():
 import io,zipfile,json,ezdxf
 d=client.post('/api/designs',json={'pattern_id':'PAT-005','auto_match':False,'width_mm':90,'height_mm':90}).json()
 package=client.get('/api/manufacturing/'+d['id']+'/package');assert package.status_code==200
 with zipfile.ZipFile(io.BytesIO(package.content)) as z:
  p=json.loads(z.read('parameters.json'));assert p['units']=='mm' and p['scale']=='1:1'
  cad=ezdxf.read(io.StringIO(z.read(d['id']+'-1to1-mm.dxf').decode()));assert cad.units==4
  assert all(e.closed for e in cad.modelspace().query('LWPOLYLINE'))
  assert len(cad.modelspace().query('LWPOLYLINE'))==sum(p['contours'].values())
  assert p['artwork_bounds_mm'][0]>=0 and p['artwork_bounds_mm'][2]<=90
 req=client.post('/api/manufacturing/requests',json={'design_id':d['id'],'quantity':2,'contact':'private contact','notes':'试制'}).json()
 assert 'contact' not in client.get('/api/manufacturing/requests/'+req['id']).json()
 assert client.get('/api/manufacturing/requests').status_code==401
 headers={'Authorization':'Bearer test-password'}
 assert client.put('/api/manufacturing/requests/'+req['id']+'/status',headers=headers,json={'status':'sampling','note':'参数沟通完成'}).json()['status']=='sampling'
 assert client.get('/api/manufacturing/requests/'+req['id']).json()['history']

def test_all_vessels_and_physical_dxf_coordinates():
 import io,zipfile,json,ezdxf
 for vessel in ['pot','tray','bookmark','box','vase','pendant','lid','cup','penholder','incense','jar','plaque']:
  d=client.post('/api/designs',json={'vessel':vessel,'pattern_id':'PAT-005','auto_match':False,'width_mm':50,'height_mm':80}).json()
  with zipfile.ZipFile(io.BytesIO(client.get('/api/manufacturing/'+d['id']+'/package').content)) as z:
   params=json.loads(z.read('parameters.json'));cad=ezdxf.read(io.StringIO(z.read(d['id']+'-1to1-mm.dxf').decode()));pts=[p for e in cad.modelspace().query('LWPOLYLINE') for p in e.get_points('xy')]
   bounds=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
   assert all(abs(a-b)<1e-6 for a,b in zip(bounds,params['artwork_bounds_mm']))

def test_atlas_uses_lightweight_thumbnails():
 atlas=client.get('/api/creation/atlas').json();n=next(n for n in atlas['nodes'] if n['kind']=='pattern')
 image=client.get(n['thumbnail']);assert image.status_code==200
 from PIL import Image
 import io
 im=Image.open(io.BytesIO(image.content));assert max(im.size)<=256
 assert len(image.content)<100000


def test_vessel_profiles_and_direction_canvas():
 from backend.vessels import VESSELS
 profiles=client.get('/api/vessels').json()
 assert len(profiles)==12 and {v['id'] for v in profiles}==set(VESSELS)
 for vessel in ['cup','penholder','incense','jar','plaque']:
  response=client.post('/api/creation/directions',json={'wish':'八方安宁','vessel':vessel})
  assert response.status_code==200,response.text
  directions=response.json()['directions']
  assert len(directions)==3
  assert all(d['recipe']['vessel']==vessel and (d['recipe']['width_mm'],d['recipe']['height_mm'])==VESSELS[vessel][2:4] for d in directions)
 assert client.post('/api/creation/directions',json={'wish':'八方安宁','vessel':'unknown'}).status_code==422


def test_planet_only_offers_eligible_creation_assets():
 nodes=client.get('/api/creation/atlas').json()['nodes']
 for n in nodes:
  if n['kind']=='pattern' and n['pattern'] in ('PAT-038','PAT-040'):assert not n['creatable']
  if n.get('usable'):assert n['kind']=='图元' and n['status']=='已确认'


def test_source_first_directions_preserve_source_and_avoid_false_semantics():
 r=client.post('/api/creation/directions',json={'wish':'客家漏石窗纹样','pattern_id':'PAT-001','gene_code':'M-SY-006'})
 assert r.status_code==200,r.text
 directions=r.json()['directions']
 assert all(d['anchor']['pattern_id']=='PAT-001' and d['anchor']['code']=='M-SY-006' for d in directions)
 assert all('本次图元来源' in d['rationale'] for d in directions)
 cross=next(d for d in directions if d['direction']=='跨源相生')
 assert len({g['pattern'] for g in cross['genes']})>1
 assert client.post('/api/creation/directions',json={'wish':'档案取材','pattern_id':'PAT-038'}).status_code==422
 assert client.post('/api/creation/directions',json={'wish':'档案取材','pattern_id':'missing'}).status_code==422

def test_contemporary_assets_are_real_vectors_and_reusable():
 from backend.geometry import read_geometry
 raw='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><path d="M100 100 L900 900" fill="none" stroke="#ffffff" stroke-width="10"/></svg>'
 payload={'name':'一线生长','description':'自由笔画形成的当代图形','svg':raw,'rights_confirmed':True,'editor_state':{'version':1,'shapes':[],'symmetry':1,'mirror':False,'template':'','sourceDesign':'','sourcePattern':''}}
 assert client.post('/api/community/patterns',json={**payload,'rights_confirmed':False}).status_code==422
 r=client.post('/api/community/patterns',json=payload);assert r.status_code==201,r.text
 p=r.json();assert p['origin']=='contemporary' and p['imagery']==[] and p['relations']==[]
 assert p['genes'][0]['status']=='可复用'
 assert p['images'][0]['url']!=p['images'][0]['svg']
 node=next(n for n in client.get('/api/creation/atlas').json()['nodes'] if n['id']=='pattern:'+p['id'])
 thumb=client.get(node['thumbnail']);assert thumb.status_code==200 and thumb.headers['content-type']=='image/webp'
 asset=client.get(p['images'][0]['svg']);assert asset.status_code==200
 geometry,_=read_geometry(asset.text);assert 11000<geometry.area<12000  # Stroke becomes an area, not a false closed triangle.
 assert client.get('/api/patterns/'+p['id']).json()['id']==p['id']
 assert any(g['pattern']==p['id'] for g in client.get('/api/genes').json())
 d=client.post('/api/designs',json={'pattern_id':p['id'],'auto_match':False,'geometry_mode':'union'});assert d.status_code==200,d.text
 design=d.json();assert design['contemporary_sources'][0]['id']==p['id'] and not design['evidence']
 assert '当代' in design['explanation']
 assert client.get('/api/manufacturing/'+design['id']+'/package').status_code==200
 assert next(a for a in client.get('/api/community/patterns').json() if a['id']==p['id'])['reuse_count']>=1
 directions=client.post('/api/creation/directions',json={'wish':p['name'],'pattern_id':p['id']});assert directions.status_code==200,directions.text
 assert all(x['anchor']['pattern_id']==p['id'] for x in directions.json()['directions'])

def test_community_svg_safety_and_immutable_lineage():
 import json
 bad=['<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', '<svg xmlns="http://www.w3.org/2000/svg"><path onload="alert(1)" d="M0 0 L100 100"/></svg>','<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.org/a.png"/></svg>','<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]><svg>&x;</svg>']
 for svg in bad:assert client.post('/api/community/patterns',json={'name':'拒绝危险输入','svg':svg,'rights_confirmed':True}).status_code==422
 source=client.post('/api/designs',json={'pattern_id':'PAT-005','auto_match':False,'geometry_mode':'union'}).json()
 p=client.post('/api/community/patterns',json={'name':'沿八角续作','svg':source['svg'],'source_design_id':source['id'],'rights_confirmed':True}).json()
 assert p['source_design_id']==source['id'] and any(x['pattern']=='PAT-005' for x in p['source_refs'])
 child=client.post('/api/community/patterns',json={'name':'第二次续作','svg':source['svg'],'source_pattern_id':p['id'],'rights_confirmed':True}).json()
 assert child['id']!=p['id'] and child['source_pattern_id']==p['id']
 assert any(x['pattern']=='PAT-005' for x in child['source_refs'])
 assert client.get('/api/community/patterns/'+p['id']).json()['version']==p['version']
 forged={'version':1,'shapes':[],'template':source['svg'],'symmetry':1}
 assert client.post('/api/community/patterns',json={'name':'缺少底稿依据','svg':source['svg'],'editor_state':forged,'rights_confirmed':True}).status_code==422
 forged['template']=bad[0]
 assert client.post('/api/community/patterns',json={'name':'危险底稿','svg':source['svg'],'editor_state':forged,'source_design_id':source['id'],'rights_confirmed':True}).status_code==422


def test_knowledge_references_follow_creation_and_asset_reuse():
 from backend.app import SEED
 import json
 records=json.loads((SEED/'knowledge_sources.json').read_text())
 a=next(a for a in records if a['source_refs'])
 d=client.post('/api/designs',json={'pattern_id':a['pattern'],'auto_match':False,'knowledge_article_ids':[a['id']]}).json()
 assert d['knowledge_refs'][0]['id']==a['id'] and d['knowledge_refs'][0]['source_refs'][0]['url'].startswith('https://')
 p=client.post('/api/community/patterns',json={'name':'读纹再创作','svg':d['svg'],'source_design_id':d['id'],'rights_confirmed':True,'editor_state':{'version':1,'shapes':[],'template':d['svg'],'symmetry':1,'mirror':False}}).json()
 assert p['knowledge_refs'][0]['id']==a['id']
 reused=client.post('/api/designs',json={'pattern_id':p['id'],'auto_match':False,'template':'original','scale':1}).json()
 assert reused['knowledge_refs'][0]['source_refs']==a['source_refs']
 assert client.post('/api/designs',json={'knowledge_article_ids':['invented-source']}).status_code==422
 graph=client.get('/api/creation/atlas').json();assert len([n for n in graph['nodes'] if n['kind']=='知识文章'])==17
 assert any(e['kind']=='reading' and e['source']=='pattern:'+p['id'] for e in graph['edges'])
 assert any(e['kind']=='derivation' and e['source']=='pattern:'+p['id'] for e in graph['edges'])


def test_original_fill_rules_match_reusable_geometry():
 from backend.community import normalize_svg
 from backend.geometry import read_geometry
 same='M100 100H300V300H100Z M150 150H250V250H150Z'
 opposite='M100 100H300V300H100Z M150 150V250H250V150Z'
 for path,rule,area in [(same,'nonzero',40000),(same,'evenodd',30000),(opposite,'nonzero',30000)]:
  svg='<svg xmlns="http://www.w3.org/2000/svg"><path fill="#000000" fill-rule="'+rule+'" d="'+path+'"/></svg>'
  normalized=normalize_svg(svg);geometry,_=read_geometry(normalized)
  assert abs(geometry.area-area)<.01



def test_sparse_direction_uses_bounded_negative_ring():
 from backend.geometry import read_geometry
 result=client.post('/api/creation/directions',json={'wish':'八方安宁','vessel':'pot'})
 assert result.status_code==200,result.text
 sparse=next(d for d in result.json()['directions'] if d['direction']=='疏朗留白')
 graph=sparse['operation_graph']
 assert graph['operation']=='sparse' and graph['engine_version']=='2.1'
 assert graph['negative_space']>.75
 assert graph['area']<200000
 geometry,_=read_geometry(sparse['svg'])
 assert geometry.is_valid and not geometry.is_empty
 assert all(part.area>=4 for part in getattr(geometry,'geoms',[geometry]))


def test_sparse_mode_stays_bounded_across_source_patterns():
 for pattern_id in ['PAT-001','PAT-004','PAT-005','PAT-039','PAT-057']:
  response=client.post('/api/designs',json={'pattern_id':pattern_id,'auto_match':False,'geometry_mode':'sparse'})
  assert response.status_code==200,(pattern_id,response.text)
  graph=response.json()['operation_graph']
  assert graph['operation']=='sparse' and graph['negative_space']>.65,(pattern_id,graph)
  assert graph['area']<250000,(pattern_id,graph)
