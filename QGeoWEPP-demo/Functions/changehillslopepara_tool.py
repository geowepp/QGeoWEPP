# -*- coding: utf-8 -*-
"""
/***************************************************************************
Change Hillslope Parameters
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
from qgis.core import  QgsProject, QgsPointXY, QgsRaster
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import os.path, os, sys, subprocess
from .getresults_def import GetResultsBtn
from .getresults_dialog import getresultsDialog

class ChangeHillSlopeTool(QgsMapTool):
    
    def __init__(self, parentself):
        canvas = parentself.iface.mapCanvas()
        self.parentself = parentself
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.getresults = getresultsDialog()

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
                if os.path.exists(hillfile):
                    hillid = str(int(wtrvalue))
                    soilstart = 'soil[' + str(int(wtrvalue)) + ']'
                    lcstart = 'management[' + str(int(wtrvalue)) + ']'
                    with open(hillfile) as hillinfo:
                        for line in hillinfo:
                            if soilstart in line:
                                soilinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if lcstart in line:
                                lcinfo = line.rstrip().split('"', 1)[-1][:-1]
                    # change soil parameter
                    msgcontent1 = 'Current soil parametrs \nWEPP Hill ID: ' + str(int(wtrvalue)) + '\nSoil: ' + soilinfo + '\nDo you want to change this soil?'
                    reconfirm1 = msg.question (None, 'Warning', msgcontent1, msg.Yes | msg.No)
                    if reconfirm1 == msg.Yes:
                        os.chdir(foldername)
                        arg = 'topwepp4 *.sol ' + hillid + ' 1'
                        subprocess.run(arg)
                    
                    # change land cover parameter
                    msgcontent2 = 'Current land cover parametrs \nWEPP Hill ID: ' + str(int(wtrvalue)) + '\nLand Cover: ' + lcinfo + '\nDo you want to change this land cover?'
                    reconfirm2 = msg.question (None, 'Warning', msgcontent2, msg.Yes | msg.No)
                    if reconfirm2 == msg.Yes:
                        os.chdir(foldername)
                        arg = 'topwepp4 *.rot ' + hillid + ' 1'
                        subprocess.run(arg)
                    
                    # get new parameter
                    with open(hillfile) as hillinfo:
                        for line in hillinfo:
                            if soilstart in line:
                                soilinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if lcstart in line:
                                lcinfo = line.rstrip().split('"', 1)[-1][:-1]               
                    msgcontent3 = 'Current WEPP parameters for Hill ' + hillid + '\nLand Cover: ' + lcinfo + '\nSoil: ' + soilinfo
                    msg.setText(msgcontent3)
                    msg.exec()
                    
                    # run wepp again
                    reconfirm3 = msg.question (None, 'Warning', 'Do you want to re-run WEPP using the new parameters?', msg.Yes | msg.No)
                    if reconfirm3 == msg.Yes:
                        self.getresults.lineEdit_Results.setText("Simulation1")    
                        self.getresults.show() 
                        result = self.getresults.exec_()
                        #ok
                        if result:
                           GetResultsBtn.runwepp(self)
                self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.changeHillSlopeTool)
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
