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

import cv2
import numpy as np

from PySide6 import QtGui
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import  Qt, Slot, Signal
from PySide6.QtGui import QBrush, QImage, QPainter, QPen, QPixmap

class VideoPreview(QOpenGLWidget):
    update_contact_pos_event = Signal(int,int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._double_buffer: QImage = None
        self._pixmap = None
        self._raw_image = None
        self._image = None
        self._image_shape = None
        self._first_show = True
        self._has_mouse = False
        self._contact_pos = None


    def update_image(self, im: np.ndarray):
        self._raw_image = im
        
        cvt_im = self.ensure_8bit_image(im)

        if len(self._image_shape ) == 2:
            depth = 1
            height, width = self._image_shape
            bytes_per_line = width
        else:
            height, width, depth = self._image_shape
            bytes_per_line = width * depth

        if depth > 1:
            qimg = QtGui.QImage(cvt_im, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            qimg_scaled = qimg.scaled(self.size(), aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation)
            self._pixmap =  QPixmap.fromImage(qimg_scaled)
            self._image = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
        else:
            qimg = QtGui.QImage(cvt_im, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
            qimg_scaled = qimg.scaled(self.size(), aspectMode=Qt.KeepAspectRatio, mode=Qt.SmoothTransformation)
            self._pixmap =  QPixmap.fromImage(qimg_scaled)
            self._image = im
        self.update()

    def ensure_8bit_image(self, img: np.ndarray):
        """ checks bit count of inut and normalizes to 8 bit if nessecary, also tries to do contrast enhancement from additional info """
        if img.dtype.itemsize > 1:
            ret = np.zeros(img.shape, dtype=np.uint8)
            cv2.normalize(img, ret, norm_type=cv2.NORM_MINMAX, alpha=0, beta=255, dtype=cv2.CV_8UC1)
            return ret
        else:
            return img

    def update_shape(self, shape):
        self._image_shape = shape
        # self.set_new_baseline_constraints()

    def get_image(self):
        return self._image

    # widget functions:
    def showEvent(self, event: QtGui.QShowEvent) -> None:
        if self._first_show:
            self._first_show = False
        return super().showEvent(event)

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        evt_ret = super().resizeEvent(e)
        if self._raw_image is not None: self.update_image(self._raw_image)
        return evt_ret
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self._has_mouse = True

    def mosueMoveEvent(self, event: QtGui.QMouseEvent):
        if self._has_mouse:
            self._contact_pos = self.mapToImage(*self.mapFromGlobal(event.globalPos()).toTuple())
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self._has_mouse = False
        self._contact_pos = self.mapToImage(*self.mapFromGlobal(event.globalPos()).toTuple())
        self.update_contact_pos_event.emit(*self._contact_pos)
        self.update()


    def get_transform(self):
        """ 
        Gets the scale and offset for a Image to QLabel coordinate transform 

        :returns: 4-Tuple: Scale factors for x and y as tuple, Offset as tuple (x,y)
        """
        pw, ph = self._pixmap.size().toTuple()              # scaled image size
        ih, iw = self._image_shape[:2]   # original size of image
        cw, ch = self.size().toTuple()                      # display container size
        scale_x = float(pw) / float(iw)
        offset_x = abs(pw - cw)/2.0
        scale_y = float(ph) / float(ih)
        offset_y = abs(ph -  ch)/2.0
        return scale_x, scale_y, offset_x, offset_y

    def mapToImage(self, x=None, y=None, w=None, h=None):
        """ 
        Convert QLabel coordinates to image pixel coordinates

        :param x: x coordinate to be transformed
        :param y: y coordinate to be transformed
        :returns: x or y or Tuple (x,y) of the transformed coordinates, depending on what parameters where given
        """
        scale_x, scale_y, offset_x, offset_y = self.get_transform()
        res: list[int] = []
        if x is not None:
            tr_x = int(round((x - offset_x) / scale_x))
            res.append(tr_x)
        if y is not None:
            tr_y = int(round((y - offset_y) / scale_y))
            res.append(tr_y)
        if w is not None:
            tr_w = int(round(w / scale_x))
            res.append(tr_w)
        if h is not None:
            tr_h = int(round(h / scale_y))
            res.append(tr_h)
        return tuple(res) if len(res)>1 else res[0]

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        # painting the buffer pixmap to screen
        buf = self.doubleBufferPaint(self._double_buffer)
        # painting the buffer pixmap to screen
        painter.drawImage(0, 0, buf)
        painter.end()

    def doubleBufferPaint(self, buffer=None):
        self.blockSignals(True)
        #self.drawFrame(painter)
        if buffer is None:
            buffer = QImage(self.width(), self.height(), QImage.Format_RGB888)
        buffer.fill(Qt.black)
        # calculate offset and scale of droplet image pixmap
        scale_x, scale_y, offset_x, offset_y = self.get_transform()

        db_painter = QPainter(buffer)
        db_painter.setRenderHints(QPainter.Antialiasing)
        db_painter.setBackground(QBrush(Qt.black))
        db_painter.setPen(QPen(Qt.black,0))
        db_painter.drawPixmap(offset_x, offset_y, self._pixmap)
        pen = QPen(Qt.magenta,2)
        pen_contour = QPen(Qt.blue,1)
        pen.setCosmetic(True)
        w,h = self.width(), self.height()

        db_painter.setPen(pen)
        if self._contact_pos:
            x,y = self.mapFromImage(*self._contact_pos)
            db_painter.drawLine(0, y, w , y)
            db_painter.drawLine(x, 0, x, h)
             
        db_painter.end()
        self.blockSignals(False)
        return buffer

    # def grab_image(self, raw=False):
    #     if raw:
    #         return self._raw_8b_image
    #     else:
    #         return self.doubleBufferPaint(self._double_buffer)

    def mapFromImage(self, x=None, y=None, w=None, h=None):
        """ 
        Convert Image pixel coordinates to QLabel coordinates

        :param x: x coordinate to be transformed
        :param y: y coordinate to be transformed
        :returns: x or y or Tuple (x,y) of the transformed coordinates, depending on what parameters where given
        """
        scale_x, scale_y, offset_x, offset_y = self.get_transform()
        res: List[int] = []
        if x is not None:
            tr_x = int(round((x  * scale_x) + offset_x))
            res.append(tr_x)
        if y is not None:
            tr_y = int(round((y * scale_y) + offset_y))
            res.append(tr_y)
        if w is not None:
            tr_w = int(round(w  * scale_x))
            res.append(tr_w)
        if h is not None:
            tr_h = int(round(h  * scale_y))
            res.append(tr_h)
        return tuple(res) if len(res)>1 else res[0]
