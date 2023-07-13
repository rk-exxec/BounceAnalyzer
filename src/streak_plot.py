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

import sys
import pandas as pd
import pyqtgraph as pg
import logging
logger = logging.getLogger(__name__)

from data_classes import BounceData


class StreakPlot(pg.PlotWidget):

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        pg.setConfigOptions(antialias=True)
        self.plotItem.clear()
        
        self.image_item = pg.ImageItem()
        self.plotItem.addItem(self.image_item)
        self.plot_item = pg.PlotDataItem()
        self.plot_item.setPen(pg.mkPen(color="r", width=2, cosmetic=True))
        self.plotItem.addItem(self.plot_item)
        self.scale_detect_item = pg.PlotDataItem()
        self.scale_detect_item.setPen(pg.mkPen(color="y", width=1, cosmetic=True))
        self.plotItem.addItem(self.scale_detect_item)
        self.x_scale_item = pg.PlotDataItem()
        self.x_scale_item.setPen(pg.mkPen(color=(3, 166, 17), width=1, cosmetic=True))
        self.plotItem.addItem(self.x_scale_item)
        self.y_scale_item = pg.PlotDataItem()
        self.y_scale_item.setPen(pg.mkPen(color=(4, 79, 217), width=1, cosmetic=True))
        self.plotItem.addItem(self.y_scale_item)
        self.x_scale_text = pg.TextItem("1 ms", color=(3, 166, 17), anchor=(0,0))
        self.x_scale_text.setPos(10,400)
        self.plotItem.addItem(self.x_scale_text)

        self.y_scale_text = pg.TextItem("1 mm", color=(4, 79, 217), angle = 90, anchor=(0,1))
        self.y_scale_text.setPos(10,400)
        self.plotItem.addItem(self.y_scale_text)

        # self.showGrid(x=True, y=True)
        self.plotItem.getViewBox().invertY()
        

        self.tab_visible = False
        self.show()

        logger.info("initialized streak plot")
        

    def plot_image(self, streak, data: BounceData):
        logger = logging.getLogger(__name__)
        logger.debug("Plotting streak image")
        self.image_item.setImage(streak.T)
        logger.debug("Plotting streak contour")
        self.plot_item.setData(data.contour_x, data.contour_y)
        self.scale_detect_item.setData([data.contour_x[10],data.contour_x[10]], [data.contour_y[10], data.contour_y[10] + 2.381/data.video_pixel_scale])
        self.x_scale_item.setData([10, 10 + 1e-3*data.video_framerate], [400, 400])
        self.y_scale_item.setData([10, 10], [400, 400 - 1/data.video_pixel_scale])
   

    def vline(self, x, color, cosmetic=True, width=2):
        self.plotItem.addItem(pg.InfiniteLine(x, angle = 90, pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))

    def hline(self, x, color, cosmetic=True, width=1):
        self.plotItem.addItem(pg.InfiniteLine(x, angle = 0, pen=pg.mkPen(color=color, width=width, cosmetic=cosmetic)))

    def clean(self):
        self.image_item.clear()
        self.plot_item.clear()
        self.x_scale_item.clear()
        self.y_scale_item.clear()
        self.scale_detect_item.clear()


