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

from enum import Enum
import logging
import os

from pathlib import Path, PurePath
import tempfile
from distutils.dir_util import copy_tree
import glob
import time
from datetime import datetime
from scipy import stats
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QGroupBox, QMessageBox
from PySide6.QtCore import Signal, Slot, QObject

from qthread_worker import Worker

from typing import TYPE_CHECKING

from video_controller import VideoController
if TYPE_CHECKING:
    from qt.ui_bounce import Ui_Bounce

class DataControl(QObject):
    """ class for data and file control """
    update_plot_signal = Signal(float,float)
    update_data_signal = Signal(pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray)
    def __init__(self, video_controller, parent=None) -> None:
        super().__init__(parent=parent)
        self.ui: Ui_Bounce = None # set post init bc of parent relationship not automatically applied on creation in generated script

        self.video_controller: VideoController = video_controller
        self.data : pd.DataFrame = None
        self.eval_data : pd.DataFrame = None
        self.streak_image = None
        self._first_show = True
        self.video_path: Path = None

        self.ui: Ui_Bounce = self.parent()
        self.connect_signals()  


    def connect_signals(self):
        self.ui.saveDataBtn.clicked.connect(self.save_data)
        self.ui.saveDataBtn_2.clicked.connect(self.save_data)
        self.ui.saveDataAsBtn.clicked.connect(self.save_dialog)
        self.ui.saveDataAsBtn_2.clicked.connect(self.save_dialog)
        self.ui.deleteDataBtn.clicked.connect(self.delete_data)
        self.update_data_signal.connect(self.update_data)
        self.video_controller.loaded_video_signal.connect(self.update_video_info)
        
    @Slot(str)
    def update_video_info(self, name):
        self.video_path = Path(name)

    @Slot(pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray)
    def update_data(self, data:pd.DataFrame, eval_data:pd.DataFrame, contour:np.ndarray, strk_img:np.ndarray):
        """ 
        add new datapoint to dataframe and invoke redrawing of table
        
        :param target_time: unused
        :param droplet: droplet data
        :param cycle: current cycle in case of repeated measurements
        """
        
        self.data = data
        self.eval_data = eval_data
        self.streak_image = strk_img

        self.ui.tableView.redraw_table_signal.emit(data)
        self.clear_plots()
        # TODO add scatter overly for live plot widget, etc, do all datahandling in this datacontrol
        self.ui.streakImage.set_image(strk_img)
        self.ui.streakImage.plot(contour, 0, 1, "", "","","","r")
        self.ui.distanceGraph.plot(data, "Time", "Distance", "Time", "Distance", "s", "m", "g")
        self.ui.distanceGraph.vline(eval_data["Contact_Time"].item(), "y")
        self.ui.velocityGraph.plot(data, "Time", "Velocity_Smooth", "Time", "Velocity", "s", "m/s", "g")
        self.ui.velocityGraph.scatter(data, "Time", "Velocity", "Time", "Velocity", "s", "m/s", "r")
        self.ui.velocityGraph.vline(eval_data["Contact_Time"].item(), "y")
        self.ui.accelGraph.plot(data, "Time", "Acceleration_Smooth", "Time", "Acceleration", "s", "m/s^2", "g", si_prefix=False)
        self.ui.accelGraph.scatter(data, "Time", "Acceleration", "Time", "Acceleration", "s", "m/s^2", "r")
        self.ui.accelGraph.vline(eval_data["Contact_Time"].item(), "y")

        self.ui.corLbl.setText(str(eval_data["COR"].item()))
        self.ui.maxDeformLbl.setText(str(eval_data["Max_Deformation"].item()))
        self.ui.maxAccelLbl.setText(str(eval_data["Max_Acceleration"].item()))

        self.ui.tabWidget.setCurrentIndex(1)

    def clear_plots(self):
        self.ui.streakImage.clear()
        self.ui.distanceGraph.clear()
        self.ui.velocityGraph.clear()
        self.ui.accelGraph.clear()


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
        if not filename:
            filename = self.video_path.with_suffix(".csv")
        filename = Path(filename)
        if not self.data.empty: self.data.to_csv(filename, sep='\t', header=True, index=False)
        if not self.eval_data.empty: self.eval_data.to_csv(filename.parent/(filename.stem + "_eval.csv"), sep='\t', header=True, index=False)

    def save_dialog(self):
        dlg = QFileDialog.getSaveFileName(parent=self.parent(), caption="Save Data", dir=str(self.video_path.with_suffix(".csv")), filter="Comma Separated Values (*.csv)")
        if dlg:
            self.save_data(dlg[0])

    def delete_data(self):
        self.data = pd.DataFrame()
        self.eval_data = pd.DataFrame()
        self.clear_plots()
        self.ui.tableView.clear()

    # def clean_temp_dir(self):
    #     self._temp_dir_handle.cleanup()
    #     self._temp_dir_handle = tempfile.TemporaryDirectory()


