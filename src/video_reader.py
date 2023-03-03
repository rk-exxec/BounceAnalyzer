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


import os,sys
import pyMRAW
import imageio.v3 as iio
import av # for pipreqs
import numpy as np
from abc import ABC

class IVideoReader(ABC):
    def __len__(self):
        """Length is number of frames."""
        raise NotImplementedError()

    def __getitem__(self, index):
        """Now we can get frame via self[index] and self[start:stop:step]."""
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self):
        """Release video file."""
        raise NotImplementedError()

    def _reset(self):
        """Re-initialize object."""
        raise NotImplementedError()
    
    @property
    def image_array(self) -> np.ndarray:
        raise NotImplementedError()

    @property
    def frame_width(self) -> int:
        raise NotImplementedError()

    @property
    def frame_height(self) -> int:
        raise NotImplementedError()

    @property
    def frame_shape(self) -> tuple[int,int]:
        raise NotImplementedError()
    
    @property
    def color_channels(self) -> int:
        raise NotImplementedError()
    
    @property
    def color_bit_depth(self) -> int:
        raise NotImplementedError()
    
    @property
    def frame_rate(self) -> float:
        raise NotImplementedError()
    
    @property
    def pixel_scale(self) -> float:
        raise NotImplementedError()
    
    @property
    def filename(self) -> str:
        raise NotImplementedError()


class VideoReaderMem(IVideoReader):
    def __init__(self, filename: str):
        """Open video in filename."""
        if not os.path.exists(filename):
            raise FileNotFoundError(f'{filename} not found.')
        if  filename.endswith("cihx"):
            self._vr, info = pyMRAW.load_video(filename)
            self._color_channels = 1
            self._number_of_frames = int(info["Total Frame"])
            self._bit_per_channel = int(info["Color Bit"])
            self._frame_rate = float(info["Record Rate(fps)"])
            self._pixel_scale = float(info["Pixel Scale"])
        else:
            self._vr = iio.imread(filename, plugin="pyav", format="gray")
        
            self._color_channels = self._vr[0].shape[-1]
            self._number_of_frames = self._vr[0].shape[0]
            self._bit_per_channel = 8
            self._pixel_scale = 1.0
            meta = iio.immeta(filename)
            self._frame_rate = meta['fps']

        self._filename = filename
        

    def __del__(self):
        try:
            del self._vr
        except AttributeError:  # if file does not exist this will be raised since _vr does not exist
            pass

    def __len__(self):
        """Length is number of frames."""
        return self._number_of_frames

    def __getitem__(self, index):
        """Now we can get frame via self[index] and self[start:stop:step]."""
        return self._vr[index]

    def __repr__(self):
        return f"{self._filename} with {len(self)} frames of size {self.frame_shape} at {self.frame_rate:1.2f} fps"

    def __iter__(self):
        return self._vr[0::1]

    def __enter__(self):
        return self

    def __exit__(self):
        """Release video file."""
        del(self)

    def _reset(self):
        """Re-initialize object."""
        self.__init__(self._filename)

    @property
    def image_array(self) -> np.ndarray:
        return self._vr

    @property
    def frame_width(self):
        return self._vr.shape[2]

    @property
    def frame_height(self):
        return self._vr.shape[1]

    @property
    def frame_shape(self):
        return self._vr.shape[1:]
    
    @property
    def color_channels(self):
        return self._color_channels
    
    @property
    def color_bit_depth(self):
        return self._bit_per_channel
    
    @property
    def frame_rate(self):
        return self._frame_rate
    
    @property
    def pixel_scale(self):
        return self._pixel_scale
    
    @property
    def filename(self) -> str:
        return self._filename
