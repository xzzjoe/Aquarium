"""
Define Torus here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
from Point import Point
import numpy as np
import ColorType
import math
try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")

##### TODO 6/BONUS 6: Texture Mapping
# Requirements:
#   1. Set up each object's vertex texture coordinates(2D) to the self.vertices 9:11 columns
#   (i.e. the last two columns). Tell OpenGL how to interpret these two columns:
#   you need to set up attribPointer in the Displayable object's initialize method.
#   2. Generate texture coordinates for the torus and sphere. Use “./assets/marble.jpg” for the torus and
#   “./assets/earth.jpg” for the sphere as the texture image.
#   There should be no seams in the resulting texture-mapped model.

class DisplayableCylinder(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    height = 0
    slices = 0
    radius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, radius = 0.25, slices=36, height = 5, color=ColorType.SOFTBLUE):
        super(DisplayableCylinder, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radius, slices, height, color)

    def generate(self, radius = 0.5, slices=36, height = 5, color=ColorType.SOFTBLUE):
        self.radius = radius
        self.height = height
        self.slices = slices
        self.color = color
        pi = math.pi
        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        self.vertices = np.zeros([(slices)*2 +4  , 11])
        n = len(self.vertices)
        cylin_vertices = np.zeros([(slices)*2 +4 , 3])
        cylin_normal = np.zeros([(slices+4), 3])
        #Which one should come first
        for i, theta in enumerate(np.arange(-pi, pi + 2*pi/slices, 2*pi/slices)):
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            z_min = 0
            z_max = height

            x_normal = radius*math.cos(theta)
            y_normal = radius*math.sin(theta)
            cylin_vertices[2*i] = [x,y,z_max]
            cylin_vertices[2*i + 1] = [x,y,z_min]
            cylin_normal[i] = [x_normal,y_normal, 0]
        
        cylin_vertices[-1] = [0,0,height]
        cylin_vertices[-2] = [0,0,0]
        cylin_normal[-1] = [0,0,1]
        cylin_normal[-2] = [0,0,-1]



        self.indices = []

        for i in range(slices+1):
            self.vertices[2*i,0:9] = np.array([cylin_vertices[2*i][0],cylin_vertices[2*i][1],cylin_vertices[2*i][2]\
                ,cylin_normal[i][0],cylin_normal[i][1],cylin_normal[i][2], *color])
            self.vertices[2*i+1,0:9] = np.array([cylin_vertices[2*i+1][0],cylin_vertices[2*i+1][1],cylin_vertices[2*i+1][2]\
                ,cylin_normal[i][0],cylin_normal[i][1],cylin_normal[i][2], *color])
            # Follow the CCW order of the triangle
            if (i < slices):
                self.indices.append(np.array([2*i,2*i+1, 2*(i+1)]))
                self.indices.append(np.array([2*(i+1), 2*i+1, 2*(i+1)+1]))
                self.indices.append(np.array([n-1, 2*i, 2*(i+1)]))
                self.indices.append(np.array([n-2, 2*i +1, 2*(i+1) + 1]))

            elif(i == slices):
                self.indices.append(np.array([2*i, 2*i+1, 0]))
                self.indices.append(np.array([0, 2*i+1, 1]))
                self.indices.append(np.array([n-1, 2*i, 0]))
                self.indices.append(np.array([n-2, 2*i+1, 1]))
        self.vertices[-1, 0:9] = np.array([cylin_vertices[-1][0],cylin_vertices[-1][1],cylin_vertices[-1][2]\
                ,cylin_normal[-1][0],cylin_normal[-1][1],cylin_normal[-1][2], *color])
        self.vertices[-2, 0:9] = np.array([cylin_vertices[-2][0],cylin_vertices[-2][1],cylin_vertices[-2][2]\
                ,cylin_normal[-2][0],cylin_normal[-2][1],cylin_normal[-2][2], *color])
        self.indices = np.stack(self.indices)

    def draw(self):
        self.vao.bind()
        # self.vbo.draw()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems which don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2)

        self.vao.unbind()
