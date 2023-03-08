# -*- coding: utf-8 -*-
"""
/***************************************************************************
Display plot
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
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import uic
from PyQt5.QtWidgets import QDialog
import pyqtgraph as pg

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'displaychart.ui'))

class displaychartDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(displaychartDialog, self).__init__(parent)
        self.setupUi(self)
