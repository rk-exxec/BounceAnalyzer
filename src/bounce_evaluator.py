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

def bounce_eval(video: np.ndarray, info: VideoInfoPresets):
    ''' evaluate movement of object '''
    logger.info("Start bounce analysis")
    frame_width,frame_height = info.shape
    total_frames = info.length
    time_step =  1/info.frame_rate
    line_fit_window = int(round(0.0025 / time_step)) # number of points before / after acceleration trigger used for line fitting
    savgol_filter_window = 21 #int(info.frame_rate * 0.0007) # approx 21 at 30000 fps seems to work
    savgol_polyorder = 2
    pixel_scale = (0.0000197) #self._video_reader.reader.pixel_scale
    rel_vel_thresh = info.rel_vel_thresh
    # eval y streak image
    data_y, streak_y, max_y_idx = bounce_eval_y(video, info, frame_width, frame_height, total_frames, time_step, line_fit_window, savgol_polyorder, savgol_filter_window, pixel_scale, relative_trig_thresh=rel_vel_thresh)
    # try find y coordinate where surface begins to use for x streak cutoff
    # so that x position streak can be calculated by just taking the mn of each frame column, without the interference of the darker sample surface
    x_cutoff = int(np.ceil(max_y_idx + ((info.ball_size/2) / data_y.video_pixel_scale)))
    pixel_scale = data_y.video_pixel_scale
    # try detex x streak
    data_x, streak_x = bounce_eval_x(video, info, data_y, time_step, line_fit_window, pixel_scale, x_cutoff)
    return data_x, streak_y, streak_x


