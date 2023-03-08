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
from scipy.interpolate import splprep, splev,splrep
from numpy.polynomial import Polynomial
from numpy.polynomial import polynomial as P

from data_classes import BounceData, VideoInfoPresets

USE_SPLINE_CONTOUR = True

def bounce_eval(video: np.ndarray, info: VideoInfoPresets):
        
    w,h = info.shape
    N = info.length
    dt =  1/info.frame_rate
    spline_smoothing_mult = np.e**(info.frame_rate/30000 -1)
    filter_window = int(info.frame_rate * 0.0007) # approx 21 at 30000 fps seems to work
    pixel_scale = (0.0000197)#self._video_reader.reader.pixel_scale
    accel_thresh = -abs(info.accel_thresh)
    
    # generate streak image
    streak = video.min(axis=2).T

    # find contours in streak image
    contour, _ = _find_contour(streak, info)
    contour_clean = _clean_contour(contour, N)

    contour_x = contour_clean[0]
    contour_y = contour_clean[1]

    # calculate pixel scale
    if not info.pixel_scale:
        pixel_scale = _get_scale(streak, contour_clean, info)
    else: pixel_scale = info.pixel_scale

    time = contour_x*dt

    if USE_SPLINE_CONTOUR:
        m = len(contour_x)
        spl = splrep(contour_x, contour_y, s=np.sqrt(2*m)*spline_smoothing_mult)
        y_new = splev(contour_x, spl, der=0)
        distance = contour_y * pixel_scale
        distance_f = y_new * pixel_scale

        velocity = np.gradient(distance, time)
        velocity_fs = np.gradient(distance_f, time)

        accel = np.gradient(velocity, time)
        accel_fs = np.gradient(velocity_fs, time)
    else:
        distance = np.array([contour_x*dt, contour_y*pixel_scale])
        distance_f = savgol_filter(distance, filter_window, 5, mode="interp")

        velocity = np.gradient(distance, time)
        velocity_fs = np.gradient(distance_f, time)

        accel = np.gradient(velocity, time)
        accel_s = np.gradient(velocity_fs, time)
        accel_fs = savgol_filter(accel_s, filter_window, 5, mode="constant")

    max_acc_idx = np.abs(accel_fs).argmax()
    max_acc = accel_fs[max_acc_idx]

    # image index and time where acceleration crosses threshold (near max accel)
    touch_point = max_acc_idx - (np.argwhere(np.flip(accel_fs[:max_acc_idx])>=accel_thresh)[0]).item()
    touch_time = touch_point*dt + time[0]
    # release is, where distance reaches same values as at touch time
    release_point = max_acc_idx + (np.argwhere(distance[max_acc_idx:]<=distance[touch_point])[0]).item()
    release_time = release_point*dt + time[0]

    max_dist = distance.argmax()
    max_deformation = np.abs(distance[touch_point] - distance.max()).squeeze()

    # linefit on distance before and after hit for velocity detection
    dist_linefit_down = Polynomial(P.polyfit(time[:touch_point], distance[:touch_point],deg=1))
    dist_linefit_up = Polynomial(P.polyfit(time[release_point:release_point + 80], distance[release_point:release_point + 80],deg=1))
    cof = abs(dist_linefit_up.coef[1] / dist_linefit_down.coef[1])


    data = BounceData(
        contour_x=contour_x,
        contour_y=y_new if USE_SPLINE_CONTOUR else contour_y,
        time=time,
        distance=distance,
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


def _second_order_central_diff(y,x):
    res = np.zeros_like(y)
    h = np.diff(x).mean()
    for i in range(len(y)):
        if i == 0:
            res[0] = (y[2] - 2*y[1] + y[0]) / h**2# / ((x[2] - x[0]) / 2 )**2
        elif i == len(y)-1:
            res[-1] = (y[-1] - 2*y[-2] + y[-3]) / h**2# / ((x[-1] - x[-3]) / 2 )**2
        else:
            res[i] = (y[i+1] - 2*y[i] + y[i-1]) / h**2 # / ((x[i+1] - x[i-1])/2)**2

    return res

def _central_diff(y,x):
    res = np.zeros_like(y)
    h = np.diff(x).mean()
    for i in range(len(y)):
        if i == 0:
            res[0] = (y[2] - y[0]) / (2*h)# / ((x[2] - x[0]) / 2 )**2
        elif i == len(y)-1:
            res[-1] = (y[-1] -y[-3]) / (2*h)# / ((x[-1] - x[-3]) / 2 )**2
        else:
            res[i] = (y[i+1] - y[i-1]) / (2*h) # / ((x[i+1] - x[i-1])/2)**2

    return res




def _find_contour(img, info:VideoInfoPresets):
    cvimg = int(2**info.bit_depth-1) - img #invert image by subtracting it from fully white maxvalue
    blur = cvimg #cv2.GaussianBlur(cvimg, (5,5), 1)#

    _, cvimg = cv2.threshold(blur, 10, 255, type=cv2.THRESH_BINARY_INV)
    # contours, _ = cv2.findContours(cvimg.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # # get the contour that has the least mean y value, which should be the upper most contour
    # avg_y = [cont.T[1].mean() for cont in contours]
    # idx = np.argmin(avg_y)
    # contour = np.asarray(contours[idx]).squeeze().T
    contour_y = np.argmin(cvimg, axis=0)
    contour_x = np.arange(len(contour_y))
    contour = np.array([contour_x, contour_y])
    return contour, cvimg

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

def _get_scale(streak, contour, info: VideoInfoPresets):
    def get_drop_pxwidth(idx):
        line = streak.T[idx]
        max_val = line.max()
        first_dip = np.argmax(line<max_val)
        first_rise = np.argmax(line[first_dip+1:] == max_val) + first_dip+1
        return abs(first_rise - first_dip)

    width = np.zeros((5,), dtype=int)

    for i,idx in enumerate(np.linspace(contour[0][0]+5, contour[1].argmax() - 10, 5, dtype=int)):
        width[i] = get_drop_pxwidth(idx)
    px_delta = width.mean()
    scale = info.ball_size / px_delta
    return scale