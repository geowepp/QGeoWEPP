# -*- coding: utf-8 -*-
"""
/***************************************************************************
SelectFeature
                                 QGeoWEPP
                              -------------------
        begin                : 2021-06-11
        git sha              : $Format:%H$
        author               : 2022 by Han Zhang, Chris S. Renschler
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
from qgis.core import QgsRasterLayer, QgsProject, QgsPointXY, QgsRaster, QgsCoordinateReferenceSystem,  QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from qgis.PyQt.QtGui import QCursor, QColor
from qgis.PyQt.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QProgressBar, QInputDialog, QWidget
from math import floor
import os.path, os, subprocess, sys, numpy, random
from shutil import copyfile

class GetZone(QWidget):
    def __init__(self):
        super().__init__()

    def getZone(self):
        i, okPressed = QInputDialog.getInt(self, "UTM Zone","UTM Zone:", 16, 1, 60, 1)
        if okPressed:
            return(i)

class SelectOutletTool(QgsMapTool):
    
    def __init__(self, parentself):
        canvas = parentself.iface.mapCanvas()
        self.parentself = parentself
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.getzone = GetZone()

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
            
            # check if Networks is in the interface
            if len(QgsProject.instance().mapLayersByName('Networks')) == 0:
                msg.setText("The channel networks layer is required. Please load 'netful.asc' and name it as 'Networks'.")
                msg.exec()
                self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.selectOutletTool)
                return
            # check if the point is on the channel
            rnetwork = QgsProject.instance().mapLayersByName('Networks')[0]
            netvalue = rnetwork.dataProvider().identify(QgsPointXY(point[0], point[1]), QgsRaster.IdentifyFormatValue).results()[1]
            if netvalue == None:
                msg.setText('Not a channel cell. Please select an outlet point over the channel.')
                msg.exec()
                self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.selectOutletTool)
            else:
                rnetwork = QgsProject.instance().mapLayersByName('Networks')[0]
                foldername = os.path.dirname(rnetwork.dataProvider().dataSourceUri()) 
                # subwatersheds already exist
                if len(QgsProject.instance().mapLayersByName('Subwatersheds')) != 0:                    
                    reconfirm = msg.question (None, 'Warning', 'This will generate a new watershed. Do you want to continue?', msg.Yes | msg.No)
                    if reconfirm == msg.Yes:
                        bar = QProgressBar()
                        self.iface.mainWindow().statusBar().addWidget(bar)
                        bar.setValue(10)
                        # if WEPP output layers exist, remove
                        layernames = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
                        for name in layernames:
                            if name[-6:] == 'Runoff':
                                runlayer = QgsProject.instance().mapLayersByName(name)[0]
                                QgsProject.instance().removeMapLayer(runlayer)
                            if name[-8:] == 'Sediment':
                                sedlayer = QgsProject.instance().mapLayersByName(name)[0]
                                QgsProject.instance().removeMapLayer(sedlayer)
                            if name[-8:] == 'absFLoss':
                                losslayer = QgsProject.instance().mapLayersByName(name)[0]
                                QgsProject.instance().removeMapLayer(losslayer)
                            if name == 'Subwatersheds':
                                wtrlayer = QgsProject.instance().mapLayersByName(name)[0]
                                QgsProject.instance().removeMapLayer(wtrlayer)
                        
                        bar.setValue(20)
                        crs = QgsCoordinateReferenceSystem()
                        crspath = os.path.join(foldername, 'crs.txt')
                        with open(crspath) as crsrecord:
                            crsproj4 = crsrecord.readline()
                        identifier = crsproj4.split('=', 2)[-1][: 2]
                        if identifier == 'WG':
                            zone = GetZone.getZone(self.getzone)
                        else:
                            zone = int(crsproj4.split('=', 2)[-1][: 2])
                        crs = crs.fromProj4(crsproj4)
                        
                        tmpdem1pnt = os.path.join(foldername, 'tmpdem1.pnt')
                        with open (tmpdem1pnt, 'w') as csaoutput:
                            csaoutput.write('Point: '+ str(floor(point[0])) + ' '+ str(floor(point[1])))
                        
                        bar.setValue(30)
                        bluebook =os.path.join(foldername,'bluebook.f81')
                        with open (bluebook, 'w') as blueoutput:
                            blueoutput.write('      *81*    Point:                        %7.7d%3.3d%8.8d%3.3d%3.3d' % (point[0], 0, point[1], 0, zone))
                            blueoutput.write ('\n')
                        
                        bar.setValue(40)
                        os.chdir(foldername)
                        os.system('utms.exe < utms.inp')

                        bar.setValue(50)
                        subprocess.call('convdem.exe')
                        
                        bar.setValue(60)
                        cellpath = os.path.join(foldername, 'cellsize.txt')
                        with open(cellpath) as cellrecord:
                            cellsize = cellrecord.readline()[:-1]
                        if float(cellsize) < 5:
                            os.system('dednm.exe')
                        else:
                            os.system('echo 1 | dednm.exe')
                        
                        bar.setValue(70)
                        subprocess.call('raspro.exe', creationflags= subprocess.CREATE_NO_WINDOW)
                        bar.setValue(80)
                        subprocess.call('rasfor.exe', creationflags= subprocess.CREATE_NO_WINDOW)
                        
                        bar.setValue(90)
                        fwtrarc = os.path.join(foldername,'SUBWTA.ARC')
                        fwtrasc = os.path.join(foldername,'subwtr.asc')
                        if os.path.isfile(fwtrarc):
                            copyfile(fwtrarc, fwtrasc)    
                        bar.setValue(100)
                        slayer = QgsRasterLayer(fwtrasc, 'Subwatersheds')     
                        slayer.setCrs(crs)
                        QgsProject.instance().addMapLayer(slayer)

                        #Disply subwatershed
                        # get all hill id
                        provider = slayer.dataProvider()
                        extent = provider.extent()
                        rows = slayer.height()
                        cols = slayer.width()
                        block = provider.block(1, extent, cols, rows)
                        hilllst = numpy.zeros(shape = (rows, cols))
                        for i in range(rows):
                            for j in range(cols):
                                hilllst[i, j] = block.value(i , j)
                        valueList = numpy.unique(hilllst).tolist()
                     
                        fnc = QgsColorRampShader()
                        fnc.setColorRampType(QgsColorRampShader.Exact)

                        lst = []
                        for hill in valueList:
                            if hill !=0:
                                colorrgb = QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
                                lst.append(QgsColorRampShader.ColorRampItem(int(hill), colorrgb, str(int(hill))))
                        
                        fnc.setColorRampItemList(lst)
                        shader = QgsRasterShader()
                        shader.setRasterShaderFunction(fnc)
                        renderer = QgsSingleBandPseudoColorRenderer(slayer.dataProvider(), slayer.type(), shader)
                        slayer.setRenderer(renderer)
                        self.iface.mainWindow().statusBar().removeWidget(bar)
                        
                
                # subwatersheds generated for the first time
                if len(QgsProject.instance().mapLayersByName('Subwatersheds')) == 0:
                    bar = QProgressBar()
                    self.iface.mainWindow().statusBar().addWidget(bar)
                    bar.setValue(10)
                    crs = QgsCoordinateReferenceSystem()
                    crspath = os.path.join(foldername, 'crs.txt')
                    with open(crspath) as crsrecord:
                        crsproj4 = crsrecord.readline()
                    identifier = crsproj4.split('=', 2)[-1][: 2]
                    if identifier == 'WG': 
                        zone = GetZone.getZone(self.getzone)
                    else:
                        zone = int(crsproj4.split('=', 2)[-1][: 2])
                    crs = crs.fromProj4(crsproj4)
                    
                    bar.setValue(20)
                    tmpdem1pnt = os.path.join(foldername, 'tmpdem1.pnt')
                    with open (tmpdem1pnt, 'w') as csaoutput:
                        csaoutput.write('Point: '+ str(floor(point[0])) + ' '+ str(floor(point[1])))
                    
                    bar.setValue(30)
                    bluebook =os.path.join(foldername,'bluebook.f81')
                    with open (bluebook, 'w') as blueoutput:
                        blueoutput.write('      *81*    Point:                        %7.7d%3.3d%8.8d%3.3d%3.3d' % (point[0], 0, point[1], 0, zone))
                        blueoutput.write ('\n')
                    
                    bar.setValue(40)
                    os.chdir(foldername)
                    os.system('utms.exe < utms.inp')

                    bar.setValue(50)
                    subprocess.call('convdem.exe', creationflags= subprocess.CREATE_NO_WINDOW)
                    
                    bar.setValue(60)
                    #identify if the cell size is smaller than 5m
                    cellpath = os.path.join(foldername, 'cellsize.txt')
                    with open(cellpath) as cellrecord:
                        cellsize = cellrecord.readline()[:-1]
                    if float(cellsize) < 5:
                        os.system('dednm.exe')
                    else:
                        os.system('echo 1 | dednm.exe')
                    
                    bar.setValue(70)
                    subprocess.call('raspro.exe', creationflags= subprocess.CREATE_NO_WINDOW)
                    bar.setValue(80)
                    subprocess.call('rasfor.exe', creationflags= subprocess.CREATE_NO_WINDOW)
                    
                    bar.setValue(90)
                    fwtrarc = os.path.join(foldername,'SUBWTA.ARC')
                    fwtrasc = os.path.join(foldername,'subwtr.asc')
                    if os.path.isfile(fwtrarc):
                        copyfile(fwtrarc, fwtrasc)   
                    bar.setValue(100)
                    slayer = QgsRasterLayer(fwtrasc, 'Subwatersheds') 
                    slayer.setCrs(crs)
                    QgsProject.instance().addMapLayer(slayer)

                    #Disply subwatershed
                    # get all hill id
                    provider = slayer.dataProvider()
                    extent = provider.extent()
                    rows = slayer.height()
                    cols = slayer.width()
                    block = slayer.dataProvider().block(1, extent, cols, rows)
                    hilllst = numpy.zeros(shape = (rows, cols))
                    for i in range(rows):
                        for j in range(cols):
                             hilllst[i, j] = block.value(i , j)
                    valueList = numpy.unique(hilllst).tolist()
                     
                    stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)
                    fnc = QgsColorRampShader()
                    fnc.setColorRampType(QgsColorRampShader.Exact)

                    lst = []
                    for hill in valueList:
                        if hill !=0:
                            colorrgb = QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
                            lst.append(QgsColorRampShader.ColorRampItem(int(hill), colorrgb, str(int(hill))))
                    fnc.setColorRampItemList(lst)
                    shader = QgsRasterShader()
                    shader.setRasterShaderFunction(fnc)
                    renderer = QgsSingleBandPseudoColorRenderer(slayer.dataProvider(), slayer.type(), shader)
                    slayer.setRenderer(renderer)
                    self.iface.mainWindow().statusBar().removeWidget(bar)
                               
                self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.selectOutletTool)
                self.iface.mainWindow().statusBar().removeWidget(bar)

        except:
            msg.setText('Oops!\n'+ str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
            self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.selectOutletTool)
            self.iface.mainWindow().statusBar().removeWidget(bar)

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
