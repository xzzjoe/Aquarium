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

class DisplayableEllipsoid(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    stacks = 0
    slices = 0
    x_radius = 0
    y_radius = 0
    z_radius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, x_radius = 0.25, y_radius = 0.5, z_radius = 0.1, stacks=36, slices=36, color=ColorType.SOFTBLUE):
        super(DisplayableEllipsoid, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(x_radius, y_radius, z_radius, stacks, slices, color)

    def generate(self, x_radius=0.25, y_radius=0.5,z_radius = 0.1, stacks=36, slices=36, color=ColorType.SOFTBLUE):
        self.x_radius = x_radius
        self.y_radius = y_radius
        self.z_radius = z_radius
        self.stacks = stacks
        self.slices = slices
        self.color = color
        pi = math.pi
        print(stacks)
        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        self.vertices = np.zeros([(stacks+1) * (slices+1), 11])
        ellip_vertices = np.zeros([slices+1,stacks+1, 3])
        ellip_normal = np.zeros([slices+1,stacks+1, 3])
        tex_coords = np.zeros([slices + 1, stacks + 1, 2])
        #Which one should come first?
        for i, phi in enumerate(np.arange(-pi/2, pi/2 + pi/slices, pi/slices)):
            for j, theta in enumerate(np.arange(-pi, pi + 2*pi/stacks, 2*pi/stacks)):
                x = x_radius * math.cos(phi) * math.cos(theta)
                y = y_radius * math.cos(phi) * math.sin(theta)
                z = z_radius * math.sin(phi)



                x_normal = -z_radius * y_radius * pow(math.cos(phi),2) * math.cos(theta)
                y_normal = z_radius * x_radius * pow(math.cos(phi),2) * math.sin(theta)
                z_normal = x_radius * y_radius * math.cos(phi) * math.sin(phi)
                # 2 * x_radius * y_radius *math.cos(phi)* math.sin(phi) * math.sin(theta) * math.cos(theta)

                # x_normal = -z_radius * 
                # z_normal = 0.5 * x_radius * y_radius * math.sin(2*phi) * math.sin(2*theta)
                tex_x = i * (1.0/slices)
                tex_y = j * (1.0/stacks)

                ellip_vertices[i][j] = [x,y,z]
                ellip_normal[i][j] = [x_normal, y_normal, z_normal] 

                tex_coords[i][j] = [tex_x, tex_y]

        self.indices = []

        for i in range(slices+1):
            for j in range(stacks+1):
                self.vertices[i*stacks + j,0:11] = np.array([ellip_vertices[i][j][0],ellip_vertices[i][j][1],ellip_vertices[i][j][2]\
                    ,ellip_normal[i][j][0],ellip_normal[i][j][1],ellip_normal[i][j][2], *color, tex_coords[i][j][0], tex_coords[i][j][1]])
                # Follow the CCW order of the triangle
                if (i < slices and j < stacks):
                    self.indices.append(np.array([i*stacks + j,i*stacks+j+1,(i+1)*stacks+j+1]))
                    self.indices.append(np.array([i*stacks + j,(i+1)*stacks + j, (i+1)*stacks +j+1]))
                elif(i < slices and j == stacks):
                    self.indices.append(np.array([i*stacks + j, i*stacks , (i+1)*stacks + j]))
                    self.indices.append(np.array([(i+1)*stacks + j, i*stacks, (i+1)*stacks]))
                elif(i == slices and j < stacks):
                    self.indices.append(np.array([i*stacks + j, i*stacks+j+1 , j]))
                    self.indices.append(np.array([j, i*stacks+j+1, j+1]))                    
                elif(i == slices and j == stacks):
                    self.indices.append(np.array([i*stacks+ j, i*stacks, j]))
                    self.indices.append(np.array([j, i*stacks, 0]))
                
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
