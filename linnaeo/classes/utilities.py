import logging
import sys
import traceback
from io import StringIO
from math import floor, trunc
from typing import TextIO

import numpy
from Bio.Blast import NCBIWWW, NCBIXML
from Bio.PDB import FastMMCIFParser, DSSP, PDBIO
from PyQt5.QtCore import pyqtSignal, QThread, QTimer, Qt, QTemporaryDir, QTemporaryFile
import clustalo

"""
Additional classes and functions that are used within Linnaeo, but are not responsible for viewing data.
"""


class SeqThread(QThread):
    """
     Determines which type of redraw should occur based on the values of rulers, colors, and "fancy", then
     does this in a separate thread.
     """
    finished = pyqtSignal()

    def __init__(self, *args, fancy=True, parent=None):
        QThread.__init__(self, parent)
        self.seqLogger = logging.getLogger("SEQDRAW")
        self.html = None
        self.seqs = args[0]
        self.chars = args[1]
        self.lines = args[2]
        self.rulers = args[3]
        self.colors = args[4]
        self.fancy = fancy

    def run(self):
        if self.fancy:
            self.html = redrawFancy(self.seqs, self.chars, self.lines, self.rulers, self.colors)
        else:
            self.html = redrawBasic(self.seqs, self.chars, self.lines, self.rulers)


def redrawBasic(seqs, chars, lines, rulers=False):
    """ Black and white only; keeps space for ruler but does not calculate the ruler, which helps with speed."""
    html = ["<pre>\n"]
    n = 0
    for line in range(lines):
        if rulers:
            html.append("\n")
        start = n * chars
        end = n * chars + chars
        if line == lines - 1:
            end = start + len(seqs[0][start:])
        for i in range(len(seqs)):
            html.append("".join([x[0][-8] for x in seqs[i][start:end]]))#+"\n")
            if line == lines-1:
                label = str(seqs[i][end - 1][1])
                if label == "0":
                    for y in range(chars):
                        label = str(seqs[i][end - 1 - y][1])
                        if label != "0":
                            break
                html.append(" "*2 + label + "\n")
            else:
                html.append("\n")

        html.append("\n")
        n+=1
    html.append("</pre>")
    return "".join(html)


def redrawFancy(seqs, chars, lines, rulers=True, colors=True):
    """ Fancy like the name implies. Called at the end of resize events. Keeps your opinion on colors and rulers. """
    html = ["<pre>"]
    n = 0
    for line in range(lines):
        start = n * chars
        end = start + len(seqs[0][start:]) if line == lines - 1 else n * chars + chars
        gap = (n * chars + chars) - end
        if rulers:
            html.append(str(buildRuler(chars, gap, start, end))+"\n")
        for i in range(len(seqs)):
            if colors:
                html.append("".join([x[0] for x in seqs[i][start:end]]))#+"\n")
            else:
                html.append("".join([x[0][-8] for x in seqs[i][start:end]]))# + "\n")
            if line == lines-1:
                label = str(seqs[i][end - 1][1])
                if label == "0":
                    for y in range(chars):
                        label = str(seqs[i][end - 1 - y][1])
                        if label != "0":
                            break
                html.append(" "*2 + label + "\n")
            else:
                html.append("\n")
        if line < lines -1:
            html.append(" "*chars+"\n")
        n += 1
    html.append("</pre>")
    return "".join(html)


def checkName(name, titles, layer=0):
    """ Tool for checking a list of titles. Used for generating a new title if it is duplicated"""
    # TODO: This isn't perfect, as it prevents duplicates of folders too... but that won't be fixed here.
    # TODO: Fix it in the item model.
    if name not in titles:
        # SAFE! You can add name and return
        finalname = name
    elif name[-2] == "_" and int(name[-1]):
        # if there's already a name with an _1, add a number
        newlayer = layer+1
        newname = str(name[:-1] + str(newlayer))
        finalname, titles = checkName(newname, titles, layer=newlayer)
        if layer > 0:
            return finalname, titles
    else:
        # It's a duplicate! Give it an underscore.
        newlayer = layer + 1
        newname = str(name + "_" + str(newlayer))
        # Run the check again with the new name
        finalname, titles = checkName(newname, titles, layer=newlayer)
        if layer > 0:
            return finalname, titles
    if layer == 0:
        titles.append(finalname)
    return finalname, titles


