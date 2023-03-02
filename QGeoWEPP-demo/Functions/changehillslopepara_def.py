# -*- coding: utf-8 -*-
"""
/***************************************************************************
Change hillslope parameters
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
import os.path, os
from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox

class ChangeHillSlopeParaBtn():

    def __init__(self, iface):
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface

    def changehillslopeparabutton(self): 
        # Check if WEPP has been run before using the tool
        if len(QgsProject.instance().mapLayersByName('Subwatersheds')) == 0:
            msg = QMessageBox()
            msg.setText('You have not performed a WEPP run yet. \nPlease get erosion patterns first.')
            msg.exec()
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            return

        rwatershed = QgsProject.instance().mapLayersByName('Subwatersheds')[0]
        foldername = os.path.dirname(rwatershed.dataProvider().dataSourceUri()) 
        if not os.path.exists(os.path.join (foldername, 'Reports')):
            msg = QMessageBox()
            msg.setText('You have not performed a WEPP run yet. \nPlease get erosion patterns first.')
            msg.exec()
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            return
        else:
            self.iface.mapCanvas().setMapTool(self.changeHillSlopeTool)
