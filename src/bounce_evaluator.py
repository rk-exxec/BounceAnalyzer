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
from qthread_worker import Worker, CallbackWorker

import numpy as np
import pandas as pd
import cv2
from scipy.ndimage import uniform_filter1d
from scipy.signal import savgol_filter, wiener
from numpy.polynomial import Polynomial
from numpy.polynomial import polynomial as P

from bounce_data import BounceData

class BounceEvaluator(QObject):
    update_progress_signal = Signal(float)
    video_eval_done_signal = Signal()
    def __init__(self, controller: VideoController, data_control: DataControl, ui, parent=None):
        super().__init__(parent=parent)
        self.ui: Ui_Bounce = ui
        self._video_controller = controller
        self._data_control = data_control
        self._thread = None
        self.update_progress_signal.connect(self.update_progress)

    def bounce_eval(self, callback=None):
    #     self.prep_progress()
    #     if callback: 
    #         self._thread = CallbackWorker(self.do_bounce_eval, slotOnFinished=callback)
    #     else:
    #         self._thread = Worker(self.do_bounce_eval)
    #     self._thread.start()
    #     # self.do_video_eval()

    # def do_bounce_eval(self):
           
        w,h = self._video_controller.reader.frame_shape
        N = self._video_controller.reader.number_of_frames
        dt =  1/self._video_controller.reader.frame_rate
        pixel_scale = (0.0000197)#self._video_controller.reader.pixel_scale
        # contact_idx = self._video_controller.contact_frame
        # contact_x, contact_y = self._video_controller.contact_pos
        # contact_time = dt*contact_idx
        # contact_mm = contact_y * pixel_scale
        accel_thresh = -abs(self.ui.accelThreshSpin.value())
       
        # streak = np.zeros((N,h), dtype=np.uint16)

        # for i in range(N):
        #     streak[i] =  self._video_controller.reader._vr[i,:,contact_x]
        # streak = streak.T
        streak = self._video_controller.reader._vr.min(axis=2).T

        contour = self.find_contour(streak)

        contour_clean = self.clean_contour(contour, N)

        if not self._data_control.pixel_scale:
            pixel_scale = self.get_scale(streak, contour_clean[0][0])
        else: pixel_scale = self._data_control.pixel_scale

        distance = np.array([contour_clean[0]*dt, contour_clean[1]*pixel_scale])
        # 
        distance_f = savgol_filter(distance[1], 21, 4, mode="interp")
        # distance_f = wiener(distance[1], 31)
        # distance_f = uniform_filter1d(distance[1],8)

        velocity = np.gradient(distance[1], distance[0])
        velocity_fs = np.gradient(distance_f, distance[0])#savgol_filter(velocity, 21, 5, mode="nearest")

        accel = np.gradient(velocity, distance[0])
        accel_fs = np.gradient(velocity_fs, distance[0])
        # accel_fs = savgol_filter(accel_s, 21, 5, mode="constant")

        max_acc_idx = np.abs(accel_fs).argmax()
        max_acc = accel_fs[max_acc_idx]

        # image index and time where acceleration crosses threshold (near max accel)
        touch_point = max_acc_idx - (np.argwhere(np.flip(accel_fs[:max_acc_idx])>=accel_thresh)[0]).item()
        touch_time = touch_point*dt + distance[0][0]
        release_point = max_acc_idx - (np.argwhere(np.flip(accel_fs[max_acc_idx:])>=accel_thresh)[0]).item()
        release_time = touch_point*dt + distance[0][0]

        max_dist = distance[1].argmax()
        max_deformation = np.abs(distance[1][touch_point] - distance[1].max()).squeeze()

        # linefit on distance before and after hit for velocity detection
        pre_impact_dist = distance.T[:touch_point].T
        post_impact_dist = distance.T[release_point:release_point + 80].T
        dist_linefit_down = Polynomial(P.polyfit(pre_impact_dist[0], pre_impact_dist[1],deg=1))
        dist_linefit_up = Polynomial(P.polyfit(post_impact_dist[0], post_impact_dist[1],deg=1))
        cof = abs(dist_linefit_up.coef[1] / dist_linefit_down.coef[1])


        data = BounceData(
            contour_x=contour_clean[0],
            contour_y=contour_clean[1],
            time=distance[0],
            distance=distance[1],
            velocity=velocity,
            acceleration=accel,
            distance_smooth=distance_f,
            velocity_smooth=velocity_fs,
            acceleration_smooth=accel_fs,
            acceleration_thresh=accel_thresh,
            impact_idx=touch_point,
            impact_time=touch_time,
            release_idx=release_point,
            release_time=release_time,
            max_deformation=max_deformation,
            max_acceleration=max_acc,
            cor=cof,
            speed_in=dist_linefit_down.coef[1],
            speed_out=dist_linefit_up.coef[1],
            speed_in_intercept=dist_linefit_down.coef[0],
            speed_out_intercept=dist_linefit_up.coef[0],
            video_framerate=self._video_controller.reader.frame_rate,
            video_resolution= f"{w}x{h}",
            video_num_frames=N,
            video_pixel_scale=pixel_scale,
            video_name=self._video_controller.reader._filename
        )
        # time_data = pd.DataFrame()
        # eval_data = pd.DataFrame()

        
        self._data_control.update_data_signal.emit(data, streak)
        self.video_eval_done_signal.emit()
        # self.update_progress_signal.emit(1)


    def find_contour(self, img):
        # ret = np.zeros(img.shape, dtype=np.uint8)
        # img = self.cv2_clahe.apply(img)
        #cv2.normalize(img, ret, norm_type=cv2.NORM_MINMAX, alpha=0, beta=255, dtype=cv2.CV_8UC1)
        cvimg = int(2**self._data_control.bit_depth-1) - img #invert image by subtracting it from fully white maxvalue
        cvimg = cv2.medianBlur(cvimg, 5)#

        _, cvimg = cv2.threshold(cvimg, 10, 255, type=cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(cvimg.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # get the contour that has the least mean y value, which should be the upper most contour
        avg_y = [cont.T[1].mean() for cont in contours]
        idx = np.argmin(avg_y)
        contour = np.asarray(contours[idx]).squeeze().T
        return contour

    def clean_contour(self, contour, num_frames):
        # remove contour parts that touch the image border
        del_pos = np.argwhere(contour[1]==0)
        contour = np.delete(contour.T, del_pos, axis=0).T
        del_pos = np.argwhere(contour[0]==0)
        contour = np.delete(contour.T, del_pos, axis=0).T
        del_pos = np.argwhere(contour[0]==(num_frames-1))
        contour = np.delete(contour.T, del_pos, axis=0).T
        #remove beginning and end, possible artifacts
        contour = contour.T[5:-5].T
        # remove duplicate x values
        _, idx = np.unique(contour[0], return_index=True)
        contour_clean = contour.T[idx].T
        return contour_clean
    
    def get_scale(self, streak, contour_start):
        line = streak.T[contour_start+5]
        max_val = line.max()
        first_dip = np.argmax(line<max_val)
        first_rise = np.argmax(line[first_dip+1:] == max_val) + first_dip+1
        px_delta = abs(first_rise - first_dip)
        scale = self._data_control.ball_size / px_delta
        return scale

    def prep_progress(self):
        pbar = self.parent().window().progressBar
        pbar.setValue(0)

    @Slot(float)
    def update_progress(self, frac):
        pbar = self.parent().window().progressBar
        pbar.setValue(int(frac*100))