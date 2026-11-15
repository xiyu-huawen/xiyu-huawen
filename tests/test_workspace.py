from fastapi.testclient import TestClient
from backend.app import app,Recipe
client=TestClient(app)
def test_vessel_shapes_roundtrip():
 for shape in ['leaf','arch','faceted','fluted','waist']:
  recipe=Recipe(vessel='bookmark',vessel_shape=shape)
  assert recipe.model_dump()['vessel_shape']==shape

def test_invalid_shape_is_rejected():
 result=client.post('/api/creation/preview',json={'vessel_shape':'untrusted'})
 assert result.status_code==422

def test_recommendation_input_boundaries():
 assert client.post('/api/creation/recommend',json={'prompt':''}).status_code==422
 assert client.post('/api/creation/recommend',json={'prompt':'x'*3001}).status_code==422
 res=client.post('/api/creation/recommend',json={'prompt':'爷爷八十寿辰，平时喜欢喝茶，希望定制一把紫砂壶'})
 assert res.status_code==200
 data=res.json()
 assert data.get('blessing_inscription') and data.get('craft_advice')
 assert isinstance(data.get('reasoning_steps'),list) and len(data['reasoning_steps'])==4

def test_dfm_craft_verification_engine():
 d=client.post('/api/designs',json={'pattern_id':'PAT-001','auto_match':False,'width_mm':120,'height_mm':120}).json()
 r=client.post('/api/manufacturing/dfm-check',json={'svg':d['svg'],'vessel':'pot','width_mm':120,'height_mm':120})
 assert r.status_code==200
 dfm=r.json()
 assert dfm['grade'] in ('A','B','C')
 assert dfm['min_feature_mm']>0
 assert len(dfm['solder_points'])==4
 assert 'Shapely' in dfm['master_advice']

def test_3d_printing_materials_catalog():
 r = client.get('/api/manufacturing/materials')
 assert r.status_code == 200
 mats = r.json()
 codes = [m['code'] for m in mats]
 assert 'pla' in codes and 'petg' in codes and 'abs' in codes and 'resin' in codes and 'tpu' in codes
 assert all('nozzle_temp_c' in m and 'bed_temp_c' in m and 'layer_height_mm' in m for m in mats)

def test_3d_printing_stl_and_bundle_export():
 import zipfile, io
 d = client.post('/api/designs', json={'pattern_id':'PAT-001','auto_match':False,'width_mm':120,'height_mm':120}).json()
 did = d['id']
 # 1. STL download with base
 r_stl = client.get(f'/api/manufacturing/{did}/stl?material=pla&thickness=1.2&with_base=true')
 assert r_stl.status_code == 200
 assert r_stl.content.startswith(b'XiyuHuawen 3D Print STL')
 assert len(r_stl.content) > 2000
 # 2. 3D Print bundle zip
 r_zip = client.get(f'/api/manufacturing/{did}/3dprint-package?material=petg&thickness=1.5&with_base=false')
 assert r_zip.status_code == 200
 z = zipfile.ZipFile(io.BytesIO(r_zip.content))
 names = z.namelist()
 assert any(n.endswith('-3dprint-petg.stl') for n in names)
 assert '3D打印切片与材料工艺指南.txt' in names
 assert '3d-printing-specs.json' in names
 # 3. Workshop package includes 3dprint sample
 r_eng = client.get(f'/api/manufacturing/{did}/package')
 assert r_eng.status_code == 200
 z_eng = zipfile.ZipFile(io.BytesIO(r_eng.content))
 assert any('3dprint' in n for n in z_eng.namelist())

def test_3d_printing_direct_stl():
 d = client.post('/api/designs', json={'pattern_id':'PAT-001','auto_match':False}).json()
 r = client.post('/api/manufacturing/export-stl', json={'svg': d['svg'], 'width_mm': 100, 'height_mm': 100, 'material': 'abs', 'thickness_mm': 1.6, 'with_base': True})
 assert r.status_code == 200
 assert len(r.content) > 2000
