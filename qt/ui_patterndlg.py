# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'patterndlg.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_PatternDialog(object):
    def setupUi(self, PatternDialog):
        if not PatternDialog.objectName():
            PatternDialog.setObjectName(u"PatternDialog")
        PatternDialog.resize(353, 168)
        self.verticalLayout = QVBoxLayout(PatternDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(PatternDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.rootPathTxt = QLineEdit(PatternDialog)
        self.rootPathTxt.setObjectName(u"rootPathTxt")
        self.rootPathTxt.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.rootPathTxt)

        self.openBtn = QPushButton(PatternDialog)
        self.openBtn.setObjectName(u"openBtn")

        self.horizontalLayout.addWidget(self.openBtn)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label_2 = QLabel(PatternDialog)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.patternTxt = QLineEdit(PatternDialog)
        self.patternTxt.setObjectName(u"patternTxt")

        self.verticalLayout.addWidget(self.patternTxt)

        self.label_3 = QLabel(PatternDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_3)

        self.buttonBox = QDialogButtonBox(PatternDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(PatternDialog)

        QMetaObject.connectSlotsByName(PatternDialog)
    # setupUi

    def retranslateUi(self, PatternDialog):
        PatternDialog.setWindowTitle(QCoreApplication.translate("PatternDialog", u"Batch Processing", None))
        self.label.setText(QCoreApplication.translate("PatternDialog", u"Root directory", None))
        self.openBtn.setText(QCoreApplication.translate("PatternDialog", u"Open...", None))
        self.label_2.setText(QCoreApplication.translate("PatternDialog", u"File match pattern", None))
        self.patternTxt.setText(QCoreApplication.translate("PatternDialog", u"*.cihx", None))
        self.label_3.setText(QCoreApplication.translate("PatternDialog", u"Process all files matching the pattern in the root directory and all subfolders recursively.", None))
    # retranslateUi

