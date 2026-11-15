"""Run the local API with private .env configuration (never prints values)."""
import os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
for line in (root/'.env').read_text().splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  key,value=line.split('=',1);os.environ.setdefault(key.strip(),value.strip())
import uvicorn
uvicorn.run('backend.app:app',host='127.0.0.1',port=8000)
