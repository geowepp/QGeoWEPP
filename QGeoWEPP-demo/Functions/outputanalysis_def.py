# -*- coding: utf-8 -*-
"""
/***************************************************************************
Output Analysis
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
 *   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as        *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from qgis.core import QgsProject
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import os.path, os, glob, sys, numpy, pyqtgraph, pandas
from datetime import datetime
from .outputanalysis_dialog import outputanalysisDialog

class OutputAnalysisBtn():

    def __init__(self):
        self.plugin_dir = os.path.dirname(__file__)
        self.outputanalysis = outputanalysisDialog()

        self.outputanalysis.radioButton_precip.toggled.connect(lambda: OutputAnalysisBtn.show_vali(self))
        self.outputanalysis.radioButton_runoff.toggled.connect(lambda: OutputAnalysisBtn.show_vali(self))
        self.outputanalysis.radioButton_peak.toggled.connect(lambda: OutputAnalysisBtn.show_vali(self))
        self.outputanalysis.radioButton_sed.toggled.connect(lambda: OutputAnalysisBtn.show_vali(self))
    

    def linear_regreassion(observed, simulated):
        n = len(observed)
        observedmean = numpy.mean(observed)
        simulatedmean = numpy.mean(simulated)
        observed = numpy.array(observed)
        simulated = numpy.array(simulated)
        b1num = numpy.sum(simulated * observed) - n * observedmean * simulatedmean
        b1den =  numpy.sum(observed**2) - n * observedmean * simulatedmean
        slope = b1num / b1den
        angle = numpy.rad2deg(numpy.arctan(slope))
        intercept = float(simulatedmean - (slope * observedmean))
        return(slope, angle, intercept)
    

    def display_scatter(self, datesim, dateobs, valuesim, valueobs):
        try:
            self.displaychart.graphicsView.clear()
            # get wepp runoff dataframe
            simweppdf = pandas.DataFrame({'Date': datesim, 'WEPP': valuesim})
            obsdf = pandas.DataFrame({'Date': dateobs, 'Measured':  valueobs})

            # get a table of simulated and observed
            mergedf = pandas.merge(simweppdf, obsdf, on = 'Date')
            mergedf = mergedf.dropna()

            # select options
            option =  self.outputanalysis.comboBox_option.currentText()
            if option == 'Keep all simulated events':
                mergedf.drop(mergedf.index[mergedf['Measured'] == 0],inplace = True)
                mergedf.reset_index(drop=True, inplace=True)
            if option == 'Keep all observed events':
                mergedf.drop(mergedf.index[mergedf['WEPP'] == 0],inplace = True)
                mergedf.reset_index(drop=True, inplace=True)
            if option == 'Keep all events':
                pass

            # get x y limits for axes
            plotx = mergedf['Measured'].tolist()
            ploty = mergedf['WEPP'].tolist()
            if len(plotx) == 0 or len(ploty) == 0:
                msg = QMessageBox()
                msg.setText('Something goes wrong! Please try again!')
                msg.exec()
            limit = max(max(plotx), max(ploty)) * 1.1 
            scatter = pyqtgraph.ScatterPlotItem(plotx, ploty, symbol = 'o', pen = 'r', brush='r')  
            self.outputanalysis.graphicsView_analysis.addItem(scatter)
            self.outputanalysis.graphicsView_analysis.setXRange(0, limit)
            self.outputanalysis.graphicsView_analysis.setYRange(0, limit)

            # add regression line
            regline = pyqtgraph.InfiniteLine()
            slope, angle, intercept = OutputAnalysisBtn.linear_regreassion(plotx, ploty)
            regline.setAngle(angle)
            regline.setValue((0, intercept))
            regline.setPen(color = (0,0,0), widht = 1)
            self.outputanalysis.graphicsView_analysis.addItem(regline)
            self.outputanalysis.graphicsView_analysis.setLabel('left', 'Simulation')
            self.outputanalysis.graphicsView_analysis.setLabel('bottom', 'Observation')
            self.outputanalysis.graphicsView_analysis.getAxis('left').setTextPen(color = (0, 0, 0)) 
            self.outputanalysis.graphicsView_analysis.getAxis('bottom').setTextPen(color = (0, 0, 0)) 
            self.outputanalysis.graphicsView_analysis.getAxis('left').setStyle(stopAxisAtTick = (True, False))
            self.outputanalysis.graphicsView_analysis.getAxis('bottom').setStyle(stopAxisAtTick = (False, True))
        
            # set the plot to fixed size
            self.outputanalysis.graphicsView_analysis.setMouseEnabled(x = False, y = False)
        
            # calculate r-square and nse
            rsq = numpy.corrcoef(plotx, ploty)[0,1] ** 2
            nse = 1-(numpy.sum((numpy.array(ploty) - numpy.array(plotx))**2)/numpy.sum((plotx-numpy.mean(plotx))**2))
            self.outputanalysis.label_rsq.setText('R<sup>2</sup> = ' + format(rsq, '.3f'))
            self.outputanalysis.label_nse.setText('NSE = ' + format(nse, '.3f'))
            self.outputanalysis.label_line.setText('y = ' + format(slope, '.3f') + 'x + (' + format(intercept, '.3f') + ')')
            self.outputanalysis.label_rsq.setVisible(True)
            self.outputanalysis.label_nse.setVisible(True)
            self.outputanalysis.label_line.setVisible(True)
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
        
    def show_vali(self):
        try:
            self.outputanalysis.label_rsq.setVisible(False)
            self.outputanalysis.label_nse.setVisible(False)
            self.outputanalysis.label_line.setVisible(False)
            msg = QMessageBox()
            seletfile = QFileDialog.getOpenFileName(self.outputanalysis, "Select a txt file", "", "*.csv")
            record = str(seletfile[0])            
            if record == '': 
                return
                
            # get all variables from event file 
            rdem = QgsProject.instance().mapLayersByName('DEM')[0]
            foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 
            eventname = self.outputanalysis.comboBox_analysis.currentText()[:-7] + '_events.txt'
            eventpath = os.path.join(foldername, 'Reports', eventname)
            if os.path.exists(eventpath):
                firstyear = self.outputanalysis.lineEdit_year.text()
                if firstyear == '':
                    msg.setText('A start year is required.')
                    msg.exec()
                    return

                daywepp, monthwepp, yearwepp, precip, runoff, peak, sed = numpy.loadtxt(eventpath, dtype = 'int, int, int, float, float, float, float', skiprows=9, unpack = True) 
                yearwepp = yearwepp.tolist()   
                yearwepp = [int(firstyear) + yearwepp[i] - 1 for i in range(len(yearwepp))]
                runoffwepp = runoff.tolist()
                peakwepp = peak.tolist()
                sedwepp = sed.tolist()
            
                # calculate runoff and peak runoff in mm
                fwtr = os.path.join(foldername, 'subwtr.asc')
                wtrvalue = numpy.loadtxt(fwtr, skiprows = 6)
                cellnum = numpy.count_nonzero(wtrvalue != 0)
                fcell = os.path.join(foldername, 'cellsize.txt')
                cellsize = float(numpy.loadtxt(fcell))
                wtrarea = cellnum * cellsize * cellsize
                runoffwepp = [(pixel/wtrarea)*1000 for pixel in runoffwepp]
                peakwepp = [(pixel/wtrarea)*1000 for pixel in peakwepp]
                sedwepp = [pixel for pixel in sedwepp]

                # get date from input and wepp
                yearin, monthin, dayin, valuein = numpy.loadtxt(record, dtype = 'int, int, int, float', delimiter = ',', unpack=True)
                datewepp = []
                [datewepp.append(datetime(yearwepp[i], monthwepp[i], daywepp[i])) for i in range(len(yearwepp))]
                datein = []
                [datein.append(datetime(yearin[i], monthin[i], dayin[i])) for i in range(len(yearin))] 
                
                # display plot
                self.outputanalysis.graphicsView_analysis.clear()                 
                if self.outputanalysis.radioButton_runoff.isChecked() == True:
                   OutputAnalysisBtn.display_scatter(self, datewepp, datein, runoffwepp, valuein)
                if self.outputanalysis.radioButton_peak.isChecked() == True:
                   OutputAnalysisBtn.display_scatter(self, datewepp, datein, peakwepp, valuein)
                if self.outputanalysis.radioButton_sed.isChecked() == True:
                   OutputAnalysisBtn.display_scatter(self, datewepp, datein, sedwepp, valuein)
                    
            else:
                msg.setText('The file does not exist.')
                msg.exec()
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()       


    def outputanalysisbutton(self):
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
                self.outputanalysis.show()
                rdem = QgsProject.instance().mapLayersByName('DEM')[0]
                foldername = os.path.dirname(rdem.dataProvider().dataSourceUri()) 

                # add existed event output to the combobox
                eventfolder = os.path.join (foldername, 'Reports')
                eventfiles = glob.glob(os.path.join(eventfolder, '*.txt'))
                for file in eventfiles:
                    filename = os.path.basename(file)[:-4]
                    if filename[-6:] == 'events':
                        if self.outputanalysis.comboBox_analysis.findText(filename[:-7] + ' Events') == -1:
                            self.outputanalysis.comboBox_analysis.addItem(filename[:-7] + ' Events')  
        except:
            msg.setText('Oops!\n' + str(sys.exc_info()) + '\nPlease try again.')
            msg.exec()
