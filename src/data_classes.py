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

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
# from dataclass_wizard import JSONSerializable, JSONFileWizard
import numpy as np

@dataclass_json
@dataclass
class VideoInfoPresets:
    length: int
    shape: tuple[int,int]
    pixel_scale: float
    frame_rate: float
    bit_depth: int
    rel_vel_thresh: float
    filename: str
    ball_size: float
    rel_threshold: float

@dataclass_json
@dataclass
class BounceData:#(JSONSerializable, JSONFileWizard):
    video_framerate: float
    video_resolution: str
    video_num_frames: int
    video_pixel_scale: float #mm/px
    video_name: str = field(compare=False)
    savgol_filter_window: int
    savgol_polyorder: int

    contour_x: list[int]
    contour_y: list[float]
    time: list[float] = field(default_factory=list)
    position: list[float] = field(default_factory=list)
    velocity: list[float] = field(default_factory=list)
    acceleration: list[float] = field(default_factory=list)
    position_smooth: list[float] = field(default_factory=list)
    velocity_smooth: list[float] = field(default_factory=list)
    acceleration_smooth: list[float] = field(default_factory=list)

    rel_velocity_thresh: float = 0.9
    impact_idx: int = 0.0
    impact_time: float = 0.0
    release_idx: int = 0.0
    release_time: float = 0.0

    max_distance_idx: int = 0
    max_deformation: float = 0.0
    cor: float = 0.0
    speed_in: float = 0.0
    speed_out: float = 0.0
    speed_in_intercept: float = 0.0
    speed_out_intercept: float = 0.0
    max_acceleration: float = 0.0
    accel_in: float = 0.0
    initial_cor: float = 0.0
    initial_speed_out: float = 0.0
    initial_speed_out_intercept: float = 0.0

    has_x_deflection_data: bool = False
    x_defl_contour_x: list[float] = field(default_factory=list)
    x_defl_contour_y: list[float] = field(default_factory=list)
    x_defl_time: list[float] = field(default_factory=list)
    x_defl_position: list[float] = field(default_factory=list)
    x_defl_velocity: list[float] = field(default_factory=list)
    x_defl_speed_in: float = 0.0
    x_defl_speed_out: float = 0.0


    def __post_init__(self):
        self.contour_x = list(self.contour_x)
        self.contour_y = list(self.contour_y)
        self.time = list(self.time)
        self.position = list(self.position)   
        self.velocity = list(self.velocity)
        self.acceleration = list(self.acceleration)
        self.position_smooth = list(self.position_smooth)
        self.velocity_smooth = list(self.velocity_smooth)
        self.acceleration_smooth = list(self.acceleration_smooth)



