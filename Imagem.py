# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Imagem
                                 A QGIS plugin
 Plugin para procedimento tais.básico de processamento de imagens digi
                              -------------------
        begin                : 2018-11-16
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Joyce Raymundo
        email                : joycerd.silva@gmail.com
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
from PyQt4.QtCore import*
from PyQt4.QtGui import*
from qgis.core import*
from qgis.gui import*
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Imagem_dialog import ImagemDialog
import os.path
import qgis.utils
import glob
import os.path
import numpy as np
import os
import math
from osgeo import gdal
import osr
import pyproj
import processing
class Imagem:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Imagem_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg = ImagemDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&IMAGE PROCESSOR')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Imagem')
        self.toolbar.setObjectName(u'Imagem')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Imagem', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = ImagemDialog()

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
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Imagem/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PDI'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg.caminho.clear()
        self.dlg.ponto2.clear()
        self.dlg.pushButton.clicked.connect(self.selecionar_saida) #conectando o botão para salvar o ponto1
        self.dlg.pushButton_2.clicked.connect(self.salvar_ponto2) #conectando o botão para salvar o ponto 2.


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&IMAGE PROCESSOR'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #Abaixo a função para que s eposso salvar os vetores de ponto 1 e 2.
    def selecionar_saida(self):
        arquivoCaminho = QFileDialog.getSaveFileName(self.dlg, "Salvar o arquivo em: ", "", "*.shp")
        self.dlg.caminho.setText(arquivoCaminho)

    def salvar_ponto2(self):
        ponto2_caminho = QFileDialog.getSaveFileName(self.dlg, "Salvar o arquivo em: ", "", "*.shp")
        self.dlg.ponto2.setText(ponto2_caminho)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop

        self.dlg.show()
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
           self.dlg.show()
           #atribuir função as janelas do qt4
           imagens = self.dlg.mMapLayerComboBox.currentLayer()
           latitude= self.dlg.lineEdit.text() #inserir valor da latitude
           longitude= self.dlg.lineEdit_2.text() #inserir valor da longitude
           latitude2= self.dlg.lineEdit_3.text() #inserir valor da latitude2
           longitude2= self.dlg.lineEdit_4.text() #inserir valor da longitude2
           projecao= self.dlg.lineEdit_5.text() #inserir o EPSG da projeção
           localSalvo = self.dlg.caminho.text() #inserir o caminho para salvar ponto 1
           localSalvo2 = self.dlg.ponto2.text() #inserir o caminho para salvar o ponto 2.
           latitudedist=float(latitude) #transformando em float
           longitudedist=float(longitude) #transformando em float
           latitude2dist=float(latitude2) #transformando em float
           longitude2dist=float(longitude2) #transformando em float

           #Cálculo de distância euclidiana entre os 2 pontos coletados na imagem em .m

           a= np.array((latitudedist,longitudedist))
           b = np.array((latitude2dist, longitude2dist))
           dist = np.linalg.norm(a-b)
           self.dlg.distancia.setValue(dist)

           #configurando o QSlider para definir valor do contraste

           self.dlg.sl.setMinimum(0)
           self.dlg.sl.setMaximum(255)
           contraste = self.dlg.sl.value()

           #abaixo o código para ler a imagem no maplayer e adicionar o contraste e em seguida exibir no Qgis
           #selecionada= QgsMapLayerRegistry.instance().mapLayersByName(imagens)[0]
           contrastFilter=QgsBrightnessContrastFilter()
           contrastFilter.setContrast(float(contraste))
           imagens.pipe().set(contrastFilter)
           imagens.triggerRepaint()

           #modificando o nome do layer após alteração
        if contraste is not 0:
            for imagens in QgsMapLayerRegistry.instance().mapLayers().values():
                imagens.setLayerName('contraste_mod')
        else:
            imagens.setLayerName('Original')
            QgsMapLayerRegistry.instance().addMapLayer(imagens)

        # Verificando a extensão da imagem em X e Y

        if imagens is not None:

            xsize = imagens.rasterUnitsPerPixelX()
            ysize = imagens.rasterUnitsPerPixelY()

            extent = imagens.extent()

            # obtendo as cordenadas de tamanho da imagem na correspondente unidadee desta.
            ymax = extent.yMaximum()
            ymin=extent.yMinimum()
            xmax = extent.xMaximum()
            xmin = extent.xMinimum()
            self.dlg.xmax.setText(str(xmax))
            self.dlg.xmin.setText(str(xmin))
            self.dlg.ymax.setText(str(ymax))
            self.dlg.ymin.setText(str(ymin))


            #transformando as coordenadas do ponto 1 em coordenada linha x coluna

            t= ymax - longitudedist
            v= latitudedist - xmin

            row = int((t/ ysize) + 1)
            column = int((v / xsize) + 1)
            self.dlg.linhas.setText(str(row))
            self.dlg.colunas.setText(str(column))

            #transformando as coordenadas do ponto 2 em coordenada linha x coluna

            t1= ymax - longitude2dist
            v1= latitude2dist - xmin

            row = int((t1/ ysize) + 1)
            column = int((v1/ xsize) + 1)
            self.dlg.linhas2.setText(str(row))
            self.dlg.colunas2.setText(str(column))


           #abaixo será criado o ponto 1
            camada = QgsVectorLayer('Point?crs=epsg:'+projecao, 'PONTO 1' , 'memory')
            pr = camada.dataProvider()
            ponto = QgsPoint(float(latitude),float(longitude))
            pt= QgsFeature()
            pt.setGeometry(QgsGeometry.fromPoint(ponto))
            pr.addFeatures([pt])
            camada.updateExtents()
            QgsMapLayerRegistry.instance().addMapLayers([camada])
            properties = {'size': '2.0', 'red': '255,0,0'}
            symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)
            camada.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)
            canvas = self.iface.mapCanvas()
            extent = camada.extent()
            canvas.setExtent(extent)

           #abaixo será criado o ponto 2
            camada2 = QgsVectorLayer('Point?crs=epsg:'+projecao, 'PONTO 2' , 'memory')
            pr2 = camada2.dataProvider()
            ponto2 = QgsPoint(float(latitude2),float(longitude2))
            pt2= QgsFeature()
            pt2.setGeometry(QgsGeometry.fromPoint(ponto2))
            pr2.addFeatures([pt2])
            camada2.updateExtents()
            QgsMapLayerRegistry.instance().addMapLayers([camada2])
            properties2 = {'size': '2.0', 'green': '0,255,0'}
            symbol2_layer = QgsSimpleMarkerSymbolLayerV2.create(properties2)
            camada2.rendererV2().symbols()[0].changeSymbolLayer(0, symbol2_layer)
            canvas2 = self.iface.mapCanvas()
            extent2 = camada2.extent()
            canvas.setExtent(extent2)

            #recrevendo todos arquivos vetores gerados para serem salvos em uma pasta selecionada.

            QgsVectorFileWriter.writeAsVectorFormat(camada, localSalvo, "utf_8_encode", camada.crs(), "ESRI Shapefile")
            pnt_layer = QgsVectorLayer(localSalvo, "Ponto B2E", "ogr")
            QgsVectorFileWriter.writeAsVectorFormat(camada2, localSalvo2, "utf_8_encode", camada2.crs(), "ESRI Shapefile")
            pnt_layer2 = QgsVectorLayer(localSalvo2, "Ponto B2E", "ogr")
