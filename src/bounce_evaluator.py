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



import numpy as np

import cv2
from scipy.ndimage import uniform_filter1d
from scipy.signal import savgol_filter, wiener
from numpy.polynomial import Polynomial
from numpy.polynomial import polynomial as P

from data_classes import BounceData, VideoInfoPresets

def bounce_eval(video: np.ndarray, info: VideoInfoPresets):
#     self.prep_progress()
#     if callback: 
#         self._thread = CallbackWorker(self.do_bounce_eval, slotOnFinished=callback)
#     else:
#         self._thread = Worker(self.do_bounce_eval)
#     self._thread.start()
#     # self.do_video_eval()

# def do_bounce_eval(self):
        
    w,h = info.shape
    N = info.length
    dt =  1/info.frame_rate
    pixel_scale = (0.0000197)#self._video_reader.reader.pixel_scale
    # contact_idx = self._video_reader.contact_frame
    # contact_x, contact_y = self._video_reader.contact_pos
    # contact_time = dt*contact_idx
    # contact_mm = contact_y * pixel_scale
    accel_thresh = -abs(info.accel_thresh)
    

    # generate streak image
    streak = video.min(axis=2).T

    # find contours in streak image
    contour = _find_contour(streak, info)
    contour_clean = _clean_contour(contour, N)

    # calculate pixel scale
    if not info.pixel_scale:
        pixel_scale = _get_scale(streak, contour_clean[0][0], info)
    else: pixel_scale = info.pixel_scale

    distance = np.array([contour_clean[0]*dt, contour_clean[1]*pixel_scale])
    distance_f = savgol_filter(distance[1], int(info.frame_rate * 0.0007), 4, mode="interp")
    # distance_f = wiener(distance[1], 31)
    # distance_f = uniform_filter1d(distance[1],8)

    velocity = np.gradient(distance[1], distance[0])
    velocity_fs = np.gradient(distance_f, distance[0])#savgol_filter(velocity, 21, 5, mode="nearest")

    accel = np.gradient(velocity_fs, distance[0])
    accel_s = np.gradient(velocity_fs, distance[0])
    # spar = (len(distance[0]) - np.sqrt(len(distance[0])*2)) * np.std(accel_s)**1.5
    # accel_fs = UnivariateSpline(distance[0], accel_s, s=spar)(distance[0])
    accel_fs = savgol_filter(accel_s, int(info.frame_rate * 0.0007), 5, mode="constant")

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
        video_framerate=info.frame_rate,
        video_resolution= f"{w}x{h}",
        video_num_frames=N,
        video_pixel_scale=pixel_scale,
        video_name=info.filename
    )

    
    return data, streak


def _find_contour(img, info:VideoInfoPresets):
    cvimg = int(2**info.bit_depth-1) - img #invert image by subtracting it from fully white maxvalue
    cvimg = cv2.medianBlur(cvimg, 5)#

    _, cvimg = cv2.threshold(cvimg, 10, 255, type=cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(cvimg.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # get the contour that has the least mean y value, which should be the upper most contour
    avg_y = [cont.T[1].mean() for cont in contours]
    idx = np.argmin(avg_y)
    contour = np.asarray(contours[idx]).squeeze().T
    return contour

def _clean_contour(contour, num_frames):
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

def _get_scale(streak, contour_start, info: VideoInfoPresets):
    line = streak.T[contour_start+5]
    max_val = line.max()
    first_dip = np.argmax(line<max_val)
    first_rise = np.argmax(line[first_dip+1:] == max_val) + first_dip+1
    px_delta = abs(first_rise - first_dip)
    scale = info.ball_size / px_delta
    return scale