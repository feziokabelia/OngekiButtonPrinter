import os
from core.printer_yuan import poll_joystick

from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, \
    QGraphicsTextItem, \
    QLabel
from PyQt6.QtGui import QPixmap, QImage, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer

import config.settings
from config.settings import BACKGROUND_IMAGE, BUTTON_CONFIG, IMAGE_MAP

LW = config.settings.LW
LR = config.settings.LR
LG = config.settings.LG
LB = config.settings.LB
RW = config.settings.RW
RR = config.settings.RR
RG = config.settings.RG
RB = config.settings.RB


class ArcadeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_button = ""  # 上次按下的按键对应的动作
        self.setWindowTitle("点击观看音击小孩玩音击 by源")
        self.setFixedSize(400, 300)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 400, 300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.setStyleSheet('background-color:transparent')
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # 变量
        self.flag = True  # 辨别初次 显示手台连接情况用
        red = QColor(255, 0, 0)
        # self.relink_count = 0
        # self.relink_count_text = QGraphicsTextItem("")
        # self.relink_count_text.setDefaultTextColor(QColor(245, 163, 118))
        bg_path_r0 = os.path.join("../jpgs", "r_0.png")
        bg_item_swing = os.path.join("../jpgs", "swing.png")
        bg_path_l0 = os.path.join("../jpgs", "l_0.png")
        self.bg_item_r0 = QGraphicsPixmapItem(QPixmap(bg_path_r0).scaled(400, 300))
        self.bg_item_swing = QGraphicsPixmapItem(QPixmap(bg_item_swing).scaled(400, 300))
        self.bg_item_l0 = QGraphicsPixmapItem(QPixmap(bg_path_l0).scaled(400, 300))
        self.release_button = {
            LW: 0,
            LR: 0,
            LG: 0,
            LB: 0,
            RR: 0,
            RG: 0,
            RB: 0,
            RW: 0,
        }  # 对应每个按键的按下释放情况  1 按下 0 没按
        self.left_button = (LW + "m", LR + "m", LG + "m", LB + "m")
        self.right_button = (RR + "m", RG + "m", RB + "m", RW + "m")
        self.last_left_button_arr = ["", "", "", ""]  # 记录左侧按下情况的数组
        self.last_left_button_i = 0
        self.last_right_button_arr = ["", "", "", ""]  # 记录右侧按下情况的数组
        self.last_right_button_i = 0
        self.left_show = ""
        self.right_show = ""

        # 加载资源
        self.button_items = {}
        self.images = {}
        self.load_images()
        self.setup_ui()
        self.text = QGraphicsTextItem("未检测到手台")
        self.text.setDefaultTextColor(red)
        self.text.setPos(30, 10)
        self.scene.addItem(self.text)
        self.text.setVisible(False)

        # 连接手台
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: poll_joystick(self))
        self.timer.start(50)

    def load_images(self):
        for btn, filename in IMAGE_MAP.items():
            path = os.path.join("../jpgs", filename)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.images[btn] = pixmap.scaled(
                        BUTTON_CONFIG[btn]["width"],
                        BUTTON_CONFIG[btn]["height"],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )

        # 加载背景
        bg_path = os.path.join("../jpgs", BACKGROUND_IMAGE)
        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))  # RGBA: A=0 表示全透明.
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path)
            if not bg_pixmap.isNull():
                bg_item = QGraphicsPixmapItem(bg_pixmap.scaled(400, 300))
                self.scene.addItem(bg_item)
                self.scene.addItem(self.bg_item_l0)
                self.scene.addItem(self.bg_item_r0)
                self.scene.addItem(self.bg_item_swing)
                self.bg_item_swing.setZValue(999)

    def setup_ui(self):  # 加载按键和动作图片
        for btn, config in BUTTON_CONFIG.items():
            if btn in self.images:
                item = QGraphicsPixmapItem(self.images[btn])
                item.setPos(config["x"], config["y"])
                self.scene.addItem(item)
                self.button_items[btn] = item
                item.setVisible(False)
