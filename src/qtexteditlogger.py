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

from rich.logging import RichHandler
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextCursor

class QTextEditLogger(QTextEdit, RichHandler):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        RichHandler.__init__(self)
        self.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.append(msg)
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())  
        c = self.textCursor()
        c.movePosition(QTextCursor.End)
        self.setTextCursor(c)

    def write(self, msg:str):
        if '\r' in msg:
            msg = msg.strip()
            self.textCursor().setPosition(max(0,self.textCursor().position() - len(msg)))
            self.insertHtml(msg)
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())  
            self.update()