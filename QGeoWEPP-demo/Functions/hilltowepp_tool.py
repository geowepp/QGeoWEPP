# -*- coding: utf-8 -*-
"""
/***************************************************************************
Load single hill to WEPP
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
from shutil import copyfile

class HilltoWeppTool(QgsMapTool):
    
    def __init__(self, parentself):
        canvas = parentself.iface.mapCanvas()
        self.parentself = parentself
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

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
            weppdir = os.path.join(os.path.dirname(self.plugin_dir), 'WEPP')
            wtrvalue = rwatershed.dataProvider().identify(QgsPointXY(point[0], point[1]), QgsRaster.IdentifyFormatValue).results()[1]
            if wtrvalue == None:
                msg.setText('The point you selected is outside the watershed. Please try again.')
                msg.exec()
            else:
                hillid = str(int(wtrvalue))
                # if the point is on the channel
                if hillid[-1] == '4':
                    # copy channal slp file to WEPP folder
                    slopefile = os.path.join(foldername, 'chan_' + hillid + '.slp')
                    slopepath = os.path.join(weppdir, 'Data', 'slopes', 'chan_'+ hillid + '.slp')
                    copyfile(slopefile, slopepath)

                    # copy channel prj file to WEPP folder
                    chanfile = os.path.join(foldername, 'chan_' + hillid + '.prj')
                    chanpath = os.path.join(weppdir, 'Data', 'projects', 'qgeowepp.prj')
                    # get slope length
                    with open(slopefile) as slopeinfo:
                        for i in range(3):
                            slopeinfo.readline()
                        slplength = slopeinfo.readline().split(' ', 1)[-1][:-1]
                    # create channel prj file
                    hillfile = os.path.join(foldername, 'weppshed.txt')
                    hillid = str(int(wtrvalue))
                    climstart = 'climate ='
                    soilstart = 'soil[' + str(int(wtrvalue)) + ']'
                    lcstart = 'management[' + str(int(wtrvalue)) + ']'
                    with open(hillfile) as hillinfo:
                        for line in hillinfo:
                            if climstart in line:
                                climinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if soilstart in line:
                                soilinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if lcstart in line:
                                lcinfo = line.rstrip().split('"', 1)[-1][:-1]
                    with open(chanfile, 'w') as chaninfo:
                        chaninfo.write('#\n')
                        chaninfo.write('# WEPP project for GeoWEPP Hillslope function\n')
                        chaninfo.write('#\n')
                        chaninfo.write('Version = 98.6\n')
                        chaninfo.write('Name = ' + hillid + '\n')
                        chaninfo.write('Comments {\n')
                        chaninfo.write('Represenative Channel Slope ' + hillid + '\n')
                        chaninfo.write('}\n')
                        chaninfo.write('Units = Metric\n')
                        chaninfo.write('Landuse = 1\n')
                        chaninfo.write('Length = ' + slplength + '\n')
                        chaninfo.write('Profile {\n')
                        chaninfo.write('   File = "chan_' + hillid + '.slp"\n')
                        chaninfo.write('}\n')
                        chaninfo.write('Climate {\n')
                        chaninfo.write('   File = "' + climinfo + '"\n')
                        chaninfo.write('}\n')
                        chaninfo.write('Soil {\n')
                        chaninfo.write('   Breaks = 0\n')
                        chaninfo.write('   default {\n')
                        chaninfo.write('      Distance = ' + slplength + '\n')
                        chaninfo.write('      File = "' + soilinfo + '"\n')
                        chaninfo.write('}\n')
                        chaninfo.write('}\n')
                        chaninfo.write('Management {\n')
                        chaninfo.write('   Breaks = 0\n')
                        chaninfo.write('   default {\n')
                        chaninfo.write('      Distance = ' + slplength + '\n')
                        chaninfo.write('      File = "' + lcinfo + '"\n')
                        chaninfo.write('}\n')
                        chaninfo.write('}\n')
                        chaninfo.write('RunOptions {\n')
                        chaninfo.write('Version = 1\n')
                        chaninfo.write('SoilLossOutputType = 1\n')
                        chaninfo.write('SoilLossOutputFile = AutoName\n')
                        chaninfo.write('PlotFile = AutoName\n')
                        chaninfo.write('EventFile = AutoName\n')
                        chaninfo.write('FinalSummaryFile = AutoName\n')
                        chaninfo.write('SimulationYears = 2\n')
                        chaninfo.write('SmallEventByPass = 1\n')
                        chaninfo.write('}\n')                  
                    copyfile(chanfile, chanpath)
                    weppwindir = os.path.join(weppdir, 'weppwin')
                    os.chdir(weppwindir)
                    os.system('start weppwin.exe ' + chanpath)

                else:
                    # if the point is not on the channel (on the hillslope)
                    # copy slp file to WEPP folder
                    slopefile = os.path.join(foldername, 'hill_' + hillid + '.slp')
                    slopepath = os.path.join(weppdir, 'Data', 'slopes', 'hill_'+ hillid + '.slp')
                    copyfile(slopefile, slopepath)

                    # copy prj file to WEPP folder
                    hillpath = os.path.join(weppdir, 'Data', 'projects','qgeowepp.prj')
                    # get slope length
                    with open(slopefile) as slopeinfo:
                        for i in range(3):
                            slopeinfo.readline()
                        slplength = slopeinfo.readline().split(' ', 1)[-1][:-1]

                    hillfile = os.path.join(foldername, 'weppshed.txt')
                    hillid = str(int(wtrvalue))
                    climstart = 'climate ='
                    soilstart = 'soil[' + str(int(wtrvalue)) + ']'
                    lcstart = 'management[' + str(int(wtrvalue)) + ']'
                    with open(hillfile) as hillinfo:
                        for line in hillinfo:
                            if climstart in line:
                                climinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if soilstart in line:
                                soilinfo = line.rstrip().split('"', 1)[-1][:-1]
                            if lcstart in line:
                                lcinfo = line.rstrip().split('"', 1)[-1][:-1]

                    with open(hillpath, 'w') as hillinfo:
                        hillinfo.write('#\n')
                        hillinfo.write('# WEPP project for GeoWEPP Hillslope function\n')
                        hillinfo.write('#\n')
                        hillinfo.write('Version = 98.6\n')
                        hillinfo.write('Name = ' + hillid + '\n')
                        hillinfo.write('Comments {\n')
                        hillinfo.write('Represenative Slope ' + hillid + '\n')
                        hillinfo.write('}\n')
                        hillinfo.write('Units = Metric\n')
                        hillinfo.write('Landuse = 1\n')
                        hillinfo.write('Length = ' + slplength + '\n')
                        hillinfo.write('Profile {\n')
                        hillinfo.write('   File = "hill_' + hillid + '.slp"\n')
                        hillinfo.write('}\n')
                        hillinfo.write('Climate {\n')
                        hillinfo.write('   File = "' + climinfo + '"\n')
                        hillinfo.write('}\n')
                        hillinfo.write('Soil {\n')
                        hillinfo.write('   Breaks = 0\n')
                        hillinfo.write('   default {\n')
                        hillinfo.write('      Distance = ' + slplength + '\n')
                        hillinfo.write('      File = "' + soilinfo + '"\n')
                        hillinfo.write('}\n')
                        hillinfo.write('}\n')
                        hillinfo.write('Management {\n')
                        hillinfo.write('   Breaks = 0\n')
                        hillinfo.write('   default {\n')
                        hillinfo.write('      Distance = ' + slplength + '\n')
                        hillinfo.write('      File = "' + lcinfo + '"\n')
                        hillinfo.write('}\n')
                        hillinfo.write('}\n')
                        hillinfo.write('RunOptions {\n')
                        hillinfo.write('Version = 1\n')
                        hillinfo.write('SoilLossOutputType = 1\n')
                        hillinfo.write('SoilLossOutputFile = AutoName\n')
                        hillinfo.write('PlotFile = AutoName\n')
                        hillinfo.write('GraphFile = AutoName\n')
                        hillinfo.write('SimulationYears = 2\n')
                        hillinfo.write('SmallEventByPass = 1\n')
                        hillinfo.write('}\n')                   
                    weppwindir = os.path.join(weppdir, 'weppwin')
                    os.chdir(weppwindir)
                    os.system('start weppwin.exe ' + hillpath)

            self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.hilltoweppTool)
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
