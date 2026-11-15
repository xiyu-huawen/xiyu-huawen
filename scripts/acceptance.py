"""Verify image deployment, persistence, offline-ready assets and backup/restore in isolated Compose projects."""
import os,json,secrets,subprocess,time,urllib.request,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def execute(arch,port):
 project='xiyu-qa-'+arch+'-'+secrets.token_hex(3); restore_project=project+'-restore'; token=secrets.token_urlsafe(20)
 env=dict(os.environ,ADMIN_PASSWORD=token,PORT=str(port),IMAGE_TAG='1.3.0-'+arch,COMPOSE_PROJECT_NAME=project)
 def compose(*args,restore=False):
  return subprocess.run(['docker','compose','-p',restore_project if restore else project,*args],cwd=ROOT,env=env,check=True,capture_output=True,text=True).stdout
 def request(path,method='GET',data=None):
  req=urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=json.dumps(data).encode() if data is not None else None,method=method,headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as r:return r.read()
 def healthy():
  for _ in range(80):
   try:
    result=json.loads(request('/api/health'))
    if result['status']=='ok':return
   except Exception:pass
   time.sleep(1)
  raise RuntimeError('Health check timeout')
 backup=Path(tempfile.mkdtemp(prefix='xiyu-backup-'))/'data'; result={'architecture':arch,'project':project}
 try:
  compose('up','-d','--no-build','--wait','--wait-timeout','120');healthy()
  html=request('/');assert b'<html' in html
  import re
  for asset in re.findall(rb'(?:src|href)="([^"]+\.(?:js|css))"',html):
   payload=request(asset.decode());assert not payload.startswith(b'{"detail'),asset
   assert len(payload)>1000,asset
  cat=json.loads(request('/api/catalog'));assert cat['stats']['patterns']==60
  asset=cat['patterns'][0]['images'][0]['url'];assert len(request(asset))>100
  assert len(request('/fonts/NotoSerifSC.ttf'))>100000
  d=json.loads(request('/api/designs','POST',{'prompt':'八方安宁，规整','pattern_id':'PAT-005','auto_match':False,'width_mm':90,'height_mm':90}))
  assert b'90mm' in request('/api/designs/'+d['id']+'/export/svg')
  assert request('/api/designs/'+d['id']+'/export/png').startswith(b'\x89PNG')
  request('/api/designs/'+d['id']+'/favorite','PUT')
  a=json.loads(request('/api/community/patterns','POST',{'name':'续作持久化','svg':d['svg'],'source_design_id':d['id'],'rights_confirmed':True,'editor_state':{'version':1,'shapes':[],'template':d['svg'],'symmetry':1,'mirror':False}}))
  assert a['origin']=='contemporary' and a['source_refs']
  compose('restart','api');healthy();assert json.loads(request('/api/designs/'+d['id']))['favorite']
  assert json.loads(request('/api/community/patterns/'+a['id']))['editor_state']['version']==1
  assert request(a['images'][0]['url']).startswith(b'<')
  compose('stop','api');compose('cp','api:/data',str(backup));compose('start','api');healthy()
  # Restore to a newly-created independent volume, never overwrite the main deployment.
  compose('create','api',restore=True);compose('cp',str(backup)+'/.','api:/data/',restore=True)
  compose('run','--rm','--no-deps','--user','0','api','chown','-R','10001:10001','/data',restore=True)
  out=compose('run','--rm','--no-deps','api','python','-c','import sqlite3,json; c=sqlite3.connect("/data/platform.db"); p=json.loads(c.execute("select body from community_patterns limit 1").fetchone()[0]); from pathlib import Path; assert p["editor_state"]["version"]==1; assert Path("/data/assets/"+p["images"][0]["url"].rsplit("/",1)[-1]).is_file(); assert Path("/data/assets/"+p["images"][0]["svg"].rsplit("/",1)[-1]).is_file(); print(c.execute("select count(*) from designs").fetchone()[0])',restore=True)
  assert int(out.strip().splitlines()[-1])>=1
  result.update(status='passed',checks=['clean volume startup','60 documents','local image and font assets','SVG/PNG export','favorite persistence after restart','consistent backup','restore to independent volume','contemporary asset, editable recipe and source lineage persistence'],design=d['id'])
 finally:
  compose('down','-v','--remove-orphans');compose('down','-v','--remove-orphans',restore=True);shutil.rmtree(backup.parent,ignore_errors=True)
 return result
if __name__=='__main__':
 import sys
 arch=sys.argv[1];port=int(sys.argv[2]);result=execute(arch,port);path=ROOT/'logs'/('acceptance-'+arch+'.json');path.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
