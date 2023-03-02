# -*- coding: utf-8 -*-
"""
/***************************************************************************
Display Chart
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
import os.path, os, glob, sys, numpy, pyqtgraph
from .displaychart_dialog import displaychartDialog

class DisplayChartBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.displaychart = displaychartDialog()

        self.displaychart.radioButton_precip.toggled.connect(lambda: DisplayChartBtn.show_chart(self))
        self.displaychart.radioButton_runoff.toggled.connect(lambda: DisplayChartBtn.show_chart(self))
        self.displaychart.radioButton_peak.toggled.connect(lambda: DisplayChartBtn.show_chart(self))
        self.displaychart.radioButton_sed.toggled.connect(lambda: DisplayChartBtn.show_chart(self))
    
    def show_chart(self):
        try:
            msg = QMessageBox()
            # get all variables from event file
            rdem = QgsProject.instance().mapLayersByName('DEM')[0]
            foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 
            eventname = self.displaychart.comboBox_chart.currentText()[:-7] + '_events.txt'
            eventpath = os.path.join(foldername, 'Reports', eventname)
            if os.path.exists(eventpath):
                precip, runoff, peak, sed = numpy.loadtxt(eventpath, skiprows=9, usecols = range(3,7), unpack = True)
                precip = precip.tolist()
                runoff = runoff.tolist()
                peak = peak.tolist()
                sed = sed.tolist()
                numofday = []
                for num in range(len(precip)):
                    numofday.append(num + 1)
                
                # calculate runoff and peak runoff in mm
                fwtr = os.path.join(foldername, 'subwtr.asc')
                wtrvalue = numpy.loadtxt(fwtr, skiprows = 6)
                cellnum = numpy.count_nonzero(wtrvalue != 0)

                fcell = os.path.join(foldername, 'cellsize.txt')
                cellsize = float(numpy.loadtxt(fcell))
                wtrarea = cellnum * cellsize
                runoff = [pixel/wtrarea*100 for pixel in runoff]
                peak = [pixel/wtrarea*100 for pixel in peak]

                self.displaychart.graphicsView.clear()
                # display plot
                if self.displaychart.radioButton_precip.isChecked() == True:  
                    plotprecip = pyqtgraph.PlotDataItem(numofday, precip, pen = pyqtgraph.mkPen('b', width = 2), name = 'Precipitation (mm)', hoverable = True)
                    legend = self.displaychart.graphicsView.addLegend() 
                    legend.setOffset(1)
                    legend.setLabelTextColor(0, 0, 0)
                    self.displaychart.graphicsView.addItem(plotprecip)
                    self.displaychart.graphicsView.setLabel('left', 'Precipitation (mm)', unit = 'mm')
                    self.displaychart.graphicsView.setLabel('bottom', 'Days in Simulation')     
                    self.displaychart.graphicsView.getAxis('left').setTextPen(color = (0, 0, 0)) 
                    self.displaychart.graphicsView.getAxis('bottom').setTextPen(color = (0, 0, 0))     
                if self.displaychart.radioButton_runoff.isChecked() == True:
                    plotrunoff = pyqtgraph.PlotDataItem(numofday, runoff, pen = pyqtgraph.mkPen('b', width = 2), name = 'Runoff (mm)')
                    legend = self.displaychart.graphicsView.addLegend() 
                    legend.setOffset(1)
                    legend.setLabelTextColor(0, 0, 0)
                    self.displaychart.graphicsView.addItem(plotrunoff)
                    self.displaychart.graphicsView.setLabel('left', 'Runoff (mm)', unit = 'mm')
                    self.displaychart.graphicsView.setLabel('bottom', 'Day of Simulation')
                    self.displaychart.graphicsView.getAxis('left').setTextPen(color = (0, 0, 0)) 
                    self.displaychart.graphicsView.getAxis('bottom').setTextPen(color = (0, 0, 0))     
                if self.displaychart.radioButton_peak.isChecked() == True:
                    plotpeak = pyqtgraph.PlotDataItem(numofday, peak, pen = pyqtgraph.mkPen('b', width = 2), name = 'Peak Runoff (mm/s)')
                    legend = self.displaychart.graphicsView.addLegend()
                    legend.setOffset(1)
                    legend.setLabelTextColor(0, 0, 0)
                    self.displaychart.graphicsView.addItem(plotpeak)
                    self.displaychart.graphicsView.setLabel('left', 'Peak Runoff (mm/s)', unit = 'mm/s')
                    self.displaychart.graphicsView.setLabel('bottom', 'Day of Simulation')
                    self.displaychart.graphicsView.getAxis('left').setTextPen(color = (0, 0, 0)) 
                    self.displaychart.graphicsView.getAxis('bottom').setTextPen(color = (0, 0, 0))   
                if self.displaychart.radioButton_sed.isChecked() == True:
                    plotsed = pyqtgraph.PlotDataItem(numofday, sed, pen = pyqtgraph.mkPen('b', width = 2), name = 'Sediment Yield (kg)')
                    legend = self.displaychart.graphicsView.addLegend()
                    legend.setOffset(1)
                    legend.setLabelTextColor(0, 0, 0)
                    self.displaychart.graphicsView.addItem(plotsed)
                    self.displaychart.graphicsView.setLabel('left', 'Sediment Yield (kg)', unit = 'kg')
                    self.displaychart.graphicsView.setLabel('bottom', 'Day of Simulation')
                    self.displaychart.graphicsView.getAxis('left').setTextPen(color = (0, 0, 0)) 
                    self.displaychart.graphicsView.getAxis('bottom').setTextPen(color = (0, 0, 0))  
            else:
                msg.setText('The file does not exist.')
                msg.exec()
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()    


    def displaychartbutton(self):
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
                self.displaychart.show()
                rdem = QgsProject.instance().mapLayersByName('DEM')[0]
                foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 

                # add existed event output to the combobox
                eventfolder = os.path.join (foldername, 'Reports')
                eventfiles = glob.glob(os.path.join(eventfolder, '*.txt'))
                for file in eventfiles:
                    filename = os.path.basename(file)[:-4]
                    if filename[-6:] == 'events':
                        if self.displaychart.comboBox_chart.findText(filename[:-7] + ' Events') == -1:
                            self.displaychart.comboBox_chart.addItem(filename[:-7] + ' Events')  
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
