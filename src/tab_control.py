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

from PySide6.QtGui import QIcon, QShowEvent
from PySide6.QtWidgets import QTabWidget, QWidget

class TabControl(QTabWidget):
    """overrides QTabWidget to preserve parent relationship with tabs and their contents as QTCreator does not do that
    """
    def __init__(self, parent):
        super().__init__(parent=parent)

    def addTab(self, widget: QWidget, icon: QIcon) -> int:
        widget.setParent(self)
        return super().addTab(widget, icon)

    def addTab(self, widget: QWidget, icon: QIcon, label:str) -> int:
        widget.setParent(self)
        return super().addTab(widget, icon, label)

    def addTab(self, widget: QWidget, label:str) -> int:
        widget.setParent(self)
        return super().addTab(widget, label)

    def showEvent(self, arg__1: QShowEvent):
        # execute first time show events for all tabs
        self.widget(1).show()
        self.widget(0).show()
        return super().showEvent(arg__1)