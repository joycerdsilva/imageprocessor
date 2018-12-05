# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Imagem
                                 A QGIS plugin
 Plugin para procedimento tais.básico de processamento de imagens digi
                             -------------------
        begin                : 2018-11-16
        copyright            : (C) 2018 by Joyce Raymundo
        email                : joycerd.silva@gmail.com
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Imagem class from file Imagem.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .Imagem import Imagem
    return Imagem(iface)
