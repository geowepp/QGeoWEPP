# -*- coding: utf-8 -*-
"""
/***************************************************************************
Inputdata
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
from qgis.core import QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from qgis.gui import QgsProjectionSelectionDialog
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QColor
import os.path, os, subprocess, numpy, sys, re
from shutil import copyfile
from distutils.dir_util import copy_tree
from .inputdata_dialog import inputdataDialog

class InputDataBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.inputdata = inputdataDialog()
    
    def select_output_folder(self):
        foldername, __ = QFileDialog.getSaveFileName(self.inputdata, "Select output project folder name", "", '*')
        self.inputdata.lineEdit_project.setText(foldername)

    def select_dem(self):
        demascii = QFileDialog.getOpenFileName(self.inputdata, "Select a DEM ASCII file", "", "*.asc")
        self.inputdata.lineEdit_DEM.setText(str(demascii[0]))
    
    def select_crs(self):
        msg = QMessageBox()
        self.crsdlg = QgsProjectionSelectionDialog()
        self.crsdlg.setCrs(QgsCoordinateReferenceSystem('EPSG:32610'))
        self.crsdlg.exec_()
        crsvalue = self.crsdlg.crs().authid()
        crscode = int(crsvalue.split(':',1)[-1])
        if crscode < 32601 or (crscode > 32660 and crscode < 32701) or crscode > 32760:
            msg.setText('Please select a WGS84/UTM Coordinate Reference System.')
            msg.exec()
            self.inputdata.lineEdit_crs.clear()
        else:
            self.inputdata.lineEdit_crs.setText(crsvalue)

    def select_soil(self):
        soilascii = QFileDialog.getOpenFileName(self.inputdata, "Select a soil ASCII file", "", "*.asc")
        self.inputdata.lineEdit_soil.setText(str(soilascii[0]))

    def select_soildscp(self):
        soildscp = QFileDialog.getOpenFileName(self.inputdata, "Select a soil description file", "", "*.txt")
        self.inputdata.lineEdit_soilDscp.setText(str(soildscp[0]))

    def select_soildb(self):
        soildb = QFileDialog.getOpenFileName(self.inputdata, "Select a soil database file", "", "*.txt")
        self.inputdata.lineEdit_soilDB.setText(str(soildb[0]))

    def select_lc(self):
        lcascii = QFileDialog.getOpenFileName(self.inputdata, "Select a land cover ASCII file", "", "*.asc")
        self.inputdata.lineEdit_lc.setText(str(lcascii[0]))

    def select_lcdscp(self):
        lcdscp = QFileDialog.getOpenFileName(self.inputdata, "Select a land cover description file", "", "*.txt")
        self.inputdata.lineEdit_lcDscp.setText(str(lcdscp[0]))
        
    def select_lcdb(self):
        lcdb = QFileDialog.getOpenFileName(self.inputdata, "Select a land cover database file", "", "*.txt")
        self.inputdata.lineEdit_lcDB.setText(str(lcdb[0]))
    
    def is_valid_path(self, string: str):
        pattern = re.compile(r'((\w:)|(\.))((/(?!/)(?!/)|\\{2})[^\n?"|></\\:*]+)+')
        if string and isinstance(string, str) and pattern.match(string):
           return True
        return False
    
    def is_float(num):
        try:
            float(num)
            return True
        except ValueError:
            return False
   

    def inputdatabutton(self):   
        try:
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.selectOutletTool)
            self.iface.mapCanvas().unsetMapTool(self.selectHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.hilltoweppTool) 

            self.inputdata.progressBar.reset()
            self.inputdata.lineEdit_CSA.setText("5")
            self.inputdata.lineEdit_MSCL.setText("100")
            msg = QMessageBox()

            # check if a previous project is in the instance
            layernames = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
            if len(layernames) != 0:         
                reconfirm = msg.question (None, 'Warning', 'This will create a new project. Do you want to continue?', msg.Yes | msg.No)
                if reconfirm == msg.Yes:
                    QgsProject.instance().clear()
                    self.inputdata.show()
                else: return
            else: self.inputdata.show()
        except:
            msg.setText('Ooops!\n'+ str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()

     
    # Load data
    def load_data(self, folder, csa, mscl, dem, landcover, lcdscp, lcdb, soil, soildscp, soildb, crsid):
        try:
            msg = QMessageBox()
            self.inputdata.progressBar.setValue(1)
            if os.path.exists(dem):
                copyfile(dem, os.path.join(folder,'dem.asc'))
            if os.path.exists(lcdscp):
                copyfile(lcdscp, os.path.join(folder,'landcov.txt'))
            if os.path.exists(lcdb):           
                copyfile(lcdb, os.path.join(folder,'landusedb.txt'))
            if os.path.exists(soildscp):           
                copyfile(soildscp, os.path.join(folder,'soilsmap.txt'))
            if os.path.exists(soildb):      
                copyfile(soildb, os.path.join(folder,'soilsdb.txt'))

            self.inputdata.progressBar.setValue(2)
            requiredfiles =os.path.join(self.plugin_dir, 'RequiredFiles')
            weppfolder = os.path.join(self.plugin_dir, 'WEPP')
            copy_tree (requiredfiles, folder)

            newdem = os.path.join(folder, 'dem.asc')
            newland = os.path.join(folder,'landcov.asc')
            newsoil = os.path.join(folder,'soilsmap.asc')
            tmpdem = os.path.join(folder, 'tmpdem1.dat')
            copyfile(landcover, newland)
            copyfile(soil, newsoil)
            copyfile(newdem, tmpdem)

            # convert dem to tmpdem1.dat
            self.inputdata.progressBar.setValue(3)
            indem = os.path.join(folder, 'dem.asc')
            outdem = os.path.join (folder, 'tmpdem1.dat')
            with open(indem) as deminput:
                with open(outdem, 'w') as demoutput:
                # copy the first six lines (header of dem) to tempdem
                    for i in range (4):
                        line = deminput.readline()
                        demoutput.write (line)
                    cellsizeline = deminput.readline()
                    demoutput.write(cellsizeline)
                    nodata = deminput.readline()
                    demoutput.write(nodata)
                    # process the elevation
                    dem2txt = numpy.loadtxt (deminput)
                    dem2txt [:, 0] = -9999
                    dem2txt [:, -1] = -9999
                    dem2txt [0, :] = -9999
                    dem2txt [-1, :] = -9999
                    numpy.savetxt (demoutput, dem2txt, '%1.3f')
                
            #convert CSA & MSCL to csa.inp
            self.inputdata.progressBar.setValue(4)
            csainp = os.path.join(folder,'csa.inp')
            with open (csainp, 'w') as outputcsa:
                line = '    1         ' + csa + '                             ' + mscl
                outputcsa.write(line)
                
            #write out cmd2.txt
            self.inputdata.progressBar.setValue(5)
            cmd2txt=os.path.join(folder,'cmd2.txt')
            with open (cmd2txt, 'w') as outputcmd2:
                outputcmd2.write('Root = ' + weppfolder + '\n') 
                outputcmd2.write('climate = "p0.cli"\n')
                outputcmd2.write('management = "grass.rot"\n')
                outputcmd2.write('soil = "KEITH.sol"\n')
                outputcmd2.write('channel = "DITCH"\n')
                outputcmd2.write('channelWidth = 3\n')
                outputcmd2.write('years = 2\n')
                outputcmd2.write('SoilLossGrid\n')
                outputcmd2.write('SedimentGrid\n')
                outputcmd2.write('RunoffGrid\n')
                outputcmd2.write('RunWatershed\n')
                outputcmd2.write('RunFlowpath\n')
                outputcmd2.write('ManagementGrid = "landcov.asc"\n')
                outputcmd2.write('SoilGrid = "soilsmap.asc"\n')
                outputcmd2.write('end of file\n')
            
            self.inputdata.progressBar.setValue(6)
            os.chdir(folder)
            subprocess.run(os.path.join(folder,'demanly.exe'), creationflags= subprocess.CREATE_NO_WINDOW)
  
            self.inputdata.progressBar.setValue(7)
            #identify if the cell size is smaller than 5m
            cellsize = cellsizeline.split(' ', 1)[-1]
            if float(cellsize) < 5:
                subprocess.run(os.path.join(folder,'dednm.exe'))
            else:
                subprocess.run(os.path.join(folder,'dednm.exe'), creationflags= subprocess.CREATE_NO_WINDOW)
            
            self.inputdata.progressBar.setValue(8)
            subprocess.run(os.path.join(folder,'rasfor.exe'), creationflags= subprocess.CREATE_NO_WINDOW)          
                
            # writeout cell size for later use
            cellout = os.path.join(folder, 'cellsize.txt')
            with open(cellout, 'w') as cellrecord:
                cellrecord.write(cellsize)
                
            # copy network to asc
            self.inputdata.progressBar.setValue(9)
            copyfile(os.path.join(folder,'NETFUL.ARC'), os.path.join(folder,'netful.asc'))
                
            # get crs and write it out for later use
            self.inputdata.progressBar.setValue(10)
            crs = QgsCoordinateReferenceSystem(crsid, QgsCoordinateReferenceSystem.EpsgCrsId)
            crspath = os.path.join(folder, 'crs.txt')
            with open(crspath, 'w') as crsfile:
                crsfile.write(crs.toProj4())
                
            self.inputdata.progressBar.setValue(11)
            #Load soil layers
            soillayer = QgsRasterLayer(newsoil, 'Soil')
            soillayer.setCrs(QgsCoordinateReferenceSystem(crsid, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsProject.instance().addMapLayer(soillayer)

            renderersoil = soillayer.renderer()
            fncsoil = QgsColorRampShader()
            fncsoil.setColorRampType(QgsColorRampShader.Exact)

            valueListsoil = []
            soillegend = []
            with open(soildscp) as soil:
                # read the first line header
                # soil.readline()
                # read soil info
                soilinfo = soil.readlines()
                for line in soilinfo:
                    linetxt = line.split(',', 1)[0]
                    if InputDataBtn.is_float(linetxt) == False:
                        pass
                    else:
                        valueListsoil.append(float(linetxt))
                        soillegend.append(line.split(',', 2)[-1][:-1])

            colorLstSoil = ['#ba7132', '#ffe1b2', '#e2a68a', '#f9c298', '#fcab41', '#e5c270', '#ed9f71', '#f9d9c0','#ea8f20',
                            '#ea8f20', '#dba555', '#c1530f', '#db9f30', '#b25d25', '#fcc997', '#bf9822', '#f4c87c', '#eda987',
                            '#f9d3b1', '#e8cc92', '#f7a576', '#b77503', '#e5af75', '#e5a00b', '#ce7244', '#b78b07', '#d6a30a',
                            '#fc6c05', '#fcbc9f', '#edbf84', '#c69413', '#e2ac8e', '#fcdbb8', '#cc9d12', '#efb9a0', '#d67544',
                            '#efad62', '#efb870', '#fcdcb0', '#bc7f34', '#f4dcab', '#fc975d', '#ff8d30', '#ffad6b', '#ddb575', 
                            '#ffe8b5', '#efb388', '#f9ad81', '#fcab83', '#ed8b0b', '#ffe2a0', '#f7debb', '#ba6435', '#f2b598', 
                            '#ffe7c4', '#e8b87a', '#f29f41', '#e59f59', '#ffeec9', '#e0a37d', '#e2841f', '#ba640e', '#d37b32',
                            '#eab06e', '#d17947', '#f7dc8c', '#dbad57', '#f4be73', '#d3a421', '#f2976a', '#f7dca8', '#f2c6b0',
                            '#e57e3d', '#b58c2f', '#ce9906']
            if len(valueListsoil) == 0:
                msg.setText('There is something wrong with the soil description file. Please check the format.')
                msg.exec()
            elif len(valueListsoil) > 75:
                msg.setText('The maximum number of soil type is 75.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return         
            else:
                colorDicSoil = {valueListsoil[i]: colorLstSoil[i] for i in range(len(valueListsoil))}
                legendDicSoil = {valueListsoil[i]: soillegend[i] for i in range(len(valueListsoil))}
                lstsoil = []
                for colors in valueListsoil:
                    lstsoil.append(QgsColorRampShader.ColorRampItem(colors, QColor(colorDicSoil[colors]), legendDicSoil[colors]))
        
                fncsoil.setColorRampItemList(lstsoil)
                shadersoil = QgsRasterShader()
                shadersoil.setRasterShaderFunction(fncsoil)
                renderersoil = QgsSingleBandPseudoColorRenderer(soillayer.dataProvider(), 1, shadersoil)
                soillayer.setRenderer(renderersoil)

            # Load land cover layer             
            landlayer = QgsRasterLayer(newland, "Land Cover")
            landlayer.setCrs(QgsCoordinateReferenceSystem(crsid, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsProject.instance().addMapLayer(landlayer)
 
            rendererland = landlayer.renderer()
            fncland = QgsColorRampShader()
            fncland.setColorRampType(QgsColorRampShader.Exact)
                
            valueListland = []
            lclegend = []
            with open(lcdscp) as landcov:
                lcinfo = landcov.readlines()
                for line in lcinfo:
                    linetxt = line.split(' ', 1)[0]
                    if InputDataBtn.is_float(linetxt) == False:
                        valueListland.clear()
                    else:
                        valueListland.append(float(linetxt))
                        lclegend.append(line.split(' ',1)[-1][:-1])
            colorLstLand = ['#5475a8', '#ffffff', '#e8d1d1', '#e29e8c', '#ff0000', '#b50000', '#d2cdc0', '#eca37e', '#85c77e',
                            '#38814e', '#d4e7b0', '#ad9538', '#dcca8f', '#1cbd58', '#e2e2c1', '#d1d180', '#a8cb4c', '#89ba9d',
                            '#fbf65d', '#fff5f0', '#63331b', '#d31b21', '#ca9146', '#c8e6f8', '#64b3d5', '#ed8b6a', '#b8d34e',
                            '#9413bf', '#f99e2f', '#d624af', '#765ddd', '#2d03c4', '#dd4953', '#67fcaa', '#f972ad', '#d82797',
                            '#a9fcd8', '#052b8c', '#af2edb', '#fcc4c2', '#c4e0ff', '#1bd698', '#26cc4a', '#7b1fdd', '#8ac7d8',
                            '#423393', '#84cc18', '#dfef00', '#64eab5', '#a2c1e8', '#7cdb6b', '#d8aa04', '#d8a758', '#f92cd4',
                            '#e21dd2', '#a372db', '#ef9e7f', '#f24be1', '#f1f9a4', '#b884ed', '#f285d5', '#9536d8', '#f972b4',
                            '#48f9b5', '#c7b7f4', '#53c615', '#cee86a', '#9a73ef', '#ffd9cc', '#edb79c', '#9162f7', '#23ffd3',
                            '#83e02c', '#ffff1e', '#e06514']   
            if len(valueListland) == 0:
                msg.setText('There is something wrong with the land cover description file. Please check the format.')
                msg.exec()       
            elif len(valueListland) > 75:
                msg.setText('The maximum number of land cover type is 75.')
                msg.exec()  
                self.inputdata.progressBar.setValue(0)   
                return
            else:
                colorDicland = {valueListland[i]: colorLstLand[i] for i in range(len(valueListland))}
                legendDicland = {valueListland[i]: lclegend[i] for i in range(len(valueListland))}
                lstland = []
                for colorl in valueListland:
                    lstland.append(QgsColorRampShader.ColorRampItem(colorl, QColor(colorDicland[colorl]), legendDicland[colorl]))   
   
                fncland.setColorRampItemList(lstland)
                shaderland = QgsRasterShader()
                shaderland.setRasterShaderFunction(fncland)
                rendererland = QgsSingleBandPseudoColorRenderer(landlayer.dataProvider(), 1, shaderland)
                landlayer.setRenderer(rendererland)
               
            # Load DEM layer   
            demlayer = QgsRasterLayer(newdem, 'DEM')
            demlayer.setCrs(QgsCoordinateReferenceSystem(crsid, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsProject.instance().addMapLayer(demlayer)

            # Load channel networks
            network = os.path.join(folder,'netful.asc')
            netlayer = QgsRasterLayer(network, 'Networks')
            netlayer.setCrs(QgsCoordinateReferenceSystem(crsid, QgsCoordinateReferenceSystem.EpsgCrsId))
            QgsProject.instance().addMapLayer(netlayer)
    
            renderernet = netlayer.renderer()
            fncnet = QgsColorRampShader()
            fncnet.setColorRampType(QgsColorRampShader.Exact)
            lstnet = [QgsColorRampShader.ColorRampItem(1, QColor('#00ffff'), 'networks')]
            fncnet.setColorRampItemList(lstnet)
            shadernet = QgsRasterShader()
            shadernet.setRasterShaderFunction(fncnet)
            renderernet = QgsSingleBandPseudoColorRenderer(netlayer.dataProvider(), 1, shadernet)
            netlayer.setRenderer(renderernet)
                
            # create a project file
            projname = os.path.join(folder, os.path.basename(folder) + '_QGeoWEPP_project.qgs')
            QgsProject.instance().write(projname)

            self.inputdata.close()
            
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
    
    # Agriculture
    def load_agriculture(self):
        foldername, __ = QFileDialog.getSaveFileName(self.inputdata, "Select output project folder name", "", '*')
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        source = os.path.join(self.plugin_dir, 'Example_Data', 'Agriculture')
        demascii = os.path.join(source, 'dem.asc')
        lcascii = os.path.join(source, 'management.asc')
        lcdb = os.path.join(source, 'landusedb.txt')
        lcdscp = os.path.join(source, 'landcov.txt')
        soilascii = os.path.join(source, 'soils.asc')
        soildb = os.path.join(source, 'soilsdb.txt')
        soildscp = os.path.join(source, 'soilsmap.txt')
        InputDataBtn.load_data(self, foldername, '5', '100', demascii, lcascii, lcdscp, lcdb, soilascii, soildscp, soildb, 32616)
    
    # BAER
    def load_baer(self):
        foldername, __ = QFileDialog.getSaveFileName(self.inputdata, "Select output project folder name", "", '*')
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        source = os.path.join(self.plugin_dir, 'Example_Data', 'BAER')
        demascii = os.path.join(source, 'dem.asc')
        lcascii = os.path.join(source, 'management.asc')
        lcdb = os.path.join(source, 'landusedb.txt')
        lcdscp = os.path.join(source, 'landcov.txt')
        soilascii = os.path.join(source, 'soils.asc')
        soildb = os.path.join(source, 'soilsdb.txt')
        soildscp = os.path.join(source, 'soilsmap.txt')
        InputDataBtn.load_data(self, foldername, '5', '100', demascii, lcascii, lcdscp, lcdb, soilascii, soildscp, soildb, 32613)
    
    # CWE
    def load_cwe(self):
        foldername, __ = QFileDialog.getSaveFileName(self.inputdata, "Select output project folder name", "", '*')
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        source = os.path.join(self.plugin_dir, 'Example_Data', 'CWE')
        demascii = os.path.join(source, 'dem.asc')
        lcascii = os.path.join(source, 'management.asc')
        lcdb = os.path.join(source, 'landusedb.txt')
        lcdscp = os.path.join(source, 'landcov.txt')
        soilascii = os.path.join(source, 'soils.asc')
        soildb = os.path.join(source, 'soilsdb.txt')
        soildscp = os.path.join(source, 'soilsmap.txt')
        InputDataBtn.load_data(self, foldername, '5', '100', demascii, lcascii, lcdscp, lcdb, soilascii, soildscp, soildb, 32613)

    # Rangeland
    def load_rangeland(self):
        foldername, __ = QFileDialog.getSaveFileName(self.inputdata, "Select output project folder name", "", '*')
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        source = os.path.join(self.plugin_dir, 'Example_Data', 'Rangeland')
        demascii = os.path.join(source, 'dem.asc')
        lcascii = os.path.join(source, 'management.asc')
        lcdb = os.path.join(source, 'landusedb.txt')
        lcdscp = os.path.join(source, 'landcov.txt')
        soilascii = os.path.join(source, 'soils.asc')
        soildb = os.path.join(source, 'soilsdb.txt')
        soildscp = os.path.join(source, 'soilsmap.txt')
        InputDataBtn.load_data(self, foldername, '5', '100', demascii, lcascii, lcdscp, lcdb, soilascii, soildscp, soildb, 32612)
    
    # Lucky Hills
    def load_luckhills(self):
        foldername, __ = QFileDialog.getSaveFileName(self.inputdata, "Select output project folder name", "", '*')
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        source = os.path.join(self.plugin_dir, 'Example_Data', 'LuckyHills')
        demascii = os.path.join(source, 'dem.asc')
        lcascii = os.path.join(source, 'management.asc')
        lcdb = os.path.join(source, 'landusedb.txt')
        lcdscp = os.path.join(source, 'landcov.txt')
        soilascii = os.path.join(source, 'soils.asc')
        soildb = os.path.join(source, 'soilsdb.txt')
        soildscp = os.path.join(source, 'soilsmap.txt')
        InputDataBtn.load_data(self, foldername, '0.1', '1', demascii, lcascii, lcdscp, lcdb, soilascii, soildscp, soildb, 32612)
    
    # Input users own data
    def load_customized(self):
        msg = QMessageBox()
        foldername = self.inputdata.lineEdit_project.text()
        demascii = self.inputdata.lineEdit_DEM.text() 
        crscode = self.inputdata.lineEdit_crs.text()
        CSA = self.inputdata.lineEdit_CSA.text()
        MSCL = self.inputdata.lineEdit_MSCL.text()

        # Check files
        self.inputdata.progressBar.setValue(1)
        if foldername == '': 
            msg.setText ('A valid project folder name is required. \nPlease try again.')
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return
        if os.path.isfile(foldername):
            msg.setText ('The directory is not a folder. \nPlease try again.')
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return
        if InputDataBtn.is_valid_path(self, foldername) == False:
            msg.setText ('Please provide a valid folder directory.')
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return
        if crscode == '':
            reconfirm = msg.question (None, 'Warning', 'A WGS84/UTM CRS is missing. Do you want to use the default WGS84?', msg.Yes | msg.No)
            if reconfirm == msg.Yes:
                pass
            else: 
                self.inputdata.progressBar.setValue(0)
                return  
        if demascii == '':
            msg.setText('A DEM ASCII file is missing. \nPlease try again.')
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return
        if not os.path.exists(demascii):
            msg.setText("The DEM ASCII file doesn't exist. \nPlease try again.")
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return
        if not os.path.exists(foldername):
            os.makedirs(foldername)           
        if CSA == '': 
            msg.setText ('CSA value is required. \nPlease try again.')
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return          
        if MSCL == '': 
            msg.setText ('MSCL value is required. \nPlease try again.')
            msg.exec()
            self.inputdata.progressBar.setValue(0)
            return
        
        if crscode != '':
            crsid = int(crscode.split(':', 1)[1])
        else:
            crsid = 4326
            
        # if checkbox for soil is checked
        if self.inputdata.checkBox_soil.isChecked():
            soilascii = self.inputdata.lineEdit_soil.text()
            soildscp = self.inputdata.lineEdit_soilDscp.text()
            soildb = self.inputdata.lineEdit_soilDB.text()
            if soilascii == '':
                msg.setText('A soil ASCII file is missing. \nPlease try again.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if not os.path.exists(soilascii):
                msg.setText("The soil ASCII file doesn't exist. \nPlease try again.")
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if soildscp == '':
                msg.setText('A soil description file is missing. \nPlease try again.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if not os.path.exists(soildscp):
                msg.setText("The soil description file doesn't exist. \nPlease try again.")
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if soildb == '':
                msg.setText('A soil database file is missing. \nPlease try again.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if not os.path.exists(soildb):
                msg.setText("The soil database file doesn't exist. \nPlease try again.")
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
        else:
            # generate default soil ascii based on dem
            defaultsoildir = os.path.join (foldername, 'defaultsoil.asc')
            with open(demascii) as demcopy:
                with open(defaultsoildir, 'w') as defaultsoil:
                    # copy the first six lines (header of dem) to defaultsoil
                    for i in range (6):
                        line = demcopy.readline()
                        defaultsoil.write (line)
                    # replace elevation to 1 as default soil id
                    for line in demcopy:
                        str2num = map (float, line.split())
                        provalue = [(1 if num > -10000 else num) for num in str2num]
                        stringpro = ' '.join(map(str, provalue))
                        defaultsoil.write (stringpro + '\n')                
            
        
            soilascii = defaultsoildir
            requiredfiles =os.path.join(self.plugin_dir, 'RequiredFiles')
            soildscp = os.path.join(requiredfiles, 'defaultsoilmap.txt')
            soildb = os.path.join(requiredfiles, 'defaultsoildb.txt')

        # if checkbox for landcover is checked
        if self.inputdata.checkBox_lc.isChecked():
            lcascii = self.inputdata.lineEdit_lc.text()
            lcdscp = self.inputdata.lineEdit_lcDscp.text()
            lcdb = self.inputdata.lineEdit_lcDB.text()
            if lcascii == '':
                msg.setText('A land cover ASCII file is missing. \n Please try again.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if not os.path.exists(lcascii):
                msg.setText("The land cover ASCII file doesn't exist. \n Please try again.")
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if lcdscp == '':
                msg.setText('A land cover description file is missing. \n Please try again.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if not os.path.exists(lcdscp):
                msg.setText("The land cover description file doesn't exist. \n Please try again.")
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if lcdb == '':
                msg.setText('A land cover database file is missing. \n Please try again.')
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return
            if not os.path.exists(lcdb):
                msg.setText("The land cover database file doesn't exist. \n Please try again.") 
                msg.exec()
                self.inputdata.progressBar.setValue(0)
                return  
        else:
            # generate default land use ascii based on dem
            defaultlcdir = os.path.join (foldername, 'defaultlc.asc')
            with open(demascii) as demcopy:
                with open(defaultlcdir, 'w') as defaultlc:
                    # copy the first six lines (header of dem) to defaultlc
                    for i in range (6):
                        line = demcopy.readline()
                        defaultlc.write (line)
                    # replace elevation to 1 as default land use id
                    for line in demcopy:
                        str2num = map (float, line.split())
                        provalue = [(1 if num > -10000 else num) for num in str2num]
                        stringpro = ' '.join(map(str, provalue))
                        defaultlc.write (stringpro + '\n')   
            lcascii = defaultlcdir
            requiredfiles =os.path.join(self.plugin_dir, 'RequiredFiles')
            lcdscp = os.path.join(requiredfiles, 'defaultlc.txt')
            lcdb = os.path.join(requiredfiles, 'defaultlcdb.txt')             

        InputDataBtn.load_data(self, foldername, CSA, MSCL, demascii, lcascii, lcdscp, lcdb, soilascii, soildscp, soildb, crsid)
