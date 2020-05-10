# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/linnaeo.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(807, 636)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_3.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter_2 = QtWidgets.QSplitter(self.widget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.gridLayout_3.addWidget(self.splitter_2, 0, 0, 1, 1)
        self.mdiWidget = QtWidgets.QWidget(self.splitter)
        self.mdiWidget.setObjectName("mdiWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.mdiWidget)
        self.gridLayout_2.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.mainMenu = QtWidgets.QMenuBar(MainWindow)
        self.mainMenu.setGeometry(QtCore.QRect(0, 0, 807, 20))
        self.mainMenu.setObjectName("mainMenu")
        self.menuFile = QtWidgets.QMenu(self.mainMenu)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QtWidgets.QMenu(self.menuFile)
        self.menuImport.setEnabled(False)
        self.menuImport.setObjectName("menuImport")
        self.menuExport = QtWidgets.QMenu(self.menuFile)
        self.menuExport.setEnabled(False)
        self.menuExport.setObjectName("menuExport")
        self.menuHelp = QtWidgets.QMenu(self.mainMenu)
        self.menuHelp.setObjectName("menuHelp")
        self.menuWindow = QtWidgets.QMenu(self.mainMenu)
        self.menuWindow.setObjectName("menuWindow")
        self.menuEdit = QtWidgets.QMenu(self.mainMenu)
        self.menuEdit.setObjectName("menuEdit")
        self.menuActions = QtWidgets.QMenu(self.mainMenu)
        self.menuActions.setObjectName("menuActions")
        MainWindow.setMenuBar(self.mainMenu)
        self.mainStatus = QtWidgets.QStatusBar(MainWindow)
        self.mainStatus.setObjectName("mainStatus")
        MainWindow.setStatusBar(self.mainStatus)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionAlign = QtWidgets.QAction(MainWindow)
        self.actionAlign.setObjectName("actionAlign")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionFasta = QtWidgets.QAction(MainWindow)
        self.actionFasta.setObjectName("actionFasta")
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionAdd = QtWidgets.QAction(MainWindow)
        self.actionAdd.setObjectName("actionAdd")
        self.actionClustal = QtWidgets.QAction(MainWindow)
        self.actionClustal.setObjectName("actionClustal")
        self.actionSequence = QtWidgets.QAction(MainWindow)
        self.actionSequence.setObjectName("actionSequence")
        self.actionAlignment_2 = QtWidgets.QAction(MainWindow)
        self.actionAlignment_2.setObjectName("actionAlignment_2")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionNewFolder = QtWidgets.QAction(MainWindow)
        self.actionNewFolder.setObjectName("actionNewFolder")
        self.actionDelete = QtWidgets.QAction(MainWindow)
        self.actionDelete.setObjectName("actionDelete")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionToggle_Tabs = QtWidgets.QAction(MainWindow)
        self.actionToggle_Tabs.setObjectName("actionToggle_Tabs")
        self.actionClose_all = QtWidgets.QAction(MainWindow)
        self.actionClose_all.setObjectName("actionClose_all")
        self.actionCascade = QtWidgets.QAction(MainWindow)
        self.actionCascade.setObjectName("actionCascade")
        self.actionTile = QtWidgets.QAction(MainWindow)
        self.actionTile.setObjectName("actionTile")
        self.actionSorry_no_help_available = QtWidgets.QAction(MainWindow)
        self.actionSorry_no_help_available.setObjectName("actionSorry_no_help_available")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionTrees = QtWidgets.QAction(MainWindow)
        self.actionTrees.setObjectName("actionTrees")
        self.menuImport.addAction(self.actionFasta)
        self.menuImport.addAction(self.actionClustal)
        self.menuExport.addAction(self.actionSequence)
        self.menuExport.addAction(self.actionAlignment_2)
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionAdd)
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.menuExport.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionSorry_no_help_available)
        self.menuWindow.addAction(self.actionTile)
        self.menuWindow.addAction(self.actionCascade)
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.actionToggle_Tabs)
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.actionClose)
        self.menuWindow.addAction(self.actionClose_all)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)
        self.menuActions.addAction(self.actionAlign)
        self.menuActions.addAction(self.actionNewFolder)
        self.menuActions.addSeparator()
        self.menuActions.addAction(self.actionDelete)
        self.mainMenu.addAction(self.menuFile.menuAction())
        self.mainMenu.addAction(self.menuEdit.menuAction())
        self.mainMenu.addAction(self.menuActions.menuAction())
        self.mainMenu.addAction(self.menuWindow.menuAction())
        self.mainMenu.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionAlign)
        self.toolBar.addAction(self.actionNewFolder)
        self.toolBar.addAction(self.actionDelete)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionTrees)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuImport.setTitle(_translate("MainWindow", "Import"))
        self.menuExport.setTitle(_translate("MainWindow", "Export"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuWindow.setTitle(_translate("MainWindow", "Window"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuActions.setTitle(_translate("MainWindow", "Tools"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionAlign.setText(_translate("MainWindow", "Align"))
        self.actionAlign.setToolTip(_translate("MainWindow", "Align the selected sequences"))
        self.actionAlign.setShortcut(_translate("MainWindow", "Ctrl+Return"))
        self.actionOpen.setText(_translate("MainWindow", "Open Workspace"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Save Workspace"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionFasta.setText(_translate("MainWindow", "Fasta Alignment"))
        self.actionNew.setText(_translate("MainWindow", "New Workspace"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionAdd.setText(_translate("MainWindow", "Add Sequence"))
        self.actionAdd.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.actionClustal.setText(_translate("MainWindow", "Clustal Alignment"))
        self.actionSequence.setText(_translate("MainWindow", "Sequence"))
        self.actionAlignment_2.setText(_translate("MainWindow", "Alignment"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.actionNewFolder.setText(_translate("MainWindow", "Add Folder"))
        self.actionNewFolder.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionDelete.setText(_translate("MainWindow", "Delete"))
        self.actionDelete.setToolTip(_translate("MainWindow", "Remove from Tree"))
        self.actionDelete.setShortcut(_translate("MainWindow", "Del"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setShortcut(_translate("MainWindow", "Ctrl+C"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionPaste.setShortcut(_translate("MainWindow", "Ctrl+V"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionPreferences.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.actionToggle_Tabs.setText(_translate("MainWindow", "Toggle Tab Mode"))
        self.actionToggle_Tabs.setShortcut(_translate("MainWindow", "Ctrl+T"))
        self.actionClose_all.setText(_translate("MainWindow", "Close all"))
        self.actionClose_all.setShortcut(_translate("MainWindow", "Ctrl+Shift+W"))
        self.actionCascade.setText(_translate("MainWindow", "Cascade"))
        self.actionTile.setText(_translate("MainWindow", "Tile"))
        self.actionSorry_no_help_available.setText(_translate("MainWindow", "Sorry, no help available!"))
        self.actionClose.setText(_translate("MainWindow", "Close"))
        self.actionTrees.setText(_translate("MainWindow", "Trees"))
