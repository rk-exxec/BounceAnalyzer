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
logger = logging.getLogger(__name__)
import math

from data_classes import BounceData
class BouncePlot(pg.GraphicsLayoutWidget):

    def __init__(self, parent = None):
        super().__init__(parent=parent)

        pg.setConfigOptions(antialias=True)
        self.accents = []

        # self.showGrid(x=True, y=True)
        self.scatter_pen = pg.mkPen((200,50,50,255))
        self.scatter_symbol = "s"
        self.scatter_brush=pg.mkBrush(None)
        self.scatter_vis = {"pen":None, "symbolPen":self.scatter_pen, "symbol":self.scatter_symbol, "symbolBrush":self.scatter_brush}
        self.plot_pen = pg.mkPen(color="g", width=2, cosmetic=True)
        self.plot_vis = {"pen":self.plot_pen}
        self.line_vis = {"pen":pg.mkPen(color="m", width=1, cosmetic=True)}
        self.slope_vis = {"pen":pg.mkPen(color=(125,125,0), width=1, cosmetic=True)}
        
        self.position = pg.PlotItem(title="Position", labels={"left":("d", "m"), "bottom":("t","s")})
        self.addItem(self.position, row=0, col=0)
        self.positionGraph = pg.PlotDataItem(x=[], y=[], **self.plot_vis)
        self.position.addItem(self.positionGraph)
        self.positionScatter = pg.PlotDataItem(x=[], y=[], **self.scatter_vis)
        self.position.addItem(self.positionScatter)
        self.positionVLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.line_vis)
        self.position.addItem(self.positionVLine)
        self.positionVLineOut = pg.InfiniteLine(None, angle = 90, movable=False, **self.line_vis)
        self.position.addItem(self.positionVLineOut)

        self.positionSpeedInLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.slope_vis)
        self.position.addItem(self.positionSpeedInLine)

        self.positionSpeedOutLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.slope_vis)
        self.position.addItem(self.positionSpeedOutLine)

        self.positionInitSpeedOutLine = pg.InfiniteLine(None, angle = 90, movable=False, **self.slope_vis)
        self.position.addItem(self.positionInitSpeedOutLine)

        self.position.getViewBox().invertY()
        # self.position.getAxis('left').enableAutoSIPrefix(False)

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
        self.speedInitOutLine = pg.InfiniteLine(None, angle = 0, movable=False, **self.slope_vis)
        self.velocity.addItem(self.speedInitOutLine)
        self.velocity.getViewBox().invertY()
        self.velocity.getViewBox().setXLink(self.position.getViewBox())

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
        self.accel.getViewBox().setXLink(self.position.getViewBox())
        # self.plt.setData(y=[], x=[])

        self.tab_visible = False
        self.show()

        logger.info("initialized live plot")
        
    def plot_graphs(self, data_plot: BounceData):
        self.positionGraph.setData(data_plot.time, data_plot.position_smooth, **self.plot_vis)
        self.positionScatter.setData(data_plot.time, data_plot.position, **self.scatter_vis)
        self.velocityGraph.setData(data_plot.time, data_plot.velocity_smooth, **self.plot_vis)
        self.velocityScatter.setData(data_plot.time, data_plot.velocity, **self.scatter_vis)
        self.accelGraph.setData(data_plot.time, data_plot.acceleration_smooth, **self.plot_vis)
        self.accelScatter.setData(data_plot.time, data_plot.acceleration, **self.scatter_vis)

        self.accelVLine.setPos(data_plot.impact_time)
        self.velocityVLine.setPos(data_plot.impact_time)
        self.positionVLine.setPos(data_plot.impact_time)
        self.positionVLineOut.setPos(data_plot.release_time)
        # self.accelHLine.setPos(data_plot.acceleration_thresh)

        self.positionSpeedInLine.setAngle(math.degrees(math.atan(data_plot.speed_in)))
        self.positionSpeedInLine.setPos((0,data_plot.speed_in_intercept))

        self.positionSpeedOutLine.setAngle(math.degrees(math.atan(data_plot.speed_out)))
        self.positionSpeedOutLine.setPos((0,data_plot.speed_out_intercept))

        self.positionInitSpeedOutLine.setAngle(math.degrees(math.atan(data_plot.initial_speed_out)))
        self.positionInitSpeedOutLine.setPos((0,data_plot.initial_speed_out_intercept))

        self.speedInLine.setPos(data_plot.speed_in)
        self.speedOutLine.setPos(data_plot.speed_out)
        self.speedInitOutLine.setPos(data_plot.initial_speed_out)

        self.position.setXRange(data_plot.impact_time/2, data_plot.impact_time*1.5)

    def clean(self):
        self.positionGraph.setData([], [], **self.plot_vis)
        self.positionScatter.setData([], [], **self.scatter_vis)
        self.velocityGraph.setData([], [], **self.plot_vis)
        self.velocityScatter.setData([], [], **self.scatter_vis)
        self.accelGraph.setData([], [], **self.plot_vis)
        self.accelScatter.setData([], [], **self.scatter_vis)

        self.accelVLine.setPos(0)
        self.velocityVLine.setPos(0)
        self.positionVLine.setPos(0)
        self.accelHLine.setPos(0)
        self.positionSpeedInLine.setAngle(0)
        self.positionSpeedInLine.setPos(0)

        self.positionSpeedOutLine.setAngle(0)
        self.positionSpeedOutLine.setPos(0)

        self.positionInitSpeedOutLine.setAngle(0)
        self.positionInitSpeedOutLine.setPos(0)

        self.speedInLine.setPos(0)
        self.speedOutLine.setPos(0)
        self.speedInitOutLine.setPos(0)


