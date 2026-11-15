"""Supported preview carriers and suggested decoration canvases, in millimetres."""
from typing import Literal
VesselKind=Literal['pot','tray','bookmark','box','vase','pendant','lid','cup','penholder','incense','jar','plaque']
VESSELS={
 'pot':('紫砂壶','茶席',90,75,'curved'),
 'tray':('圆形茶承','茶席',120,120,'flat'),
 'bookmark':('书签','文房',30,140,'flat'),
 'box':('圆形首饰盒','随身',80,80,'flat'),
 'vase':('花器','案头',70,100,'curved'),
 'pendant':('圆形挂坠','随身',35,35,'flat'),
 'lid':('茶罐盖','茶席',70,70,'flat'),
 'cup':('茶杯','茶席',70,55,'curved'),
 'penholder':('笔筒','文房',75,90,'curved'),
 'incense':('香插','案头',80,80,'flat'),
 'jar':('茶叶罐','茶席',80,90,'curved'),
 'plaque':('案头摆牌','案头',100,130,'flat'),
}
def profiles():
 return [dict(id=k,name=v[0],category=v[1],decoration_width_mm=v[2],decoration_height_mm=v[3],surface=v[4]) for k,v in VESSELS.items()]
