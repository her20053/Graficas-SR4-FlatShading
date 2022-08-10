# Importando libreria para manejo de bytes
from utilities import *

# Importando libreria para manejo de colores
from colors import *

from vector import V3

import random

class Obj(object):
  def __init__(self, filename):
    with open(filename) as f:
      self.lines = f.read().splitlines()

    self.vertices = []
    self.faces = []

    for line in self.lines:

      if line:

        if ' ' not in line:
          continue

        prefix, value = line.split(' ', 1)

        if value[0] == ' ':
          value = '' + value[1:]
        
        if prefix == 'v':
          self.vertices.append(
            list(
              map(float, value.split(' '))
            )
          )

        if prefix == 'f':
          self.faces.append([
            list(map(int, face.split('/')))
                for face in value.split(' ') if face != ''
          ]) 

class Render(object):

	# Metodo ejecutado al inicializar la clase:
    def __init__(self, width, height):
		
		# Estableciendo el ancho y el largo del framebuffer
        self.width = width  
        self.height = height    
        
		# Estableciendo el desface del Viewport en el framebuffer
        self.vp_x = 0
        self.vp_y = 0

		# Estableciendo el ancho y el largo del Viewport
        self.vp_width = 0
        self.vp_height = 0

        # Estableciendo el color por defecto con el que pintara el Render en caso de no ser cambiado
        self.current_color = WHITE 

		# Estableciendo el color con el que se realizara cualquier clear() en caso de no ser cambiado
        self.clear_color = BLACK 

		# Limpiando el framebuffer para llenarlo con el color del clear()
        self.clear()

	# Metodo encargado de limpiar el framebuffer 
    def clear(self):

		# Utilizando list comprehension se llenan todos los pixeles usando width y height
        self.framebuffer = [
            [self.clear_color for x in range(self.width)]
            for y in range(self.height)
        ]

        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]

    def clamping(self, num):
        return int(max(min(num, 255), 0))

	# Metodo utilizado para dibujar el framebuffer en un archivo bmp
    def write(self, filename):
        f = open(filename, 'bw')

        # pixel header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(word(0))
        f.write(word(0))
        f.write(dword(14 + 40))

        # info header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # pixel data
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[y][x])

        f.close()

	# Metodo utilizado para establecer un punto especifico en el framebuffer
    def point(self, x, y):
        try:
            self.framebuffer[x][y] = self.current_color
        except:
            pass
    
    def line(self, v1,v2):

        x0 = v1.x
        y0 = v1.y
        x1 = v2.x
        y1 = v2.y

        coordenadas = []

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        # Si es empinado, poco movimiento en x y mucho en y.
        steep = dy > dx

        # Se invierte si es empinado
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        # Si la linea tiene direccion contraria, invertir
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        offset = 0
        threshold = dx
        y = y0

        for x in range(round(x0), round(x1 + 1)):
            if steep:
                self.point(y, x)
                # print(y,x,'\n')
                coordenadas.append([y,x])
            else:
                self.point(x, y)
                # print(x,y,'\n')
                coordenadas.append([x,y])

            offset += dy * 2

            if offset >= threshold:
                y += 1 if y0 < y1 else -1

                threshold += dx * 2

        return coordenadas
    
    def transformarVertice(self, vertex, scale, translate):
        # return [
        #     ((vertex[0] * scale[0]) + translate[0]),
        #     ((vertex[1] * scale[1]) + translate[1])
        # ]
        return V3(
            ((vertex[0] * scale[0]) + translate[0]),
            ((vertex[1] * scale[1]) + translate[1]),
            ((vertex[2] * scale[2]) + translate[2])
        )

    def convertirCoordenadas(self, x,y):

        x_ini = x + 1
        y_ini = y + 1

        # calculada = (Sumada * width) / numero sumado

        calcux = (x_ini * self.vp_width) / 2
        calcuy = (y_ini * self.vp_height) / 2

        #  xfinal = (coordenada inicial del viewport + calculada )
        xfinal = round(self.vp_x + calcux)
        yfinal = round(self.vp_y + calcuy)

        return [xfinal , yfinal]

    def triangle(self, v1, v2, v3):
        self.line(round(v1[0]), round(v1[1]), round(v2[0]), round(v2[1]))
        self.line(round(v2[0]), round(v2[1]), round(v3[0]), round(v3[1]))
        self.line(round(v3[0]), round(v3[1]), round(v1[0]), round(v1[1]))
    
    def boundingBox(self, A, B, C):
        coords = [(A.x,A.y), (B.x,B.y), (C.x,C.y)]

        xmin = float('inf')
        xmax = float('-inf')
        ymin = float('inf')
        ymax = float('-inf')

        for (x,y) in coords:
            if x < xmin:
                xmin = x
            if x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            if y > ymax:
                ymax = y
        
        return V3(xmin,ymin), V3(xmax,ymax)

    def crossProduct(self,v1,v2):
        return (
            (v1.y * v2.z) - (v1.z * v2.y),
            (v1.z * v2.x) - (v1.x * v2.z),
            (v1.x * v2.y) - (v1.y * v2.x)
        )

    def barycentricCoordinates(self,A,B,C,P):
        cx, cy, cz = self.crossProduct(
            V3(B.x - A.x, C.x - A.x, A.x - P.x),
            V3(B.y - A.y, C.y - A.y, A.y - P.y)
        )
        u = cx/cz
        v = cy/cz
        w = 1 - (u + v)
        return (w,v,u)

    def productoPunto(self,v1,v2):
        return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

    def barycentricTriangle(self, A, B, C,):

        # Colores aleatorios para rellenar cada triangulo:

        # self.current_color = color(round(255*random.random()), round(255*random.random()), round(255*random.random()))

        # --------------------------------------------------------------


        # Colores rojo, verde y azul para llenar dependiendo de que tan lejos de su vertice se encuentre:

        Acolor = (255,0,0)
        Bcolor = (0,255,0)
        Ccolor = (0,0,255)

        # --------------------------------------------------------------

        # Obteniendo las normales para poder dibujar en 3D:

        L = V3(0,0,-5)
        N = (C-A) * (B-A)
        I = self.productoPunto(L.normalize(),N.normalize())

        # print(I)

        if I < 0:
            return
            
        
        # Pintar en escala de grises:

        self.current_color = color(round(255 * I), round(255 * I), round(255 * I))

        Bminimo, Bmaximo = self.boundingBox(A, B, C)

        for x in range(round(Bminimo.x), round(Bmaximo.x) + 1):
            for y in range(round(Bminimo.y), round(Bmaximo.y) + 1):
                w,v,u = self.barycentricCoordinates(A,B,C, V3(x,y))
                if(w < 0 or v < 0 or u < 0):
                    continue

                z = A.z * w + B.z * v + C.z * u

                # Colores rojo, verde y azul para llenar dependiendo de que tan lejos de su vertice se encuentre:

                a = round(Acolor[0] * w) + round(Bcolor[0] * v) + round(Ccolor[0] * u)
                b = round(Acolor[1] * w) + round(Bcolor[1] * v) + round(Ccolor[1] * u)
                c = round(Acolor[2] * w) + round(Bcolor[2] * v) + round(Ccolor[2] * u)

                # self.current_color = color(a,b,c)


                # --------------------------------------------------------------

                if(self.zBuffer[x][y] < z):
                    self.zBuffer[x][y] = z
                    self.point(x,y)

                # self.point(x,y)


    def vertexTriangle(self, v1, v2, v3):
        
        self.current_color = color(round(255*random.random()), round(255*random.random()), round(255*random.random()))

        self.line(v1,v2)
        self.line(v2,v3)
        self.line(v3,v1)

        # Proceso para rellenar triangulo:

        A = v1
        B = v2
        C = v3

        if A.y > B.y:
            A, B = B, A
        if A.y > C.y:
            A, C = C, A
        if B.y > C.y:
            B, C = C, B
        
        dx_ac = (C.x - A.x) 
        dy_ac = (C.y - A.y) 

        if dy_ac == 0:
            return

        mi_ac = dx_ac / dy_ac

        dx_ab = (B.x - A.x)
        dy_ab = (B.y - A.y)

        if dy_ab != 0:
            
            mi_ab = dx_ab / dy_ab

            for y in range(round(A.y), round(B.y + 1)):
                xi = round(A.x - mi_ac * (A.y - y))
                xf = round(A.x - mi_ab * (A.y - y))

                if xi > xf:
                    xi, xf = xf, xi

                for x in range(xi, xf + 1):
                    self.point(x, y)

        dx_bc = (C.x - B.x)
        dy_bc = (C.y - B.y)

        if dy_bc != 0:

            mi_bc = dx_bc / dy_bc

            for y in range(round(B.y), round(C.y + 1)):
                xi = round(A.x - mi_ac * (A.y - y))
                xf = round(B.x - mi_bc * (B.y - y))

                if xi > xf:
                    xi, xf = xf, xi

                for x in range(xi, xf + 1):
                    self.point(x, y)


    def cube(self, v1, v2, v3, v4):
        # self.line(round(v1[0]), round(v1[1]), round(v2[0]), round(v2[1]))
        # self.line(round(v2[0]), round(v2[1]), round(v3[0]), round(v3[1]))
        # self.line(round(v3[0]), round(v3[1]), round(v4[0]), round(v4[1]))
        # self.line(round(v4[0]), round(v4[1]), round(v1[0]), round(v1[1]))

        # self.line(round(v1.x), round(v1.y), round(v2.x), round(v2.y))
        # self.line(round(v2.x), round(v2.y), round(v3.x), round(v3.y))
        # self.line(round(v3.x), round(v3.y), round(v4.x), round(v4.y))
        # self.line(round(v4.x), round(v4.y), round(v1.x), round(v1.y))

        self.line(v1,v2)
        self.line(v2,v3)
        self.line(v3,v4)
        self.line(v4,v1)

    def renderObject(self, name, scaleFactor, translateFactor):
        cube = Obj(name)

        for face in cube.faces:
            if len(face) == 4:

                v1 = self.transformarVertice(cube.vertices[face[0][0] - 1], scaleFactor, translateFactor)
                v2 = self.transformarVertice(cube.vertices[face[1][0] - 1], scaleFactor, translateFactor)
                v3 = self.transformarVertice(cube.vertices[face[2][0] - 1], scaleFactor, translateFactor)
                v4 = self.transformarVertice(cube.vertices[face[3][0] - 1], scaleFactor, translateFactor)

                self.cube(v1, v2, v3, v4)
            
            if len(face) == 3:

                v1 = self.transformarVertice(cube.vertices[face[0][0] - 1], scaleFactor, translateFactor)
                v2 = self.transformarVertice(cube.vertices[face[1][0] - 1], scaleFactor, translateFactor)
                v3 = self.transformarVertice(cube.vertices[face[2][0] - 1], scaleFactor, translateFactor)

                self.barycentricTriangle(v1, v2, v3)