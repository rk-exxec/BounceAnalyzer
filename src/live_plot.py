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

import random
import sys

from PySide6.QtCore import QRectF, Slot
from PySide6.QtWidgets import QGraphicsRectItem

import pyqtgraph as pg

import logging

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from qt.ui_bounce import Ui_bounce

class LivePlot(pg.PlotWidget):

    def __init__(self, parent = None):
        super(LivePlot, self).__init__(parent=parent)

        self.ui : Ui_bounce = None # set post init bc of parent relationship not automatically applied on creation in generated script
        self._first_show = True
        self.color_cnt = 0
        self.color = pg.intColor(self.color_cnt)

        pg.setConfigOptions(antialias=True)
        self.xdata = []
        self.ydata = []
        self.plotItem.clear()
        self.img_item = None
        self.plt: pg.PlotDataItem = self.plotItem.plot(y=self.ydata, x=self.xdata, pen=self.color) #, symbol='x', symbolPen='y', symbolBrush=0.2)
        self.plt.setPen('y')
        self.showGrid(x=True, y=True)
        
        self.plt.setData(y=[], x=[])

        self.tab_visible = False
        self.show()

        logging.info("initialized live plot")
        

    def showEvent(self, event):
        super().showEvent(event)
        if self._first_show:
            self.ui = self.window()
            self._first_show = False

    @Slot(bool)
    def prepare_plot(self, hold=False):
        """prepares the plot
        """
        if hold:
            self.color_cnt += 1
        else:
            self.color_cnt = 0
            self.plotItem.clear()
        self.ydata = []
        self.xdata = []
        self.color = pg.intColor(self.color_cnt)
        self.plt = self.plotItem.plot(y=self.ydata, x=self.xdata, pen=self.color)

    def plot(self, data, x, y, label_x, label_y, unit_x, unit_y, color, si_prefix=True, cosmetic=True, width=2):
        # self.plotItem.clear()
        self.setLabel('left', label_y, units=unit_y)
        self.setLabel('bottom', label_x, units=unit_x)
        self.plotItem.addItem(pg.PlotDataItem(y=data[y], x=data[x], pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))
        self.plotItem.getViewBox().invertY()
        self.plotItem.getAxis('left').enableAutoSIPrefix(si_prefix)

    def scatter(self, data, x, y, label_x, label_y, unit_x, unit_y, color):
        # self.plotItem.clear()
        self.setLabel('left', label_y, units=unit_y)
        self.setLabel('bottom', label_x, units=unit_x)
        plt = self.plotItem.addItem(pg.ScatterPlotItem(y=data[y], x=data[x], pen=pg.mkPen((200,50,50,100)), symbol="s", brush=pg.mkBrush(None)))

    def vline(self, x, color, cosmetic=True, width=2):
        self.plotItem.addItem(pg.InfiniteLine(x, angle = 90, pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))

    def hline(self, x, color, cosmetic=True, width=1):
        self.plotItem.addItem(pg.InfiniteLine(x, angle = 0, pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))

    def set_image(self, image):
        self.image_item = pg.ImageItem(image.T, autoDownsample=False,)
        self.plotItem.addItem(self.image_item)

    def clear(self):
        self.plotItem.clear()
        self.image_item.clear()


