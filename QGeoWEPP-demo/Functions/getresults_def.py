# -*- coding: utf-8 -*-
"""
/***************************************************************************
Getresult
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
from qgis.core import QgsRasterLayer, QgsProject, QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsCoordinateReferenceSystem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QColor
import os.path, os, sys, subprocess
from shutil import copyfile
from .getresults_dialog import getresultsDialog

class GetResultsBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.getresults = getresultsDialog()

    def getresultsbutton(self):
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

            self.getresults.lineEdit_Results.setText("Simulation1")    
            self.getresults.show() 
            result = self.getresults.exec_()
            #ok
            if result:
                GetResultsBtn.runwepp(self)
        except:
            msg.setText('Ooops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()

    def runwepp(self): 
        try:  
            msg = QMessageBox()
            outname = self.getresults.lineEdit_Results.text()
            rnetwork = QgsProject.instance().mapLayersByName('Subwatersheds')[0]
            foldername = os.path.dirname(rnetwork.dataProvider().dataSourceUri()) 

            if outname == "": 
                msg.setText ("A result name is required.")
                msg.exec()
                return
                
            if os.path.exists(os.path.join(foldername, 'Reports', outname + '_output.txt')):
                msg.setText (outname + ' already exist. Please use a different name.')
                msg.exec()
                return
                
            os.chdir(foldername)
            subprocess.call(os.path.join(foldername, 'climport.exe'))
            subprocess.call(os.path.join(foldername, 'topwepp2.exe'))
            
            #gather results
            fileRunoff = os.path.join(foldername,'weppRunoff.arc')
            fileSed = os.path.join(foldername,'weppSediment.arc')
            fileSummary = os.path.join(foldername,'summary.txt')
            fileEvents = os.path.join(foldername,'ww2events.txt')
            fileOutput = os.path.join(foldername,'ww2output.txt') 
            fileReturn = os.path.join(foldername,'return_periods.txt')
            fileFlow = os.path.join(foldername,'weppFLoss.arc')
            folderResults = os.path.join(foldername,'Reports')         
            if not os.path.exists(folderResults):
                os.makedirs(folderResults)

            # Load runoff layer
            if os.path.exists(fileRunoff):
                nfileRunoff = os.path.join(folderResults, outname + '_' + 'Runoff.asc')
                copyfile(fileRunoff, nfileRunoff)
                runofffileInfo = QFileInfo(nfileRunoff)
                runoffbaseName = runofffileInfo.baseName()
                runofflayer = QgsRasterLayer(nfileRunoff, runoffbaseName)
                if not runofflayer.isValid():
                    msg.setText ('The layer is not valid.')
                    msg.exec()

                #Dislay runoff layer
                crs = QgsCoordinateReferenceSystem()
                crspath = os.path.join(foldername, 'crs.txt')
                with open(crspath) as crsrecord:
                    crs = crs.fromProj4(crsrecord.readline())
                runofflayer.setCrs(crs)
                QgsProject.instance().addMapLayer(runofflayer)

                runoffstats = runofflayer.dataProvider().bandStatistics(1, QgsRasterBandStats.All, runofflayer.extent(), 0)
                maxRunoff = runoffstats.maximumValue
                runofffnc = QgsColorRampShader()
                runofffnc.setColorRampType(QgsColorRampShader.Discrete)
                
                colDicRunoff = {'Runoffmax': '#481610', 'Runoff4': '#793329', 'Runoff3': '#a5564a', 'Runoff2': '#a58681', 'Runoff1': '#0786fd',
                                    'Runoff0.75':'#3fa1fd', 'Runoff0.5':'#74b9fd', 'Runoff0.25':'#b0d5fe', 'Runoff0.01':'#c6c6c6'}
                valueListRunoff = [1, 25, 50, 75, 100, 200, 300, 400, maxRunoff]
                lstRunoff = [QgsColorRampShader.ColorRampItem(valueListRunoff[0], QColor(colDicRunoff['Runoff0.01']),'0T <= Runoff < 1/100T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[1], QColor(colDicRunoff['Runoff0.25']), '0/100T <= Runoff < 1/4T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[2], QColor(colDicRunoff['Runoff0.5']), '1/4T <= Runoff < 1/2T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[3], QColor(colDicRunoff['Runoff0.75']), '1/2T <= Runoff < 3/4T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[4], QColor(colDicRunoff['Runoff1']), '3/4T <= Runoff < 1T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[5], QColor(colDicRunoff['Runoff2']), '1T <= Runoff < 2T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[6], QColor(colDicRunoff['Runoff3']), '2T <= Runoff < 3T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[7], QColor(colDicRunoff['Runoff4']), '3T <= Runoff < 4T'),
                                 QgsColorRampShader.ColorRampItem(valueListRunoff[8], QColor(colDicRunoff['Runoffmax']), 'Runoff >= 4T')]
                runofffnc.setColorRampItemList(lstRunoff)
                runoffshader = QgsRasterShader()
                runoffshader.setRasterShaderFunction(runofffnc)
                runoffrenderer = QgsSingleBandPseudoColorRenderer(runofflayer.dataProvider(), runofflayer.type(), runoffshader)
                runofflayer.setRenderer(runoffrenderer)

            # Load sediment yeilds
            if os.path.exists(fileSed):
                nfileSed = os.path.join(folderResults, outname+'_'+'Sediment.asc')     
                copyfile(fileSed, nfileSed)
                sedfileInfo = QFileInfo(nfileSed)
                sedbaseName = sedfileInfo.baseName()
                sedlayer = QgsRasterLayer(nfileSed, sedbaseName)
                if not sedlayer.isValid():
                    msg.setText ("Failed to load the layer.")
                    msg.exec()  
                
                #Dislay sediment layer
                crs = QgsCoordinateReferenceSystem()
                crspath = os.path.join(foldername, 'crs.txt')
                with open(crspath) as crsrecord:
                    crs = crs.fromProj4(crsrecord.readline())
                sedlayer.setCrs(crs)   
                QgsProject.instance().addMapLayer(sedlayer)
                sedstats = sedlayer.dataProvider().bandStatistics(1, QgsRasterBandStats.All, sedlayer.extent(), 0)
                sedmax = sedstats.maximumValue
                sedfnc = QgsColorRampShader()
                sedfnc.setColorRampType(QgsColorRampShader.Discrete)

                SedcolDic = {'Sed0.25':'#376b06', 'Sed0.5':'#4e9909','Sed0.75':'#66c80c','Sed1':'#7ef014','Sed2':'#fedcda',
                              'Sed3':'#ff7f78','Sed4':'#ff2216','Sedmax':'#b30900','Sed0.01':'#c6c6c6'}
                SedvalueList =[0.001, 0.25, 0.5, 0.75, 1, 2, 3, 4, sedmax]
                Sedlst = [ QgsColorRampShader.ColorRampItem(SedvalueList[0], QColor(SedcolDic['Sed0.01']),'0T <= Sediment Yield < 1/100T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[1], QColor(SedcolDic['Sed0.25']),'0/100T <= Sediment Yield < 1/4T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[2], QColor(SedcolDic['Sed0.5']),'1/4T <= Sediment Yield < 1/2T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[3], QColor(SedcolDic['Sed0.75']),'1/2T <= Sediment Yield < 3/4T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[4], QColor(SedcolDic['Sed1']),'3/4T <= Sediment Yield < 1T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[5], QColor(SedcolDic['Sed2']),'1T <= Sediment Yield < 2T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[6], QColor(SedcolDic['Sed3']),'2T <= Sediment Yield < 3T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[7], QColor(SedcolDic['Sed4']),'3T <= Sediment Yield < 4T'),
                            QgsColorRampShader.ColorRampItem(SedvalueList[8], QColor(SedcolDic['Sedmax']),'Sediment Yield >= 4T')
                            ]
                sedfnc.setColorRampItemList(Sedlst)
                sedshader = QgsRasterShader()
                sedshader.setRasterShaderFunction(sedfnc)
                sedrenderer = QgsSingleBandPseudoColorRenderer(sedlayer.dataProvider(), sedlayer.type(), sedshader)
                sedlayer.setRenderer(sedrenderer)
            
            # Load soil loss
            if os.path.exists(fileFlow):
                nfileLoss = os.path.join(folderResults,outname+'_'+'absFLoss.asc')
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
                            'Loss0.01':'#f3e483', 'Loss00':'#c6c6c6','Loss-1':'#ffe90c','Loss-2':'#69b9e6','Loss-3':'#428fbf','Loss-4':'#1c4a66'}
                valueListLoss =[-4, -3, -2, -1, -0.01, 0.01, 0.25, 0.5, 0.75, 1, 2, 3, 4, maxLoss]
                lstLoss = [ QgsColorRampShader.ColorRampItem(valueListLoss[0], QColor(colDicLoss['Loss-4']),'Deposition > 4T'), 
                            QgsColorRampShader.ColorRampItem(valueListLoss[1], QColor(colDicLoss['Loss-3']),'3T < Deposition <= 4T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[2], QColor(colDicLoss['Loss-2']),'2T < Deposition <= 3T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[3], QColor(colDicLoss['Loss-1']),'1T < Deposition <= 2T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[4], QColor(colDicLoss['Loss0.01']),'0/100T < Deposition <= 1T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[5], QColor(colDicLoss['Loss00']),'-0/100T <= Soil Loss < 0/100T'), 
                            QgsColorRampShader.ColorRampItem(valueListLoss[6], QColor(colDicLoss['Loss0.25']),'0/100T <= Soil Loss < 1/4T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[7], QColor(colDicLoss['Loss0.5']),'1/4T <= Soil Loss < 1/2T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[8], QColor(colDicLoss['Loss0.75']),'1/2T <= Soil Loss < 3/4T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[9], QColor(colDicLoss['Loss1']),'3/4T <= Soil Loss < 1T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[10], QColor(colDicLoss['Loss2']),'1T <= Soil Loss < 2T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[11], QColor(colDicLoss['Loss3']),'2T <= Soil Loss < 3T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[12], QColor(colDicLoss['Loss4']),'3T <= Soil Loss < 4T'),
                            QgsColorRampShader.ColorRampItem(valueListLoss[13], QColor(colDicLoss['Lossmax']),'Soil Loss >= 4T')
                            ]
                lossfnc.setColorRampItemList(lstLoss)
                lossshader = QgsRasterShader()
                lossshader.setRasterShaderFunction(lossfnc)
                lossrenderer = QgsSingleBandPseudoColorRenderer(losslayer.dataProvider(), losslayer.type(), lossshader)
                losslayer.setRenderer(lossrenderer)      
                  
            if os.path.exists(fileSummary):
                nfileSummary = os.path.join(folderResults, outname+'_' + 'summary.txt')
                copyfile(fileSummary, nfileSummary)
            if os.path.exists(fileEvents):
                nfileEvents = os.path.join(folderResults, outname+'_' + 'events.txt')
                copyfile(fileEvents, nfileEvents)
            if os.path.exists(fileOutput):
                nfileOutput = os.path.join(folderResults, outname+'_' + 'output.txt')
                copyfile(fileOutput, nfileOutput)
            if os.path.exists(fileReturn):
                nfileReturn = os.path.join(folderResults,outname+'_' + 'return_periods.txt')
                copyfile(fileReturn, nfileReturn)

        except:
            msg.setText('Ooops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
