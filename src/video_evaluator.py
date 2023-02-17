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

from PySide6.QtWidgets import QFileDialog, QProgressDialog
from PySide6.QtCore import Signal, Slot, QObject
from ui_bounce import Ui_Bounce
from video_controller import VideoController
from data_control import DataControl
import numpy as np
import pandas as pd
import cv2
from scipy.ndimage import uniform_filter1d
from scipy.signal import savgol_filter
from numpy.polynomial import Polynomial
from numpy.polynomial import polynomial as P

class VideoEvaluator(QObject):
    update_progress_signal = Signal(float)
    def __init__(self, controller: VideoController, data_control: DataControl, ui, parent=None):
        super().__init__(parent=parent)
        self.ui: Ui_Bounce = ui
        self._video_controller = controller
        self._data_control = data_control
        self._progress: QProgressDialog = None
        self._thread = None
        self.update_progress_signal.connect(self.update_progress)

    def video_eval(self):
        self.prep_progress()
        # self._thread = threading.Thread(target=self.do_video_eval)
        # self._thread.start()
        self.do_video_eval()

    def do_video_eval(self):
           
        w,h = self._video_controller.reader.frame_shape
        N = self._video_controller.reader.number_of_frames
        dt =  1/self._video_controller.reader.frame_rate
        pixel_scale = self._video_controller.reader.pixel_scale
       
        streak = np.zeros((N,h), dtype=np.uint16)

        for i in range(N):
            streak[i] =  self._video_controller.reader._vr[i,:,w//2]

        streak = streak.T
        cvimg = 4096 - streak
        cvimg = cv2.medianBlur(cvimg, 5)#

        _, cvimg = cv2.threshold(cvimg, 1, 255, type=cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(cvimg.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # get the contour that has the least mean y value, which should be the upper most contour
        avg_y = [cont.T[1].mean() for cont in contours]
        idx = np.argmin(avg_y)
        contour = np.asarray(contours[idx]).squeeze().T

        # remove contour parts that touch the image border
        del_pos = np.argwhere(contour[1]==0)
        contour = np.delete(contour.T, del_pos, axis=0).T

        # remove duplicate x values
        unique_x, idx = np.unique(contour[0], return_index=True)
        contour_clean = contour.T[idx].T

        distance = np.array([contour_clean[0]*dt, contour_clean[1]*pixel_scale])

        velocity = np.gradient(distance[1], distance[0])

        down = np.argwhere(velocity < -10)
        up = np.argwhere(velocity > 10)
        contact_idx = self._video_controller.contact_frame
        contact_x, contact_y = self._video_controller.contact_pos
        contact_time = dt*contact_idx
        contact_y *= pixel_scale
        accel_thresh = -abs(self.ui.accelThreshSpin.value())

        velocity_f = uniform_filter1d(velocity, 10)
        velocity_fs = savgol_filter(velocity, 21, 5, mode="nearest")
        max_dist = distance[1].argmax()


        dist_linefit_down = Polynomial(P.polyfit(distance.T[:max_dist].T[0],distance.T[:max_dist].T[1],deg=1))
        dist_linefit_up = Polynomial(P.polyfit(distance.T[max_dist:max_dist+20].T[0],distance.T[max_dist:max_dist+20].T[1],deg=1))

        accel = np.gradient(velocity_f, distance[0])
        accel_s = np.gradient(velocity_fs, distance[0])
        accel_f = savgol_filter(accel_s, 21, 5, mode="constant")

        # jerk = np.gradient(accel_f, distance[0])

        touch_point = (np.argwhere(accel_f[contact_idx//2:]<=accel_thresh)[0] + contact_idx//2).item()
        touch_time = touch_point*dt + distance[0][0]

        max_deformation = np.abs(distance[1][touch_point] - distance[1].max()).squeeze()
        cof = abs(dist_linefit_up.coef[1] / dist_linefit_down.coef[1])
        max_acc = np.abs(accel_f).max()

        time_data = pd.DataFrame()
        eval_data = pd.DataFrame()

        time_data["Time"] = distance[0]
        time_data["Distance"] = distance[1]
        time_data["Velocity"] = velocity
        time_data["Acceleration"] = accel
        time_data["Velocity_Smooth"] = velocity_fs
        time_data["Acceleration_Smooth"] = accel_f
        time_data["Contact_Time"] = contact_time
        time_data["Contact_Idx"] = contact_idx
        time_data["Contact_Pos_X"] = contact_x
        time_data["Contact_Pos_Y"] = contact_y
        time_data["Accel_Thresh"] = accel_thresh
        time_data["Accel_Thresh_Trig_Idx"] = touch_point
        time_data["Accel_Thresh_Trig_Time"] = touch_time

        filename = self._data_control.video_path
        *_, material, height, magnet, spacing, _, _  = filename.parts

        time_data["Material"] = material.split("_")[-1].replace(".","")+"22"
        time_data["Drop_Height"] = float(height[1:])*1e-3
        time_data["Magnet"] = magnet
        time_data["Lamella_Spacing"] = spacing

        time_data["Video_Framerate"] = self._video_controller.reader.frame_rate
        time_data["Video_Res"] = f"{w}x{h}"
        time_data["Video_Num_Frames"] = N
        time_data["Video_Name"] = self._video_controller.reader._filename

        eval_data["Accel_Thresh"] = [accel_thresh]
        eval_data["Accel_Thresh_Trig_Idx"] = touch_point
        eval_data["Accel_Thresh_Trig_Time"] = touch_time
        eval_data["Max_Deformation"] = max_deformation
        eval_data["COR"] = cof
        eval_data["Max_Acceleration"] = max_acc
        eval_data["Material"] = material.split("_")[-1].replace(".","")+"22"
        eval_data["Drop_Height"] = float(height[1:])*1e-3
        eval_data["Magnet"] = magnet
        eval_data["Lamella_Spacing"] = spacing    
        eval_data["Contact_Time"] = contact_time
        eval_data["Contact_Idx"] = contact_idx
        eval_data["Contact_Pos_X"] = contact_x
        eval_data["Contact_Pos_Y"] = contact_y
        eval_data["Video_Framerate"] = self._video_controller.reader.frame_rate
        eval_data["Video_Res"] = f"{w}x{h}"
        eval_data["Video_Num_Frames"] = N
        eval_data["Video_Name"] = self._video_controller.reader._filename

        self._data_control.update_data_signal.emit(time_data, eval_data, contour_clean, streak)
        self.update_progress_signal.emit(1)

    def prep_progress(self):
        pbar = self.parent().window().progressBar
        pbar.setValue(0)

    @Slot(float)
    def update_progress(self, frac):
        pbar = self.parent().window().progressBar
        pbar.setValue(int(frac*100))

    def get_data(self):
        return self.data_frame

    def save_data(self, filename):
        self.data_frame.to_csv(filename, sep='\t', header=True, index=False)

    def save_dialog(self):
        dlg = QFileDialog.getSaveFileName(parent=self.parent(), caption="Save Data", dir=f"D:/Messungen/Angle_Measurements/{self._video_controller.video_name}.csv", filter="Comma Separated Values (*.csv)")
        if dlg:
            self.save_data(dlg[0])
        