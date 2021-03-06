import logging

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontMetricsF, QColor, QFont
from PyQt5.QtWidgets import QWidget, QDialog, QDialogButtonBox, QPushButton, QTextEdit, QFrame, QSizePolicy, qApp

from linnaeo import __version__
from linnaeo.classes import widgets, utilities, themes
from linnaeo.classes.utilities import lookupTheme
from linnaeo.ui import alignment_ui, quit_ui, about_ui, ali_settings_ui, comments_ui


class AlignSubWindow(QWidget, alignment_ui.Ui_aliWindow):
    """
    Alignment SubWindow UI. Takes in a dictionary of sequences that have been aligned and arranges them.
    Sequences in the alignment are threaded and prepared as HTML; the color is stored in the array in order to
    reduce the load on display. However, just drawing the display is computationally expensive (as is generating
    the ruler for it), so both are turned off during resizing.
    # TODO: This does not maintain the alignment order -- trouble with the ClustalO API. Shant be helped?...
    """
    resized = pyqtSignal()
    nameChange = pyqtSignal((str, str))
    lineChange = pyqtSignal(int)

    def __init__(self, seqs, params):
        super(self.__class__, self).__init__()
        self.done = False
        # Construct the window
        self.alignLogger = logging.getLogger("AlignWindow")
        self.alignPane = widgets.AlignPane(self)
        self.rulerPane = QTextEdit()
        self.commentPane = CommentsPane()
        self.commentButton = QPushButton("Save")

        # Init functional variables
        self.fmF = None
        self._seqs = seqs
        self.dssps = {}
        self.splitNames = []
        self.splitSeqs = []
        self.userIsResizing = False
        self.refseq = None
        self.last = 0
        self.maxlen = 0
        self.maxname = 0
        self.lines = 0
        self.comments = {}
        self.showRuler = False
        self.showColors = False
        self.consvColors = False
        self.showDSSP = True
        self.ssFontWidth = None

        # Draw the window
        self.setupUi(self)
        self.setupCustomUi()

        # Connect all slots and start
        #self.rulerPane.verticalScrollBar().valueChanged.connect(self.alignPane.verticalScrollBar().setValue)
        self.alignPane.verticalScrollBar().valueChanged.connect(self.rulerPane.verticalScrollBar().setValue)
        self.alignPane.verticalScrollBar().valueChanged.connect(self.namePane.verticalScrollBar().setValue)
        #self.namePane.verticalScrollBar().valueChanged.connect(self.alignPane.verticalScrollBar().setValue)
        self.nameChange.connect(self.updateName)
        self.lineChange.connect(self.nameArrange)
        #self.alignPane.commentAdded.connect(self.showCommentWindow)

        # Initialize settings
        self.theme = lookupTheme('Default').theme
        self.params = {}
        self.setParams(params)
        self.ssFontWidth = QFontMetricsF(QFont("Default-Noto", self.params['fontsize'])).averageCharWidth()
        # print("Setting ssFONT Width to %s" % self.ssFontWidth)

        self.done = True
        self.seqInit()

    def setupCustomUi(self):
        # self.rulerPane.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.rulerPane.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.namePane.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.alignPane.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.alignPane.setMinimumWidth(100)
        self.rulerPane.setMaximumWidth(50)
        self.rulerPane.setMinimumWidth(5)
        self.alignPane.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.alignPane.setFrameShape(QFrame.StyledPanel)
        self.alignPane.setFrameShadow(QFrame.Plain)
        self.rulerPane.setFrameShape(QFrame.NoFrame)
        self.namePane.setFrameShape(QFrame.NoFrame)
        self.rulerPane.setCursorWidth(0)
        # self.namePane.setLineWidth(0)
        # self.alignPane.setLineWidth(0)
        # self.rulerPane.setLineWidth(0)
        bgcolor = self.palette().color(self.backgroundRole())
        self.alignPane.setStyleSheet("QTextEdit {padding-left:15px; padding-right:0px;background-color:white}")
        self.namePane.setStyleSheet("QTextEdit {padding-top:1px;background-color:%s;}" % bgcolor.name())
        self.rulerPane.setStyleSheet("QTextEdit {padding-top:1px;padding-left:0px;padding-right:0px;\
            background-color:%s;}" % bgcolor.name())
        self.gridLayout_2.addWidget(self.alignPane, 0, 1)
        self.gridLayout_2.addWidget(self.rulerPane, 0, 2)
        self.namePane.viewport().installEventFilter(self)
        self.rulerPane.viewport().installEventFilter(self)
        del bgcolor

    def eventFilter(self, obj, event):
        #print(event.type())
        if event.type() == 31:
            qApp.sendEvent(self.alignPane.viewport(), event)
            return True
        else:
            return False

    def seqInit(self):
        """
        Sequences are stored as double layer arrays of each character.
        First layer is SEQUENCE
        Second layer is SEQUENCE POSITION
        Third layer is RESIDUE and COLOR
        so self.seq = [SEQ = [Position = [HTML Char/Color, ResID, Dssp], ... ], ... ]
        """
        self.splitSeqs = []
        self.splitNames = []
        self.maxname = 0
        consv = True if self.theme == themes.Conservation().theme else False
        comments = True if self.theme == themes.Comments().theme else False
        for seq in self._seqs.values():
            if len(seq) > self.maxlen:
                self.maxlen = len(seq)
        for name, seq in self._seqs.items():
            self.splitNames.append(name)
            if len(name) > self.maxname:
                self.maxname = len(name)
            if len(seq) < self.maxlen:
                for n in range(self.maxlen - len(seq)):
                    seq.append(" ")
            local = []
            count = 0
            for i in range(self.maxlen):
                char = seq[i]
                if char not in ["-", " "]:
                    color = None
                    count += 1
                    tcount = count
                    dssp = None
                    if not consv:
                        #print("Consv theme is off, skipping alt colors")
                        color = self.theme[char]
                        #print("DEFAULTING %s to %s" % (char, color.name()))
                        if self.consvColors and self.refseq is not None:
                            ref = list(self._seqs.values())[self.refseq][i]
                            compare = utilities.checkConservation(char, ref)
                            if compare is not None:
                         #       print(compare)
                                if compare > 10:
                                    color = QColor(Qt.white)
                            else:
                                color = QColor(Qt.white)
                            del compare
                    elif consv:
                        #print("Consv theme iS ON", i)
                        if self.consvColors and self.refseq is not None:
                            ref = list(self._seqs.values())[self.refseq][i]
                            compare = utilities.checkConservation(char, ref)
                            if compare is not None and compare <= len(self.theme):
                         #       print(compare)
                                color = self.theme[compare]
                            else:
                                color = QColor(Qt.white)
                            del compare
                    if comments:
                        if i in self.comments.keys():
                            color = QColor(Qt.yellow)
                    if not color:
                        color = QColor(Qt.white)
                    #print(color.name())
                    tcolor = str(self.palette().color(self.alignPane.backgroundRole()).name()) if \
                        color.getHsl()[2] / 255 * 100 <= 50 else '#000000'
                    #print("tColor is %s" % tcolor)
                    char = '<span style=\"background-color: %s; color: %s\">%s</span>' % (
                        color.name(), tcolor, char)
                    #print('char is now %s' % char)
                    if self.dssps:
                        index = list(self._seqs.values()).index(seq)
                        try:
                            # print("adding dssp")
                            dssp = self.dssps[index][tcount]
                        except KeyError:
                            dssp = '-'
                        del index
                    else:
                        dssp = None
                else:
                    char = '<span style=\"background-color:#FFFFFF;\">' + seq[i] + "</span>"
                    tcount = 0
                    dssp = "-"
                local.append([char, tcount, dssp])
            self.splitSeqs.append(local)
            del i, char, color, tcount, dssp
        self.alignPane.seqs = self.splitSeqs
        del consv, comments, seq, name, local, count

    def nameArrange(self, lines):
        """ Generates the name panel; only fires if the number of lines changes to avoid needless computation"""
        if lines:
            self.namePane.clear()
            self.namePane.setMinimumWidth((self.maxname * self.fmF.averageCharWidth()) + 5)

            names = ["<pre style=\"font-family:%s; font-size:%spt; text-align: right;\">\n" % (self.font().family(),
                                                                                               self.font().pointSize())]
            for line in range(lines):
                if self.showRuler:
                    names.append("\n")
                if self.showDSSP:
                    names.append("\n")
                for i in range(len(self.splitNames)):
                    names.append(self.splitNames[i] + "\n")
                names.append("\n")
            names.append("</pre>")
            self.namePane.setHtml("".join(names))
            del names, line, lines, i

    def seqArrange(self, color=True, rulers=True, dssp=True):
        """
        The bread and butter. This fires upon creation and any resizing event. Computing the resize is done
        in a separate thread to help with smoothness; showing color and rulers is still very slow though. Resize events
        call this function with color off, and the ruler is turned off automatically.
        """
        try:
            #self.last = None
            if not self.showColors:
                color = False
            if not self.showRuler:
                rulers = False
            if not self.showDSSP:
                # print("Drawing with no DSSP")
                dssp = False
            charpx = self.fmF.averageCharWidth()
            self.rulerPane.size().setWidth(4 * charpx + 3)
            width = self.alignPane.size().width()
            char_count = int(width / charpx - 40 / charpx)
            if self.rulerPane.verticalScrollBar().isVisible():
                self.rulerPane.resize(int(4 * charpx + 3 + (self.rulerPane.verticalScrollBar().size().width())),
                                      self.rulerPane.size().height())
                self.last = self.rulerPane.verticalScrollBar().sliderPosition() / (
                        self.rulerPane.verticalScrollBar().maximum() -
                        self.rulerPane.verticalScrollBar().minimum())
            lines = int(self.maxlen / char_count) + 1
            if lines != self.lines:
                self.lineChange.emit(lines)
                self.lines = lines
            self.alignPane.lines = lines
            self.alignPane.setChars(char_count)
            self.alignPane.names = self.splitNames
            self.alignPane.clear()
            fancy = False if self.userIsResizing else True
            # print("Sending seq with dssp:", dssp)
            worker = utilities.SeqThread(self.splitSeqs, char_count, lines, rulers, color, dssp, fancy=fancy,
                                         parent=self, )
            worker.start()
            worker.finished.connect(worker.deleteLater)
            worker.finished.connect(worker.quit)
            worker.wait()
            style = "<style>pre{font-family:%s; font-size:%spt;}</style>" % (
                self.font().family(), self.font().pointSize())
            self.alignPane.setHtml(style + worker.html)
            del worker
            # RULER CALCULATION --> SIDE PANEL.
            self.rulerPane.clear()
            rulerHtml = ["<pre style=\"font-family:%s; font-size:%spt; text-align: left;\">" %
                         (self.font().family(), self.font().pointSize())]
            for x in range(self.lines):
                if self.showRuler and self.showDSSP:
                    exline = "\n\n\n"
                elif self.showRuler or self.showDSSP:
                    exline = "\n\n"
                else:
                    exline = "\n"
                # exline = "\n\n" if self.showRuler else "\n"
                rulerHtml.append(exline)
                for i in range(len(self.splitSeqs)):
                    try:
                        label = str(self.splitSeqs[i][x * char_count + char_count - 1][1])
                        if label == "0":
                            for y in range(char_count):
                                label = str(self.splitSeqs[i][x * char_count + char_count - 1 - y][1])
                                if label != "0":
                                    break
                    except IndexError:
                        label = ""
                    rulerHtml.append(label + "\n")
                    del label
                del i
            del x, exline

            rulerHtml.append('</pre>')
            self.rulerPane.setHtml(style + "".join(rulerHtml))
            prev = self.rulerPane.verticalScrollBar().sliderPosition()
            if self.rulerPane.verticalScrollBar().isVisible():
                if self.last:
                    self.last = int(round(((self.rulerPane.verticalScrollBar().maximum() -
                                    self.rulerPane.verticalScrollBar().minimum()) *
                                    self.last)))
                    self.rulerPane.verticalScrollBar().setSliderPosition(self.last)
            del prev
            del charpx, width, char_count, lines, fancy, style, rulerHtml
        except ZeroDivisionError:
            self.alignLogger.info("Font returned zero char width. Please choose a different font")
        del color, rulers, dssp

    # UTILITY FUNCTIONS
    def setTheme(self, theme):
        self.theme = lookupTheme(theme).theme
        self.params['theme'] = theme
        self.seqInit()
        self.seqArrange()
        del theme

    def toggleRuler(self, state):
        self.showRuler = state
        self.params['ruler'] = state
        self.nameArrange(self.lines)
        self.seqArrange()
        del state

    def toggleColors(self, state):
        self.showColors = state
        self.params['colors'] = state
        self.seqArrange()
        del state

    def toggleStructure(self, state):
        # print("In alignment", state)
        self.params['dssp'] = state
        self.showDSSP = state
        self.nameArrange(self.lines)
        self.seqArrange()
        del state

    def seqs(self):
        return self._seqs

    def setSeqs(self, seqs):
        self._seqs = seqs
        self.seqArrange()
        del seqs

    def updateName(self, old, new):
        self.alignLogger.debug("Received name change alert: %s to %s" % (old, new))
        seq = self._seqs[old]
        self._seqs[new] = seq
        self._seqs.pop(old)
        if self.done:
            self.seqInit()
            self.nameArrange(self.lines)
            self.seqArrange()
        del old, new, seq

    def setFont(self, font):
        """
        Sets the current font. Structure symbols are always the default font, because I hand-made those symbols.
        Therefore, when changing the font, the main Linnaeo app determines whether the new font is compatible with the
        default font and disables the symbols if it is not.
        """
        # Selected font has a baked-in size, so have to account for when changing the font.
        if font.family() != self.font().family() and font.pointSize() != self.font().pointSize():
            font.setPointSize(self.font().pointSize())
        super().setFont(font)
        self.fmF = QFontMetricsF(self.font())
        if self.done:
            self.seqInit()
            self.nameArrange(self.lines)
            self.seqArrange()
        del font

    def setFontSize(self, size):
        """ Updates the symbol font size too -- make sure it matches. """
        font = self.font()
        font.setPointSize(size)
        self.ssFontWidth = QFontMetricsF(QFont("Default-Noto", size)).averageCharWidth()
        self.setFont(font)
        del size, font

    def setParams(self, params):
        #print("UPDATING VALUES")
        self.params = params.copy()
        # print(self.params)
        self.showRuler = self.params['ruler']
        self.showColors = self.params['colors']
        self.consvColors = self.params['byconsv']
        self.showDSSP = self.params['dssp']
        if self.font().pointSize() != self.params['fontsize']:
            # print("Changing font size")
            self.setFontSize(self.params['fontsize'])
        if self.font() != self.params['font']:
            self.setFont(self.params['font'])
        newtheme = lookupTheme(self.params['theme']).theme
        if self.theme != newtheme:
            self.theme = newtheme
            if self.done:
                self.seqInit()
                self.seqArrange()
        del params, newtheme

    def showCommentWindow(self, target):
        # TODO: shows for ALL rows!
        name = self.splitNames[target[0]]
        resi = self.splitSeqs[target[0]][target[2]]
        self.comments[target[2]] = "COMMENT"
        self.seqInit()
        self.seqArrange()
        #self.commentPane.lineEdit.setText(str(name) + " " + str(resi))
        # self.gridLayout.addWidget(self.commentButton,1,0)
        self.gridLayout.addWidget(self.commentPane, 1, 1)
        del target, name, resi

    def addStructure(self, dssp, seq):
        """ Adds DSSP data to the SplitSeqs array. """
        seqs = [x.replace('-', '') for x in self._seqs.values()]
        test = str(seq.seq).replace('-', '')
        # print("Query:\n%s" % test)
        # print(seqs)
        if test in seqs:
            index = seqs.index(test)
            # print("Matched sequence to index %s" % index)
            self.dssps[index] = dssp
            for res in self.splitSeqs[index]:
                # print(res[1], res[2])
                if not res[2]:
                    try:
                        res[2] = dssp[res[1]]
                        # print("Adding structure info %s" % res[2])
                    except KeyError:
                        # print("skipping!")
                        res[2] = "-"
                else:
                    pass
                    #print("Weird, got a duplicate at %s " % res[1])
            # print(self.splitSeqs[index])
            del index, res
        del dssp, seq, seqs, test,

    def setReference(self, name):
        if name in self.splitNames:
            self.refseq = self.splitNames.index(name)
            #print("refseq set to ", self.refseq)
            if self.done:
                self.seqInit()
                self.seqArrange()
        elif name == "Select seq...":
            self.refseq = None
            if self.done:
                self.seqInit()
                self.seqArrange()
        else:
            pass
            #print("ERROR -- SEQUENCE NOT FOUND")
        del name

    def setConsvColors(self, state):
        self.consvColors = state
        self.seqInit()
        self.seqArrange()
        del state


