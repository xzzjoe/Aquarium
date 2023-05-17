"""
Define a fixed scene with rotating lights
First version in 11/08/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
import math

import numpy as np

import ColorType
from Animation import Animation
from Component import Component
from Light import Light
from Material import Material
from Point import Point
import GLUtility

from DisplayableCube import DisplayableCube
from DisplayableTorus import DisplayableTorus
from DisplayableSphere import DisplayableSphere
from DisplayableCylinder import DisplayableCylinder
from DisplayableEllipsoid import DisplayableEllipsoid

##### TODO 1: Generate Triangle Meshes
# Requirements:
#   1. Use Element Buffer Object (EBO) to draw the cube. The cube provided in the start code is drawn with Vertex Buffer
#   Object (VBO). In the DisplayableCube class draw method, you should switch from VBO draw to EBO draw. To achieve
#   this, please first read through VBO and EBO classes in GLBuffer. Then you rewrite the self.vertices and self.indices
#   in the DisplayableCube class. Once you have all these down, then switch the line vbo.draw() to ebo.draw().
#   2. Generate Displayable classes for an ellipsoid, torus, and cylinder with end caps.
#   These classes should be like the DisplayableCube class and they should all use EBO in the draw method.
#   PS: You must use the ellipsoid formula to generate it, scaling the Displayable sphere doesn't count
#
#   Displayable object's self.vertices numpy matrix should be defined as this table:
#   Column | 0:3                | 3:6           | 6:9          | 9:11
#   Stores | Vertex coordinates | Vertex normal | Vertex Color | Vertex texture Coordinates
#
#   Their __init__ method should accept following input
#   arguments:
#   DisplayableEllipsoid(radiusInX, radiusInY, radiusInZ, slices, stacks)
#   DisplayableTorus(innerRadius, outerRadius, nsides, rings)
#   DisplayableCylinder(endRadius, height, slices, stacks)
#

##### TODO 5: Create your scenes
# Requirements:
#   1. We provide a fixed scene (SceneOne) for you with preset lights, material, and model parameters.
#   This scene will be used to examine your illumination implementation, and you should not modify it.
#   2. Create 3 new scenes (can be static scenes). Each of your scenes must have
#      * at least 3 differently shaped solid objects
#      * each object should have a different material
#      * at least 2 lights
#      * All types of lights should be used
#   3. Provide a keyboard interface that allows the user to toggle on/off each of the lights in your scene model:
#   Hit 1, 2, 3, 4, etc. to identify which light to toggle.


class SceneFour(Component):
    shaderProg = None
    glutility = None

    lights = None
    lightCubes = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()

        ellip = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.7,0.3, 36, 72, ))
        m1 = Material(np.array((0.1, 0.1, 0.1, 1)), np.array((0.4, 0.4, 0.4, 1)),
                      np.array((0, 0, 0, 0)), 64)
        ellip.setMaterial(m1)
        textPath = "./assets/marble.jpg"
        ellip.setTexture(shaderProg, textPath)
        ellip.renderingRouting = "lighting texture"
        self.addChild(ellip)

        myCube = Component(Point((-1,1,0)), DisplayableCube(shaderProg,1,2,3, ColorType.BLACK))
        m2 = Material(np.array((0.1, 0.1, 0.1, 1.0)), np.array((0.1, 0.1, 0.1, 1)),
                      np.array((0.5, 0.5, 0.5, 1.0)), 64)
        myCube.setMaterial(m2)
        myCube.renderingRouting = "lighting"
        self.addChild(myCube)

        urCube = Component(Point((2,0,0)), DisplayableCube(shaderProg, 0.5,0.6, 0.4, ColorType.GRAY))
        m3 = Material(np.array((0.1, 0.1, 0.1, 1.0)), np.array((0.4, 0.4, 0.4, 1)),
                      np.array((0.2, 0.2, 0.2, 1.0)), 64)
        urCube.setMaterial(m3)
        self.addChild(urCube)
        l0 = Light(Point((0.0, 6.0, -1.0)),
                   np.array((*ColorType.WHITE, 1.0)),  infiniteDirection = Point((0, 6.0, -1.0)))
        lightCube0 = Component(Point((0.0, 6.0, -1.0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.WHITE))
        lightCube0.renderingRouting = "vertex"
        l1 = Light(Point((-1, -1, 0.0)),
                   np.array((*ColorType.NAVY, 1.0)))
        lightCube1 = Component(Point((-1, -1, 0.0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.NAVY))
        lightCube1.renderingRouting = "vertex"
        l2 = Light(Point((1, 0, 1)),
                   np.array((*ColorType.RED, 1.0)))
        lightCube2 = Component(Point((1, 0, 1)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.RED))
        lightCube2.renderingRouting = "vertex"
        self.addChild(lightCube2)
        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.lights = [l0, l1,l2]
        self.lightCubes = [lightCube0, lightCube1,lightCube2]

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
