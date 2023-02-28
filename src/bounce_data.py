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

from dataclasses import dataclass
from dataclasses_json import dataclass_json
import numpy as np

@dataclass_json
@dataclass
class BounceData:
    contour_x: np.ndarray[(1,), int]
    contour_y: np.ndarray[(1,), int]
    time: np.ndarray[(1,), float]
    distance: np.ndarray[(1,), float]
    velocity: np.ndarray[(1,), float]
    acceleration: np.ndarray[(1,), float]
    distance_smooth: np.ndarray[(1,), float]
    velocity_smooth: np.ndarray[(1,), float]
    acceleration_smooth: np.ndarray[(1,), float]

    acceleration_thresh: float
    impact_idx: int
    impact_time: float
    release_idx: int
    release_time: float

    max_deformation: float
    COR: float
    speed_in: float
    speed_out: float
    max_acceleration: float

    video_framerate: float
    video_resolution: str
    video_num_frames: int
    video_pixel_scale: float #mm/px
    video_name: str




