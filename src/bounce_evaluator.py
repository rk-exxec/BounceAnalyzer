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
import logging
logger = logging.getLogger(__name__)
import cv2
from scipy.ndimage import uniform_filter1d
from scipy.signal import savgol_filter, wiener
from scipy.interpolate import splprep, splev,splrep, interp1d
from scipy.signal import argrelmin
from numpy.polynomial import Polynomial
from numpy.polynomial import polynomial as P

from data_classes import BounceData, VideoInfoPresets

USE_SPLINE_CONTOUR = False

def bounce_eval(video: np.ndarray, info: VideoInfoPresets):
    logger.info("Start bounce analysis")
    frame_width,frame_height = info.shape
    total_frames = info.length
    time_step =  1/info.frame_rate
    line_fit_window = int(round(0.0025 / time_step)) # number of points before / after acceleration trigger used for line fitting
    spline_smoothing_mult = np.e**(info.frame_rate/30000 -1) # magic number
    savgol_filter_window = int(info.frame_rate * 0.0007) # approx 21 at 30000 fps seems to work
    pixel_scale = (0.0000197) #self._video_reader.reader.pixel_scale
    accel_thresh = -abs(info.accel_thresh)

    
    # generate streak image
    streak = video.min(axis=2).T

    # find contours in streak image
    contour_x, contour_y, _ = _find_contour(streak, info)
    # contour_clean = _clean_contour(contour, N)

    # calculate pixel scale
    if not info.pixel_scale:
        pixel_scale = _get_scale(streak, contour_y, contour_x[0], info)
    else: pixel_scale = info.pixel_scale

    time = contour_x * time_step
    position = contour_y * pixel_scale

    data = BounceData(
        contour_x=contour_x,
        contour_y=contour_y,
        time=time,
        position=position,
        video_framerate=info.frame_rate,
        video_resolution= f"{frame_width}x{frame_height}",
        video_num_frames=total_frames,
        video_pixel_scale=pixel_scale,
        video_name=info.filename,
        acceleration_thresh=accel_thresh
    )

    try:
        if USE_SPLINE_CONTOUR:
            m = len(contour_x)
            spl = splrep(contour_x, contour_y, s=np.sqrt(2*m)*spline_smoothing_mult)
            y_new = splev(contour_x, spl, der=0)
            data.contour_y = y_new
            position_smoothed = y_new * pixel_scale

            velocity = np.gradient(savgol_filter(position, savgol_filter_window, 5, mode="interp"), time)
            velocity_smoothed = np.gradient(position_smoothed, time)

            accel = savgol_filter(np.gradient(velocity, time), savgol_filter_window, 5, mode="interp")
            accel_smoothed = np.gradient(velocity_smoothed, time)
        else:
            savgol_filter_window = min(savgol_filter_window, len(position))
            position_smoothed = savgol_filter(position, savgol_filter_window, 5, mode="interp")

            velocity = np.gradient(position, time)
            velocity_smoothed = np.gradient(position_smoothed, time)

            accel = np.gradient(velocity_smoothed, time)
            # accel_s = np.gradient(velocity_fs, time)
            accel_smoothed = savgol_filter(accel, savgol_filter_window, 5, mode="interp")

        data.position_smooth = position_smoothed
        data.velocity = velocity
        data.velocity_smooth = velocity_smoothed
        data.acceleration = accel
        data.acceleration_smooth = accel_smoothed

        max_acc_idx = np.abs(accel_smoothed).argmax()
        max_acceleration = accel[max_acc_idx]

        data.max_acceleration = max_acceleration

        # image index and time where acceleration crosses threshold (just before max accel)
        touch_pos = max_acc_idx - (np.argwhere(np.flip(accel_smoothed[:max_acc_idx])>=accel_thresh)[0]).item()
        touch_time = touch_pos*time_step + time[0]

        data.impact_idx = touch_pos
        data.impact_time = touch_time
        # release is, where object reaches same position as at touch time
        try:
            release_pos = max_acc_idx + (np.argwhere(position[max_acc_idx:]<=position[touch_pos])[0]).item()
        except IndexError:
            # ball was not released, set release pos to be symmetrical to touch pos
            release_pos = (max_acc_idx - touch_pos) + max_acc_idx
        release_time = release_pos*time_step + time[0]

        data.release_idx = release_pos
        data.release_time = release_time
        
        max_dist = position.argmax()
        max_deformation = np.abs(position[touch_pos] - position.max()).squeeze()

        data.max_deformation=max_deformation

        # linefit on position before and after hit for velocity detection
        down_window_start = (touch_pos - line_fit_window)
        if down_window_start < 0 : down_window_start = 0

        up_window_end = release_pos + line_fit_window
        if up_window_end >= len(time): up_window_end = len(time) - 1

        pos_linefit_down = Polynomial(P.polyfit(time[down_window_start:touch_pos], position[down_window_start:touch_pos],deg=1))
        pos_linefit_up = Polynomial(P.polyfit(time[release_pos:up_window_end], position[release_pos:up_window_end],deg=1))
        coef_of_restitution = abs(pos_linefit_up.coef[1] / pos_linefit_down.coef[1])

        data.cor=coef_of_restitution
        data.speed_in=pos_linefit_down.coef[1]
        data.speed_out=pos_linefit_up.coef[1]
        data.speed_in_intercept=pos_linefit_down.coef[0]
        data.speed_out_intercept=pos_linefit_up.coef[0]

    except Exception as e:
        logger.error("Bounce analysis not finished due to:\n" + str(e))
    
    logger.info("Done analyzing")
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


