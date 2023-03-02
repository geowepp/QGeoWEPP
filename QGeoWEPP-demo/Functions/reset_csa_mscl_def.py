# -*- coding: utf-8 -*-
"""
/***************************************************************************
Reset CSA abd MSCL
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
from qgis.core import QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from PyQt5.QtWidgets import QMessageBox, QProgressBar
from PyQt5.QtGui import QColor
import os.path, os, subprocess, sys
from shutil import copyfile
from .reset_csa_mscl_dialog import resetcsamsclDialog

class Reset_CSA_MSCLBtn():

    def __init__(self, iface):
        self.plugin_dir = os.path.dirname(__file__)
        self.reset_csa_mscl = resetcsamsclDialog()
        self.iface = iface

    def resetcsamsclbutton(self): 
        try:
            msg = QMessageBox() 
            if len(QgsProject.instance().mapLayersByName('Networks')) == 0: 
                msg.setText('The channel networks layer is required. Please load "netful.asc" to the instance and name it as "Networks".')
                msg.exec()
                return
            else:
                self.reset_csa_mscl.lineEdit_CSA2.setText("5")
                self.reset_csa_mscl.lineEdit_MSCL2.setText("100")
                rnetwork = QgsProject.instance().mapLayersByName('Networks')[0]
                foldername = os.path.dirname(rnetwork.dataProvider().dataSourceUri()) 
                self.reset_csa_mscl.show()
                result = self.reset_csa_mscl.exec_()

                # ok
                if result:   
                    reconfirm = msg.question (None, 'Warning', 'This will generate a new network layer. Do you want to continue?', msg.Yes | msg.No)
                    if reconfirm == msg.Yes:
                        bar = QProgressBar()
                        self.iface.mainWindow().statusBar().addWidget(bar)

                        # if WEPP output layers exist, remove
                        bar.setValue(17)
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
                            if name == 'Networks':
                                netlayer = QgsProject.instance().mapLayersByName(name)[0]
                                QgsProject.instance().removeMapLayer(netlayer)
                        
                        CSA = self.reset_csa_mscl.lineEdit_CSA2.text()
                        MSCL = self.reset_csa_mscl.lineEdit_MSCL2.text()
                        
                        bar.setValue(34)
                        csainp=os.path.join(foldername,'csa.inp')
                        with open (csainp, 'w') as outputcsa:
                            line = '    1         ' + CSA + '                             ' + MSCL
                            outputcsa.write(line)

                        os.chdir(foldername)
                        bar.setValue(51)
                        subprocess.call(os.path.join(foldername,'demanly.exe'),  creationflags= subprocess.CREATE_NO_WINDOW)
                        
                        bar.setValue(68)
                        with open(os.path.join(foldername, 'cellsize.txt')) as cellrecord:
                            cellsize = cellrecord.readline()[:-1]
                        if float(cellsize) < 5:
                            subprocess.call(os.path.join(foldername,'dednm.exe'))
                        else:
                            subprocess.call(os.path.join(foldername,'dednm.exe'),  creationflags= subprocess.CREATE_NO_WINDOW)
                            
                        bar.setValue(85)
                        subprocess.call(os.path.join(foldername,'rasfor.exe'),  creationflags= subprocess.CREATE_NO_WINDOW)   
                        
                        bar.setValue(100)
                        fnetasc =  os.path.join(foldername,'netful.asc')
                        copyfile(os.path.join(foldername,'NETFUL.ARC'), os.path.join(foldername,'netful.asc'))
                        crs = QgsCoordinateReferenceSystem()
                        crspath = os.path.join(foldername, 'crs.txt')
                        with open(crspath) as crsrecord:
                            crs = crs.fromProj4(crsrecord.readline())
                        netlayer = QgsRasterLayer(fnetasc, 'Networks')
                        netlayer.setCrs(crs)
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

                        self.iface.mainWindow().statusBar().removeWidget(bar)
        except:
            msg.setText('Oops!\n'+ str(sys.exc_info()) +'\nPlease try again.')
            msg.exec()