def bounce_eval_y(video: np.ndarray, info: VideoInfoPresets, frame_width, frame_height, total_frames, time_step: float, line_fit_window, savgol_polyorder, savgol_filter_window, pixel_scale, relative_trig_thresh=0.9):
    ''' evaluate vertical movement and bounce of object '''
    # deflicker
    # brightest_value = video.max()
    # brightest_in_frames = video.max(axis=(1,2))
    # brightnes_eq_mult = brightest_value / brightest_in_frames

    # defl_video = video * brightnes_eq_mult[:,np.newaxis,np.newaxis]

    # generate streak image
    streak = video.min(axis=2).T

    # deflicker
    # brightest_value = streak.max()
    # brightest_in_frames = streak.max(axis=(0))
    # brightnes_eq_mult = np.nan_to_num((brightest_value / brightest_in_frames), posinf=1, neginf=1)
    # streak = streak * brightnes_eq_mult[np.newaxis,:]
    

    # find contours in streak image
    contour_x, contour_y, thresh_streak = _find_contour_y(streak, info)
    # contour_clean = _clean_contour(contour, N)
    max_y_idx = contour_y.max()

    # calculate pixel scale
    if not info.pixel_scale:
        pixel_scale = _get_scale(thresh_streak, contour_y, contour_x[0], info)
    else: pixel_scale = info.pixel_scale

    if abs(contour_y.max() - contour_y.min()) < 40:
        raise ValueError("No bounce detected!")

    time = contour_x * time_step
    position = contour_y * (pixel_scale / 1000)

    data = BounceData(
        contour_x=contour_x.tolist(),
        contour_y=contour_y.tolist(),
        time=time.tolist(),
        position=position.tolist(),
        video_framerate=info.frame_rate,
        video_resolution= f"{frame_width}x{frame_height}",
        video_num_frames=total_frames,
        video_pixel_scale=pixel_scale,
        video_name=info.filename,
        savgol_filter_window=savgol_filter_window,
        savgol_polyorder=savgol_polyorder,
        rel_velocity_thresh=relative_trig_thresh
    )

    try:
        # position and derivatives
        savgol_filter_window = min(savgol_filter_window, len(position))
        position_smoothed = savgol_filter(position, savgol_filter_window, savgol_polyorder, mode="interp")

        velocity: np.ndarray = np.gradient(position, time)
        velocity_smoothed: np.ndarray = np.gradient(position_smoothed, time)

        accel = np.gradient(velocity_smoothed, time)
        accel_smoothed = savgol_filter(accel, savgol_filter_window, savgol_polyorder, mode="interp")

        data.position_smooth = position_smoothed.tolist()
        data.velocity = velocity.tolist()
        data.velocity_smooth = velocity_smoothed.tolist()
        data.acceleration = accel.tolist()
        data.acceleration_smooth = accel_smoothed.tolist()

        # key points
        max_pos_idx = position.argmax()
        # min_acc_idx = np.abs(accel_smoothed).argmax()
        min_acc_idx = accel_smoothed.argmin()
        max_acceleration = accel[min_acc_idx]
        data.max_acceleration = float(max_acceleration)
        


        # find touch point by 10% veolicty change
        #estimate first touch point by subtracting material thickness from max pos
        estimate_touch_idx = np.argwhere(position >=(position[max_pos_idx] - 0.0012))[0].item()

        max_out_vel_idx = velocity_smoothed[estimate_touch_idx:].argmin() + estimate_touch_idx

        # accel fit
        down_window_start = (estimate_touch_idx - line_fit_window)
        if down_window_start < 0 : down_window_start = 0
        accel_linefit_down = Polynomial(P.polyfit(time[down_window_start:estimate_touch_idx], accel[down_window_start:estimate_touch_idx],deg=1))
        accel_in = float(accel_linefit_down.coef[0])

        data.accel_in = accel_in

        # when accel in change, consider touch pos
        touch_idx = max_pos_idx - np.argwhere(np.flip(accel[:max_pos_idx]) >= relative_trig_thresh*accel_in)[0].item()

        touch_time = touch_idx*time_step + time[0]

        data.impact_idx = int(touch_idx)
        data.impact_time = float(touch_time)

        # release is, where acceleration reaches same value as before bounce >after< short upward acceleration phase due to elasticity
        try:
            # check if there is a release, pos after bounce should be much larger than touch_pos, if almost identical, there is no bounce
            release_range_start = min_acc_idx + (np.argwhere(position[min_acc_idx:]<position[touch_idx]+0.01)[0]).item()
            ball_release = True
        except IndexError:
            release_range_start = max_out_vel_idx+2
            ball_release= False

        # determine average outgoing acceleration
        accel_linefit_up = Polynomial(P.polyfit(time[min_acc_idx+4*(min_acc_idx-touch_idx):], accel_smoothed[min_acc_idx+4*(min_acc_idx-touch_idx):],deg=0))
        accel_out = float(accel_linefit_up.coef[0])
        data.accel_out = accel_out
        # the detection range for release starts after object reached max velocity plus some buffer for noise
        # this does not actuall check if ball released, just finds the location where the accelereation returns to normal
        # accel_local_min_idx = min_acc_idx + np.argmax(accel_smoothed[min_acc_idx:min_acc_idx+3*(min_acc_idx-touch_idx)])
        # first find first dip above 0
        acc_zero_after_min = min_acc_idx + (np.argwhere(accel_smoothed[min_acc_idx:] >= accel_out)[0]).item()
        # find pos where pos gets above or to avg accel after zero crossing
        release_idx = acc_zero_after_min + (np.argwhere(accel_smoothed[acc_zero_after_min:] <= (accel_out))[0]).item()

        release_time = release_idx*time_step + time[0]
        # store release only if found, else only use for internal processing steps
        data.release_idx = int(release_idx) if ball_release else None
        data.release_time = float(release_time) if ball_release else None
        

        max_deformation = np.abs(position[touch_idx] - position.max()).squeeze()

        data.max_distance_idx = int(max_pos_idx)
        data.max_deformation = float(max_deformation)

        # linefit on position before and after hit for velocity detection
        up_window_end = release_idx + line_fit_window
        if up_window_end >= len(time): up_window_end = len(time) - 1
        # speed out
        pos_linefit_up = Polynomial(P.polyfit(time[release_idx:], position[release_idx:],deg=2))

        # pos in fit
        down_window_start = (touch_idx - line_fit_window)
        if down_window_start < 0 : down_window_start = 0
        pos_linefit_down = Polynomial(P.polyfit(time[:touch_idx], position[:touch_idx],deg=2))
        # speed_in = float(pos_linefit_down.coef[1])

        # object coming back up not yet decelerated by surface adhesion
        init_rebound_window = slice(min_acc_idx, release_idx - 5)
        # pos_linefit_init = Polynomial(P.polyfit(time[init_rebound_window], position[init_rebound_window],deg=1)) # replaced by just getting max vel
        data.speed_in= float(pos_linefit_down.deriv()(touch_time)) # m/s
        data.speed_out= float(pos_linefit_up.deriv()(release_time)) # m/s
        # if abs(data.speed_out) < 0.05: # if out speed too slow assume no release
        #     data.release_idx = None 
        #     data.release_time = None
        data.speed_in_intercept = float(pos_linefit_down(0))
        data.speed_out_intercept = float(pos_linefit_up(0))

         # calculated with sustained out velocity
        coef_of_restitution = abs(data.speed_out / data.speed_in)
        data.cor= float(coef_of_restitution)

        # maximum velocity on rebound, might be decelerated due to adhesive forces
        # max_out_vel = velocity[max_out_vel_idx]
        max_out_vel = velocity_smoothed[max_out_vel_idx]
        init_cor = abs(max_out_vel / data.speed_in)

        data.initial_cor =  float(init_cor)
        data.initial_speed_out= float(max_out_vel) # pos_linefit_init.coef[1] # m/s
        data.initial_speed_out_intercept= float(position[max_out_vel_idx] - max_out_vel*time[max_out_vel_idx]) #float(pos_linefit_init.coef[0]) # float(position[velocity[min_acc_idx:].argmin()+min_acc_idx]) #

    except Exception as e:
        logger.error("Bounce analysis not finished due to:\n" + str(e))
    
    logger.info("Done analyzing")
    return data, streak, max_y_idx


