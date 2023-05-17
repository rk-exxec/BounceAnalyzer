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

import logging

from pathlib import Path
from dataclasses import asdict
from scipy import stats
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Signal, Slot, QObject

from qthread_worker import Worker

from PIL import Image

from video_controller import VideoController
from data_classes import BounceData, VideoInfoPresets
from video_reader import IVideoReader

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from qt.ui_bounce import Ui_Bounce


class DataControl(QObject):
    """ class for data and file control """
    update_plot_signal = Signal(float,float)
    # update_data_signal = Signal(pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray)
    update_data_signal = Signal(BounceData, np.ndarray)
    data_update_done_signal = Signal()
    def __init__(self, video_controller, parent=None) -> None:
        super().__init__(parent=parent)
        self.ui: Ui_Bounce = None # set post init bc of parent relationship not automatically applied on creation in generated script

        self.video_controller: VideoController = video_controller
        self.bounce_data : BounceData = None
        self.streak_image: np.ndarray = None
        self._first_show = True

        self.video_path: Path = None
        self.ball_size = 2.5e-3
        self.pixel_scale = None
        self.accel_thresh = 1500.0
        self.bit_depth = 8
        self.save_on_data_event = False
        self.rel_threshold = 0.5
        self.target_path = None

        self._plot_thread: Worker = None
        self.ui: Ui_Bounce = self.parent()

        self.bounce_plot = self.ui.positionGraph
        self.streak_plot = self.ui.streakImage

        self.connect_signals()  


    def connect_signals(self):
        self.ui.saveDataBtn.clicked.connect(self.save_data)
        self.ui.saveDataBtn_2.clicked.connect(self.save_data)
        self.ui.saveDataAsBtn.clicked.connect(self.save_dialog)
        self.ui.saveDataAsBtn_2.clicked.connect(self.save_dialog)
        self.ui.deleteDataBtn.clicked.connect(self.delete_data)
        self.ui.accelThreshSpin.valueChanged.connect(self.set_accel_thresh)
        self.ui.relThreshSpin.valueChanged.connect(self.set_rel_thresh)
        self.update_data_signal.connect(self.update_data)
        self.video_controller.loaded_video_signal.connect(self.update_video_info)


    def set_accel_thresh(self, value):
        self.accel_thresh = value

    def set_rel_thresh(self, value):
        self.rel_threshold = value
        
    @Slot(str, IVideoReader)
    def update_video_info(self, name, reader: IVideoReader):
        self.video_path = Path(name)
        self.pixel_scale = reader.pixel_scale if reader.pixel_scale != 1.0 else None
        self.bit_depth = reader.color_bit_depth

    @Slot(float)
    def update_ball_size(self, value):
        self.ball_size = value/1000

    @Slot(float)
    def update_scale(self, value):
        if value == 0.0:
            self.pixel_scale = None
        else:
            self.pixel_scale = value

    # @Slot(pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray)
    @Slot(BounceData, np.ndarray)
    def update_data(self, bounce_data: BounceData, streak: np.ndarray):
        """ 
        add new datapoint to dataframe and invoke redrawing of table
        
        :param target_time: unused
        :param droplet: droplet data
        :param cycle: current cycle in case of repeated measurements
        """
        
        self.bounce_data = bounce_data
        # self.eval_data = eval_data
        self.streak_image = streak

        self.ui.tableView.redraw_table_signal.emit(pd.DataFrame.from_dict(asdict(bounce_data)))
        self.update_plots()
        # TODO add scatter overly for live plot widget, etc, do all datahandling in this datacontrol
        self.ui.tabWidget.setCurrentIndex(1)
        if self.save_on_data_event:
            self.save_data()
            self.save_on_data_event = False
        self.data_update_done_signal.emit()

    def update_plots(self):
        self.clear_plots()
        self.plot_image(self.streak_image, self.bounce_data)
        self.plot_graphs(self.bounce_data)
        self.set_info(self.bounce_data)

    def plot_graphs(self, data):
        self.ui.positionGraph.plot_graphs(data)

    def plot_image(self, streak, data):
        self.ui.streakImage.plot_image(streak, data)

    def set_info(self, data:BounceData):
        self.ui.corLbl.setText(f"{data.cor:0.3f}")
        self.ui.speedInLbl.setText(f"{data.speed_in:0.3f} m/s")
        self.ui.speedOutLbl.setText(f"{data.speed_out:0.3f} m/s")

        self.ui.maxDeformLbl.setText(f'{data.max_deformation*1000:0.3f} mm')
        self.ui.maxAccelLbl.setText(f'{data.max_acceleration:0.1f} m/s^2')
        self.ui.pxScaleLbl.setText(f'{data.video_pixel_scale*1000:.5f} mm/px')

    def clear_plots(self):
        self.ui.streakImage.clean()
        self.ui.positionGraph.clean()


    # @Slot(int)
    # def save_image(self, mag_pos, cycle, material_id, type='static'):
    #     """try to save droplet image if option selected

    #     :param cycle: current cycle for filename indexing
    #     :type cycle: int
    #     """
    #     if self.ui.saveImgsChk.isChecked():
    #         #self._cur_image_path.mkdir(exist_ok=True)
    #         self.ui.camera_ctl.save_image(self._temp_dir_handle.name + f'/img_{material_id}_{mag_pos}_{cycle}_{type}.png')
            

    def save_data(self, filename=None):
        """ saves data as json (can be loaded to view curves again) and as csv (for the extracted parameters). Also saves streak image."""
        if not filename:
            filename = self.video_path.with_suffix(".json")
        filename = Path(filename).with_suffix(".json")

        if self.bounce_data is not None:
            self.bounce_data.to_json_file(filename)

            eval_data = pd.DataFrame()
            eval_data["acceleration_thresh"] = [self.bounce_data.acceleration_thresh]
            eval_data["impact_idx"] = self.bounce_data.impact_idx
            eval_data["impact_time"] = self.bounce_data.impact_time    
            eval_data["release_idx"] = self.bounce_data.release_idx
            eval_data["release_time"] = self.bounce_data.release_time   
            eval_data["max_deformation"] = self.bounce_data.max_deformation
            eval_data["COR"] = self.bounce_data.cor
            eval_data["speed_in"] = self.bounce_data.speed_in
            eval_data["speed_out"] = self.bounce_data.speed_out
            eval_data["max_acceleration"] = self.bounce_data.max_acceleration
            eval_data["video_framerate"] = self.bounce_data.video_framerate
            eval_data["video_resolution"] = self.bounce_data.video_resolution#f"{w}x{h}"
            eval_data["video_num_frames"] = self.bounce_data.video_num_frames
            eval_data["video_pixel_scale"] = self.bounce_data.video_pixel_scale
            eval_data["video_name"] = self.bounce_data.video_name
            eval_data["img_rel_threshold"] = self.rel_threshold

            eval_data.to_csv(filename.parent/(filename.stem + "_eval.csv"), sep='\t', header=True, index=False)
        if self.streak_image is not None: Image.fromarray(self.streak_image).save(filename.with_stem(filename.stem + "_streak").with_suffix(".png"))

    def save_dialog(self):
        dlg = QFileDialog.getSaveFileName(parent=self.parent(), caption="Save Data", dir=str(self.video_path.with_suffix(".csv")), filter="Comma Separated Values (*.csv)")
        if dlg:
            self.save_data(dlg[0])

    def load_data(self, file):
        """ loads previously saved csv and json files
        will also check if json is in same directory as csv or streak image and then load that additionally
        """
        file = Path(file)
        self.clear_plots()

        # check if the wrong file was dropped by accident, and correct file names
        if file.suffix == ".csv":
            eval_file = file
            file = Path(file.with_stem(file.stem[:-5]))

        if file.exists() and file.suffix == ".json":
            data = BounceData.from_json_file(file)
            self.plot_graphs(data)
            self.set_info(data)

        streak_path = file.with_stem(file.stem + "_streak").with_suffix(".png")
        if streak_path.exists():
            img = np.asarray(Image.open(streak_path))
            self.plot_image(img, data)
        


    def delete_data(self):
        self.bounce_data = None
        self.clear_plots()
        self.ui.tableView.clear()

    def get_info_obj(self):
        info = VideoInfoPresets(
            length = len(self.video_controller.reader),
            shape = self.video_controller.reader.frame_shape,
            pixel_scale = self.pixel_scale,
            frame_rate = self.video_controller.reader.frame_rate,
            accel_thresh = self.accel_thresh,
            bit_depth=self.bit_depth,
            filename=str(self.video_path),
            ball_size=self.ball_size,
            rel_threshold=self.rel_threshold
        )
        return info
    
    @property
    def eval_params(self):
        return self.get_info_obj()


    # def clean_temp_dir(self):
    #     self._temp_dir_handle.cleanup()
    #     self._temp_dir_handle = tempfile.TemporaryDirectory()
