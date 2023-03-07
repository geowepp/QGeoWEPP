# -*- coding: utf-8 -*-
"""
/***************************************************************************
Add Basemap
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
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from qgis.core import QgsRasterLayer, QgsProject
from PyQt5.QtWidgets import QMessageBox
import os.path, os, sys, requests

class AddBasemapBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)

    def addbasemapbutton(self):
        try:
            msg = QMessageBox()
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.selectOutletTool)
            self.iface.mapCanvas().unsetMapTool(self.selectHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.hilltoweppTool) 
            
            if len(QgsProject.instance().mapLayersByName('Google Satellite Basemap')) == 0:
                service_url = "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" 
                service_uri = "type=xyz&zmin=0&zmax=21&url=https://" + requests.utils.quote(service_url)

                # add the map to the bottom
                root = QgsProject.instance().layerTreeRoot()
                basemap = QgsRasterLayer(service_uri, "Google Satellite Basemap", "wms")
                QgsProject.instance().addMapLayer(basemap, False)
                root.addLayer(basemap)

        except:
            msg.setText('Ooops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
