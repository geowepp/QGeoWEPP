# -*- coding: utf-8 -*-
"""
/***************************************************************************
Get hillslope information
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
from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox
import os.path, os

class GetHillSlopeInfoBtn():

    def __init__(self, iface):
        self.iface = iface

    def gethillslopeinfobutton(self): 
        msg = QMessageBox()   
        if len(QgsProject.instance().mapLayersByName('DEM')) == 0:
            msg.setText('Please load a QGeoWEPP project first.')
            msg.exec()
        else:
            # Check if WEPP has been run before using the tool
            rdem = QgsProject.instance().mapLayersByName('DEM')[0]
            foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 
            if not os.path.exists(os.path.join (foldername, 'Reports')):
                msg.setText('You have not performed a WEPP run yet. \nPlease get erosion patterns first.')
                msg.exec()
                return
            else:
                self.iface.mapCanvas().setMapTool(self.selectHillSlopeTool)