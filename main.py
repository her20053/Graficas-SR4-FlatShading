from gl import *
from vector import V3

# glInit(width=200, height=200)
# glTriangle(V3(10,70), V3(50,160), V3(70,80), (1,1,0))
# glTriangle(V3(180, 50), V3(150, 1),  V3(70, 180), (0,1,1))
# glTriangle(V3(180, 150), V3(120, 160), V3(130, 180), (1,0,1))

glInit(width=1000, height=1000)
glRenderObject(name ='tree_obj.obj',scaleFactor=(40, 40, 100),translateFactor=(500, 0, 0))


glFinish('Triangulos.bmp')
