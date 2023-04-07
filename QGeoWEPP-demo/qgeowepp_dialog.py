# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGeoWEPPDialog
                                 A QGIS plugin
 GeoWEPP (Geospatial interface to WEPP) for QGIS Research Version
                             -------------------
        begin                : 2021-6-11
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Han Zhang
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

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgeowepp_dialog_base.ui'))


class QGeoWEPPDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(QGeoWEPPDialog, self).__init__(parent)
        self.setupUi(self)
