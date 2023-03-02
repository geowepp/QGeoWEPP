# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGeoWEPP
                                 A QGIS plugin
 GeoWEPP (Geo-spatial interface of WEPP) for QGIS
                             -------------------
        begin                : 2021-6-11
        copyright            : (C) 2022 by Han Zhang, Chris S. Renschler
        email                : support@geowepp.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory():  
    """Load QGeoWEPP class from file QGeoWEPP.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    
