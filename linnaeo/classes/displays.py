from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QFontDatabase, QFont, QFontMetricsF, QTextCursor, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QDialogButtonBox

from linnaeo.classes import widgets, utilities, themes
from linnaeo.resources import linnaeo_rc
from linnaeo.ui import alignment_ui, quit_ui, about_ui


class AlignSubWindow(QWidget, alignment_ui.Ui_aliWindow):
    """
    Alignment SubWindow UI. Takes in a dictionary of sequences that have been aligned and arranges them.
    # TODO: This does not maintain the alignment order. Shant be helped?...
    """
    resized = pyqtSignal()
    nameChange = pyqtSignal((str, str))

    def __init__(self, seqs):
        super(self.__class__, self).__init__()

        # Construct the window
        self.alignPane = widgets.AlignPane(self)
        self.family = (QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(
            ':/fonts/LiberationMono.ttf'))[0])
        self.font = QFont(self.family, 10)
        self.fmF = QFontMetricsF(self.font) # FontMetrics Float... because default FontMetrics gives Int

        # Initialize settings
        self.theme = themes.PaleTheme().theme
        self.showRuler = True
        self.showColors = True
        self.relColors = False

        # Init functional variables
        self._seqs = seqs
        self.splitNames = []
        self.splitSeqs = []
        self.userIsResizing = False
        self.refseq = None
        self.lastpos = None
        self.maxlen = 0
        self.maxname = 0

        # Draw the window
        self.setupUi(self)
        self.setupCustomUi()

        # Connect all slots and start
        self.resized.connect(self.externalResizeDone)
        self.alignPane.verticalScrollBar().valueChanged.connect(self.namePane.verticalScrollBar().setValue)
        self.nameChange.connect(self.updateName)
        self.seqInit()

    def setupCustomUi(self):
        self.horizontalLayout.addWidget(self.alignPane)
        self.alignPane.setFont(self.font)
        self.alignPane.setStyleSheet("QTextEdit {padding-left:20px; padding-right:0px; background-color: \
                                             rgb(255,255,255)}")
        self.namePane.setStyleSheet("QTextEdit {padding-top:1px;}")

    def seqInit(self):
        """
        Sequences are stored as double layer arrays of each character.
        First layer is SEQUENCE
        Second layer is SEQUENCE POSITION, saved as an html snippet.
        Third layer is RESIDUE and COLOR
        so self.seq = [SEQA = [Position = Color,
        """
        self.splitSeqs = []
        self.splitNames = []
        for seq in self._seqs.values():
            if len(seq) > self.maxlen:
                self.maxlen = len(seq)
        for name, seq in self._seqs.items():
            self.splitNames.append(name)
            if len(name) > self.maxname:
                self.maxname = len(name)
            local = []
            count = 0
            for i in range(self.maxlen):
                try:
                    char = seq[i]
                    color = self.theme[char]
                    local.append([char, color, count])
                    if char != "-":
                        count += 1
                except IndexError:
                    local.append([" ", None])
                except KeyError:
                    char = seq[i]
                    local.append([char, None])
            self.splitSeqs.append(local)

    def seqArrange(self, color=True, rulers=True):
        if not self.showColors:
            color = False
        if not self.showRuler:
            rulers = False
        nseqs = len(self._seqs.keys())  # Calculate number of sequences
        charpx = self.fmF.averageCharWidth()
        print("CHARPX: ",charpx)
        width = self.alignPane.size().width() - 30
        char_count = int(width / charpx - 20 / charpx)
        if self.alignPane.verticalScrollBar().isVisible():
            char_count = int(width / charpx - 20 / charpx - \
                             self.alignPane.verticalScrollBar().size().width() / charpx)
        lines = int(self.maxlen / char_count) + 1
        self.namePane.setMinimumWidth((self.maxname * charpx) + 5)
        nline = 0
        # if not self.userIsResizing:
        # TODO: ISOLATE THIS OUT TO DO IN THREADS
        self.alignPane.clear()
        self.namePane.clear()
        for line in range(lines):
            self.alignPane.moveCursor(QTextCursor.End)
            start = nline * char_count
            end = nline * char_count + char_count
            gap = 0
            if line == lines - 1:
                oldend = end
                end = start + len(self.splitSeqs[0][start:])
                gap = oldend - end
            if self.showRuler and rulers:  # TODO REMOVE AND NOT
                self.namePane.insertPlainText("\n")
                ruler = utilities.buildRuler(char_count, gap, start, end)
                self.alignPane.insertPlainText(ruler)
                self.alignPane.insertPlainText("\n")
            elif self.showRuler and not rulers:  # TODO MOVE THIS TO BELOW
                self.namePane.insertPlainText("\n")
                self.alignPane.insertPlainText(" ")
                self.alignPane.insertPlainText("\n")
            for n in range(nseqs):
                self.namePane.setAlignment(Qt.AlignRight)
                self.namePane.insertPlainText(self.splitNames[n])
                self.alignPane.moveCursor(QTextCursor.End)
                if not color:
                    self.alignPane.insertPlainText("".join([x[0] for x in self.splitSeqs[n][start:end]]))
                    self.alignPane.insertPlainText("\n")
                elif color:
                    for i in range(start, end):
                        self.alignPane.moveCursor(QTextCursor.End)
                        self.alignPane.setTextBackgroundColor(Qt.white)
                        if self.splitSeqs[n][i][1]:
                            self.alignPane.setTextBackgroundColor(self.splitSeqs[n][i][1])
                        self.alignPane.insertPlainText(self.splitSeqs[n][i][0])
                        self.alignPane.setTextBackgroundColor(Qt.white)
                    self.alignPane.insertPlainText("\n")
                self.namePane.insertPlainText("\n")
            nline += 1
            self.alignPane.insertPlainText("\n")
            self.namePane.insertPlainText("\n")
        if self.lastpos:
            self.alignPane.moveCursor(self.lastpos)
            self.namePane.moveCursor(self.lastpos)
        else:
            self.alignPane.moveCursor(QTextCursor.Start)
            self.namePane.moveCursor(QTextCursor.Start)

    # elif self.userIsResizing:  # TODO DO IN SEPARATE THREAD
    #    print("RESIZING")
    #    self.alignPane.clear()
    #    self.namePane.clear()

    # UTILITY FUNCTIONS
    def setTheme(self, theme):
        self.theme = theme

    def toggleRulers(self):
        self.showRuler = not self.showRuler
        self.seqArrange()

    def toggleColors(self):
        self.showColors = not self.showColors
        self.seqArrange()

    def resizeEvent(self, event):
        """
        This gets called anytime the window is in the process of being redrawn. If the MDI Subwindow is maximized,
        it calls a resizeEvent upon release too.
        """
        if self.userIsResizing:
            self.seqArrange(color=False, rulers=False)
        elif not self.userIsResizing:
            self.resized.emit()
        super(AlignSubWindow, self).resizeEvent(event)
        # self.oldwidth = event.oldSize().width()

    def externalResizeDone(self):
        """
        This only happens if the MDI sub window is not maximized and it gets resized; that does
        not normally call the resizeEvent for the alignment window for some reason.
        """
        self.seqArrange()

    def seqs(self):
        return self._seqs

    def setSeqs(self, seqs):
        self._seqs = seqs
        self.seqArrange()

    def updateName(self, old, new):
        seq = self._seqs[old]
        self._seqs[new] = seq
        self._seqs.pop(old)
        self.seqInit()
        self.seqArrange()

    def increaseFont(self):
        size = self.font.pointSizeF() + 1
        self.font.setPointSizeF(size)
        self.fmF = QFontMetricsF(self.font)
        print(self.fmF.averageCharWidth())
        self.alignPane.setFont(self.font)
        self.seqArrange()

    def decreaseFont(self):
        size = self.font.pointSizeF() - 1
        self.font.setPointSizeF(size)
        self.fmF = QFontMetricsF(self.font)
        print(self.fmF.averageCharWidth())
        self.alignPane.setFont(self.font)
        self.seqArrange()

    def getFontSize(self):
        return self.font.pointSize()




