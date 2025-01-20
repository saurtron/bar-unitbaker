import os
import sys
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QTextEdit, QProgressBar, QSizeGrip

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.dirname(script_dir)
sys.path.append(script_dir)

import unitbake
import baker
import prebake

class Thread(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(float)

    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)

    def setMethod(self, cb):
        if not self.isRunning():
            baker.set_progress_cb(self.report_progress)
            self.cb = cb

    def report_progress(self, val, text=None):
        self.emit_progress(val)
        if text:
            self.log.emit(str(text))

    def emit_log(self, text):
        self.log.emit(str(text))

    def emit_progress(self, val):
        self.progress.emit(val)

    def run(self):
        try:
            self.cb()
        except Exception as e:
            self.emit_log("Exception!!:")
            self.emit_log("Error: "+str(e))
            self.emit_progress(1.0)
            raise e

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.create_widgets()
        self._worker = Thread(self)
        self._worker.log.connect(self.log)
        self._worker.progress.connect(self.report_progress)
        self._worker.started.connect(lambda: self.log('start'))
        self._worker.finished.connect(lambda: self.workerFinished())

    def workerFinished(self):
        self.button_bake.setEnabled(True)
        self.button_prebake.setEnabled(True)
        self.log("Finished")
        self.pbar.reset()
        self.pbar.setEnabled(False)

    def log(self, txt):
        self.logOutput.append(txt)

    def report_progress(self, value):
        self.pbar.setValue(int(value*100.0))

    def create_widgets(self):
        layout_buttons = QVBoxLayout()
        hlayout = QHBoxLayout()
        layout_content = QVBoxLayout()

        # buttons
        button = QPushButton("Prebake")
        button.clicked.connect(self.prebake)

        layout_buttons.addWidget(button)
        self.button_prebake = button

        button = QPushButton("Bake")
        button.clicked.connect(self.bake)

        layout_buttons.addWidget(button)
        self.button_bake = button

        layout_buttons.addStretch()
        hlayout.addLayout(layout_buttons)

        # content
        logOutput = QTextEdit()
        logOutput.setReadOnly(True)
        logOutput.setLineWrapMode(QTextEdit.NoWrap)
        self.logOutput = logOutput
        layout_content.addWidget(logOutput)

        layout_bar = QHBoxLayout()
        self.pbar = QProgressBar(self)
        layout_bar.addWidget(self.pbar)

        self.size_grip = QSizeGrip(self)
        layout_bar.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        layout_content.addLayout(layout_bar)

        hlayout.addLayout(layout_content)

        # top layout widget
        widget = QWidget()
        widget.setLayout(hlayout)
        self.setCentralWidget(widget)
        self.pbar.setEnabled(False)

    def prebake(self):
        self.pbar.setEnabled(True)
        self.button_bake.setEnabled(False)
        self.button_prebake.setEnabled(False)
        self.logOutput.clear()
        self.logOutput.append("Prebake")
        self._worker.setMethod(prebake.prebake)
        self._worker.start()

    def bake(self):
        self.pbar.setEnabled(True)
        self.button_bake.setEnabled(False)
        self.button_prebake.setEnabled(False)
        self.logOutput.clear()
        self.logOutput.append("Bake")
        self._worker.setMethod(baker.bake_all)
        self._worker.start()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
