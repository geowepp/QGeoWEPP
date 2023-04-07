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
 *   it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as        *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QGeoWEPP class from file QGeoWEPP.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgeowepp import QGeoWEPP
    return QGeoWEPP(iface)
