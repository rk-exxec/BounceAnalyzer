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


from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

import pandas as pd
from data_classes import BounceData
from dataclasses import asdict


class TableControl(QTableWidget):
    """Derivative of QTableWidget with support to draw a pandas dataframe
    """
    redraw_table_signal = Signal(BounceData)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.redraw_table_signal.connect(self.update_data)
        self._needs_update = False
        self.data = None

    def showEvent(self,event) -> None:
        if self._needs_update and self.data != None:
            self.redraw_table(pd.DataFrame.from_dict(asdict(self.data)))
            self._needs_update = False

        return super().show()
    
    @Slot(BounceData)
    def update_data(self, data:BounceData):
        self.data = data
        if not self.isVisible():
            self._needs_update = True
        else:
            self.redraw_table(pd.DataFrame.from_dict(asdict(data)))

    # @Slot(pd.DataFrame)
    def redraw_table(self, data: pd.DataFrame):
        """ Redraw table with contents of dataframe """
        n_rows, n_cols = data.shape
        self.setRowCount(n_rows)
        self.setColumnCount(n_cols)

        for r in range(n_rows):
            for c in range(n_cols):
                val = data.iloc[r, c]
                if isinstance(val, float):
                    val = f'{val:g}'
                else:
                    val = str(val)
                self.setItem(r, c, QTableWidgetItem(val))

        self.setHorizontalHeaderLabels(list(data.columns))
        self.scrollToBottom()
