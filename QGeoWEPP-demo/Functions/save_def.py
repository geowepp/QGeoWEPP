# -*- coding: utf-8 -*-
"""
/***************************************************************************
Save QGIS project
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
from qgis.core import  QgsProject
from PyQt5.QtWidgets import QMessageBox
import os.path, os, sys
from .inputdata_dialog import inputdataDialog

class SaveBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.inputdata = inputdataDialog()

    def savebutton(self):
        try:
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.selectOutletTool)
            self.iface.mapCanvas().unsetMapTool(self.selectHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.hilltoweppTool) 

            msg = QMessageBox()
            if len(QgsProject.instance().mapLayersByName('DEM')) == 0:
                msg.setText('Please load a QGeoWEPP project first.')
                msg.exec()
                return
            else:
                rdem = QgsProject.instance().mapLayersByName('DEM')[0]
                foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 
       
                projname = os.path.join(foldername, os.path.basename(foldername) + '_QGeoWEPP_project.qgs')
                QgsProject.instance().write(projname)

                msg.setText('The project has been saved sucessfully as ' + os.path.basename(projname) + '.')
                msg.exec()
        except:
            msg.setText('Oops!\n'+ str(sys.exc_info()) +'\nPlease try again.')
            msg.exec()
