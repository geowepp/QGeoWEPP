# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MyPluginToolBarDialog
                                 A QGIS plugin
                             -------------------
        begin                : 2021-06-11
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Han Zhang, Chris S. Renschler
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
from PyQt5.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'inputdata.ui'))

class inputdataDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(inputdataDialog, self).__init__(parent)
        self.setupUi(self)
