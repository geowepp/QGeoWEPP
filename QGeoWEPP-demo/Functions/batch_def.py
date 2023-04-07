# -*- coding: utf-8 -*-
"""
/***************************************************************************
Batch Processing for Soil Redistribution
                                 QGeoWEPP
                              -------------------
        begin                : 2021-06-11
        git sha              : $Format:%H$
        author               : (C) 2022 by Han Zhang
        email                : support@geowepp.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as        *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from qgis.core import *
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt import QtGui
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor
from PIL import Image
import os.path, os, subprocess, time, glob
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
import pywinauto.timings, sys
from cmath import inf
from shutil import copyfile
from .batch_dialog import batchDialog

class BatchBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.batchprocessing = batchDialog()

    def batchbutton(self):
        try:
            msg = QMessageBox()
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.selectOutletTool)
            self.iface.mapCanvas().unsetMapTool(self.selectHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.hilltoweppTool) 
            
            # check if watersheds have been created
            if len(QgsProject.instance().mapLayersByName('Subwatersheds')) == 0:
                msg.setText("Subwatersheds are required. Please select an outlet first.")
                msg.exec()
                return
            else:
                self.batchprocessing.lineEdit_year.setText('5')
                self.batchprocessing.lineEdit_name.setText('Batch1')
                self.batchprocessing.show()
                
        except:
            msg.setText('Ooops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
    
    def batch_process(self):
        try:
            msg = QMessageBox()
            year = self.batchprocessing.lineEdit_year.text()
            #climate = self.batchprocessing.lineEdit_climate.text()
            name = self.batchprocessing.lineEdit_name.text()

            rnetwork = QgsProject.instance().mapLayersByName('Subwatersheds')[0]
            foldername = os.path.dirname(rnetwork.dataProvider().dataSourceUri()) 

            if name == "": 
                msg.setText ("A result name is required.")
                msg.exec()
                return
                
            if os.path.exists(os.path.join(foldername, 'Reports', name)):
                msg.setText (name + ' already exist. Please use a different name.')
                msg.exec()
                return
            
            # create a folder for one batch processing
            folderBatch = os.path.join(foldername,'Reports', name)         
            if not os.path.exists(folderBatch):
                os.makedirs(folderBatch)
            
            os.chdir(foldername)
            subprocess.call(os.path.join(foldername, 'climport.exe'))
                
            # create batch loop
            for i in range(int(year)):
                simyear = i + 2

                # rewrite cmd2.txt
                cmd2txt = os.path.join(foldername,'cmd2.txt')
                with open (cmd2txt, 'r') as inputcmd2:
                    linelst = inputcmd2.readlines()
                    linelst [6] = 'years = ' + str(simyear) + '\n'
                with open (cmd2txt, 'w') as outputcmd2:
                    outputcmd2.writelines(linelst)
                    
                # run wepp
                os.chdir(foldername)
                weppapp = os.path.join(foldername, 'topwepp2.exe')
                #subprocess.call(weppapp)

                # simulate clicking event for topwepp2
                app = Application(backend="uia").start(weppapp)
                time.sleep(2)
                send_keys('{ENTER}')

                dlg_spec = app.window(title = 'WEPP/TOPAZ Translator')
                dlg_spec.set_focus()
                dlg_spec.ComboBox.Button.type_keys('%{DOWN}')
                send_keys('{DOWN}')
                send_keys('{ENTER}')
                send_keys('{ENTER}')
                
                window = pywinauto.timings.wait_until_passes(inf, 5, lambda:app.window(title=u'WEPP Complete').wait('visible'))
                window.type_keys('{ENTER}')

                #gather soil loss
                fileFlow = os.path.join(foldername,'weppFLoss.arc')

                # Load soil loss
                if os.path.exists(fileFlow):
                    nfileLoss = os.path.join(folderBatch, name + '_' + str(simyear) + '_yrs.asc')
                    copyfile(fileFlow, nfileLoss)
                    lossfileInfo = QFileInfo(nfileLoss)
                    lossbaseName = lossfileInfo.baseName()
                    losslayer = QgsRasterLayer(nfileLoss, lossbaseName)
                    if not losslayer.isValid():
                        msg.setText ("Soil Loss Layer failed to load!")
                        msg.exec()      

                    # display soil loss layer       
                    crs = QgsCoordinateReferenceSystem()
                    crspath = os.path.join(foldername, 'crs.txt')
                    with open(crspath) as crsrecord:
                        crs = crs.fromProj4(crsrecord.readline())
                    losslayer.setCrs(crs)
                    QgsProject.instance().addMapLayer(losslayer)

                    lossstats = losslayer.dataProvider().bandStatistics(1, QgsRasterBandStats.All, losslayer.extent(), 0)
                    maxLoss = lossstats.maximumValue
                    lossfnc = QgsColorRampShader()
                    lossfnc.setColorRampType(QgsColorRampShader.Discrete)
               
                    colDicLoss = {'Lossmax':'#5b3361', 'Loss4':'#a45daf','Loss3':'#c03bd4','Loss2':'#e5a4ee',
                            'Loss1':'#b6390b','Loss0.75':'#f14628','Loss0.5':'#f5864e','Loss0.25':'#eca37e',
                            'Loss0':'#f3e483','Loss-1':'#ffe90c','Loss-2':'#69b9e6','Loss-3':'#428fbf','Loss-4':'#1c4a66'}
                    valueListLoss =[-4, -3, -2, -1, 0, 0.25, 0.5, 0.75, 1, 2, 3, 4, maxLoss]
                    lstLoss = [ QgsColorRampShader.ColorRampItem(valueListLoss[0], QColor(colDicLoss['Loss-4']),'Deposition > 4T'), 
                            QgsColorRampShader.ColorRampItem(valueListLoss[1], QColor(colDicLoss['Loss-3']),'3T < Deposition <= 4T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[2], QColor(colDicLoss['Loss-2']),'2T < Deposition <= 3T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[3], QColor(colDicLoss['Loss-1']),'1T < Deposition <= 2T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[4], QColor(colDicLoss['Loss0']),'0T < Deposition <= 1T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[5], QColor(colDicLoss['Loss0.25']),'0T <= Soil Loss < 0.25T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[6], QColor(colDicLoss['Loss0.5']),'0.25T <= Soil Loss < 0.5T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[7], QColor(colDicLoss['Loss0.75']),'0.5T <= Soil Loss < 0.75T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[8], QColor(colDicLoss['Loss1']),'0.75T <= Soil Loss < 1T'), 
                            QgsColorRampShader.ColorRampItem(valueListLoss[9], QColor(colDicLoss['Loss2']),'1T <= Soil Loss < 2T'), 
                            QgsColorRampShader.ColorRampItem(valueListLoss[10], QColor(colDicLoss['Loss3']),'2T <= Soil Loss < 3T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[11], QColor(colDicLoss['Loss4']),'3T <= Soil Loss < 4T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[12], QColor(colDicLoss['Lossmax']),'Soil Loss >= 4T')
                            ]
                    lossfnc.setColorRampItemList(lstLoss)
                    lossshader = QgsRasterShader()
                    lossshader.setRasterShaderFunction(lossfnc)
                    lossrenderer = QgsSingleBandPseudoColorRenderer(losslayer.dataProvider(), losslayer.type(), lossshader)
                    losslayer.setRenderer(lossrenderer)
                
                    # create png map
                    '''
                    netlayer = QgsProject.instance().mapLayersByName('Networks')[0]
                    layers = [netlayer, losslayer]
                    extent = QgsRectangle()
                    for layer in layers:
                        extent.combineExtentWith(layer.boundinBoxofSelected())
                    self.iface.mapCanvas().setExtent(extent)
                    self.iface.mapCanvas().refresh()
                    '''
                    netlayer = QgsProject.instance().mapLayersByName('Networks')[0]
                    manager = QgsProject.instance().layoutManager()
                    layoutName = 'Batch Soil Loss'
                    layout_list = manager.printLayouts()
                    for layout in layout_list:
                        if layout.name() == layoutName:
                            manager.removeLayout(layout)
                    layout = QgsPrintLayout(QgsProject.instance())
                    layout.initializeDefaults()
                    layout.setName(layoutName)
                    manager.addLayout(layout)
                    #map
                    map = QgsLayoutItemMap(layout)
                    rect = losslayer.extent()
                    rect.scale(1.1)
                    ratio = rect.width()/rect.height()
                    map.setRect(20, 20, 20, 20)
                    ms = QgsMapSettings()
                    ms.setLayers([losslayer, netlayer])
                    
                    ms.setExtent(losslayer.extent())
                    map.setExtent(rect)
                    map.setBackgroundColor(QColor(255, 255, 255, 0))
                    layout.addLayoutItem(map)
                    #map.attemptMove(QgsLayoutPoint(5, 15, QgsUnitTypes.LayoutMillimeters))
                    map.attemptMove(QgsLayoutPoint(70, 40, QgsUnitTypes.LayoutMillimeters))
                    map.attemptResize(QgsLayoutSize(180*ratio, 180, QgsUnitTypes.LayoutMillimeters))

                    
                    #legend
                    legend = QgsLayoutItemLegend(layout)
                    legend.setTitle("Legend")
                    layerTree = QgsLayerTree()
                    layerTree.addLayer(losslayer)
                    layerTree.addLayer(netlayer)
                    legend.model().setRootGroup(layerTree)
                    layout.addLayoutItem(legend)
                    legend.attemptMove(QgsLayoutPoint(5, 70, QgsUnitTypes.LayoutMillimeters))

                    '''
                    #scalebar
                    scale = QgsLayoutItemScaleBar(layout)
                    scale.setStyle('Single Box')
                    scale.setFont(QtGui.QFont("Arial",15))
                    scale.setFontColor(QColor("Black"))
                    scale.setFillColor(QColor("Black"))
                    scale.applyDefaultSize(QgsUnitTypes.DistanceMeters)
                    scale.setMapUnitsPerScaleBarUnit(1000.0)
                    scale.setNumberOfSegments(2)
           
                    #scale.setUnitsPerSegment(1*10)
                    scale.setUnitLabel("m")
                    scale.setLinkedMap(map)
                    layout.addLayoutItem(scale)
                    scale.attemptMove(QgsLayoutPoint(5, 190, QgsUnitTypes.LayoutMillimeters))
                    '''

                    #title
                    title = QgsLayoutItemLabel(layout)
                    title.setText(str(simyear) + " Years Average Annual Soil Redistribution")
                    title.setFont(QtGui.QFont('Arial', 24))
                    title.adjustSizeToText()
                    layout.addLayoutItem(title)
                    title.attemptMove(QgsLayoutPoint(5, 5, QgsUnitTypes.LayoutMillimeters))
                     
                    
                    north=QgsLayoutItemPicture(layout)
                    north.setMode(QgsLayoutItemPicture.FormatSVG)
                    picpath = os.path.join(self.plugin_dir, 'icons', 'north-arrow-2.svg')
                    north.setPicturePath(picpath)
                    north.attemptMove(QgsLayoutPoint(8, 20, QgsUnitTypes.LayoutMillimeters))
                    north.attemptResize(QgsLayoutSize(*[300,300], QgsUnitTypes.LayoutPixels))
                    layout.addLayoutItem(north)
                    

                    layout = manager.layoutByName(layoutName)
                    exporter = QgsLayoutExporter(layout)

                    fn = os.path.join(folderBatch, name + '_' + str(simyear) + '_yrs.png')
                    exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())

                    # gif
                    # Create the frames
                    frames = []
                    imgs = glob.glob(os.path.join(folderBatch, "*.png"))
                    for i in imgs:
                        new_frame = Image.open(i)
                        frames.append(new_frame)
                        
                    # Save into a GIF file that loops forever
                    gifpath = os.path.join(folderBatch, 'annual_average_animation.gif')
                    frames[0].save(gifpath, format='GIF',
                    append_images=frames[1:],
                    save_all=True,
                    duration=700, loop=0)

                   
                # set progress bar for each simulation
                self.batchprocessing.progressBar_batch.setValue(simyear/int(year)*100)


                

        except:
            msg.setText('Ooops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
