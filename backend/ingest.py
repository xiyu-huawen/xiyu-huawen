"""Deterministic DOCX import; retain cell-level provenance and conflicting definitions."""
import hashlib,json,re,io
from pathlib import Path
from zipfile import ZipFile
import defusedxml.ElementTree as ET
from PIL import Image,ImageChops,ImageFilter
import vtracer
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
def txt(el): return ''.join(n.text or '' for n in el.iter(W+'t')).strip()
def parse(path,out):
 out=Path(out); (out/'assets').mkdir(parents=True,exist_ok=True)
 raw=Path(path).read_bytes(); version=hashlib.sha256(raw).hexdigest()[:16]
 with ZipFile(io.BytesIO(raw)) as z:
  if len(z.infolist())>3000 or sum(i.file_size for i in z.infolist())>100*1024*1024: raise ValueError('文档解压体积超限')
  root=ET.fromstring(z.read('word/document.xml'))
  rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('word/_rels/document.xml.rels')) if r.attrib.get('TargetMode')!='External'}
  text='\n'.join(txt(p) for p in root.iter(W+'p') if txt(p)); pid=re.search(r'PAT-\d+',Path(path).name).group()
  data=dict(id=pid,name=txt(next(root.iter(W+'p'))).replace(pid,'').strip(),version=version,document=Path(path).name,text=text,images=[],genes=[],imagery=[],relations=[],issues=[],colors=[])
  def images(el,where,code=None):
   result=[]
   for blip in el.iter(A+'blip'):
    target=rels.get(blip.attrib.get(R+'embed'),''); name='word/'+target.lstrip('/')
    if '..' in Path(name).parts or not name.startswith('word/media/'): continue
    b=z.read(name); h=hashlib.sha256(b).hexdigest()[:20]; ext=Path(name).suffix.lower(); filename=h+ext
    (out/'assets'/filename).write_bytes(b)
    asset=dict(url='/assets/'+filename,source=where,code=code,quality='bitmap',version=h)
    if code and code.startswith('M-'):
     try:
      src=Image.open(io.BytesIO(b)).convert('RGBA'); background=Image.new('RGBA',src.size,'white'); background.alpha_composite(src); im=background.convert('RGB'); im.thumbnail((1500,1500))
      mask=im.convert('L').point(lambda x:255 if x<170 else 0).filter(ImageFilter.MedianFilter(3)); bbox=mask.getbbox()
      ratio=sum(mask.histogram()[128:])/max(1,im.width*im.height)
      if not bbox or ratio<.002 or ratio>.8: raise ValueError('前景比例异常')
      mask=mask.crop(bbox); rgba=Image.new('RGBA',mask.size,(30,65,54,0)); rgba.putalpha(mask)
      png=out/'assets'/(h+'-clean.png'); mask.point(lambda x:255-x).convert('RGB').save(png)
      svg=out/'assets'/(h+'.svg'); vtracer.convert_image_to_svg_py(str(png),str(svg),colormode='binary',filter_speckle=8,mode='spline')
      tree=ET.parse(svg); sr=tree.getroot(); sr.set('viewBox',f'0 0 {mask.width} {mask.height}'); sr.set('width','1000'); sr.set('height','1000'); tree.write(svg,encoding='unicode')
      asset.update(svg='/assets/'+svg.name,quality='auto-vector',bounds=list(bbox))
     except Exception as e: data['issues'].append(dict(code=code,source=where,message='矢量化失败：'+str(e)))
    result.append(asset)
   return result
  body=root.find(W+'body'); pi=0
  for child in body:
   if child.tag==W+'p':
    data['images']+=images(child,f'paragraph:{pi}'); pi+=1
  for ti,table in enumerate(root.iter(W+'tbl')):
   rows=table.findall(W+'tr'); headers=[txt(c) for c in rows[0].findall(W+'tc')]
   for ri,row in enumerate(rows[1:],1):
    cells=row.findall(W+'tc'); vals=[txt(c) for c in cells]; where=f'table:{ti}/row:{ri}'
    if not vals: continue
    code=vals[0]
    for ci,c in enumerate(cells): data['images']+=images(c,where+f'/cell:{ci}',code)
    if headers[0]=='基因编码' and len(vals)>=6: data['genes'].append(dict(code=code,type=vals[1],name=vals[2],structure=vals[3],position=vals[4],status=vals[5],source=where))
    elif headers[0]=='意象编号' and len(vals)>=6: data['imagery'].append(dict(id=pid+':'+code,code=code,category=vals[1],word=vals[2],synonyms=vals[3],evidence=vals[4],status=vals[5]))
    elif headers[0]=='关系编号' and len(vals)>=7:
     data['relations'].append(dict(id=pid+':'+code,code=code,gene=vals[1].split('／')[0].split('/')[0],imagery=pid+':'+vals[2].split('／')[0].split('/')[0],type=vals[3],weight=float(vals[4]) if re.fullmatch(r'\d*\.?\d+',vals[4]) else 0,evidence=vals[5],status=vals[6]))
  for g in data['genes']: g['assets']=[a for a in data['images'] if a['code']==g['code']]
  for m in re.finditer(r'([^\s，。；]{2,8})\s*C(\d+)\s*M(\d+)\s*Y(\d+)\s*K(\d+)',text):
   c,mv,y,k=[int(x)/100 for x in m.groups()[1:]]; data['colors'].append(dict(name=m[1],hex='#'+''.join(f'{round(255*(1-v)*(1-k)):02x}' for v in [c,mv,y]),note='CMYK屏幕近似色'))
  if not data['genes']: data['issues'].append(dict(message='未识别基因表'))
  return data

def build(source,out):
 out=Path(out); patterns=[]; errors=[]
 for p in sorted(Path(source).glob('PAT-*.docx')):
  try: patterns.append(parse(p,out))
  except Exception as e: errors.append(dict(document=p.name,message=str(e)))
 registry={}; conflicts=[]
 for p in patterns:
  for g in p['genes']:
   key=g['code']; clean=lambda s:re.sub(r'〔.*?〕','',s).strip()
   if key in registry and clean(registry[key]['name'])!=clean(g['name']): conflicts.append(dict(code=key,first=registry[key]['pattern'],other=p['id'],names=[registry[key]['name'],g['name']]))
   registry.setdefault(key,dict(name=g['name'],pattern=p['id']))
 result=dict(patterns=patterns,stats=dict(patterns=len(patterns),genes=len(registry),gene_occurrences=sum(len(p['genes']) for p in patterns),vectors=sum(bool(a.get('svg')) for p in patterns for a in p['images'])),conflicts=conflicts,errors=errors)
 (out/'catalog.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
 (out/'quality-report.json').write_text(json.dumps(dict(stats=result['stats'],conflicts=conflicts,errors=errors,issues=[dict(pattern=p['id'],issues=p['issues']) for p in patterns if p['issues']]),ensure_ascii=False,indent=2))
 return result
if __name__=='__main__':
 import sys
 result=build(sys.argv[1],sys.argv[2]); print(json.dumps(result['stats'],ensure_ascii=False))