def _find_contour(img: np.ndarray, info:VideoInfoPresets):
    """
    this determines the top contour of the streak image by fractional indexing (similar to LabView Threshold 1D)
    uses user defined relative threshold (to max value) for edge detection
    """
    cvimg = int(2**info.bit_depth-1) - img #invert image by subtracting it from fully white max value
    # blur = cvimg #cv2.GaussianBlur(cvimg, (5,5), 1)#

    thresh = info.rel_threshold * cvimg.max()
    thresh_idx = np.argmin(cvimg <= thresh, axis=0)
    thresh_x = np.arange(len(thresh_idx))
    contour_x, upper_idx = _clean_contour(np.array([thresh_x, thresh_idx]), info.length)

    # fractional indexing to return smoother position line
    lower_idx = upper_idx - 1
    upper_values = cvimg[upper_idx,contour_x].astype(np.float64)
    lower_values = cvimg[lower_idx,contour_x].astype(np.float64)

    delta = (upper_values - lower_values)

    frac_idx = lower_idx + (upper_idx - lower_idx) * (thresh - lower_values)/delta
    contour_y = np.where(delta == 0, upper_idx, frac_idx)

    # contour_y = upper_idx

    # contour = np.array([clean_x, frac_idx])
    
    # contours, _ = cv2.findContours(cvimg.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # # get the contour that has the least mean y value, which should be the upper most contour
    # avg_y = [cont.T[1].mean() for cont in contours]
    # idx = np.argmin(avg_y)
    # contour = np.asarray(contours[idx]).squeeze().T

    # _, cvimg = cv2.threshold(blur, 10, 255, type=cv2.THRESH_BINARY_INV)
    # contour_y = np.argmin(cvimg, axis=0)
    # contour_x = np.arange(len(contour_y))
    # contour = np.array([contour_x, contour_y])
    return contour_x, contour_y, cvimg

def _clean_contour(contour, num_frames):
    # remove contour parts that touch the image border
    del_pos = np.argwhere(contour[1]==0)
    #find gaps, gaps represent where contour is not touching upper image border
    jmps = []
    for i in range(len(del_pos)-1):
        if abs(del_pos[i]-del_pos[i+1]) > 100:
            jmps.append(i)

    # remove everything after first jump, first jump being the actual bounce
    if jmps: 
        # if bounce finishes way before end of video, prevent contour from being used outside of bounce event
        del_low = slice(del_pos[:jmps[0]].max())
        del_high = slice(del_pos[jmps[0]+1:].min(), None)
        # del_high = np.argwhere(del_pos > contour[0][jmps[0]+1])
        contour = np.delete(contour.T, del_low, axis=0).T
        contour = np.delete(contour.T, del_high, axis=0).T
    else:
        # ball only touches image top once, assume beginning, remove everything before
        contour = np.delete(contour.T, slice(del_pos.max()), axis=0).T
    
    # another pass to cleanup fragments
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

def _get_scale(streak, y_values, first_x, info: VideoInfoPresets):
    """ calculate pixel scale from known width of object"""
    def get_obj_px_height(idx):
        # calculate height of streak
        line = streak.T[idx]
        max_val = line.max()
        top_border = np.argmax(line<max_val)
        bottom_border = np.argmax(line[top_border+1:] == max_val) + top_border+1
        return abs(bottom_border - top_border)

    height = np.zeros((5,), dtype=int)

    # sample multiple positions and average for more accurate result
    # exclude regions, where surface and object overlap, or object is cut off
    for i,idx in enumerate(np.linspace(first_x+5, y_values.argmax() - 10, 5, dtype=int)):
        height[i] = get_obj_px_height(idx)
    px_delta = height.mean()

    scale = info.ball_size / px_delta
    return scale