def bounce_eval_x(video: np.ndarray, info: VideoInfoPresets, data: BounceData, time_step, line_fit_window, pixel_scale, cutoff):
    ''' evaluate the sideways movement of the falling/bouncing object '''
    CUTOFF = cutoff
    try:
        # generate streak image
        streak = video[:,:CUTOFF,:].min(axis=1).T

        # find contours in streak image
        contour_x, contour_y, thresh_streak = _find_contour_x(streak, info)
        # imit contour to extent of contour found by y-deflection
        left_cutoff_idx = min(data.contour_x)
        right_cutoff_idx = max(data.contour_x)
        contour_x = contour_x[left_cutoff_idx:right_cutoff_idx]
        contour_y = contour_y[left_cutoff_idx:right_cutoff_idx]
        # contour_clean = _clean_contour(contour, N)

        time = contour_x * time_step
        position = contour_y * (pixel_scale / 1000)

        velocity = np.gradient(position, time)

        # linefit on position before and after hit for velocity detection
        down_window_start = (data.impact_idx - line_fit_window)
        if down_window_start < 0 : down_window_start = 0

        if data.release_idx is None: 
            release_idx = abs(data.impact_idx - data.max_distance_idx) + data.max_distance_idx
        else:
            release_idx = data.release_idx

        up_window_end = release_idx + line_fit_window
        if up_window_end >= len(time): up_window_end = len(time) - 1

        pos_linefit_down = Polynomial(P.polyfit(time[down_window_start:data.impact_idx], position[down_window_start:data.impact_idx],deg=1))
        pos_linefit_up = Polynomial(P.polyfit(time[release_idx:up_window_end], position[release_idx:up_window_end],deg=1))


    except Exception as e:
        logger.error("X deflection not detected!:\n" + str(e))
        streak = None

    else:
        # if x deflection detection dod not throw error, add results to data structure
        data.x_defl_contour_x, data.x_defl_contour_y = contour_x.tolist(), contour_y.tolist()
        data.x_defl_time = time.tolist()
        data.x_defl_position = position.tolist()
        data.x_defl_velocity = velocity.tolist()
        data.x_defl_speed_in = float(pos_linefit_down.coef[1]) # m/s
        data.x_defl_speed_out = float(pos_linefit_up.coef[1]) # m/s
        data.has_x_deflection_data = True
    
        logger.info("X deflection analyzed")

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

def _find_contour_y(img: np.ndarray, info:VideoInfoPresets) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    this determines the top contour of the streak image by fractional indexing (similar to LabView Threshold 1D)
    uses user defined relative threshold (to max value) for edge detection
    """
    cvimg = int(2**info.bit_depth-1) - img #invert image by subtracting it from fully white max value
    # img = cv2.GaussianBlur(img, (5,5), 1)#

    thresh = info.rel_threshold * cvimg.max()
    thresh_idx = np.argmin(cvimg <= thresh, axis=0)
    thresh_x = np.arange(len(thresh_idx))
    contour_x, upper_idx = _clean_contour(np.array([thresh_x, thresh_idx]), info.length)

    # calculate thresholded image for further processing down the line
    _, thresh_img = cv2.threshold(img, (1-info.rel_threshold) * img.max(), int(2**info.bit_depth-1), cv2.THRESH_BINARY)

    # fractional indexing to return smoother position line
    lower_idx = upper_idx - 1
    upper_values = cvimg[upper_idx,contour_x].astype(np.float64)
    lower_values = cvimg[lower_idx,contour_x].astype(np.float64)

    delta = (upper_values - lower_values)

    frac_idx = lower_idx + (upper_idx - lower_idx) * (thresh - lower_values)/delta
    contour_y = np.where(delta == 0, upper_idx, frac_idx)

    return contour_x, contour_y, thresh_img

_find_contour_x = _find_contour_y

def _clean_contour(contour, num_frames) -> tuple[np.ndarray,np.ndarray]:
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

def _get_scale(streak, y_values, first_x, info: VideoInfoPresets) -> float:
    """ calculate pixel scale from known width of object"""
    def get_obj_px_height(idx):
        # calculate height of streak
        line = streak.T[idx]
        max_val = line.max()
        top_border = np.argmax(line < max_val)
        bottom_border = np.argmax(line[top_border+1:] == max_val) + top_border+1
        return abs(bottom_border - top_border)

    height = np.zeros((15,), dtype=int)

    # sample multiple positions and average for more accurate result
    # exclude regions, where surface and object overlap, or object is cut off
    # pos_range = np.linspace(first_x+5, y_values.argmax() - 20, 5, dtype=int)
    pos_range = range(first_x+5,first_x+20,1)
    for i,idx in enumerate(pos_range):
        height[i] = get_obj_px_height(idx)
    px_delta = height.mean()
    
    scale = info.ball_size / px_delta
    logger.debug(f"Pixelscale: {scale:0.4f} | {height} | {pos_range}")
    return scale