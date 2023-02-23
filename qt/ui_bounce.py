# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bounce.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QDoubleSpinBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QStatusBar, QTableWidgetItem, QVBoxLayout, QWidget)

from bounce_plot import BouncePlot
from qtexteditlogger import QTextEditLogger
from streak_plot import StreakPlot
from tab_control import TabControl
from table_control import TableControl
from video_preview import VideoPreview

class Ui_Bounce(object):
    def setupUi(self, Bounce):
        if not Bounce.objectName():
            Bounce.setObjectName(u"Bounce")
        Bounce.resize(1217, 682)
        self.actionOpen = QAction(Bounce)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionPreferences = QAction(Bounce)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionCalibrate_Scale = QAction(Bounce)
        self.actionCalibrate_Scale.setObjectName(u"actionCalibrate_Scale")
        self.actionDelete_Scale = QAction(Bounce)
        self.actionDelete_Scale.setObjectName(u"actionDelete_Scale")
        self.actionBatch_Process = QAction(Bounce)
        self.actionBatch_Process.setObjectName(u"actionBatch_Process")
        self.centralwidget = QWidget(Bounce)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tabWidget = TabControl(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.videoTab = QWidget()
        self.videoTab.setObjectName(u"videoTab")
        self.horizontalLayout_4 = QHBoxLayout(self.videoTab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.playerLayout = QVBoxLayout()
        self.playerLayout.setObjectName(u"playerLayout")
        self.videoViewer = VideoPreview(self.videoTab)
        self.videoViewer.setObjectName(u"videoViewer")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.videoViewer.sizePolicy().hasHeightForWidth())
        self.videoViewer.setSizePolicy(sizePolicy)
        self.videoViewer.setMinimumSize(QSize(600, 480))

        self.playerLayout.addWidget(self.videoViewer)

        self.statusLbl = QLabel(self.videoTab)
        self.statusLbl.setObjectName(u"statusLbl")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.statusLbl.sizePolicy().hasHeightForWidth())
        self.statusLbl.setSizePolicy(sizePolicy1)
        self.statusLbl.setMinimumSize(QSize(100, 15))

        self.playerLayout.addWidget(self.statusLbl)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.playBtn = QPushButton(self.videoTab)
        self.playBtn.setObjectName(u"playBtn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.playBtn.sizePolicy().hasHeightForWidth())
        self.playBtn.setSizePolicy(sizePolicy2)
        self.playBtn.setMinimumSize(QSize(10, 22))

        self.horizontalLayout.addWidget(self.playBtn)

        self.pauseBtn = QPushButton(self.videoTab)
        self.pauseBtn.setObjectName(u"pauseBtn")
        self.pauseBtn.setMinimumSize(QSize(10, 22))

        self.horizontalLayout.addWidget(self.pauseBtn)

        self.seekBar = QSlider(self.videoTab)
        self.seekBar.setObjectName(u"seekBar")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.seekBar.sizePolicy().hasHeightForWidth())
        self.seekBar.setSizePolicy(sizePolicy3)
        self.seekBar.setMinimumSize(QSize(400, 22))
        self.seekBar.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.seekBar)

        self.resetFrame = QPushButton(self.videoTab)
        self.resetFrame.setObjectName(u"resetFrame")

        self.horizontalLayout.addWidget(self.resetFrame)


        self.playerLayout.addLayout(self.horizontalLayout)

        self.line_2 = QFrame(self.videoTab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.playerLayout.addWidget(self.line_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_8 = QLabel(self.videoTab)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_3.addWidget(self.label_8)

        self.accelThreshSpin = QDoubleSpinBox(self.videoTab)
        self.accelThreshSpin.setObjectName(u"accelThreshSpin")
        self.accelThreshSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.accelThreshSpin.setDecimals(1)
        self.accelThreshSpin.setMaximum(100000.000000000000000)
        self.accelThreshSpin.setValue(1500.000000000000000)

        self.horizontalLayout_3.addWidget(self.accelThreshSpin)

        self.line = QFrame(self.videoTab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.label_3 = QLabel(self.videoTab)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.pxScaleSpin = QDoubleSpinBox(self.videoTab)
        self.pxScaleSpin.setObjectName(u"pxScaleSpin")
        self.pxScaleSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.pxScaleSpin.setDecimals(6)
        self.pxScaleSpin.setSingleStep(0.001000000000000)
        self.pxScaleSpin.setValue(0.000000000000000)

        self.horizontalLayout_3.addWidget(self.pxScaleSpin)

        self.line_3 = QFrame(self.videoTab)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line_3)

        self.label_7 = QLabel(self.videoTab)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_3.addWidget(self.label_7)

        self.ballSizeSpin = QDoubleSpinBox(self.videoTab)
        self.ballSizeSpin.setObjectName(u"ballSizeSpin")
        self.ballSizeSpin.setDecimals(3)
        self.ballSizeSpin.setValue(2.500000000000000)

        self.horizontalLayout_3.addWidget(self.ballSizeSpin)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.startEvalBtn = QPushButton(self.videoTab)
        self.startEvalBtn.setObjectName(u"startEvalBtn")

        self.horizontalLayout_3.addWidget(self.startEvalBtn)


        self.playerLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_4.addLayout(self.playerLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.videoTab)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.textEdit = QTextEditLogger(self.videoTab)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy4)

        self.verticalLayout_2.addWidget(self.textEdit)


        self.horizontalLayout_4.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.videoTab, "")
        self.dataTab = QWidget()
        self.dataTab.setObjectName(u"dataTab")
        self.horizontalLayout_5 = QHBoxLayout(self.dataTab)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.streakImage = StreakPlot(self.dataTab)
        self.streakImage.setObjectName(u"streakImage")

        self.verticalLayout_3.addWidget(self.streakImage)

        self.groupBox = QGroupBox(self.dataTab)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer_3 = QSpacerItem(40, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 0, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.corLbl = QLabel(self.groupBox)
        self.corLbl.setObjectName(u"corLbl")

        self.gridLayout.addWidget(self.corLbl, 1, 1, 1, 1)

        self.maxDeformLbl = QLabel(self.groupBox)
        self.maxDeformLbl.setObjectName(u"maxDeformLbl")

        self.gridLayout.addWidget(self.maxDeformLbl, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.maxAccelLbl = QLabel(self.groupBox)
        self.maxAccelLbl.setObjectName(u"maxAccelLbl")

        self.gridLayout.addWidget(self.maxAccelLbl, 2, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.pxScaleLbl = QLabel(self.groupBox)
        self.pxScaleLbl.setObjectName(u"pxScaleLbl")

        self.gridLayout.addWidget(self.pxScaleLbl, 3, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox)


        self.horizontalLayout_5.addLayout(self.verticalLayout_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.distanceGraph = BouncePlot(self.dataTab)
        self.distanceGraph.setObjectName(u"distanceGraph")

        self.verticalLayout.addWidget(self.distanceGraph)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)

        self.saveDataBtn_2 = QPushButton(self.dataTab)
        self.saveDataBtn_2.setObjectName(u"saveDataBtn_2")

        self.horizontalLayout_6.addWidget(self.saveDataBtn_2)

        self.saveDataAsBtn = QPushButton(self.dataTab)
        self.saveDataAsBtn.setObjectName(u"saveDataAsBtn")

        self.horizontalLayout_6.addWidget(self.saveDataAsBtn)

        self.deleteDataBtn = QPushButton(self.dataTab)
        self.deleteDataBtn.setObjectName(u"deleteDataBtn")

        self.horizontalLayout_6.addWidget(self.deleteDataBtn)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_5.addLayout(self.verticalLayout)

        self.tabWidget.addTab(self.dataTab, "")
        self.rawDataTab = QWidget()
        self.rawDataTab.setObjectName(u"rawDataTab")
        self.gridLayout_2 = QGridLayout(self.rawDataTab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tableView = TableControl(self.rawDataTab)
        self.tableView.setObjectName(u"tableView")
        sizePolicy4.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy4)
        self.tableView.setMinimumSize(QSize(500, 480))

        self.gridLayout_2.addWidget(self.tableView, 0, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_4)

        self.saveDataBtn = QPushButton(self.rawDataTab)
        self.saveDataBtn.setObjectName(u"saveDataBtn")

        self.horizontalLayout_7.addWidget(self.saveDataBtn)

        self.saveDataAsBtn_2 = QPushButton(self.rawDataTab)
        self.saveDataAsBtn_2.setObjectName(u"saveDataAsBtn_2")

        self.horizontalLayout_7.addWidget(self.saveDataAsBtn_2)


        self.gridLayout_2.addLayout(self.horizontalLayout_7, 1, 0, 1, 1)

        self.tabWidget.addTab(self.rawDataTab, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        Bounce.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Bounce)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1217, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        Bounce.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Bounce)
        self.statusbar.setObjectName(u"statusbar")
        Bounce.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addAction(self.actionBatch_Process)

        self.retranslateUi(Bounce)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Bounce)
    # setupUi

    def retranslateUi(self, Bounce):
        Bounce.setWindowTitle(QCoreApplication.translate("Bounce", u"BounceAnalyzer", None))
        self.actionOpen.setText(QCoreApplication.translate("Bounce", u"Open...", None))
        self.actionPreferences.setText(QCoreApplication.translate("Bounce", u"Preferences", None))
        self.actionCalibrate_Scale.setText(QCoreApplication.translate("Bounce", u"Calibrate Scale", None))
        self.actionDelete_Scale.setText(QCoreApplication.translate("Bounce", u"Delete Scale", None))
        self.actionBatch_Process.setText(QCoreApplication.translate("Bounce", u"Batch Process", None))
        self.statusLbl.setText(QCoreApplication.translate("Bounce", u"TextLabel", None))
        self.playBtn.setText(QCoreApplication.translate("Bounce", u"\u25ba", None))
        self.pauseBtn.setText(QCoreApplication.translate("Bounce", u"||", None))
        self.resetFrame.setText(QCoreApplication.translate("Bounce", u"Reset", None))
        self.label_8.setText(QCoreApplication.translate("Bounce", u"Acceleration Threshold:", None))
        self.label_3.setText(QCoreApplication.translate("Bounce", u" Pixel Scale:", None))
        self.pxScaleSpin.setSpecialValueText(QCoreApplication.translate("Bounce", u"Auto", None))
        self.pxScaleSpin.setSuffix(QCoreApplication.translate("Bounce", u" mm", None))
        self.label_7.setText(QCoreApplication.translate("Bounce", u"Ball Size", None))
        self.ballSizeSpin.setSuffix(QCoreApplication.translate("Bounce", u" mm", None))
        self.startEvalBtn.setText(QCoreApplication.translate("Bounce", u"Start Eval", None))
        self.label.setText(QCoreApplication.translate("Bounce", u"Log:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.videoTab), QCoreApplication.translate("Bounce", u"Video", None))
        self.groupBox.setTitle(QCoreApplication.translate("Bounce", u"Info", None))
        self.label_6.setText(QCoreApplication.translate("Bounce", u"Max Acceleration", None))
        self.corLbl.setText(QCoreApplication.translate("Bounce", u"0", None))
        self.maxDeformLbl.setText(QCoreApplication.translate("Bounce", u"0", None))
        self.label_2.setText(QCoreApplication.translate("Bounce", u"Max Deformation", None))
        self.maxAccelLbl.setText(QCoreApplication.translate("Bounce", u"0", None))
        self.label_4.setText(QCoreApplication.translate("Bounce", u"COR (Vo/Vi)", None))
        self.label_5.setText(QCoreApplication.translate("Bounce", u"Pixel Scale", None))
        self.pxScaleLbl.setText(QCoreApplication.translate("Bounce", u"0", None))
        self.saveDataBtn_2.setText(QCoreApplication.translate("Bounce", u"Save Data", None))
        self.saveDataAsBtn.setText(QCoreApplication.translate("Bounce", u"Save Data As", None))
        self.deleteDataBtn.setText(QCoreApplication.translate("Bounce", u"Delete Data", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dataTab), QCoreApplication.translate("Bounce", u"Data", None))
        self.saveDataBtn.setText(QCoreApplication.translate("Bounce", u"Save Data", None))
        self.saveDataAsBtn_2.setText(QCoreApplication.translate("Bounce", u"Save Data As", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rawDataTab), QCoreApplication.translate("Bounce", u"Raw Data", None))
        self.menuFile.setTitle(QCoreApplication.translate("Bounce", u"File", None))
    # retranslateUi