class AlignSubWindowBackup(QWidget, alignment_ui.Ui_aliWindow):
    """
    Alignment SubWindow UI. Takes in a dictionary of sequences that have been aligned and arranges them.
    # TODO: This does not maintain the alignment order. Shant be helped?...
    """
    resized = pyqtSignal()
    nameChange = pyqtSignal((str, str))
    toolTipReq = pyqtSignal()

    def __init__(self, seqs):
        super(self.__class__, self).__init__()
        self.userIsResizing = False
        self.setupUi(self)
        self.alignPane = widgets.AlignPane(self)
        # print(self.alignPane.pos().x(), self.alignPane.pos().y())
        self.horizontalLayout.addWidget(self.alignPane)
        self._seqs = seqs
        self.resized.connect(self.externalResizeDone)
        self.alignPane.verticalScrollBar().valueChanged.connect(self.namePane.verticalScrollBar().setValue)
        # self.toolTipReq.connect(self.getSeqTT)
        self.nameChange.connect(self.updateName)
        self.theme = None
        self.splitNames = []
        self.splitSeqs = []
        # self.alignPane.setMouseTracking(True)
        # self.installEventFilter(self.alignPane)

        # FANCY FONTWORK
        # This maintains the font within the application.
        fid = QFontDatabase.addApplicationFont(":/fonts/LiberationMono.ttf")
        family = QFontDatabase.applicationFontFamilies(fid)[0]
        font = QFont(family, 10)
        self.fmF = QFontMetricsF(font)  # FontMetrics Float... because default FontMetrics gives Int
        self.alignPane.document().setDefaultFont(font)
        self.alignPane.setStyleSheet("QTextEdit {padding-left:20px; padding-right:0px; background-color: \
                                     rgb(255,255,255)}")
        self.namePane.setStyleSheet("QTextEdit {padding-top:1px;}")

        self.refseq = None
        self.maxlen = 0
        self.maxname = 0
        self.lastpos = None

        # options to do
        # TODO: Implement these
        self.showRuler = True
        self.showColors = True  # Partially implemented
        self.relColors = False

        if self.showColors:
            self.theme = themes.PaleTheme().theme
        self.seqInit()

    def eventFilter(self, obj, event):
        if event.type() == 129:
            print("HOVER")
        if event.type() == 5:
            print("MOUSE MOVE")
        return super().eventFilter(obj, event)

    def event(self, event):
        # print(event, event.type())
        if event.type() == 110:
            self.toolTipReq.emit()
        return super().event(event)

    def setTheme(self, theme):
        self.theme = theme

    def toggleRulers(self):
        self.showRuler = not self.showRuler
        self.seqArrange()

    def toggleColors(self):
        self.showColors = not self.showColors
        self.seqArrange()

    def resizeEvent(self, event):
        """
        This gets called anytime the window is in the process of being redrawn. If the MDI Subwindow is maximized,
        it calls a resizeEvent upon release too.
        """
        if self.userIsResizing:
            self.seqArrange(color=False, rulers=False)
        elif not self.userIsResizing:
            self.resized.emit()
        super(AlignSubWindow, self).resizeEvent(event)
        # self.oldwidth = event.oldSize().width()

    def externalResizeDone(self):
        """
        This only happens if the MDI sub window is not maximized and it gets resized; that does
        not normally call the resizeEvent for the alignment window for some reason.
        """
        self.seqArrange()

    def seqInit(self):
        """
        Sequences are stored as triple layer arrays:
        First layer is SEQUENCE
        Second layer is SEQUENCE POSITION
        Third layer is RESIDUE and COLOR
        """
        self.splitSeqs = []
        self.splitNames = []
        for seq in self._seqs.values():
            if len(seq) > self.maxlen:
                self.maxlen = len(seq)
        for name, seq in self._seqs.items():
            self.splitNames.append(name)
            if len(name) > self.maxname:
                self.maxname = len(name)
            local = []
            count = 0
            for i in range(self.maxlen):
                try:
                    char = seq[i]
                    color = self.theme[char]
                    local.append([char, color, count])
                    if char != "-":
                        count += 1
                except IndexError:
                    local.append([" ", None])
                except KeyError:
                    char = seq[i]
                    local.append([char, None])
            self.splitSeqs.append(local)

    def seqArrange(self, color=True, rulers=True):
        if not self.showColors:
            color = False
        if not self.showRuler:
            rulers = False
        nseqs = len(self._seqs.keys())  # Calculate number of sequences
        charpx = self.fmF.averageCharWidth()
        width = self.alignPane.size().width() - 30
        char_count = int(width / charpx - 20 / charpx)
        if self.alignPane.verticalScrollBar().isVisible():
            char_count = int(width / charpx - 20 / charpx - \
                             self.alignPane.verticalScrollBar().size().width() / charpx)
        lines = int(self.maxlen / char_count) + 1
        self.namePane.setMinimumWidth((self.maxname * charpx) + 5)
        nline = 0
        # if not self.userIsResizing:
        # TODO: ISOLATE THIS OUT TO DO IN THREADS
        self.alignPane.clear()
        self.namePane.clear()
        for line in range(lines):
            self.alignPane.moveCursor(QTextCursor.End)
            start = nline * char_count
            end = nline * char_count + char_count
            gap = 0
            if line == lines - 1:
                oldend = end
                end = start + len(self.splitSeqs[0][start:])
                gap = oldend - end
            if self.showRuler and rulers:  # TODO REMOVE AND NOT
                self.namePane.insertPlainText("\n")
                ruler = utilities.buildRuler(char_count, gap, start, end)
                self.alignPane.insertPlainText(ruler)
                self.alignPane.insertPlainText("\n")
            elif self.showRuler and not rulers:  # TODO MOVE THIS TO BELOW
                self.namePane.insertPlainText("\n")
                self.alignPane.insertPlainText(" ")
                self.alignPane.insertPlainText("\n")
            for n in range(nseqs):
                self.namePane.setAlignment(Qt.AlignRight)
                self.namePane.insertPlainText(self.splitNames[n])
                self.alignPane.moveCursor(QTextCursor.End)
                if not color:
                    self.alignPane.insertPlainText("".join([x[0] for x in self.splitSeqs[n][start:end]]))
                    self.alignPane.insertPlainText("\n")
                elif color:
                    for i in range(start, end):
                        self.alignPane.moveCursor(QTextCursor.End)
                        self.alignPane.setTextBackgroundColor(Qt.white)
                        if self.splitSeqs[n][i][1]:
                            self.alignPane.setTextBackgroundColor(self.splitSeqs[n][i][1])
                        self.alignPane.insertPlainText(self.splitSeqs[n][i][0])
                        self.alignPane.setTextBackgroundColor(Qt.white)
                    self.alignPane.insertPlainText("\n")
                self.namePane.insertPlainText("\n")
            nline += 1
            self.alignPane.insertPlainText("\n")
            self.namePane.insertPlainText("\n")
        if self.lastpos:
            self.alignPane.moveCursor(self.lastpos)
            self.namePane.moveCursor(self.lastpos)
        else:
            self.alignPane.moveCursor(QTextCursor.Start)
            self.namePane.moveCursor(QTextCursor.Start)

    # elif self.userIsResizing:  # TODO DO IN SEPARATE THREAD
    #    print("RESIZING")
    #    self.alignPane.clear()
    #    self.namePane.clear()

    def seqs(self):
        return self._seqs

    def setSeqs(self, seqs):
        self._seqs = seqs
        self.seqArrange()

    def updateName(self, old, new):
        seq = self._seqs[old]
        self._seqs[new] = seq
        self._seqs.pop(old)
        self.seqInit()
        self.seqArrange()


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


class AboutDialog(QDialog, about_ui.Ui_Dialog):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Thanks for reading this!")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.ok)

    def ok(self):
        self.done(1)
