# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGeoWEPP
                                 A QGIS plugin
 GeoWEPP (Geo-spatial interface of WEPP) for QGIS
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
from __future__ import print_function
from __future__ import absolute_import
from builtins import object
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtWidgets import QAction, QDialogButtonBox
from PyQt5.QtGui import QIcon
from qgis.utils import reloadPlugin
import os.path, os, subprocess
# check if pyqtgraph and pywinauto is installed
try: import pyqtgraph, pywinauto
except ImportError:
    subprocess.call(['pip', 'install', 'pyqtgraph'], creationflags= subprocess.CREATE_NO_WINDOW)
    subprocess.call(['pip', 'install', 'pywinauto'], creationflags= subprocess.CREATE_NO_WINDOW)
    reloadPlugin('QGeoWEPP')

# check if 
from .Functions.outputanalysis_dialog import outputanalysisDialog
from .Functions.inputdata_dialog import inputdataDialog
from .Functions.reset_csa_mscl_dialog import resetcsamsclDialog
from .Functions.getresults_dialog import getresultsDialog
from .Functions.changetrvalue_dialog import changetrvalueDialog
from .Functions.displayreport_dialog import displayreportDialog
from .Functions.displaychart_dialog import displaychartDialog
from .Functions.batch_dialog import batchDialog

from .Functions.inputdata_def import InputDataBtn
from .Functions.addbasemap_def import AddBasemapBtn
from .Functions.reset_csa_mscl_def import Reset_CSA_MSCLBtn
from .Functions.selectoutlet_def import SelectOutletBtn
from .Functions.getresults_def import GetResultsBtn
from .Functions.changetrvalue_def import ChangeTRValueBtn
from .Functions.displayreport_def import DisplayReportBtn
from .Functions.displaychart_def import DisplayChartBtn
from .Functions.outputanalysis_def import OutputAnalysisBtn
from .Functions.gethillslopeinfo_def import GetHillSlopeInfoBtn
from .Functions.changehillslopepara_def import ChangeHillSlopeParaBtn
from .Functions.hilltowepp_def import LoadHilltoWeppBtn
from .Functions.batch_def import BatchBtn
from .Functions.save_def import SaveBtn

from .Functions.selectoutlet_tool import SelectOutletTool
from .Functions.gethillslopeinfo_tool import SelectHillSlopeTool
from .Functions.changehillslopepara_tool import ChangeHillSlopeTool
from .Functions.hilltowepp_tool import HilltoWeppTool

