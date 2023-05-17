"""
Define displayable cube here. Current version only use VBO
First version in 10/20/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
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


class DisplayableSphere(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None  # array to store vertices information
    indices = None  # stores triangle indices to vertices

    # stores current cube's information, read-only
    length = None
    width = None
    height = None
    color = None

    def __init__(self, shaderProg, radius=1,slices = 36, stacks = 36, color=ColorType.BLUE):
        super(DisplayableSphere, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()
        self.generate(radius,slices, stacks, color)

    def generate(self, radius=1, slices = 32, stacks =32, color=None):
        # self.length = length
        # self.width = width
        # self.height = height
        self.color = color
        pi = math.pi

        self.vertices = np.zeros([(slices+1)*(stacks+1),11])
        sphere_vertices = np.zeros([slices + 1,stacks + 1,3])
        sphere_normals = np.zeros([slices + 1,stacks + 1,3])
        text_coords = np.zeros([slices + 1, stacks + 1,2])
        for i,phi in enumerate(np.arange(-pi/2,pi/2+pi/slices,pi/slices)):
            for j,theta in enumerate(np.arange(-pi,pi+2*pi/stacks,2*pi/stacks)):
                x = radius*math.cos(phi)*math.cos(theta)
                y = radius*math.cos(phi)*math.sin(theta)
                z = radius*math.sin(phi)

                x_normal = math.cos(phi)*math.cos(theta)
                y_normal = math.cos(phi)*math.sin(theta)
                z_normal = math.sin(phi)

                tex_x = i * (1.0/(slices))
                tex_y = j * (1.0/(stacks))
                sphere_vertices[i][j] = [x,y,z]
                sphere_normals[i][j] = [x_normal,y_normal,z_normal]
                text_coords[i, j] = [tex_y, tex_x]

        triangle_list = []
        self.indices = []
        for i in range(slices+1):
            for j in range(stacks+1):
                self.vertices[i*slices + j, 0:11] = [sphere_vertices[i][j][0],sphere_vertices[i][j][1],sphere_vertices[i][j][2],
                                     sphere_normals[i][j][0], sphere_normals[i][j][1], sphere_normals[i][j][2], *color, text_coords[i][j][0], text_coords[i][j][1]]
                if(i<slices and j<stacks):
                    self.indices.append(np.array([i*stacks + j, i*stacks + j+1, (i+1)*stacks + j+1]))
                    self.indices.append(np.array([i*stacks + j, (i+1)*stacks + j, (i+1)*stacks + j+1]))

                elif(i==slices and j<stacks):
                    self.indices.append(np.array([i*stacks + j, i*stacks + j+1, j+1]))
                    self.indices.append(np.array([i*stacks + j,  j,  j+1]))

                elif(i<slices and j==stacks):
                    self.indices.append(np.array([i*stacks + j, i*stacks, (i+1)*stacks]))
                    self.indices.append(np.array([i*stacks + j,  (i+1)*stacks+j,  (i+1)*stacks]))

                elif (i==slices and j==stacks):
                    self.indices.append(np.array([i*stacks + j, i*stacks, 0]))
                    self.indices.append(np.array([i*stacks + j,  j,  0]))


        self.indices = np.stack(self.indices)

    def draw(self):
        self.vao.bind()
        # TODO 1.1 is at here, switch from vbo to ebo
        # self.vbo.draw()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems that don't enable a default VAO after GLProgram compilation
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
        # TODO/BONUS 6.1 is at here, you need to set attribPointer for texture coordinates
        # you should check the corresponding variable name in GLProgram and set the pointer
        self.vao.unbind()

