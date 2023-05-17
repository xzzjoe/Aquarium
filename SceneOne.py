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
from DisplayableSphere import DisplayableSphere
from DisplayableTorus import DisplayableTorus
from DisplayableEllipsoid import DisplayableEllipsoid
from DisplayableCylinder import DisplayableCylinder

class SceneOne(Component, Animation):
    lights = None
    lightCubes = None
    shaderProg = None
    glutility = None

    lRadius = None
    lAngles = None
    lTransformations = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()

        self.lTransformations = [self.glutility.translate(0, 2, 0, False),
                                 self.glutility.rotate(60, [0, 0, 1], False),
                                 self.glutility.rotate(120, [0, 0, 1], False)]
        self.lRadius = 3
        self.lAngles = [0, 0, 0]

        cube = Component(Point((0, 0, 0)), DisplayableSphere(shaderProg, 1.0),)
        m1 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.4, 0.4, 0.4, 0.1)), 64)
        cube.setMaterial(m1)
        cube.renderingRouting = "lighting"
        self.addChild(cube)

        torus = Component(Point((1.5, 0, 0)), DisplayableTorus(shaderProg, 0.25, 0.5, 36, 36, ColorType.BLUE))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.1, 0.1, 0.1, 1)),
                      np.array((0.4, 0.4, 0.4, 1.0)), 64)
        torus.setMaterial(m2)
        torus.renderingRouting = "lighting"
        torus.rotate(90, torus.uAxis)
        self.addChild(torus)

        myCube = Component(Point((0, 1, 1)), DisplayableCube(shaderProg, 0.5, 0.5, 0.5, ColorType.BLUE))
        myCube.setMaterial(m1)
        myCube.renderingRouting = 'lighting'
        self.addChild(myCube)

        l0 = Light(self.lightPos(self.lRadius, self.lAngles[0], self.lTransformations[0]),
                   np.array((*ColorType.SOFTBLUE, 1.0)))
        lightCube0 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTBLUE))
        lightCube0.renderingRouting = "vertex"
        l1 = Light(self.lightPos(self.lRadius, self.lAngles[1], self.lTransformations[1]),
                   np.array((*ColorType.SOFTRED, 1.0)))
        lightCube1 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTRED))
        lightCube1.renderingRouting = "vertex"
        l2 = Light(self.lightPos(self.lRadius, self.lAngles[2], self.lTransformations[2]),
                   np.array((*ColorType.YELLOW, 1.0)))
        lightCube2 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.YELLOW))
        
        lightCube2.renderingRouting = "vertex"
        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.addChild(lightCube2)
        self.lights = [l0, l1,l2]
        self.lightCubes = [lightCube0, lightCube1, lightCube2]
        
        ellip = Component(Point((1, 1, 0)), DisplayableEllipsoid(shaderProg, 0.25, 0.5,0.1, 36, 72, color= ColorType.BLUE))
        m3 = Material(np.array((0.2, 0.3, 0.2, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                    np.array((0, 1.0, 0, 1.0)), 64)
        ellip.setMaterial(m3)
        ellip.renderingRouting = "lighting"
        ellip.rotate(-90, ellip.uAxis)
        self.addChild(ellip)

        cylin = Component(Point((-1,1,0)), DisplayableCylinder(shaderProg, 0.25,36, 5, ColorType.BLACK))
        cylin.setMaterial(m3)
        cylin.rotate(90, cylin.uAxis)
        cylin.renderingRouting = "lighting"
        self.addChild(cylin)
                
    def lightPos(self, radius, thetaAng, transformationMatrix):
        r = np.zeros(4)
        r[0] = radius * math.cos(thetaAng / 180 * math.pi)
        r[2] = radius * math.sin(thetaAng / 180 * math.pi)
        r[3] = 1
        r = transformationMatrix @ r
        return r[0:3]

    def animationUpdate(self):
        self.lAngles[0] = (self.lAngles[0] + 0.5) % 360
        self.lAngles[1] = (self.lAngles[1] + 0.7) % 360
        self.lAngles[2] = (self.lAngles[2] + 1.0) % 360
        for i, v in enumerate(self.lights):
            lPos = self.lightPos(self.lRadius, self.lAngles[i], self.lTransformations[i])
            self.lightCubes[i].setCurrentPosition(Point(lPos))
            self.lights[i].setPosition(lPos)
            self.shaderProg.setLight(i, v)

        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
