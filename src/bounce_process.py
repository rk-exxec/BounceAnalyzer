#     BounceAnalyzer is a porgam to analyze the bounces of objects
#     Copyright (C) 2023  Raphael Kriegl

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
sys.path.append('src')
sys.path.append('qt')
import logging
#silences error on program quit, as handler is deleted before logger
logging.raiseExceptions = False
logging.getLogger("numba").setLevel(logging.WARNING)
from PySide6 import QtGui
from PySide6.QtGui import QShortcut, QFont
from PySide6.QtWidgets import QMainWindow, QApplication, QProgressBar
from PySide6.QtCore import QCoreApplication

from ui_bounce import Ui_Bounce
from video_controller import VideoController
from video_evaluator import VideoEvaluator
from data_control import DataControl

class BounceAnalyzer(QMainWindow, Ui_Bounce):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.statusBar().setFont(QFont("Consolas",10))
        self.progressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setRange(0,100)
        self.progressBar.setValue(0)
        self.videoController = VideoController(self)
        self.data_control = DataControl(self.videoController, self)
        self.evaluator = VideoEvaluator(self.videoController, self.data_control, self, parent=self)

        self.videoController.load_video("data/ball_12bit_full.cihx")
        self.tabWidget.setCurrentIndex(0)
        self.register_action_events()


    def closeEvent(self, event):
        self.videoViewer.closeEvent(event)
        return super().closeEvent(event)

    def register_action_events(self):
        self.playBtn.clicked.connect(self.videoController.play)
        self.pauseBtn.clicked.connect(self.videoController.pause)
        self.seekBar.sliderMoved.connect(self.videoController.update_position)
        self.startEvalBtn.clicked.connect(self.evaluator.video_eval)
        self.actionOpen.triggered.connect(self.videoController.open_file)
        
        self.saveDataBtn.clicked.connect(self.evaluator.save_dialog)

        # self.actionCalibrate_Scale.triggered.connect(self.videoController.calib_size)
        # self.actionDelete_Scale.triggered.connect(self.videoController.remove_size_calib)
        # shortcuts
        QShortcut(QtGui.QKeySequence("Space"), self, self.videoController.play_pause)
        QShortcut(QtGui.QKeySequence("Ctrl+S"), self, lambda: self.videoController.save_current_frame())



class App(QApplication):
    def __init__(self, *args, **kwargs):
        super(App,self).__init__(*args, **kwargs)

        self.window = BounceAnalyzer()
        self.window.show()

def initialize_logger(out_dir, handlers=None):
    logger = logging.getLogger("bounce")
    logger.setLevel(logging.DEBUG)
     
    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    logger.addHandler(handler)

    if handlers:
        handlers.setLevel(logging.DEBUG)
        logger.addHandler(handlers)

    return logger

if __name__ == "__main__":

    # pyside6 settings config
    QCoreApplication.setOrganizationName("OTH Regensburg")
    QCoreApplication.setApplicationName("BounceProcess")

    # init application
    app = App(sys.argv)
    # setup logging
    # global logger
    logger = initialize_logger("./log", app.window.textEdit)
    app.processEvents()

    # execute qt main loop
    sys.exit(app.exec())
