# -*- coding: utf-8 -*-
"""
/***************************************************************************
Change Tolerance Value
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
 *   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as        *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from qgis.core import QgsProject, QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor
import os.path, os, sys
from .changetrvalue_dialog import changetrvalueDialog

class ChangeTRValueBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.changetrvalue = changetrvalueDialog()
    
    # set defult value
    def setTRvalue(self):
        changelayer = self.changetrvalue.comboBox_TR.currentText()
        target = changelayer.split(' ', 1) [0]
        if target == 'Runoff':
            self.changetrvalue.lineEdit_TR.setText("100")
        if target == 'Sediment':
            self.changetrvalue.lineEdit_TR.setText('1')
        if target == 'absFLoss':
            self.changetrvalue.lineEdit_TR.setText('1')

    def changetrvaluebutton(self):
        try:
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.selectOutletTool)
            self.iface.mapCanvas().unsetMapTool(self.selectHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.hilltoweppTool) 

            msg = QMessageBox()
            self.changetrvalue.show()
            # add existed wepp output layer to the combobox
            layernames = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
            for name in layernames:
                if name[-6:] == 'Runoff':
                    if self.changetrvalue.comboBox_TR.findText('Runoff (mm/Year)') == -1:
                        self.changetrvalue.comboBox_TR.addItem(name[-6:]+' (mm/Year)')
                if name[-8:] == 'Sediment':
                    if self.changetrvalue.comboBox_TR.findText('Sediment (Tones/Hectare/Year)') == -1:
                        self.changetrvalue.comboBox_TR.addItem(name[-8:] + ' (Tones/Hectare/Year)')
                if name[-8:] == 'absFLoss':
                    if self.changetrvalue.comboBox_TR.findText('absFLoss (Tones/Hectare/Year)') == -1:
                        self.changetrvalue.comboBox_TR.addItem(name[-8:] + ' (Tones/Hectare/Year)')
            
            # ok
            result = self.changetrvalue.exec_()
            if result:   
                trValue = float(self.changetrvalue.lineEdit_TR.text())
                targetlayer = self.changetrvalue.comboBox_TR.currentText()
                
                # update runoff layers
                runofflst = []
                if targetlayer == 'Runoff (mm/Year)':
                    # get all runoff layers in the instance
                    for name in layernames:
                        if name[-6:] == 'Runoff':
                            runofflst.append(name)
                    
                    for layer in runofflst:
                        runofflayer = QgsProject.instance().mapLayersByName(layer)[0]
                        fcnRunoff = QgsColorRampShader()
                        fcnRunoff.setColorRampType(QgsColorRampShader.Discrete)
                        lstRunoff = [QgsColorRampShader.ColorRampItem(0, QColor(0, 255, 0)), QgsColorRampShader.ColorRampItem(255, QColor(255, 255, 0))]
                        fcnRunoff.setColorRampItemList(lstRunoff)
                        shaderRunoff = QgsRasterShader()
                        shaderRunoff.setRasterShaderFunction(fcnRunoff)
                        rendererRunoff = QgsSingleBandPseudoColorRenderer(runofflayer.dataProvider(), 1, shaderRunoff)
                        runofflayer.setRenderer(rendererRunoff)

                        rendererRunoff = runofflayer.renderer()
                        providerRunoff = runofflayer.dataProvider()
                        extentRunoff = runofflayer.extent()
                        statsRunoff = providerRunoff.bandStatistics(1, QgsRasterBandStats.All, extentRunoff, 0)
                        maxRunoff = statsRunoff.maximumValue
                
                        colDicRunoff = {'Runoffmax': '#b30900', 'Runoff4': '#ff2216', 'Runoff3': '#ff7f78', 'Runoff2': '#fedcda', 'Runoff1': '#7ef014',
                                    'Runoff0.75':'#66c80c', 'Runoff0.5':'#4e9909', 'Runoff0.25':'#376b06'}
                        valueListRunoff = [0.25 * trValue, 50 * trValue, 75 * trValue, 100 * trValue, 200 * trValue, 300 * trValue, 400 * trValue, maxRunoff]
                        lstRunoff = [QgsColorRampShader.ColorRampItem(valueListRunoff[0], QColor(colDicRunoff['Runoff0.25']), '0T <= Runoff < 1/4T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[1], QColor(colDicRunoff['Runoff0.5']), '1/4T <= Runoff < 1/2T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[2], QColor(colDicRunoff['Runoff0.75']), '1/2T <= Runoff < 3/4T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[3], QColor(colDicRunoff['Runoff1']), '3/4T <= Runoff < 1T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[4], QColor(colDicRunoff['Runoff2']), '1T <= Runoff < 2T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[5], QColor(colDicRunoff['Runoff3']), '2T <= Runoff < 3T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[6], QColor(colDicRunoff['Runoff4']), '3T <= Runoff < 4T'),
                                     QgsColorRampShader.ColorRampItem(valueListRunoff[6], QColor(colDicRunoff['Runoffmax']), 'Runoff >= 4T')]

                        myRasterShaderRunoff = QgsRasterShader()
                        myColorRampRunoff = QgsColorRampShader()
                        myColorRampRunoff.setColorRampItemList(lstRunoff)
                        myColorRampRunoff.setColorRampType(QgsColorRampShader.Discrete)
                        myRasterShaderRunoff.setRasterShaderFunction(myColorRampRunoff)
                        myPseudoRendererRunoff = QgsSingleBandPseudoColorRenderer(runofflayer.dataProvider(), runofflayer.type(), myRasterShaderRunoff)
                        runofflayer.setRenderer(myPseudoRendererRunoff)
                        runofflayer.triggerRepaint()
                

                # update sediment layers
                if targetlayer == 'Sediment (Tones/Hectare/Year)':
                # get all sediment layers in the instance
                    sedimentlst = []
                    for name in layernames:
                        if name[-8:] == 'Sediment':
                            sedimentlst.append(name)
                      
                    for layer in sedimentlst:
                        Sedlayer = QgsProject.instance().mapLayersByName(layer)[0]
                        Sedfcn = QgsColorRampShader()
                        Sedfcn.setColorRampType(QgsColorRampShader.Discrete)
                        lstSed = [ QgsColorRampShader.ColorRampItem(0, QColor(0,255,0)),QgsColorRampShader.ColorRampItem(255, QColor(255,255,0)) ]
                        Sedfcn.setColorRampItemList(lstSed)
                        Sedshader = QgsRasterShader()
                        Sedshader.setRasterShaderFunction(Sedfcn)
                        Sedrenderer = QgsSingleBandPseudoColorRenderer(Sedlayer.dataProvider(), 1, Sedshader)
                        Sedlayer.setRenderer(Sedrenderer)
                        Sedrenderer = Sedlayer.renderer()
                        provider = Sedlayer.dataProvider()
                        Sedextent = Sedlayer.extent()
                        Sedstats = provider.bandStatistics(1, QgsRasterBandStats.All, Sedextent, 0)
                        Sedmax = Sedstats.maximumValue

                        SedcolDic = {'Sed0.25':'#376b06', 'Sed0.5':'#4e9909','Sed0.75':'#66c80c','Sed1':'#7ef014','Sed2':'#fedcda',
                                    'Sed3':'#ff7f78','Sed4':'#ff2216','Sedmax':'#b30900'}
                        SedvalueList =[0.25 * trValue , 0.5 * trValue, 0.75 * trValue, 1 * trValue, 2 * trValue, 3 * trValue, 4 * trValue, Sedmax]
                        Sedlst = [ QgsColorRampShader.ColorRampItem(SedvalueList[0], QColor(SedcolDic['Sed0.25']),'0T <= Sediment Yield < 1/4T'), 
                                    QgsColorRampShader.ColorRampItem(SedvalueList[1], QColor(SedcolDic['Sed0.5']),'1/4T <= Sediment Yield < 1/2T'), 
                                    QgsColorRampShader.ColorRampItem(SedvalueList[2], QColor(SedcolDic['Sed0.75']),'1/2T <= Sediment Yield < 3/4T'),
                                    QgsColorRampShader.ColorRampItem(SedvalueList[3], QColor(SedcolDic['Sed1']),'3/4T <= Sediment Yield < 1T'),
                                    QgsColorRampShader.ColorRampItem(SedvalueList[4], QColor(SedcolDic['Sed2']),'1T <= Sediment Yield < 2T'),
                                    QgsColorRampShader.ColorRampItem(SedvalueList[5], QColor(SedcolDic['Sed3']),'2T <= Sediment Yield < 3T'),
                                    QgsColorRampShader.ColorRampItem(SedvalueList[6], QColor(SedcolDic['Sed4']),'3T <= Sediment Yield < 4T'),
                                    QgsColorRampShader.ColorRampItem(SedvalueList[7], QColor(SedcolDic['Sedmax']),'Sediment Yield >= 4T')
                                    ]

                        myRasterShaderSed = QgsRasterShader()
                        myColorRampSed = QgsColorRampShader()
                        myColorRampSed.setColorRampItemList(Sedlst)
                        myColorRampSed.setColorRampType(QgsColorRampShader.Discrete)
                        myRasterShaderSed.setRasterShaderFunction(myColorRampSed)
                        myPseudoRendererSed = QgsSingleBandPseudoColorRenderer(Sedlayer.dataProvider(), Sedlayer.type(), myRasterShaderSed)
                        Sedlayer.setRenderer(myPseudoRendererSed)
                        Sedlayer.triggerRepaint()

                # update soil loss layers
                if targetlayer == 'absFLoss (Tones/Hectare/Year)':
                # get all soil loss layers in the instance
                    soillosslst = []
                    for name in layernames:
                        if name[-8:] == 'absFLoss':
                            soillosslst.append(name)
                      
                    for layer in soillosslst:
                        Losslayer = QgsProject.instance().mapLayersByName(layer)[0]
                        fcnLoss = QgsColorRampShader()
                        fcnLoss.setColorRampType(QgsColorRampShader.Discrete)
                        lstLoss = [ QgsColorRampShader.ColorRampItem(0, QColor(0,255,0)),QgsColorRampShader.ColorRampItem(255, QColor(255,255,0)) ]
                        fcnLoss.setColorRampItemList(lstLoss)
                        shaderLoss = QgsRasterShader()
                        shaderLoss.setRasterShaderFunction(fcnLoss)
                        rendererLoss = QgsSingleBandPseudoColorRenderer(Losslayer.dataProvider(), 1, shaderLoss)
                        Losslayer.setRenderer(rendererLoss)
                        rendererLoss = Losslayer.renderer()
                        providerLoss = Losslayer.dataProvider()
                        extentLoss = Losslayer.extent()
                        statsLoss = providerLoss.bandStatistics(1, QgsRasterBandStats.All,extentLoss, 0)
                        maxLoss = statsLoss.maximumValue
               
                        #create color legend for displaying results
                        colDicLoss = {'Lossmax':'#5b3361', 'Loss4':'#a45daf','Loss3':'#c03bd4','Loss2':'#e5a4ee',
                                  'Loss1':'#b6390b','Loss0.75':'#f14628','Loss0.5':'#f5864e','Loss0.25':'#eca37e',
                                 'Loss0':'#f3e483','Loss-1':'#ffe90c','Loss-2':'#69b9e6','Loss-3':'#428fbf','Loss-4':'#1c4a66'}
                        valueListLoss =[-4 * trValue, -3 * trValue, -2 * trValue, -1 * trValue, 0 * trValue, 0.25 * trValue, 0.5 * trValue, 0.75 * trValue, 1 * trValue, 2 * trValue, 3 * trValue, 4 * trValue, maxLoss]
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

                        myRasterShaderLoss = QgsRasterShader()
                        myColorRampLoss = QgsColorRampShader()
                        myColorRampLoss.setColorRampItemList(lstLoss)
                        myColorRampLoss.setColorRampType(QgsColorRampShader.Discrete)
                        myRasterShaderLoss.setRasterShaderFunction(myColorRampLoss)
                        myPseudoRendererLoss = QgsSingleBandPseudoColorRenderer(Losslayer.dataProvider(), Losslayer.type(), myRasterShaderLoss)
                        Losslayer.setRenderer(myPseudoRendererLoss)
                        Losslayer.triggerRepaint()

        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
