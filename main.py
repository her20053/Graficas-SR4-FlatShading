from gl import *

glInit(width=1000, height=1000)

glColor(r=0,g=0,b=0)

glRenderObject('tree_obj.obj', (50, 50), (500, 0))

glFinish('SR3.bmp')
