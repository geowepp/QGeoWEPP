# -*- coding: utf-8 -*-
"""
/***************************************************************************
Load Single Hill to WEPP
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

class LoadHilltoWeppBtn():

    def __init__(self, iface):
        self.iface = iface

    def loadhilltoweppbutton(self): 
        msg = QMessageBox()
        if len(QgsProject.instance().mapLayersByName('Subwatersheds')) == 0:
            msg.setText('Please load a QGeoWEPP project first.')
            msg.exec()
            return
        else:
            # Check if WEPP has been run before using the tool
            rwatershed = QgsProject.instance().mapLayersByName('Subwatersheds')[0]
            foldername = os.path.dirname(rwatershed.dataProvider().dataSourceUri()) 
            if not os.path.exists(os.path.join (foldername, 'Reports')):
                msg.setText('You have not performed a WEPP run yet. \n Please get erosion patterns first.')
                msg.exec()
                self.parentself.iface.mapCanvas().unsetMapTool(self.parentself.hilltoweppTool)
                return
            else:
                self.iface.mapCanvas().setMapTool(self.hilltoweppTool)