def iterTreeView(root):
    """
    Internal function for iterating a TreeModel. Shamelessly stolen from StackOverflow. It is wonderful though.
    Usage: for node in iterTreeView(root): --> returns all the nodes.
    """
    def recurse(parent):
        for row in range(parent.rowCount()):
            child = parent.child(row)
            yield child
            if child.hasChildren():
                yield from recurse(child)
    if root is not None:
        yield from recurse(root)


def nodeSelector(tree, model):
    """ Utility for selection of nodes and anything under a folder. """
    seqs = []
    copied = []
    indices = tree.selectedIndexes()
    if indices:
        for index in indices:
            node = model.itemFromIndex(index)
            if not node.data(role=Qt.UserRole + 2):
                for subnode in iterTreeView(model.itemFromIndex(index)):
                    i = model.indexFromItem(subnode)
                    copied.append(i)
                    seqr = subnode.data(role=Qt.UserRole + 2)[0]
                    seqs.append(seqr)
            if node.data(role=Qt.UserRole + 2) and index not in copied:
                copied.append(index)
                seqr = node.data(role=Qt.UserRole + 2)[0]
                seqs.append(seqr)
    return indices, seqs


def buildRuler(chars,gap,start,end,interval=False):
    # TODO: Consider putting numbers at left and right, as in normal alignments. Particularly if also showing SS.
    """ This version uses even spacing of the numbers (either 10 or 20 depending on screen width) but looks messy. """
    ruler = None
    if interval:
        if start != end:
            interval = 10 if chars < 100 else 20
            labels = list(numpy.arange(round(start, -1), round(end, -1), interval))
            #print(start + 1, end, labels)
            if len(labels) == 1:
            #    print(labels[0])
                if labels[0] <= (start + 1):
            #        print("removed ", labels[0])
                    labels.pop(0)
                elif labels[0] - (start+1) < len(str(labels[-1]))*2+2:
            #        print("removed ", labels[0])
                    labels.pop(0)
            if len(labels) > 1:
                rm = []
                for x in range(2):
            #        print(labels[x])
                    if labels[x] - (start+1) < len(str(labels[-1]))*2+2:
            #            print("Removed ",labels[x])
                        rm.append(labels[x])
                        if len(labels) <= 1:
                            break
                    if end - labels[-x] < len(str(labels[-1]))*2+2:
            #            print("Removed ",labels[-x])
                        rm.append(labels[-x])
                [labels.remove(x) for x in rm]
            labels.insert(0, start + 1)
            if end-(start+1) >= len(str(start+1)) + len(str(end)) + 2:
                labels.append(end)
            #print(labels)
            rulel = ['<u>' + str(labels[0])[0] + '</u>' + str(labels[0])[1:]]
            for x in labels[1:]:
                prevx = labels[labels.index(x) - 1]
                xlab = len(str(x))
                if labels.index(x) == 1 and len(str(prevx)) > 1:
                    # Different for first space because I left align the first number.
                    xlab = len(str(x)) + len(str(prevx)) - 1
                spacer = x - prevx - xlab
             #   print("Spacer is (%s-%s)-%s=%s " % (x, prevx, xlab, spacer))
                rulel.append("&nbsp;" * spacer)
                rulel.append(str(x)[:-1] + '<u>' + str(x)[-1:] + '</u>')
            ruler = "".join(rulel)
    else:
        # TODO: THIS IS BUGGY. ADD UNDERLINES. HAVE ALL ALIGNED (NOT ALL BUT LAST LINE)
        """
        This version is cleaner but the numbers end up with random numbers. Calculates the spacing
        and labeling based on the width of the screen. Pretty computationally intensive,
        so I make a point to hide it (and the colors) when resizing.
        """
        if start != end:
            if gap != 0 and chars != end-start:
                # Have to adjust the spacing for the last line
                # Don't go below 8 chars so the numbers don't merge.
                # May want to extend to 10... rare but some seqs are >1000
                if end - start > 8:
                    chars = (end - start)
                else:
                    chars = 8
            # labels is all the possible numbers between the start and end
            labels = list(range(start+1, end+1))
            spacing = chars
            # My hacky way to add more numbers as the screen increases in size.
            # Spacing is the distance between numbers of the rulers.
            # Not all numbers are divisible by 2, 3, etc so there are uneven spaces, which I account for badly below.
            # TODO: Consider changing this to floor?
            if chars < 20:
                pass
            elif 20 <= chars < 60:
                spacing = int(chars/2)
            elif 60 <= chars < 100:
                spacing = int(chars/3)
            elif 100 <= chars < 150:
                spacing = int(chars/4)
            elif 150 <= chars:
                spacing = int(chars/5)
            n = 0
            speclabels = []
            rulerlist = []
            # spec labels are the numbers that are actually used based on the spacing.
            while n < chars:
                speclabels.append(labels[n])
                n+=spacing
            if labels[-1] not in speclabels:
                # a little hack because sometimes the end doesn't  get added
                speclabels.append(labels[-1])
            for n in range(1,4):
                # another little hack for when math makes it so there are two labels right next to each other at the end
                if labels[-1]-n in speclabels:
                    speclabels.remove(labels[-1]-n)
            if len(speclabels)>2:
                # more complicated logic for when there are multiple labels
                # builds a list (compressed to a string) of the labels and spacing, accounting for the length of the numbers
                count = range(1,len(speclabels))
                for x in count:
                    if x == count[-1]:
                        #rulerlist.append('<u>'+str(speclabels[x - 1])+'</u>')
                        rulerlist.append(str(speclabels[x - 1]))
                        rulerlist.append(" "*(chars - len(str("".join(rulerlist)))-len(str(speclabels[x]))))
                        rulerlist.append(str(speclabels[x]))
                    else:
                        rulerlist.append(str(speclabels[x-1]))
                        first = 0
                        if x == count[0]:
                            first = len(str(speclabels[x-1]))
                        next = len(str(speclabels[x]))
                        rulerlist.append(" "*(spacing - next - first))
                ruler = "".join(rulerlist)
            elif len(speclabels)==2:
                # Ah! so easy.
                ruler = str(start + 1) + " " * (chars - len(str(start + 1)) - len(str(end))) + str(end)
            else:
                # Just show a single number.
                ruler = str(start+1)
    return ruler