# main plugin
class QGeoWEPP(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QGeoWEPP_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.inputdata = inputdataDialog()
        self.reset_csa_mscl = resetcsamsclDialog()
        self.getresults = getresultsDialog()
        self.displayreport = displayreportDialog()
        self.changetrvalue = changetrvalueDialog()
        self.displaychart = displaychartDialog()
        self.outputanalysis = outputanalysisDialog()
        self.batchprocessing = batchDialog()
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QGeoWEPP ')
        self.toolbar = self.iface.addToolBar(u'QGeoWEPP')
        self.toolbar.setObjectName(u'QGeoWEPP')
   
        # Set for inputdata ui
        #self.inputdata.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.inputdata.button_box.button(QDialogButtonBox.Apply).clicked.connect(lambda:InputDataBtn.load_customized(self))
        
        self.inputdata.pushButton_agri.clicked.connect(lambda:InputDataBtn.load_agriculture(self))
        self.inputdata.pushButton_baer.clicked.connect(lambda:InputDataBtn.load_baer(self))
        self.inputdata.pushButton_cwe.clicked.connect(lambda:InputDataBtn.load_cwe(self))
        self.inputdata.pushButton_ran.clicked.connect(lambda:InputDataBtn.load_rangeland(self))
        self.inputdata.pushButton_lh.clicked.connect(lambda:InputDataBtn.load_luckhills(self))
        
        self.inputdata.lineEdit_project.clear()
        self.inputdata.pushButton.clicked.connect(lambda:InputDataBtn.select_output_folder(self))
  
        self.inputdata.lineEdit_DEM.clear()
        self.inputdata.pushButton_DEM.clicked.connect(lambda:InputDataBtn.select_dem(self))

        self.inputdata.lineEdit_crs.clear()
        self.inputdata.pushButton_crs.clicked.connect(lambda:InputDataBtn.select_crs(self))

        self.inputdata.lineEdit_soil.clear()
        self.inputdata.pushButton_soil.clicked.connect(lambda:InputDataBtn.select_soil(self))

        self.inputdata.lineEdit_soilDscp.clear()
        self.inputdata.pushButton_soilDscp.clicked.connect(lambda:InputDataBtn.select_soildscp(self))

        self.inputdata.lineEdit_soilDB.clear()
        self.inputdata.pushButton_soilDB.clicked.connect(lambda:InputDataBtn.select_soildb(self))

        self.inputdata.lineEdit_lc.clear()
        self.inputdata.pushButton_lc.clicked.connect(lambda:InputDataBtn.select_lc(self))

        self.inputdata.lineEdit_lcDscp.clear()
        self.inputdata.pushButton_lcDscp.clicked.connect(lambda:InputDataBtn.select_lcdscp(self))

        self.inputdata.lineEdit_lcDB.clear()
        self.inputdata.pushButton_lcDB.clicked.connect(lambda:InputDataBtn.select_lcdb(self))
        
        self.inputdata.label_2.setVisible(False)
        self.inputdata.lineEdit_project.setVisible(False)
        self.inputdata.pushButton.setVisible(False)

        self.inputdata.label_3.setVisible(False)
        self.inputdata.lineEdit_DEM.setVisible(False)
        self.inputdata.pushButton_DEM.setVisible(False)

        self.inputdata.label_6.setVisible(False)
        self.inputdata.lineEdit_crs.setVisible(False)
        self.inputdata.pushButton_crs.setVisible(False)
        
        self.inputdata.checkBox_soil.setVisible(False)
        self.inputdata.label_soil.setVisible(False)
        self.inputdata.lineEdit_soil.setVisible(False)
        self.inputdata.pushButton_soil.setVisible(False)
        
        self.inputdata.checkBox_lc.setVisible(False)
        self.inputdata.label_soilDscp.setVisible(False)
        self.inputdata.lineEdit_soilDscp.setVisible(False)
        self.inputdata.pushButton_soilDscp.setVisible(False)

        self.inputdata.label_soilDB.setVisible(False)
        self.inputdata.lineEdit_soilDB.setVisible(False)
        self.inputdata.pushButton_soilDB.setVisible(False)
        
        self.inputdata.label_lc.setVisible(False)
        self.inputdata.lineEdit_lc.setVisible(False)
        self.inputdata.pushButton_lc.setVisible(False)

        self.inputdata.label_lcDscp.setVisible(False)
        self.inputdata.lineEdit_lcDscp.setVisible(False)
        self.inputdata.pushButton_lcDscp.setVisible(False)

        self.inputdata.label_lcDB.setVisible(False)
        self.inputdata.lineEdit_lcDB.setVisible(False)
        self.inputdata.pushButton_lcDB.setVisible(False)

        self.inputdata.label_4.setVisible(False)
        self.inputdata.lineEdit_CSA.setVisible(False)
        self.inputdata.label_5.setVisible(False)
        self.inputdata.lineEdit_MSCL.setVisible(False)

        # Set for displayreport ui
        self.displayreport.pushButton_show.clicked.connect(lambda:DisplayReportBtn.show_report(self))    

        # Set for displaychart ui
        self.displaychart.pushButton_show.clicked.connect(lambda:DisplayChartBtn.show_chart(self))    
        self.displaychart.graphicsView.setBackground('w')

        # Set for outputanalysis ui
        self.outputanalysis.pushButton_vali.clicked.connect(lambda:OutputAnalysisBtn.show_vali(self))
        self.outputanalysis.graphicsView_analysis.setBackground('w')
        self.outputanalysis.label_rsq.setVisible(False)
        self.outputanalysis.label_nse.setVisible(False)
        self.outputanalysis.label_line.setVisible(False)

        # set for changetrvalue.ui
        self.changetrvalue.comboBox_TR.currentIndexChanged.connect(lambda: ChangeTRValueBtn.setTRvalue(self))

        # Set for batchprocessing.ui
        self.batchprocessing.button_box.button(QDialogButtonBox.Apply).clicked.connect(lambda:BatchBtn.batch_process(self))


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        return QCoreApplication.translate('QGeoWEPP', message)

    # set action
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
            parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action

    def initGui(self):
        #Input data
        icon_inputdata = os.path.join (self.plugin_dir, 'icons','inputdatabutton.png')
        action = self.add_action(
            icon_inputdata,
            text = self.tr(u'QGeoWEPP: Input data'),
            callback = lambda: InputDataBtn.inputdatabutton(self),
            parent = self.iface.mainWindow())
        
        # Add basemap
        icon_inputdata = os.path.join (self.plugin_dir, 'icons','basemapbutton.png')
        action = self.add_action(
            icon_inputdata,
            text = self.tr(u'QGeoWEPP: Add satellite basemap'),
            callback = lambda: AddBasemapBtn.addbasemapbutton(self),
            parent = self.iface.mainWindow())

        # Change CSA and MSCL
        icon_reset = os.path.join (self.plugin_dir, 'icons','changeCSA_MSCL.png')
        self.add_action(
            icon_reset,
            text = self.tr(u'QGeoWEPP: Reset CSA and MSCL'),
            callback = lambda: Reset_CSA_MSCLBtn.resetcsamsclbutton(self),
            parent = self.iface.mainWindow())
        
        # Select outlet
        icon_selectoutput = os.path.join (self.plugin_dir, 'icons','selectoutletbutton.png')
        self.selectOutletTool = SelectOutletTool(self)
        self.add_action(
            icon_selectoutput,
            text = self.tr(u'QGeoWEPP: Select outlet'),
            callback = lambda: SelectOutletBtn.selectoutletbutton(self),
            parent = self.iface.mainWindow())
        action.setCheckable(True)
        self.selectOutletTool.setAction(action)
        
        # Get erosion patterns
        icon_getresults = os.path.join (self.plugin_dir, 'icons','getresultsbutton.png')
        self.add_action(
            icon_getresults,
            text = self.tr(u'QGeoWEPP: Run WEPP'),
            callback = lambda: GetResultsBtn.getresultsbutton(self),
            parent = self.iface.mainWindow())
        
        # change target value
        icon_newtrvalue = os.path.join(self.plugin_dir, 'icons','newTRvalue.png')
        self.add_action(
            icon_newtrvalue,
            text = self.tr(u'QGeoWEPP: Change target value'),
            callback = lambda: ChangeTRValueBtn.changetrvaluebutton(self),
            parent = self.iface.mainWindow())
        
        
        # Display reports
        icon_displayreport = os.path.join (self.plugin_dir, 'icons', 'displayreportbutton.png')
        self.add_action(
            icon_displayreport,
            text = self.tr(u'Display reports'),
            callback = lambda: DisplayReportBtn.displayreportbutton(self),
            parent = self.iface.mainWindow())
        
        # Display charts
        icon_displaychart = os.path.join (self.plugin_dir, 'icons', 'displaychartbutton.png')
        self.add_action(
            icon_displaychart,
            text = self.tr(u'Display plots'),
            callback = lambda: DisplayChartBtn.displaychartbutton(self),
            parent = self.iface.mainWindow())
        
        # Output analysis
        icon_analysis = os.path.join (self.plugin_dir, 'icons', 'analysisbutton.png')
        self.add_action(
            icon_analysis,
            text = self.tr(u'Output analysis'),
            callback = lambda: OutputAnalysisBtn.outputanalysisbutton(self),
            parent = self.iface.mainWindow())
        
        # Identify hillslope parameters information
        icon_hillslopeinfo = os.path.join(self.plugin_dir, 'icons', 'infobutton.png')
        self.selectHillSlopeTool = SelectHillSlopeTool(self)
        self.add_action(
            icon_hillslopeinfo,
            text = self.tr(u'Identify hillslope parameters information'),
            callback = lambda: GetHillSlopeInfoBtn.gethillslopeinfobutton(self),
            parent = self.iface.mainWindow())
        action.setCheckable(True)
        self.selectHillSlopeTool.setAction(action)
 
        #Change hillslope parameters
        icon_changehillpara = os.path.join(self.plugin_dir, 'icons', 'changeparabutton.png')
        self.changeHillSlopeTool = ChangeHillSlopeTool(self)
        self.add_action(
            icon_changehillpara,
            text = self.tr(u'Change hillslope parameters'),
            callback = lambda: ChangeHillSlopeParaBtn.changehillslopeparabutton(self),
            parent = self.iface.mainWindow())
        action.setCheckable(True)
        self.changeHillSlopeTool.setAction(action)

        # Load a single hillslope to WEPP
        icon_hill2wepp = os.path.join(self.plugin_dir, 'icons', 'hillweppbutton.png')
        self.hilltoweppTool = HilltoWeppTool(self)
        self.add_action(
            icon_hill2wepp,
            text = self.tr(u'Load single hillslope to WEPP'),
            callback = lambda: LoadHilltoWeppBtn.loadhilltoweppbutton(self),
            parent = self.iface.mainWindow())
        action.setCheckable(True)
        self.hilltoweppTool.setAction(action)

        # Batch Processing for Soil Redistribution
        icon_batch = os.path.join (self.plugin_dir, 'icons','batchbutton.jpg')
        self.add_action(
            icon_batch,
            text = self.tr(u'Batch processing for soil redistribution'),
            callback = lambda: BatchBtn.batchbutton(self),
            parent=self.iface.mainWindow())
        
        # Save QGeoWEPP project
        icon_save = os.path.join (self.plugin_dir, 'icons','savebutton.png')
        self.add_action(
            icon_save,
            text = self.tr(u'Save QGeoWEPP project'),
            callback = lambda: SaveBtn.savebutton(self),
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QGeoWEPP '),
                action)
            self.iface.removeToolBarIcon(action)
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.selectOutletTool)
            self.iface.mapCanvas().unsetMapTool(self.selectHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.changeHillSlopeTool)
            self.iface.mapCanvas().unsetMapTool(self.hilltoweppTool)
        # remove the toolbar
        del self.toolbar