class OptionsPane(QWidget, ali_settings_ui.Ui_Form):
    # updateParam = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedWidth(140)
        self.params = {}
        self.themeIndices = {}
        self.initPane()
        self.lastStruct = False

    def initPane(self):
        for index in range(0, self.comboTheme.model().rowCount()):
            self.themeIndices[self.comboTheme.model().itemData(self.comboTheme.model().index(index, 0))[0]] = index

        self.checkRuler.toggled.connect(self.rulerToggle)
        self.checkColors.toggled.connect(self.colorToggle)
        self.comboTheme.currentIndexChanged.connect(self.changeTheme)
        self.comboFont.currentFontChanged.connect(self.changeFont)
        self.spinFontSize.valueChanged.connect(self.changeFontSize)
        self.checkStructure.toggled.connect(self.structureToggle)
        self.checkConsv.toggled.connect(self.consvToggle)
        del index

    def setParams(self, params):
        """ These are set by the preferences pane --> default for every new window """
        #print("SETTING PARAMS")
        self.params = params.copy()
        # print(params["font"].family(),
        #     self.params["font"].family())  # 'rulers', 'colors', 'fontsize', 'theme', 'font', 'byconsv'
        self.checkRuler.setChecked(self.params['ruler'])
        self.checkColors.setChecked(self.params['colors'])
        self.checkConsv.setChecked(self.params['byconsv'])
        self.checkStructure.setChecked(self.params['dssp'])
        self.comboTheme.setCurrentIndex(self.themeIndices[self.params['theme']])
        self.spinFontSize.setValue(self.params['fontsize'])
        self.comboFont.setCurrentFont(self.params['font'])
        del params
        # print(self.params['font'].family())

    def consvToggle(self):
        self.params['byconsv'] = self.checkConsv.isChecked()
        self.comboReference.setEnabled(self.checkConsv.isChecked())

    def rulerToggle(self):
        self.params['ruler'] = self.checkRuler.isChecked()

    def colorToggle(self):
        self.params['colors'] = self.checkColors.isChecked()

    def structureToggle(self):
        #print("Toggled structure")
        self.params['dssp'] = self.checkStructure.isChecked()
        """print("Toggled structure")
        if self.checkStructure.isEnabled():
            print("Setting to %s" % self.checkStructure.isChecked())
            self.params['dssp'] = self.checkStructure.isChecked()
            print("1",self.params['dssp'])
        else:
            print("DISABLED")
            print("2",self.params['dssp'])"""

    def changeTheme(self):
        self.params['theme'] = self.comboTheme.currentText()

    def changeFont(self):
        self.params['font'] = self.comboFont.currentFont()

    def changeFontSize(self):
        self.params['fontsize'] = self.spinFontSize.value()

    def showColorDesc(self):
        self.params['colordesc'] = self.checkColorDesc.isChecked()

    def structureActivate(self, state):
        self.checkStructure.setEnabled(state)
        if state:
            # print("Recalling setting of %s " % self.lastStruct)
            self.checkStructure.setChecked(self.lastStruct)
            self.buttonStructure.setEnabled(False)
        if not state:
            self.lastStruct = self.params['dssp']
            self.buttonStructure.setEnabled(True)
            # print("Deactivating, but keep setting of %s " % self.lastStruct)
            self.checkStructure.setChecked(False)
            # print("3",self.params['dssp'])
        del state


class CommentsPane(QWidget, comments_ui.Ui_Form):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)


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
        self.versionLabel.setText(__version__)

    def ok(self):
        self.done(1)
