# -*- coding: utf-8 -*-
"""
/***************************************************************************
Output Analysis
                                 A QGIS plugin
                             -------------------
        begin                : 2021-06-11
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

import os, sys, importlib
from qgis.PyQt import uic
from PyQt5.QtWidgets import QDialog
import pyqtgraph as pg

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'outputanalysis.ui'))

class outputanalysisDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(outputanalysisDialog, self).__init__(parent)
        self.setupUi(self)
