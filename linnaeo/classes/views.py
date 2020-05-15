#!/usr/bin/python3
import logging
import sys
from math import trunc

import Bio
from PyQt5.QtGui import QStandardItemModel, QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, \
    QTextCursor, QFontMetricsF
from PyQt5.QtWidgets import QWidget, QMdiSubWindow, QMdiArea, QTabBar, QTreeView, QSizePolicy, QAbstractItemView, \
    QDialog, QDialogButtonBox, QMainWindow, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRegExp, QRegularExpression, QTimer, QEvent, QObject
from PyQt5.uic.properties import QtGui

from linnaeo.ui import alignment_ui, quit_ui
from linnaeo.resources import linnaeo_rc
import textwrap as tw

from linnaeo.classes import utilities



class LinnaeoApp(QApplication):
    barClick = pyqtSignal()

    def __init__(self, *args):
        print("INITIALIZING APP")
        super().__init__(*args)
        self.installEventFilter(self)
        #self.barClick.connect(self.setSizing)
        self._window = None

    def eventFilter(self, obj, event):
        #print(event, event.type())
        if event.type() == 214:
            self.barClick.emit()
        elif event.type() == 174 or event.type() == 175:
            self.barClick.emit()

        return super().eventFilter(obj, event)

    #def setSizing(self):
    #    if self._window:
    #        if not self._window.beingClicked:
    #            print("CLICK")
    #            self._window.beingClicked = True
    #            print(self._window.beingClicked)
    #        elif self._window.beingClicked:
    #            print("UNCLICK")
    #            self._window.beingClicked = False
    #            print(self._window.beingClicked)


class QuitDialog(QDialog, quit_ui.Ui_closeConfirm):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Leaving so soon?")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.ok)
        self.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.discard)

    def ok(self):
        self.done(1)

    def discard(self):
        self.done(2)


class TreeView(QTreeView):
    generalClick = pyqtSignal()

    def __init__(self):
        super(TreeView, self).__init__()
        self.sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(self.sizePolicy)
        self.setMinimumWidth(150)
        self.setEditTriggers(QAbstractItemView.SelectedClicked)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def mousePressEvent(self, event):
        self.generalClick.emit()
        return super(TreeView, self).mousePressEvent(event)


class MDIArea(QMdiArea):
    """
    Custom QMdiArea class -- the native class had some strange bugs with closing tabs, where it would keep the tab
    due to how the closing was happening. I've subclassed it to make things easy in finding bugs.
    This works well and should be more customizable if needed.
    """
    def __init__(self):
        super(MDIArea, self).__init__()
        self.tabbed = False  # tabbed by default
        self.tabBar = None
        self.setTabs(True) if self.tabbed else self.setTabs(False)
        self.WindowOrder(2)

    def toggleTabs(self):
        self.tabbed = not self.tabbed
        if self.tabbed:
            self.setTabs(True)
        else:
            self.setTabs(False)
            for sub in self.subWindowList():
                sub.showNormal()
            self.tileSubWindows()

    def setTabs(self, on):
        if on:
            self.setViewMode(1)
            self.tabbed = True
            self.tabBar = self.findChild(QTabBar)
            self.setupTabBar()
        else:
            self.tabbed = False
            self.setViewMode(0)

    def setupTabBar(self):
        # self.tabBar.setAutoHide(True)
        self.setTabsMovable(True)
        self.setTabsClosable(True)
        #self.tabBar.tabCloseRequested.connect(self.closeTab)

    def closeTab(self):
        try:
            self.activeSubWindow().showMaximized()
        except:
            # So I can close all tabs
            pass

    def resizeEvent(self, event):
        # TODO: CAN I DELETE THIS??
        # passes a resize event to all subwindows to make sure the sequence is updated
        for sub in self.subWindowList():
            sub.resizeEvent(event)
        return super(MDIArea, self).resizeEvent(event)

    def addSubWindow(self, window, flags=Qt.WindowFlags()):
        super(MDIArea, self).addSubWindow(window, flags)
        if self.tabbed:
            print(self.tabbed)
            for sub in self.subWindowList():
                sub.showMinimized()
            self.activeSubWindow().showMaximized()
        window.show()
        self.setActiveSubWindow(window)

    def setActiveSubWindow(self, window):
        if self.tabbed:
            titles = []
            for index in range(len(self.tabBar.children())):
                titles.append(self.tabBar.tabText(index))
            if window.windowTitle() not in titles:
                self.addSubWindow(window)
                self.tabBar.addTab(window.windowIcon(), window.windowTitle())
                self.activeSubWindow().showMaximized()
            else:
                super(MDIArea, self).setActiveSubWindow(window)
                self.activeSubWindow().showMaximized()
        else:
            super(MDIArea, self).setActiveSubWindow(window)
            window.widget().resized.emit()
            #print("Unable to resize")
            #self.activeSubWindow().showMaximized()