def export_data_csv(data: pd.DataFrame, filename, sep='\t'):
    """ Export data as csv with selected separator

    :param filename: name of file to create and write data to
    """
    with open(filename, 'w', newline='') as f:
        if data is not None:
            data.to_csv(f, sep=sep, index=False)

def export_data_excel(data: pd.DataFrame, filename: Path):
    """ Export data as csv with selected separator

    :param filename: name of file to create and write data to
    """
    filename = Path(filename).with_suffix(".xlsx")
    with pd.ExcelWriter(filename) as f:
    # with open(filename, 'wb') as f:
        if data is not None:
            data.to_excel(f, index=False, sheet_name="RawData")
            calc_mean_and_error(data).to_excel(f, index=False, sheet_name="MeanAndError")
            calc_anova(data).to_excel(f, index=True, sheet_name="ANOVA_One_Way")

def calc_mean_and_error(data: pd.DataFrame) -> pd.DataFrame:
    grouped_df = data[['Left_Angle', 'Right_Angle', 'R2', 'Drplt_Vol', 'Magn_Pos', 'Magn_Field']].groupby('Magn_Pos',sort=False)
    num_points_per_group = grouped_df.size().values
    mean_df = grouped_df.mean()

    # standard deviation
    mean_df[['Left_Angle_SDEV','Right_Angle_SDEV']] = grouped_df[['Left_Angle','Right_Angle']].std()

    # standard error, 1 sigma confidence interval
    mean_df[['Left_Angle_SEM_68','Right_Angle_SEM_68']] = grouped_df[['Left_Angle','Right_Angle']].sem()

    # standard error, 2 sigma confidence interval - t distribution
    t_fac_95_conf_int = stats.t.ppf(0.95, num_points_per_group) # factor according to https://en.wikipedia.org/wiki/Student%27s_t-distribution
    mean_df[['Left_Angle_SEM_95','Right_Angle_SEM_95']] = mean_df[['Left_Angle_SEM_68','Right_Angle_SEM_68']].multiply(t_fac_95_conf_int, axis=0)

    # standard error, 3 sigma confidence interval - t distribution
    t_fac_99_conf_int = stats.t.ppf(0.997, num_points_per_group)
    mean_df[['Left_Angle_SEM_99','Right_Angle_SEM_99']] = mean_df[['Left_Angle_SEM_68','Right_Angle_SEM_68']].multiply(t_fac_99_conf_int, axis=0)

    mean_df = mean_df.reset_index()
    return mean_df

def calc_anova(data: pd.DataFrame) -> pd.DataFrame:
    left_angle_grps = [d['Left_Angle'] for _, d in data[['Left_Angle', 'Magn_Pos']].groupby('Magn_Pos',sort=False)]
    right_angle_grps = [d['Right_Angle'] for _, d in data[['Right_Angle', 'Magn_Pos']].groupby('Magn_Pos',sort=False)]
    left_F, left_p = stats.f_oneway(*left_angle_grps)
    right_F, right_p = stats.f_oneway(*right_angle_grps)
    return pd.DataFrame(
        data=[[left_F, right_F], ['',''], [left_p, right_p], [left_p < 0.05, right_p < 0.05], [left_p < 0.01, right_p < 0.01]], 
        index=['F', '','p', 'Sig 5%', 'Sig 1%'], 
        columns=['Left_Angle', 'Right_Angle']
        )