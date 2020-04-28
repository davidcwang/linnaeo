#!/usr/bin/python3

# Bioscience components
import Bio.Seq as Bseq
from Bio.Alphabet import generic_protein
from clustalo import clustalo

# PyQt components
from PyQt5.Qt import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QLabel

# Internal components
from ui import sherlock_ui
from ui import views

# Additional libraries
import os
import logging
import psutil

# TODO: Add functionality for removing sequences and alignments (from the dicts too)
# TODO: Add functionality for saving workspace.
# TODO: Add functionality for combining sequences into new alignments!


def _iterTreeView(root):
    """Internal function for iterating a TreeModel"""
    def recurse(parent):
        for row in range(parent.rowCount()):
            child=parent.child(row)
            yield child
            if child.hasChildren():
                yield from recurse(child)
    if root is not None:
        yield from recurse(root)


class Sherlock(QMainWindow, sherlock_ui.Ui_MainWindow):
    """ Main Window for Sherlock App """
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # Instantiation.
        # Dict:alignments --> {window ID : [all sequences]}
        # Dict:windows --> {window ID :
        self.mainProcess = psutil.Process(os.getpid())
        self.processTimer = QTimer()
        self.windex = -1
        self.alignments = {}
        self.windows = {}
        self.SequenceRole = Qt.UserRole + 1
        self.WindowRole = Qt.UserRole + 2
        self.mainLogger = logging.getLogger("Main")
        self.memLabel = QLabel("Memory Use: ")
        self.bioModel = QStandardItemModel()
        self.bioRoot = QStandardItem("Folder")
        self.projectModel = QStandardItemModel()
        self.projectRoot = QStandardItem("Folder")
        # Startup functions
        self.setupUi(self)
        self.guiInit()

        self.DEBUG()

    def updateUsage(self):
        mem = self.mainProcess.memory_info().rss/1000000
        cpu = self.mainProcess.cpu_percent()
        self.memLabel.setText("CPU: "+str(cpu)+" % | RAM: "+str(round(mem, 2))+" MB")

    def guiInit(self):
        """ Initialize GUI with default parameters. """
        # Tree setup
        self.bioTree.setModel(self.bioModel)
        self.bioModel.appendRow(self.bioRoot)
        self.bioTree.setExpanded(self.bioRoot.index(), True)
        self.bioModel.setHorizontalHeaderLabels(["Sequences"])
        self.projectTree.setModel(self.projectModel)
        self.projectModel.appendRow(self.projectRoot)
        self.projectTree.setExpanded(self.projectRoot.index(), True)
        self.projectModel.setHorizontalHeaderLabels(["Alignments"])

        # Status bar setup
        self.updateUsage()
        self.statusBar().addPermanentWidget(self.memLabel)
        self.processTimer.setInterval(2000)
        self.processTimer.start()

        # Slot connections
        self.processTimer.timeout.connect(self.updateUsage)
        self.bioTree.doubleClicked.connect(self.tryCreateAlignment)
        self.actionAlign.triggered.connect(self.tryCreateAlignment)
        self.projectTree.doubleClicked.connect(self.reopenWindow)
        #self.projectTree.dropEvent.connect(self.seqDropEvent)

    def seqDropEvent(self):
        """
        When dropping either a separate window or sequence onto either another
        sequence or another alignment window, it creates a new window using all unique components
        """

    def tryCreateAlignment(self):
        """
        This will create a new alignment from the currently selected sequences in top Tree.
        Ignores any folders that were included in the selection.
        Will not duplicate alignments. Creates a new window if alignment is new.
        """
        items = {}
        for index in self.bioTree.selectedIndexes():
            # Quick and dirty way to ignore folders that are selected:
            # Only does the thing if there is a sequence present in the node.
            if self.bioModel.itemFromIndex(index).data(role=self.SequenceRole):
                items[self.bioModel.itemFromIndex(index).text()] = \
                    str(self.bioModel.itemFromIndex(index).data(role=self.SequenceRole))
            else:
                self.mainStatus.showMessage("Not including selected folder \"" +
                                            self.bioModel.itemFromIndex(index).text() + "\"",
                                            msecs=5000)
                continue

        # Check if the two sequences have been aligned before.
        # If not, align with ClustalO and create a new window from the alignment.
        # If so, provide focus to that window.
        seqs = list(items.values())
        if len(seqs) > 1:
            seqs.sort()
        if items and seqs not in self.alignments.values():
            # create new unique identifier for tracking alignment!
            self.windex += 1
            wid = str(self.windex)
            self.mainLogger.debug("Alignment stored with ID " + wid + " and sequence(s) "
                                  + str([x[:10]+'..'+x[-10:] for x in seqs]))
            self.alignments[wid] = seqs

            # TODO: have this form a new thread (probably necessary for long alignments)
            aligned = clustalo(items)
            self.mainLogger.debug("Sending alignment to clustal omega using default options (1 core, protein seq)")
            self.mainStatus.showMessage("Aligning selection...", msecs=1000)
            self.makeNewWindow(aligned, wid)
        else:
            self.mainStatus.showMessage("Reopening alignment!", msecs=1000)
            for key, value in self.alignments.items():
                if seqs == value:
                    self.reopenWindow(windowID=key)

    def makeNewWindow(self, ali, windowID):
        # TODO: don't add single sequences to the project pane!
        sub = views.MDISubWindow()
        sub.setAttribute(Qt.WA_DeleteOnClose, False)
        widget = views.AlignSubWindow(ali)

        sub.setWidget(widget)

        # Show window in the view panel
        self.mdiArea.addSubWindow(sub)
        self.windows[windowID] = sub
        if len(ali.keys()) > 1:
            node = QStandardItem(sub.windowTitle())
            node.setData(windowID, self.WindowRole)
            self.projectRoot.appendRow(node)
        else:
            sub.setWindowTitle(list(ali.keys())[0])
        sub.show()

    def reopenWindow(self, windowID=None):
        """
        Checks to see if a window is open already.
        If it is not, reopens the window. If it is, gives focus.
        Also refreshes the title.
        """
        # TODO: consider returning a try:catch here...
        if isinstance(windowID, str):
            # if WindowID is a string, that means it was sent by a deliberate search.
            sub = self.windows[windowID]
        else:
            # if not string it should be a QModelIndex (from selection? Not sure how that works...)
            item = self.projectModel.itemFromIndex(windowID)
            sub = self.windows[item.data(role=self.WindowRole)]
            sub.setWindowTitle(item.text())
        #sub.widget().seqArrange()
        if not sub.isVisible():
            sub.show()
        self.mdiArea.setActiveSubWindow(sub)


    # INITIAL TESTING DATA
    # Builds a basic tree model for testing.
    def DEBUG(self):
        test1 = ['GPI1A', 'MSLSQDATFVELKRHVEANEKDAQLLELFEKDPARFEKFTRLFATPDGDFLFDF'+
                 'SKNRITDESFQLLMRLAKSRGVEESRNAMFSAEKINFTENRAVLHVALRNRANRP'+
                 'ILVDGKDVMPDVNRVLAHMKEFCNEIISGSWTGYTGKKITDVVNIGIGGSDLGPL'+
                 'MVTESLKNYQIGPNVHFVSNVDGTHVAEVTKKLNAETTLFIIASKTFTTQETITN'+
                 'AETAKEWFLAKAGDAGAVAKHFVALSTNVTKAVEFGIDEKNMFEFWDWVGGRYSL'+
                 'WSAIGLSIAVHIGFDNYEKLLDGAFSVDEHFVNTPLEKNIPVILAMIGVLYNNIY'+
                 'GAETHALLPYDQYMHRFAAYFQQGDMESNGKFVTRHGQRVDYSTGPIVWGEPGTN'+
                 'GQHAFYQLIHQGTRLIPADFIAPVKTLNPIRGGLHHQILLANFLAQTEALMKGKT'+
                 'AAVAEAELKSSGMSPESIAKILPHKVFEGNKPTTSIVLPVVTPFTLGALIAFYEH'+
                 'KIFVQGIIWDICSYDQWGVELGKQLAKVIQPELASADTVTSHDASTNGLIAFIKNNA']
        seq_GPI1A = Bseq.MutableSeq(test1[1], generic_protein)
        test1alt = [test1[0], seq_GPI1A]
        test2 = ['GPI1B', 'MIFELFRFIFRKKKMLGYLSDLIGTLFIGDSTEKAMSLSQDATFVELKRHVEANE'+
                 'KDAQLLELFEKDPARFEKFTRLFATPDGDFLFDFSKNRITDESFQLLMRLAKSRG'+
                 'VEESRNAMFSAEKINFTENRAVLHVALRNRANRPILVDGKDVMPDVNRVLAHMKE'+
                 'FCNEIISGSWTGYTGKKITDVVNIGIGGSDLGPLMVTESLKNYQIGPNVHFVSNV'+
                 'DGTHVAEVTKKLNAETTLFIIASKTFTTQETITNAETAKEWFLAKAGDAGAVAKH'+
                 'FVALSTNVTKAVEFGIDEKNMFEFWDWVGGRYSLWSAIGLSIAVHIGFDNYEKLL'+
                 'DGAFSVDEHFVNTPLEKNIPVILAMIGVLYNNIYGAETHALLPYDQYMHRFAAYF'+
                 'QQGDMESNGKFVTRHGQRVDYSTGPIVWGEPGTNGQHAFYQLIHQGTRLIPADFI'+
                 'APVKTLNPIRGGLHHQILLANFLAQTEALMKGKTAAVAEAELKSSGMSPESIAKI'+
                 'LPHKVFEGNKPTTSIVLPVVTPFTLGALIAFYEHKIFVQGIIWDICSYDQWGVEL'+
                 'GKQLAKVIQPELASADTVTSHDASTNGLIAFIKNNA']
        seq_GPI1B = Bseq.MutableSeq(test2[1], generic_protein)
        test2alt = [test2[0], seq_GPI1B]
        test = [test1alt, test2alt]
        for i in list(range(0, len(test))):
            #node = models.SeqNode(test[i][0], sequence=test[i][1])
            node = QStandardItem(test[i][0])
            node.setData(test[i][1], self.SequenceRole)
            node.setFlags(node.flags() ^ Qt.ItemIsDropEnabled)
            self.bioRoot.appendRow(node)

        """
        # SAVED THIS FOR LATER!
        # Read in config (linux)
        config = configparser.ConfigParser()
        try:
            config.read(str(Path.home())+"/.sherlock/config.ini")
            # Open last used workspace automatically.
            if config['RECENTS']['LAST'] != "":
                last = config['RECENTS']['LAST']
                f = QFile(last)
                f.open(QIODevice.ReadOnly)
                model = workspace.WorkspaceModel()
                f.close()
                self.workspaceTree.setModel(model)
        except:
            print("No config file found!")
            """
