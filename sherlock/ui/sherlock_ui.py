# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sherlock.ui'
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
        self.widget_3 = QtWidgets.QWidget(self.splitter_2)
        self.widget_3.setObjectName("widget_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget_3)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 1)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.bioTree = QtWidgets.QTreeView(self.widget_3)
        self.bioTree.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.bioTree.setDragEnabled(True)
        self.bioTree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.bioTree.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.bioTree.setAlternatingRowColors(False)
        self.bioTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.bioTree.setAutoExpandDelay(0)
        self.bioTree.setWordWrap(False)
        self.bioTree.setObjectName("bioTree")
        self.gridLayout_4.addWidget(self.bioTree, 0, 0, 1, 1)
        self.widget_4 = QtWidgets.QWidget(self.splitter_2)
        self.widget_4.setObjectName("widget_4")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.widget_4)
        self.gridLayout_5.setContentsMargins(0, 1, 0, 0)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.projectTree = QtWidgets.QTreeView(self.widget_4)
        self.projectTree.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.projectTree.setDragEnabled(True)
        self.projectTree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.projectTree.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.projectTree.setAlternatingRowColors(False)
        self.projectTree.setAutoExpandDelay(0)
        self.projectTree.setObjectName("projectTree")
        self.gridLayout_5.addWidget(self.projectTree, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.splitter_2, 0, 0, 1, 1)
        self.mdiWidget = QtWidgets.QWidget(self.splitter)
        self.mdiWidget.setObjectName("mdiWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.mdiWidget)
        self.gridLayout_2.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.mainMenu = QtWidgets.QMenuBar(MainWindow)
        self.mainMenu.setGeometry(QtCore.QRect(0, 0, 807, 24))
        self.mainMenu.setObjectName("mainMenu")
        self.menuFile = QtWidgets.QMenu(self.mainMenu)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QtWidgets.QMenu(self.menuFile)
        self.menuImport.setObjectName("menuImport")
        self.menuExport = QtWidgets.QMenu(self.menuFile)
        self.menuExport.setObjectName("menuExport")
        self.menuHelp = QtWidgets.QMenu(self.mainMenu)
        self.menuHelp.setObjectName("menuHelp")
        self.menuWindow = QtWidgets.QMenu(self.mainMenu)
        self.menuWindow.setObjectName("menuWindow")
        self.menuEdit = QtWidgets.QMenu(self.mainMenu)
        self.menuEdit.setObjectName("menuEdit")
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
        self.actionWorkspace = QtWidgets.QAction(MainWindow)
        self.actionWorkspace.setObjectName("actionWorkspace")
        self.actionAlignment = QtWidgets.QAction(MainWindow)
        self.actionAlignment.setObjectName("actionAlignment")
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
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
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
        self.menuFile.addAction(self.actionClose)
        self.mainMenu.addAction(self.menuFile.menuAction())
        self.mainMenu.addAction(self.menuEdit.menuAction())
        self.mainMenu.addAction(self.menuWindow.menuAction())
        self.mainMenu.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionAlign)

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
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionAlign.setText(_translate("MainWindow", "Align"))
        self.actionAlign.setToolTip(_translate("MainWindow", "Align the selected sequences"))
        self.actionAlign.setShortcut(_translate("MainWindow", "Ctrl+Alt+A"))
        self.actionOpen.setText(_translate("MainWindow", "Open Set"))
        self.actionSave.setText(_translate("MainWindow", "Save Set"))
        self.actionFasta.setText(_translate("MainWindow", "Fasta"))
        self.actionWorkspace.setText(_translate("MainWindow", "Workspace"))
        self.actionAlignment.setText(_translate("MainWindow", "Sequence"))
        self.actionNew.setText(_translate("MainWindow", "New Set"))
        self.actionAdd.setText(_translate("MainWindow", "Add Sequence"))
        self.actionClustal.setText(_translate("MainWindow", "Clustal"))
        self.actionSequence.setText(_translate("MainWindow", "Sequence"))
        self.actionAlignment_2.setText(_translate("MainWindow", "Alignment"))
        self.actionClose.setText(_translate("MainWindow", "Quit"))