# -*- coding: utf-8 -*-
"""Maya ramp widget as pySide2 wieget

MIT License

Copyright (c) 2020 Mauro Lopez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFT
"""
from functools import partial
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance 

from maya import cmds
from maya import OpenMayaUI as omui

import ui_utils
import widgets
INTERPTYPES = ["None", "Linear", "Smooth", "Spline"]

class RampWidget(QtWidgets.QWidget):
    def __init__(self, initalPoints=((1,0),(0,1)), interpolation ='Smooth', parent=None):
        super(RampWidget, self).__init__(parent)
        self._rampPoints = list()
        for val, pos in initalPoints:
            self._rampPoints.append((val, pos, INTERPTYPES.index(interpolation)))
        self.setupUI()
        self._connectSignals()
        self._initDefault()

    def _initDefault(self):
        self.setValue(self._rampPoints)

    def _initMayaGradientCtrl(self):
        self.rampCtrlName  = cmds.gradientControlNoAttr(h=90, changeCommand=self.rampWidgetEditedCallback,
                                                        p=self.layout.objectName())
        ptr = omui.MQtUtil.findControl(self.rampCtrlName)
        self.rampWidget = wrapInstance(int(ptr), QtWidgets.QWidget)

    def setupUI(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setObjectName('rampMainLayout')
        self.editWidg = QtWidgets.QWidget(self)
        self.editlayout = QtWidgets.QVBoxLayout(self)
        self.editlayout.setContentsMargins(0, 0, 0, 0)
        self.editlayout.setSpacing(5)
        interpWidg, self.interpCB = widgets.labeledWidget(QtWidgets.QComboBox,self, "interp")
        self.editlayout.addWidget(interpWidg)
        for name in INTERPTYPES:
            self.interpCB.addItem(name)
        posWidg, self.posField = widgets.labeledWidget(QtWidgets.QDoubleSpinBox,self, "pos")
        self.editlayout.addWidget(posWidg)
        self.posField.setMaximum(1)
        self.posField.setMinimum(0)
        self.posField.setSingleStep(.1)
        valuewidg, self.valueField = widgets.labeledWidget(QtWidgets.QDoubleSpinBox,self, "val")
        self.editlayout.addWidget(valuewidg)
        self.valueField.setMaximum(1)
        self.valueField.setMinimum(0)
        self.valueField.setSingleStep(.1)
        self.editlayout.addStretch()
        self.editWidg.setLayout(self.editlayout)
        self.layout.addWidget(self.editWidg)
        self._initMayaGradientCtrl()
        self.layout.addWidget(self.rampWidget)
        self.layout.setStretch(0, 0)
        self.layout.setStretch(1, 1)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.layout.setSpacing(0)

    def _connectSignals(self):
        self.interpCB.currentIndexChanged.connect(partial(self.updateCurrentRampPoint, "intrep"))
        self.valueField.valueChanged.connect(partial(self.updateCurrentRampPoint, "value"))
        self.posField.valueChanged.connect(partial(self.updateCurrentRampPoint, "pos"))

    def rampWidgetEditedCallback(self, valueStr):
        valueList = [float(a) for a in valueStr.split(',')]
        self._rampPoints = list(ui_utils.chunks(valueList, 3))
        self.updateFields()

    def updateFields(self):
        self.updateInterpField()
        self.updateValueField()
        self.updatePosField()

    def updateInterpField(self):
        interp = cmds.gradientControlNoAttr(self.rampCtrlName, q=1, currentKeyInterpValue=1)
        self.interpCB.setCurrentIndex(interp)

    def updateValueField(self):
        currValue = round(cmds.gradientControlNoAttr(self.rampCtrlName, q=1, currentKeyCurveValue=1), 4)
        self.valueField.setValue(currValue)

    def updatePosField(self):
        currKey = cmds.gradientControlNoAttr(self.rampCtrlName, q=1, currentKey=1)
        pos = self._rampPoints[currKey][1]
        self.posField.setValue(pos)

    def updateCurrentRampPoint(self, mode, value):
        key = cmds.gradientControlNoAttr(self.rampCtrlName, q=1, currentKey=1)
        if mode == "value":
            self._rampPoints[key][0] = value
        elif mode == "pos":
            self._rampPoints[key][1] = value
        elif mode == "intrep":
            self._rampPoints[key][2] = value
        self.setValue(self._rampPoints)


    def setValue(self, rampPoints):
        valueStr = ','.join([','.join([str(b) for b in a]) for a in rampPoints])
        cmds.gradientControlNoAttr(self.rampCtrlName, e=1, asString=valueStr)
        self._rampPoints = rampPoints

    def getValue(self, asString=True):
        if asString:
            valueStr = ','.join([','.join([str(b) for b in a]) for a in self._rampPoints])
            return valueStr
        else:
            return self._rampPoints

    def getValueAtPoint(self, point):
        return cmds.gradientControlNoAttr(self.rampCtrlName, q=1, valueAtPoint=point)

    def getValueAtPoints(self, rampPoints):
        result = list()
        for point in rampPoints:
            result.append(self.getValueAtPoint(point))
        return result