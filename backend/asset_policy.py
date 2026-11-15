def is_usable(g):
 return g.get('type')=='图元' and (g.get('status')=='已确认' or (g.get('origin')=='contemporary' and g.get('status')=='可复用')) and any(a.get('svg') for a in g.get('assets',[]))
