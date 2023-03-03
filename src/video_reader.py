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
import av

class VideoReaderMem:
    def __init__(self, filename: str):
        """Open video in filename."""
        if not os.path.exists(filename):
            raise FileNotFoundError(f'{filename} not found.')
        if  filename.endswith("cihx"):
            self._vr, info = pyMRAW.load_video(filename)
            self.frame_channels = 1
            self.number_of_frames = int(info["Total Frame"])
            self.bit_per_channel = int(info["Color Bit"])
            self.frame_rate = float(info["Record Rate(fps)"])
            self.pixel_scale = float(info["Pixel Scale"])
        else:
            self._vr = iio.imread(filename, plugin="pyav", format="gray")
        
            self.frame_channels = self._vr[0].shape[-1]
            self.number_of_frames = self._vr[0].shape[0]
            self.bit_per_channel = 8
            self.pixel_scale = 1.0
            meta = iio.immeta(filename)
            self.frame_rate = meta['fps']

        self._filename = filename
        

    def __del__(self):
        try:
            del self._vr
        except AttributeError:  # if file does not exist this will be raised since _vr does not exist
            pass

    def __len__(self):
        """Length is number of frames."""
        return self.number_of_frames

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
    def frame_width(self):
        return self._vr.shape[2]

    @property
    def frame_height(self):
        return self._vr.shape[1]

    @property
    def frame_shape(self):
        return self._vr.shape[1:]