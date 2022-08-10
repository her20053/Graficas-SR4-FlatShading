# Importando libreria para manejo de bytes
from utilities import *

# Importando libreria para manejo de colores
from colors import *

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
        self.clear_color = WHITE 

		# Limpiando el framebuffer para llenarlo con el color del clear()
        self.clear()

	# Metodo encargado de limpiar el framebuffer 
    def clear(self):

		# Utilizando list comprehension se llenan todos los pixeles usando width y height
        self.framebuffer = [
            [self.clear_color for x in range(self.width)]
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
    
    def line(self, x0, y0, x1, y1):

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

        for x in range(x0, x1 + 1):
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
        return [
            ((vertex[0] * scale[0]) + translate[0]),
            ((vertex[1] * scale[1]) + translate[1])
        ]

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

    def cube(self, v1, v2, v3, v4):
        self.line(round(v1[0]), round(v1[1]), round(v2[0]), round(v2[1]))
        self.line(round(v2[0]), round(v2[1]), round(v3[0]), round(v3[1]))
        self.line(round(v3[0]), round(v3[1]), round(v4[0]), round(v4[1]))
        self.line(round(v4[0]), round(v4[1]), round(v1[0]), round(v1[1]))

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

                self.triangle(v1, v2, v3)