class MDISubWindow(QMdiSubWindow):
    """
    Have to subclass QMdiSubWindow because it doesn't automatically
    show the widget if I close the window, which is strange and annoying.
    """
    def __init__(self):
        super(MDISubWindow, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.widget_ = None
        # TODO: TAKE OUT EXTRA CLOSE COMMAND IN MDISUBWINDOW
        # remove extra close command
        # menu = self.systemMenu()
        # for action in menu.actions():
        #    if action.text()=="&Close":
        #        print("Found")
        #        menu.actions().remove(action)
        # self.setSystemMenu(menu)

    def event(self, event):
        # EventFilter doesn't capture type 2 events on title bar of subwindow for some reason
        # Is there a better way to do this???
        #print(event, event.type())
        if event.type() == 2:
            #linnaeo = self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget()
            print("REDRAWING FROM MDI")
            self.widget_.userIsResizing = True
            self.widget_.seqArrangeNoColor()
        elif event.type() == 3:
            print("DONE REDRAWING FROM MDI")
            self.widget_.userIsResizing = False
            self.widget_.seqArrangeColor()
        return super().event(event)

    def setWidget(self, widget):
        self.widget_ = widget
        super(MDISubWindow, self).setWidget(widget)

    def widget(self):
        return self.widget_

    def show(self):
        self.widget_.show()
        super(MDISubWindow, self).show()

    def closeEvent(self, event):
        if self.mdiArea():
            self.mdiArea().removeSubWindow(self)
        self.close()
        return super(MDISubWindow, self).closeEvent(event)

    def close(self):
        super(MDISubWindow, self).close()


class AlignSubWindow(QWidget, alignment_ui.Ui_aliWindow):
    """
    Alignment SubWindow UI. Takes in a dictionary of sequences that have been aligned and arranges them.
    # TODO: This does not maintain the alignment order. Shant be helped?...
    """
    resized = pyqtSignal()

    # THEMES #

    pos = QColor(100, 140, 255)
    neg = QColor(255, 70, 90)
    cys = QColor(255, 255, 85)
    aro = QColor(145, 255, 168)

    defTheme = {
        # Charged; positive
        "R": pos, "H": aro, "K": pos,
        # Charged, negative
        "D": neg, "E": neg,
        # Misc
        "C": cys, #"G": gly, "A": ala,
        # Aromatic
        "W": aro, "F": aro, "Y": aro
    }

    def __init__(self, seqs):
        super(self.__class__, self).__init__()
        self.userIsResizing = False
        self.setupUi(self)
        self._seqs = seqs
        self.resized.connect(self.resizeDone)
        self.alignPane.verticalScrollBar().valueChanged.connect(self.namePane.verticalScrollBar().setValue)
        self.theme = None
        self.splitNames = []
        self.splitSeqs = []


        #FANCY FONTWORK
        fid = QFontDatabase.addApplicationFont(":/fonts/LiberationMono.ttf")
        family = QFontDatabase.applicationFontFamilies(fid)[0]
        font = QFont(family, 10)
        self.fmF = QFontMetricsF(font)  # FontMetrics Float... because default FontMetrics gives Int
        self.alignPane.setFont(font)
        self.alignPane.setStyleSheet("QTextEdit {padding-left:20px; padding-right:0px; padding-top:0px; background-color: \
                                     rgb(255,255,255)}")
        self.namePane.setStyleSheet("QTextEdit {padding-top:0px;}")

        self.alignPane.setCursorWidth(0)

        self.refseq = None
        self.maxlen = 0


        # options to do
        # TODO: Implement these
        self.showRuler = False
        self.showColors = True
        self.relColors = False

        if self.showColors:
            self.theme = self.defTheme

        self.seqInit()

    def setTheme(self, theme):
        self.theme = theme

    def toggleRulers(self):
        self.showRuler = not self.showRuler

    def resizeEvent(self, event):
        self.resized.emit()
        super(AlignSubWindow, self).resizeEvent(event)
        # self.oldwidth = event.oldSize().width()

    def resizeDone(self):
        if self.userIsResizing:
            print("REDRAW FROM INSIDE")
            self.seqArrangeNoColor()
        elif not self.userIsResizing:
            print("DONE FROM INSIDE")
            self.seqArrangeColor()


    def seqInit(self):
        """
        Sequences are stored as triple layer arrays:
        First layer is SEQUENCE
        Second layer is SEQUENCE POSITION
        Third layer is RESIDUE and COLOR
        """
        for seq in self._seqs.values():
            if len(seq) > self.maxlen:
                self.maxlen = len(seq)
        for name, seq in self._seqs.items():
            self.splitNames.append(name)
            local = []
            for i in range(self.maxlen):
                try:
                    char = seq[i]
                    color = self.theme[char]
                    local.append([char, color])
                except IndexError:
                    local.append([" ", None])
                except KeyError:
                    char = seq[i]
                    local.append([char, None])
            self.splitSeqs.append(local)

    def seqArrangeNoColor(self):
        print("NO COLOR")
        nseqs = len(self._seqs.keys())  # Calculate number of sequences
        charpx = self.fmF.averageCharWidth()
        width = self.alignPane.size().width() - 30
        char_count = int(width / charpx - 20 / charpx)
        if self.alignPane.verticalScrollBar().isVisible():
            char_count = int(width / charpx - 20 / charpx - \
                             self.alignPane.verticalScrollBar().size().width() / charpx)

        lines = int(self.maxlen / char_count)
        self.alignPane.clear()
        nline = 0
        for line in range(lines):
            start = nline * char_count
            end = nline * char_count + char_count
            for n in range(nseqs):
                self.alignPane.append("".join([x[0] for x in self.splitSeqs[n][start:end]]))
            self.alignPane.append("")
            self.alignPane.moveCursor(QTextCursor.Start)
            nline += 1

    def seqArrangeColor(self):
        print("COLOR")
        nseqs = len(self._seqs.keys())  # Calculate number of sequences
        charpx = self.fmF.averageCharWidth()
        width = self.alignPane.size().width() - 30
        char_count = int(width / charpx - 20 / charpx)
        if self.alignPane.verticalScrollBar().isVisible():
            char_count = int(width / charpx - 20 / charpx - \
                             self.alignPane.verticalScrollBar().size().width() / charpx)

        lines = int(self.maxlen/char_count)
        self.alignPane.clear()
        nline = 0
        for line in range(lines):
            start = nline * char_count
            end = nline * char_count + char_count
            for n in range(nseqs):
                for i in range(start, end):
                    self.alignPane.moveCursor(QTextCursor.End)
                    self.alignPane.setTextBackgroundColor(Qt.white)
                    if self.splitSeqs[n][i][1]:
                        self.alignPane.setTextBackgroundColor(self.splitSeqs[n][i][1])
                    self.alignPane.insertPlainText(self.splitSeqs[n][i][0])
                    self.alignPane.setTextBackgroundColor(Qt.white)
                self.alignPane.insertPlainText("\n")
            nline += 1
            self.alignPane.insertPlainText("\n")
        self.alignPane.moveCursor(QTextCursor.Start)






    """
    def seqArrange(self):
        splitseqs = []
        prettynames = []
        prettyseqs = []
        maxname = 0
        wrapper = SeqWrap()
        wrapper.break_on_hyphens = False
        nseqs = len(self._seqs.keys())
        charpx = self.fmF.averageCharWidth()
        width = self.alignPane.size().width() - 30  # 5 pixel gap on both sides. plus 20 px on left edge
        nlines = 0
        wrapper.width = int(width / charpx - 20/charpx)  # Left edge is 20 px, want to match
        if self.alignPane.verticalScrollBar().isVisible():
            wrapper.width = int(width / charpx -20/charpx - self.alignPane.verticalScrollBar().size().width()/charpx)

        #print("\nExpected Text Px:",textpx)
        #print("Width is:",width,"and char is",charpx,"so number of chars is", wrapper.width)
        for name, seq in self._seqs.items():
            lines = wrapper.wrap(seq)
            splitseqs.append([name, lines])
            if len(lines) > nlines:
                nlines = len(lines)
            if len(name) > maxname:
                maxname = len(name)
        # Set name window width to account for max name
        self.namePane.setMinimumWidth((maxname*charpx)+5)

        # Adjust the number of lines so that it accounts for the number of sequences
        # as well as a blank line (minus one for the last blank line)
        nlines = nlines*(nseqs+1)-1
        subline = 0
        seqid = 0
        # This loop creates a single alignment array by threading each of the individual lines
        # into each other.
        # TODO: Add a line for sequence number! Make it toggleable!
        for line in range(nlines):
            if seqid != nseqs:
                try:
                    prettynames.append(splitseqs[seqid][0])
                    prettyseqs.append(splitseqs[seqid][1][subline])
                    seqid += 1
                except IndexError:
                    prettynames.append(splitseqs[seqid][0])
                    prettyseqs.append("")
                    seqid += 1
            elif seqid == nseqs:
                prettyseqs.append("")
                prettynames.append("")
                seqid = 0
                subline += 1
        # Initialize the text frames
        self.namePane.setAlignment(Qt.AlignRight)
        self.alignPane.setAlignment(Qt.AlignLeft)
        self.namePane.setText(prettynames[0])
        for line in prettynames[1:]:
            self.namePane.setAlignment(Qt.AlignRight)
            self.namePane.append(line)
        self.namePane.verticalScrollBar().setValue(self.alignPane.verticalScrollBar().value())

        self.alignPane.clear()
        if nseqs == 1:
            for line in prettyseqs:
                self.alignPane.setAlignment(Qt.AlignLeft)
                self.alignPane.append(line)

        if nseqs > 1:
            # TODO: Figure out a way to set reference sequence (or rearrange)
            prevline = ""
            for index in range(len(prettyseqs)):
                line = prettyseqs[index]
                if len(line) == 0:
                    # Blank line, just add to window ###############
                    self.alignPane.append(line)
                    prevline = line
                elif len(prevline) == 0:
                    # Reference sequence, always format ##############
                    self.alignPane.moveCursor(QTextCursor.End)
                    if index > 0:
                        self.alignPane.insertPlainText("\n")
                        self.alignPane.setTextBackgroundColor(Qt.white)
                    for i in range(len(line)):
                        if line[i] in self.theme.keys():
                            color = self.theme[line[i]]
                            self.alignPane.setTextBackgroundColor(color)
                        self.alignPane.insertPlainText(line[i])
                        self.alignPane.moveCursor(QTextCursor.End)
                        self.alignPane.setTextBackgroundColor(Qt.white)
                    prevline = line
                else:
                    # All others, conditional format ##################
                    self.alignPane.moveCursor(QTextCursor.End)
                    self.alignPane.insertPlainText("\n")
                    for i in range(len(line)):
                        self.alignPane.setTextBackgroundColor(Qt.white)
                        if line[i] in self.theme.keys() and line[i]:
                            color = self.theme[line[i]]
                            self.alignPane.setTextBackgroundColor(color)
                        if self.relColors and line[i] != prevline[i]:
                            self.alignPane.setTextBackgroundColor(Qt.white)
                        self.alignPane.insertPlainText(line[i])
                        self.alignPane.moveCursor(QTextCursor.End)
                        self.alignPane.setTextBackgroundColor(Qt.white)
        self.alignPane.moveCursor(QTextCursor.Start)
    """

    def seqs(self):
        return self._seqs

    def setSeqs(self, seqs):
        self._seqs = seqs
        self.seqArrangeColor()

    def updateName(self, old, new):
        seq = self._seqs[old]
        self._seqs[new]=seq
        self._seqs.pop(old)
        self.seqArrangeColor()


class AlignTheme(QSyntaxHighlighter):
    theme = None

    def setTheme(self, theme=1):
        """
        Should make a dictionary of formats per type.
        """
        fmtPos = QTextCharFormat()
        fmtNeg = QTextCharFormat()
        fmtAro = QTextCharFormat()
        fmtHydro = QTextCharFormat()
        fmtPolar = QTextCharFormat()
        fmtCys = QTextCharFormat()
        fmtGly = QTextCharFormat()
        fmtPro = QTextCharFormat()

        if theme == 0:
            fmtPos.setBackground(QColor(50, 69, 97))
            fmtPos.setForeground(Qt.white)
            fmtNeg.setBackground(QColor(158, 31, 50))
            fmtNeg.setForeground(Qt.white)
            fmtAro.setBackground(QColor(85,133,142))
            fmtAro.setForeground(Qt.black)
            fmtHydro.setBackground(QColor(150,173,200))
            fmtHydro.setForeground(Qt.black)
            fmtPolar.setBackground(QColor(103,125,76))
            fmtPolar.setForeground(Qt.white)
            fmtCys.setBackground(QColor(241,154,74))
            fmtCys.setForeground(Qt.black)
            fmtGly.setBackground(QColor(245,200,185))
            fmtGly.setForeground(Qt.black)
            fmtPro.setBackground(QColor(243,65,63))
            fmtPro.setForeground(Qt.black)

        if theme == 1:
            fmtPos.setBackground(QColor(70,70,70))
            fmtPos.setForeground(Qt.white)
            fmtNeg.setBackground(QColor(47,47,47))
            fmtNeg.setForeground(Qt.white)
            fmtAro.setBackground(QColor(24,24,24))
            fmtAro.setForeground(Qt.white)
            fmtHydro.setBackground(QColor(93,93,93))
            fmtHydro.setForeground(Qt.white)
            fmtPolar.setBackground(QColor(186,186,186))
            fmtPolar.setForeground(Qt.black)
            fmtCys.setBackground(QColor(140,140,140))
            fmtCys.setForeground(Qt.white)
            fmtGly.setBackground(QColor(163,163,163))
            fmtGly.setForeground(Qt.black)
            fmtPro.setBackground(QColor(116,116,116))
            fmtPro.setForeground(Qt.white)

        self.theme = {
            "[R,K]": fmtPos,
            "[D,E]": fmtNeg,
            "[F,Y,W,H]": fmtAro,
            "[A,V,I,L,M]": fmtHydro,
            "[S,T,N,Q]": fmtPolar,
            "[G]": fmtGly,
            "[C]": fmtCys,
            "[P]": fmtPro
        }

    def highlightBlock(self, text):
        for pattern, fmt in self.theme.items():
            print("FMT: ", fmt)
            print("Pattern: ", pattern)
            regex = QRegularExpression(pattern)
            index = regex.globalMatch(text)
            while index.hasNext():
                match = index.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)


