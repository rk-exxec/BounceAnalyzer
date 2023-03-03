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

import random
import sys
import pandas as pd
import pyqtgraph as pg
import logging
import math

from bounce_data import BounceData
class BouncePlot(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        pg.setConfigOptions(antialias=True)
        self.accents = []

        # self.showGrid(x=True, y=True)
        self.scatter_pen = pg.mkPen((200,50,50,100))
        self.scatter_symbol = "s"
        self.scatter_brush=pg.mkBrush(None)
        self.scatter_vis = {"pen":None, "symbolPen":self.scatter_pen, "symbol":self.scatter_symbol, "symbolBrush":self.scatter_brush}
        self.plot_pen = pg.mkPen(color="g", width=2, cosmetic=True)
        self.plot_vis = {"pen":self.plot_pen}
        self.line_vis = {"pen":pg.mkPen(color="m", width=1, cosmetic=True)}
        self.slope_vis = {"pen":pg.mkPen(color="y", width=1, cosmetic=True)}
        
        self.distance = pg.PlotItem(title="Distance", labels={"left":("d", "m"), "bottom":("t","s")})
        self.addItem(self.distance, row=0, col=0)
        self.distanceGraph = pg.PlotDataItem(x=[], y=[], **self.plot_vis)
        self.distance.addItem(self.distanceGraph)
        self.distanceScatter = pg.PlotDataItem(x=[], y=[], **self.scatter_vis)
        self.distance.addItem(self.distanceScatter)
        self.distanceVLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.line_vis)
        self.distance.addItem(self.distanceVLine)

        self.distanceSpeedInLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.slope_vis)
        self.distanceSpeedOutLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.slope_vis)
        self.distance.addItem(self.distanceSpeedInLine)
        self.distance.addItem(self.distanceSpeedOutLine)

        self.distance.getViewBox().invertY()
        # self.distance.getAxis('left').enableAutoSIPrefix(False)

        self.velocity = pg.PlotItem(title="Velocity", labels={"left":("v", "m/s"), "bottom":("t","s")})
        self.addItem(self.velocity, row=1, col=0)
        self.velocityGraph = pg.PlotDataItem(x=[], y=[], **self.plot_vis)
        self.velocity.addItem(self.velocityGraph)
        self.velocityScatter = pg.PlotDataItem(x=[], y=[], **self.scatter_vis)
        self.velocity.addItem(self.velocityScatter)
        self.velocityVLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.line_vis)
        self.velocity.addItem(self.velocityVLine)
        self.speedInLine = pg.InfiniteLine(None, angle = 0, movable=False, **self.slope_vis)
        self.velocity.addItem(self.speedInLine)
        self.speedOutLine = pg.InfiniteLine(None, angle = 0, movable=False, **self.slope_vis)
        self.velocity.addItem(self.speedOutLine)
        self.velocity.getViewBox().invertY()
        self.velocity.getViewBox().setXLink(self.distance.getViewBox())

        self.accel= pg.PlotItem(title="Acceleration", labels={"left":("a", "m/s^2"), "bottom":("t","s")})
        self.accel.getAxis('left').enableAutoSIPrefix(False)
        self.addItem(self.accel, row=2, col=0)
        self.accelGraph = pg.PlotDataItem(x=[], y=[], **self.plot_vis)
        self.accel.addItem(self.accelGraph)
        self.accelScatter = pg.PlotDataItem(x=[], y=[], **self.scatter_vis)
        self.accel.addItem(self.accelScatter)
        self.accelVLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.line_vis)
        self.accel.addItem(self.accelVLine)
        self.accelHLine = pg.InfiniteLine(None, angle = 0, movable=False, **self.line_vis)
        self.accel.addItem(self.accelHLine)
        self.accel.getViewBox().invertY()
        self.accel.getViewBox().setXLink(self.distance.getViewBox())
        # self.plt.setData(y=[], x=[])

        self.tab_visible = False
        self.show()

        logging.info("initialized live plot")
        
    def plot_graphs(self, data_plot: BounceData):
        self.distanceGraph.setData(data_plot.time, data_plot.distance_smooth, **self.plot_vis)
        self.distanceScatter.setData(data_plot.time, data_plot.distance, **self.scatter_vis)
        self.velocityGraph.setData(data_plot.time, data_plot.velocity_smooth, **self.plot_vis)
        self.velocityScatter.setData(data_plot.time, data_plot.velocity, **self.scatter_vis)
        self.accelGraph.setData(data_plot.time, data_plot.acceleration_smooth, **self.plot_vis)
        self.accelScatter.setData(data_plot.time, data_plot.acceleration, **self.scatter_vis)

        self.accelVLine.setPos(data_plot.impact_time)
        self.velocityVLine.setPos(data_plot.impact_time)
        self.distanceVLine.setPos(data_plot.impact_time)
        self.accelHLine.setPos(data_plot.acceleration_thresh)

        self.distanceSpeedInLine.setAngle(math.degrees(math.atan(data_plot.speed_in)))
        self.distanceSpeedOutLine.setAngle(math.degrees(math.atan(data_plot.speed_out)))
        self.distanceSpeedInLine.setPos((0,data_plot.speed_in_intercept))
        self.distanceSpeedOutLine.setPos((0,data_plot.speed_out_intercept))

        self.speedInLine.setPos(data_plot.speed_in)
        self.speedOutLine.setPos(data_plot.speed_out)

        self.distance.setXRange(data_plot.impact_time/2, data_plot.impact_time*1.5)

    def clean(self):
        self.distanceGraph.setData([], [], **self.plot_vis)
        self.distanceScatter.setData([], [], **self.scatter_vis)
        self.velocityGraph.setData([], [], **self.plot_vis)
        self.velocityScatter.setData([], [], **self.scatter_vis)
        self.accelGraph.setData([], [], **self.plot_vis)
        self.accelScatter.setData([], [], **self.scatter_vis)

        self.accelVLine.setPos(0)
        self.velocityVLine.setPos(0)
        self.distanceVLine.setPos(0)
        self.accelHLine.setPos(0)
        self.distanceSpeedInLine.setAngle(0)
        self.distanceSpeedOutLine.setAngle(0)
        self.distanceSpeedInLine.setPos(0)
        self.distanceSpeedOutLine.setPos(0)

        self.speedInLine.setPos(0)
        self.speedOutLine.setPos(0)


