import os
import sys
from ctypes import cdll
from core.printer_HID import poll_joystick

from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, \
    QGraphicsTextItem, \
    QLabel
from PyQt6.QtGui import QPixmap, QImage, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer

import config.settings_HID
from config.settings_HID import BACKGROUND_IMAGE, BUTTON_CONFIG, IMAGE_MAP, dll_path, VENDOR_ID, PRODUCT_ID

LW = config.settings_HID.LW
LR = config.settings_HID.LR
LG = config.settings_HID.LG
LB = config.settings_HID.LB
RW = config.settings_HID.RW
RR = config.settings_HID.RR
RG = config.settings_HID.RG
RB = config.settings_HID.RB

try:
    cdll.LoadLibrary(dll_path)  # 使用绝对路径
    import hid
    # print(f"成功加载 hidapi!  路径{dll_path}")
except Exception as e:
    with open('hid_error.log', 'w') as file:
        file.write("fail to load hidapi.dll!")
        file.write(str(e))
    print(f"加载失败: {e}")
    sys.exit()


class ArcadeController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device = None
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
        bg_path_r0 = os.path.join("jpgs", "r_0.png")
        bg_item_swing = os.path.join("jpgs", "swing.png")
        bg_path_l0 = os.path.join("jpgs", "l_0.png")
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
        self.last_lever_pos = ""
        self.is_show_bg_l0 = False
        self.is_show_bg_r0 = False
        self.is_left = True
        self.last_ana = 0
        self.first_down = True
        self.last_subpos = 0

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
        self.init_timer = QTimer(self)  # 用于初始化的定时器
        self.timer = QTimer(self)
        self.relink_timer = QTimer(self)  # 用于relink
        self.init_timer.timeout.connect(self.try_init_joystick)
        self.init_timer.start(1000)  # 每秒检查一次连接

    def try_init_joystick(self):

        if self.hid_init():  # 如果初始化成功
            try:
                self.timer.timeout.connect(lambda: poll_joystick(self))
            except Exception as e:
                print(e)
            self.init_timer.stop()
            self.timer.start(50)  # 50ms 启动一次计时器

    def hid_init(self):
        try:
            if self.flag:
                self.text.setVisible(False)
            # self.device = hid.Device(VENDOR_ID, PRODUCT_ID)
            device = hid.device()
            device.open(VENDOR_ID, PRODUCT_ID)
            self.device = device
            self.text.setVisible(False)
            return True
        except Exception as e:  # 没有连接到手台
            self.text.setVisible(True)
            self.flag = False
            return False

    def load_images(self):
        for btn, filename in IMAGE_MAP.items():
            path = os.path.join("jpgs", filename)
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
        bg_path = os.path.join("jpgs", BACKGROUND_IMAGE)
        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))  # RGBA: A=0 表示全透明.
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path)
            if not bg_pixmap.isNull():
                # 使用平滑转换
                scaled_pixmap = bg_pixmap.scaled(400, 300,
                                                 Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
                bg_item = QGraphicsPixmapItem(scaled_pixmap)
                bg_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                bg_item.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
                self.scene.addItem(bg_item)
                self.bg_item_l0.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                self.bg_item_r0.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                self.scene.addItem(self.bg_item_l0)
                self.scene.addItem(self.bg_item_r0)
                self.scene.addItem(self.bg_item_swing)
                self.bg_item_swing.setZValue(999)
                self.bg_item_swing.setVisible(False)

    def setup_ui(self):  # 加载按键和动作图片
        for btn, config in BUTTON_CONFIG.items():
            if btn in self.images:
                item = QGraphicsPixmapItem(self.images[btn])
                item.setPos(config["x"], config["y"])
                # 平滑处理
                item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                item.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
                self.scene.addItem(item)
                self.button_items[btn] = item
                item.setVisible(False)

    def close_swing(self):
        self.button_items["lever_0"].setVisible(False)
        self.button_items["lever_1"].setVisible(False)
        self.button_items["lever_-1"].setVisible(False)
        self.button_items["lever_2"].setVisible(False)
        self.button_items["lever_-2"].setVisible(False)

    def relink(self):
        self.relink_timer = QTimer(self)  # 初始化定时器
        self.relink_timer.timeout.connect(self.try_init_joystick)
        self.relink_timer.start(1000)  # 每秒检查一次连接