class ItemModel(QStandardItemModel):
    nameChanging = pyqtSignal()
    dupeName = pyqtSignal()
    nameChanged = pyqtSignal()

    def __init__(self, windows, seqTree=False):
        super(ItemModel, self).__init__()
        self.modelLogger = logging.getLogger("ItemModel")
        self.lastClickedNode = None
        #self._root = root
        self._windows = windows
        self._titles = []
        self.isSeqs = False
        if seqTree:
            self.isSeqs = True

    def updateLastClicked(self, node):
        self.lastClickedNode = node

    def updateNames(self, titles):
        self._titles = titles

    def updateWindows(self, windows):
        self._windows = windows

    def setData(self, index, value, role=Qt.UserRole+1):
        oldvalue = None
        self.modelLogger.debug("Updating data for node")
        if self.isSeqs:
            self.modelLogger.debug("Sequence node; checking name!")
            #self.nameChanging.emit()
            # Only do this check if this is coming from the top Tree and is not a folder
            if value != self.lastClickedNode.text():
                oldvalue = self.lastClickedNode.text()
                newvalue, self._titles = utilities.checkName(value, self._titles)
                if newvalue != value:
                    self.modelLogger.debug("Item duplicates a different node! "+str(value)+" in "+str(self._titles))
                    value = newvalue
                    self.dupeName.emit()
                    self.modelLogger.debug("Name changed to "+str(value))
                try:
                    sub = self._windows[self.itemFromIndex(index).data(role=Qt.UserRole+3)]
                    sub.widget().updateName(oldvalue, newvalue)
                except KeyError:
                    pass
                if self.itemFromIndex(index).data(role=Qt.UserRole+2):
                    seqr = self.itemFromIndex(index).data(role=Qt.UserRole+2)[0]
                    seqr.name = newvalue
        self.modelLogger.debug("Setting node text to "+str(value))
        self.itemFromIndex(index).setData(value)
        self.itemFromIndex(index).setText(value)
        self.nameChanged.emit()
        try:
            sub = self._windows[self.itemFromIndex(index).data(role=Qt.UserRole+3)]
            sub.setWindowTitle(value)

            sub.mdiArea().setActiveSubWindow(sub)
        except:
            exctype, val = sys.exc_info()[:2]
            self.modelLogger.debug("Detected exception, but probably fine: "+str(exctype))
        finally:
            return super(ItemModel, self).setData(index, value, role)
