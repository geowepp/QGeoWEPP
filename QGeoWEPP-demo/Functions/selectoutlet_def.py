# -*- coding: utf-8 -*-
"""
/***************************************************************************
SelectOutlet
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
 *   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as        *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox

class SelectOutletBtn():

    def __init__(self, iface):
        self.iface = iface

    def selectoutletbutton(self): 
        if len(QgsProject.instance().mapLayersByName('Networks')) == 0:
            msg = QMessageBox()
            msg.setText('The Channel Netorks are required. \nPlease load "netful.asc" to the instance and name it as "Networks".')
            return
        else:
            self.iface.mapCanvas().setMapTool(self.selectOutletTool)
