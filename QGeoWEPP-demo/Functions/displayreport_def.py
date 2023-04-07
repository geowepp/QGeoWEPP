# -*- coding: utf-8 -*-
"""
/***************************************************************************
Display Report
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
 *   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as        *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox
import os.path, os, glob, sys
from .displayreport_dialog import displayreportDialog

class DisplayReportBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.displayreport = displayreportDialog()


    def show_report(self):
        reportname = self.displayreport.comboBox.currentText() + '.txt'
        rdem = QgsProject.instance().mapLayersByName('DEM')[0]
        foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 
        reportpath = os.path.join (foldername, 'Reports', reportname)
        if os.path.exists(reportpath):
            reporttext = open(reportpath).read()
            self.displayreport.plainTextEdit.setPlainText(reporttext)       
        else:
            return

    def displayreportbutton(self):
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
                self.displayreport.show()
                rdem = QgsProject.instance().mapLayersByName('DEM')[0]
                foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 
                reportfolder = os.path.join (foldername, 'Reports')
                reportfiles = glob.glob(os.path.join(reportfolder, '*.txt'))
                for file in reportfiles:
                    reportname = os.path.basename(file)[:-4]
                    if self.displayreport.comboBox.findText(reportname) == -1:
                        self.displayreport.comboBox.addItem(reportname)
        
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