class BlastThread(QThread):
    finished = pyqtSignal(StringIO)

    def __init__(self, seq, parent=None):
        QThread.__init__(self, parent)
        self.seq = seq
        self.result = None

    def run(self):

        print("BLASTING SEQUENCE: ", self.seq.format('fasta'))
        blast = NCBIWWW.qblast('blastp', 'refseq_protein', str(self.seq.format('fasta')))
        print("BLAST COMPLETE")
        #blast = "yay"
        print(type(blast))
        self.finished.emit(blast)

        '''struct = self.args[0]
        tmp = QTemporaryFile()
        run = {}
        if tmp.open():
            io = PDBIO()
            io.set_structure(struct)
            io.save(tmp.fileName())
            dssp = DSSP(struct[0], tmp.fileName(), dssp='mkdssp')
            for key in dssp.keys():
                run[dssp[key][0]] = dssp[key][2]
            self.sstruct = run'''

class DSSPThread(QThread):
    def __init__(self, args, parent=None):
        QThread.__init__(self, parent)

class AlignThread(QThread):
    """
    Clustal Omega is run in a separate thread. Currently have no idea how to access the alignment order;
    I'm hoping there is a way, rather than returning it with the input order.
    I can't find anything in the source code of ClustalO for the API though, sadly.
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        self.clustalLogger = logging.getLogger("ClustalO")
        self.args = list(args)
        parent = self.args[0]
        self.args.pop(0)
        QThread.__init__(self, parent)
        self.kwargs = kwargs
        self.aligned = {}
        #self.clustalLogger.debug("Thread for ClustalO created")

    def run(self):
        try:
            result = clustalo.clustalo(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.aligned = result
            self.clustalLogger.debug("Thread returned alignment successfully")


class ProcTimerThread(QThread):
    """
    Thread for the timer, because Windows complains like hell otherwise.
    For memory and CPU usage refresh.
    """
    timeout = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.processTimer = QTimer()
        self.processTimer.setInterval(1000)
        self.processTimer.timeout.connect(self.timerDone)
        self.processTimer.start()

    def timerDone(self):
        self.timeout.emit()
'''
class ResizeTimerThread(QThread):
    """
    Thread for the timer, because Windows complains like hell otherwise.
    Also used for resizing with a super short countdown
    """
    timeout = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.processTimer = QTimer()
        #self.processTimer.setSingleShot(True)
        self.processTimer.setInterval(500)
        self.processTimer.timeout.connect(self.timerDone)

    def timerDone(self):
        self.timeout.emit()

    def run(self):
        self.processTimer.start()
'''



