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

from dataclasses import dataclass
from dataclass_wizard import JSONSerializable, JSONFileWizard
import numpy as np

@dataclass
class VideoInfoPresets:
    length: int
    shape: tuple[int,int]
    pixel_scale: float
    frame_rate: float
    bit_depth: int
    accel_thresh: float
    filename: str
    ball_size: float

# @dataclass_json
@dataclass
class BounceData(JSONSerializable, JSONFileWizard):
    contour_x: list[int]
    contour_y: list[int]
    time: list[float]
    distance: list[float]
    velocity: list[float]
    acceleration: list[float]
    distance_smooth: list[float]
    velocity_smooth: list[float]
    acceleration_smooth: list[float]

    acceleration_thresh: float
    impact_idx: int
    impact_time: float
    release_idx: int
    release_time: float

    max_deformation: float
    cor: float
    speed_in: float
    speed_out: float
    speed_in_intercept: float
    speed_out_intercept: float
    max_acceleration: float

    video_framerate: float
    video_resolution: str
    video_num_frames: int
    video_pixel_scale: float #mm/px
    video_name: str


    def __post_init__(self):
        self.contour_x = list(self.contour_x)
        self.contour_y = list(self.contour_y)
        self.time = list(self.time)
        self.distance = list(self.distance)   
        self.velocity = list(self.velocity)
        self.acceleration = list(self.acceleration)
        self.distance_smooth = list(self.distance_smooth)
        self.velocity_smooth = list(self.velocity_smooth)
        self.acceleration_smooth = list(self.acceleration_smooth)



