#     BounceAnalyzer is a program to analyze the bounces of objects
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

import os
from pathlib import Path
from video_preview import VideoPreview
from video_reader import IVideoReader, VideoReaderMem

import numpy as np
import pandas as pd

import cv2

import logging
logger = logging.getLogger(__name__)
from PySide6.QtCore import  Slot, QTimer, Signal, QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog


class VideoController(QObject):
    """ 
    controller for the video player
    """
    loaded_video_signal = Signal(str, IVideoReader)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = parent
        self.player: VideoPreview = self.ui.videoViewer
        self.player.update_contact_pos_event.connect(self.update_contact_pos)
        # self.reader: VideoReader = None
        self.reader: IVideoReader = None
        self._play_timer = QTimer()
        self._play_timer.timeout.connect(self.timer_handler)
        self._video_limits = [0,None]
        self.video_name = ""
        self.current_frame_pos = 0
        self.contact_pos = 0
        self.contact_frame = 0
        

    @Slot()
    def play(self):
        logging.debug(f"Start playback of video @ {self.reader.frame_rate} FPS")
        self._play_timer.setInterval(1000/self.reader.frame_rate)
        self._play_timer.start()
        #self.media_player.play()

    @Slot()
    def pause(self):
        logging.debug("Pause playback of video")
        self._play_timer.stop()
        #self.media_player.play()

    @Slot()
    def play_pause(self):
        if self._play_timer.isActive():
            logging.debug("Pause playback of video")
            self._play_timer.stop()
        else:
            logging.debug(f"Start playback of video @ {self.reader.frame_rate} FPS")
            self._play_timer.setInterval(1000/self.reader.frame_rate)
            self._play_timer.start()

    @Slot()
    def on_eval_btn_clicked(self):
        self.eval()

    @Slot(int,int)
    def update_contact_pos(self, pos_x, pos_y):
        self.contact_pos = (pos_x, pos_y)
        self.contact_frame = self.current_frame_pos

    def get_iterframes(self, stepsize=5):
        return self.reader[slice(*self._video_limits,stepsize)]



    def get_num_frames(self, stepsize=5):
        tot_num = len(self.reader)
        return len(range(tot_num)[slice(*self._video_limits,stepsize)])

    @Slot()
    def open_file(self):
        path,_ = QFileDialog.getOpenFileName(self.ui.centralwidget, "Select Video File", r"G:\Messungen", "Video Files (*.cihx *.avi *.mp4 *.mkv *.m4a *.webm *.flv *.wmv)")
        if path:
            self.load_video(path)

    def load_video(self, path):
        # self.reader = VideoReader(str(path))
        self.reader = VideoReaderMem(str(path))
        self.video_name = Path(path).stem
        self.ui.seekBar.setMaximum(len(self.reader) - 1)
        self.ui.seekBar.setMinimum(0)
        self.player.update_shape(self.reader.frame_shape)
        self.read_image(self.ui.seekBar.sliderPosition())
        self.loaded_video_signal.emit(str(path), self.reader)

    
    def read_image(self, pos):
        frame = self.reader[pos]
        self._raw_image = frame
        self.player.update_image(frame)
        

    @Slot()
    def timer_handler(self):
        if not self.advance_image():
            self._play_timer.stop()
        self.ui.seekBar.setValue(self.current_frame_pos)

    def advance_image(self):
        if self.current_frame_pos < len(self.reader) - 1:
            self.read_image(self.current_frame_pos + 1)
            self.current_frame_pos += 1
            return True
        else:
            self.read_image(0)
            self.current_frame_pos = 0
            return True

    @Slot(int)
    def update_position(self, pos):
        self.read_image(pos)
        self.current_frame_pos = pos


    def save_current_frame(self, raw=True):
        dlg = QFileDialog.getSaveFileName(parent=self.ui, caption="Save Data", dir=r"C:\Users\krr38985\Documents\Python\DropletEval", filter="Image_Files (*.bmp *.png)")
        if dlg:
            im = self.player.get_image()
            im = cv2.cvtColor(im,cv2.COLOR_GRAY2RGB)
            from PIL import Image
            Image.fromarray(im).save(dlg[0])

    # @Slot()
    # def calib_size(self):
    #     """ 
    #     map pixels to mm 
        
    #     - use needle mask to closely measure needle
    #     - call this fcn
    #     - enter size of needle
    #     - fcn calculates scale factor and saves it to droplet object
    #     """
    #     if self.player._needle_mask.isHidden():
    #         QMessageBox.warning(self.ui, "Error setting scale", "The needle mask needs to be active and set to a known width!")
    #         return
    #     # get size of needle mask
    #     rect = self.player._mask

    #     # do oneshot eval and extract height from droplet, then calc scale and set in droplet
    #     res,ok = QInputDialog.getDouble(self.ui,"Size of calib element", "Please enter the size of the test subject in mm:", 0, 0, 100)
    #     if not ok or res == 0.0:
    #         return
        
    #     QMessageBox.information(self.ui, "Success", f"Scale set to {res / rect[2]:.3f} mm/px")
    #     logging.info(f"set image to real scale to {res / rect[2]}")

    # @Slot()
    # def remove_size_calib(self):
    #     Droplet.delete_scale()
