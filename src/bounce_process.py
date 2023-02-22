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

import os, sys
sys.path.append('src')
sys.path.append('qt')
import logging
import traceback
from pathlib import Path
#silences error on program quit, as handler is deleted before logger
logging.raiseExceptions = False
logging.getLogger("numba").setLevel(logging.WARNING)
import warnings

warnings.filterwarnings('ignore', module='pyMRAW')

from PySide6 import QtGui
from PySide6.QtGui import QShortcut, QFont, QPixmap
from PySide6.QtWidgets import QMainWindow, QApplication, QProgressBar, QMessageBox, QDialog, QFileDialog, QSplashScreen
from PySide6.QtCore import QCoreApplication, Qt, Signal, Slot

from ui_bounce import Ui_Bounce
from ui_patterndlg import Ui_PatternDialog
from video_controller import VideoController
from video_evaluator import VideoEvaluator
from data_control import DataControl
from qthread_worker import Worker


class PatternDialog(QDialog, Ui_PatternDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.openBtn.clicked.connect(self.open_path)
        self.buttonBox.accepted.connect(lambda: self.quit(True))
        self.buttonBox.rejected.connect(lambda: self.quit(False))

    def open_path(self):
        pth = QFileDialog.getExistingDirectory(self,"Select root directory", "D:/Messungen/")
        self.rootPathTxt.setText(pth)

    @property
    def values(self):
        return (self.rootPathTxt.text(), self.patternTxt.text())

    def quit(self, accepted):
        if accepted:
            self.accept()
        else:
            self.reject()


class BounceAnalyzer(QMainWindow, Ui_Bounce):
    file_drop_event = Signal(list)
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
        self.batch_done = False
        self.batch_thread = None
        self.setAcceptDrops(True)

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
        self.pxScaleSpin.valueChanged.connect(self.data_control.update_scale)
        self.ballSizeSpin.valueChanged.connect(self.data_control.update_ball_size)
        self.startEvalBtn.clicked.connect(self.evaluator.video_eval)
        self.actionOpen.triggered.connect(self.videoController.open_file)
        self.actionBatch_Process.triggered.connect(self.start_batch_process)
        self.file_drop_event.connect(self.file_dropped)
        
        self.saveDataBtn.clicked.connect(self.data_control.save_dialog)

        # self.actionCalibrate_Scale.triggered.connect(self.videoController.calib_size)
        # self.actionDelete_Scale.triggered.connect(self.videoController.remove_size_calib)
        # shortcuts
        QShortcut(QtGui.QKeySequence("Space"), self, self.videoController.play_pause)
        QShortcut(QtGui.QKeySequence("Ctrl+S"), self, lambda: self.videoController.save_current_frame())

    
    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.file_drop_event.emit(links)
        else:
            event.ignore()

    @Slot(list)
    def file_dropped(self, files):
        if len(files)>1: QMessageBox.warning(self, "Warning", "Only first file will be loaded!")
        file = Path(files[0])
        if file.exists():
            logging.info(f"Loading file {str(file)}")
            if file.suffix == ".csv":
                self.data_control.load_data(file)
                self.tabWidget.setCurrentIndex(1)
            else:
                self.videoController.load_video(str(file))
                self.tabWidget.setCurrentIndex(0)

    def start_batch_process(self):
        dlg = PatternDialog(parent=self)
        if dlg.exec():
            root, pattern = dlg.values
            # self.batch_thread = Worker(self.batch_process, root, pattern)
            # self.batch_thread.start()
            self.batch_process(root, pattern)

    def set_done(self):
        self.batch_done = True
        
    def batch_process(self, root, pattern):
        glb = Path(root).rglob(pattern)
        for f in glb:
            try:
                self.auto_process(f)
            except Exception as e:
                res = QMessageBox.question(self,"Error encountered!", f"While prosessing the program encountered an error. Continue?\n\nError:\n{traceback.print_exc()}")
                if res == QMessageBox.StandardButton.Yes:
                    continue
                else:
                    return
                
            QApplication.processEvents()

        QMessageBox.information(self, "Done", "Batch processing done!")

    def auto_process(self, filename):
        logging.info(f"Process file {filename}")
        self.data_control.save_on_data_event = True
        self.videoController.load_video(filename)
        self.evaluator.do_video_eval()
        # self.evaluator.video_eval(callback=self.set_done)
        # while not self.batch_done: pass
        # self.batch_done = False


class App(QApplication):
    def __init__(self, argv, *args, **kwargs):
        super(App,self).__init__(*args, **kwargs)           
        pic = QPixmap('qt/maesure.png')
        self.splash = QSplashScreen(pic)#, Qt.WindowStaysOnTopHint)
        #splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash.setMask(pic.mask())
        self.splash.show()
        self.window = None

    def load_main(self):
        self.window = BounceAnalyzer()
        self.window.show()
        
        self.splash.finish(self.window) 

        


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
    app.load_main()
    # setup logging
    # global logger
    logger = initialize_logger("./log", app.window.textEdit)
    
    app.processEvents()

    # execute qt main loop
    sys.exit(app.exec())
