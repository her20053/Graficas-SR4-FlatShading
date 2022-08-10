from math import floor
from render import *
from utilities import *

objetoRender = None

def glInit(width, height):
	glCreateWindow(width,height)

def glCreateWindow(width, height):
	global objetoRender
	objetoRender = Render(width, height)

def glViewport(x,y, width, height):

	global objetoRender

	objetoRender.vp_x = x
	objetoRender.vp_y = y
	objetoRender.vp_width = width 
	objetoRender.vp_height = height

	for ancho in range(x, width+x):
		for alto in range(y, height+y):
			objetoRender.point(ancho,alto)

def glClear():
	objetoRender.clear()

def glClearColor(r, g, b):
	objetoRender.clear_color = color(round(255*r), round(255*g), round(255*b))
	glClear()

def glColor(r, g, b):
	objetoRender.current_color = color(round(255*r), round(255*g), round(255*b))

def glVertex(x,y):
	objetoRender.current_color = color(0,255,0)

def glLine(x0, y0, x1, y1):

	# CONVERTIR COORDENADAS EN RENDER

	objetoRender.line(x0, y0, x1, y1)

def glPoint(x, y):
	objetoRender.point(x,y)

def glRenderObject(name, scaleFactor, translateFactor):
	objetoRender.renderObject(name, scaleFactor, translateFactor)

def glFinish(fileName):
	objetoRender.write(fileName)


def glCreateLine(x0, y0, x1, y1):
	objetoRender.line(*objetoRender.convertirCoordenadas(x0,y0), *objetoRender.convertirCoordenadas(x1,y1))


