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
import pandas as pd

import pyqtgraph as pg

import logging

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from qt.ui_bounce import Ui_bounce

class StreakPlot(pg.PlotWidget):

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        self.ui : Ui_bounce = None # set post init bc of parent relationship not automatically applied on creation in generated script
        self._first_show = True
        self.color_cnt = 0
        self.color = pg.intColor(self.color_cnt)

        pg.setConfigOptions(antialias=True)
        self.plotItem.clear()
        
        self.image_item = pg.ImageItem(autoDownsample=False)
        self.plotItem.addItem(self.image_item)
        self.plot_item = pg.PlotDataItem()
        self.plot_item.setPen(pg.mkPen(color="r", width=2, cosmetic=True))
        self.plotItem.addItem(self.plot_item)
        # self.showGrid(x=True, y=True)
        self.plotItem.getViewBox().invertY()
        

        self.tab_visible = False
        self.show()

        logging.info("initialized streak plot")
        

    def showEvent(self, event):
        super().showEvent(event)
        if self._first_show:
            self.ui = self.window()
            self._first_show = False

    def plot_image(self, streak, data):
        self.image_item.setImage(streak.T)
        self.plot_item.setData(data["Contour_x"], data["Contour_y"])
   

    def vline(self, x, color, cosmetic=True, width=2):
        self.plotItem.addItem(pg.InfiniteLine(x, angle = 90, pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))

    def hline(self, x, color, cosmetic=True, width=1):
        self.plotItem.addItem(pg.InfiniteLine(x, angle = 0, pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))

    def clean(self):
        self.image_item.clear()
        self.plot_item.clear()


