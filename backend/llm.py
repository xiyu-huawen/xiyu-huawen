"""Optional OpenAI/Ark-compatible intent helper. Geometry always comes from the registry."""
import os,json
import httpx
async def interpret(prompt,allowed_codes):
 base=os.getenv('ARK_BASE_URL') or os.getenv('AI_BASE_URL','');key=os.getenv('ARK_API_KEY') or os.getenv('AI_API_KEY','');model=os.getenv('ARK_MODEL') or os.getenv('AI_MODEL','')
 if not (base and key and model): return None
 async with httpx.AsyncClient(timeout=15) as client:
  response=await client.post(base.rstrip('/')+'/chat/completions',headers={'Authorization':'Bearer '+key},json={'model':model,'temperature':0,'messages':[{'role':'system','content':'你是锡语华纹非遗纹样基因推理引擎。仅返回JSON对象，包含keywords字符串数组、gene_codes字符串数组。只能从以下基因白名单选择：'+','.join(allowed_codes)},{'role':'user','content':prompt}]})
  response.raise_for_status();content=response.json()['choices'][0]['message']['content'].strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
  result=json.loads(content)
  return {'keywords':[s[:40] for s in result.get('keywords',[]) if isinstance(s,str)][:10],'gene_codes':[s for s in result.get('gene_codes',[]) if s in allowed_codes][:3]}
