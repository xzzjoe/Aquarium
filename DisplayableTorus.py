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

class DisplayableTorus(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    nsides = 0
    rings = 0
    innerRadius = 0
    outerRadius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        super(DisplayableTorus, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(innerRadius, outerRadius, nsides, rings, color)

    def generate(self, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.nsides = nsides
        self.rings = rings
        self.color = color
        pi = math.pi

        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        self.vertices = np.zeros([(nsides+1) * (rings+1), 11])
        torus_vertices = np.zeros([rings+1,nsides+1, 3])
        torus_normal = np.zeros([rings+1,nsides+1, 3])
        for i, theta in enumerate(np.arange(-pi, pi + pi/rings, 2*pi/rings)):
            for j, phi in enumerate(np.arange(-pi, pi + pi/nsides, 2*pi/nsides)):
                inner_sum = outerRadius + innerRadius*math.cos(phi)
                x = inner_sum*math.cos(theta)
                y = inner_sum*math.sin(theta)
                z = innerRadius*math.sin(phi)

                x_normal = -innerRadius*math.cos(phi)*math.cos(theta) * inner_sum
                y_normal = -innerRadius*math.cos(phi)*math.sin(theta) * inner_sum
                z_normal = innerRadius*math.sin(phi) * inner_sum

                torus_vertices[i][j] = np.array([x,y,z])
                torus_normal[i][j] = np.array([x_normal,y_normal,z_normal])


        self.indices = []

        for i in range(rings+1):
            for j in range(nsides+1):
                self.vertices[i*nsides + j,0:9] = np.array([torus_vertices[i][j][0],torus_vertices[i][j][1],torus_vertices[i][j][2]\
                    ,torus_normal[i][j][0],torus_normal[i][j][1],torus_normal[i][j][2], *color])
                # Follow the CCW order of the triangle
                if (i < rings and j < nsides):
                    self.indices.append(np.array([i*nsides + j,i*nsides+j+1,(i+1)*nsides+j]))
                    self.indices.append(np.array([(i+1)*nsides + j,i*nsides + j+1, (i+1)*nsides +j + 1]))
                elif(i < rings and j == nsides):
                    self.indices.append(np.array([i*nsides + j, i*nsides , (i+1)*nsides+j]))
                    self.indices.append(np.array([(i+1)*nsides + j, i*nsides, (i+1)*nsides]))
                elif(i == rings and j < nsides):
                    self.indices.append(np.array([i*nsides + j, i*nsides+j+1 ,j]))
                    self.indices.append(np.array([j, i*nsides + j+ 1, j+1]))                    
                elif(i == rings and j == nsides):
                    self.indices.append(np.array([i*nsides + j, i*nsides,j]))
                    self.indices.append(np.array([j, i*nsides, 0]))
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
