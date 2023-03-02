# -*- coding: utf-8 -*-
"""
/***************************************************************************
Get hillslope information
                                 QGeoWEPP
                              -------------------
        begin                : 2021-06-11
        git sha              : $Format:%H$
        author               : (C) 2022 by Han Zhang, Chris S. Renschler
        email                : support@geowepp.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from builtins import str
from qgis.gui import QgsMapTool
from qgis.utils import iface
from qgis.core import QgsProject, QgsPointXY, QgsRaster
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import os.path, os, sys

class SelectHillSlopeTool(QgsMapTool):
    
    def __init__(self, parentself):
        canvas = parentself.iface.mapCanvas()
        self.parentself = parentself
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

    def canvasReleaseEvent(self, event):
        try:
            msg = QMessageBox()
            #Get the coordinate of the outlet
            x = event.pos().x()
            y = event.pos().y()
            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
             
            rwatershed = QgsProject.instance().mapLayersByName('Subwatersheds')[0]
            foldername = os.path.dirname(rwatershed.dataProvider().dataSourceUri()) 
            # check if the point is on the watershed
            wtrvalue = rwatershed.dataProvider().identify(QgsPointXY(point[0], point[1]), QgsRaster.IdentifyFormatValue).results()[1]
            if wtrvalue == None:
                msg.setText('The point you selected is outside the watershed. Please try again.')
                msg.exec()
            else:
                hillfile = os.path.join(foldername, 'weppshed.txt')
                climstart = 'climate ='
                soilstart = 'soil[' + str(int(wtrvalue)) + ']'
                lcstart = 'management[' + str(int(wtrvalue)) + ']'
                if os.path.exists(hillfile):
                    with open(hillfile) as hillinfo:
                        for line in hillinfo:
                            if climstart in line:
                                climinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if soilstart in line:
                                soilinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if lcstart in line:
                                lcinfo = line.rstrip().split('"', 1)[-1][:-1]
                    msgcontent = 'WEPP Hill ID: ' + str(int(wtrvalue)) + '\nClimate: ' + climinfo + '\nLand Cover: ' + lcinfo + '\nSoil: ' + soilinfo
                    msg.setText(msgcontent)
                    msg.exec()

            self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.selectHillSlopeTool)
        except:
            msg.setText('Oops!\n'+ str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
