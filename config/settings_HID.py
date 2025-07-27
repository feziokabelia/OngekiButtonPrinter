# 31 0 5 4 | 1 16 15 14 ←从左到右是左侧键到右侧键 用hid这里字符串是什么无所谓
import math
import configparser
import os

config = configparser.ConfigParser()
try:
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_path)
    VENDOR_ID = int(config.get('deviceid', 'VENDOR_ID'), 16)
    PRODUCT_ID = int(config.get('deviceid', 'PRODUCT_ID'), 16)
    L_MAX = int(config.get('boundary', 'L_MAX'))
    R_MAX = int(config.get('boundary', 'R_MAX'))
    # 摇杆边界值设定 [L_MAX L2] [L2 L1] [L1 R1] [R1 R2] [R2 R_MAX]
    if L_MAX < R_MAX:
        temp = L_MAX
        L_MAX = R_MAX
        R_MAX = temp
    space = math.ceil((L_MAX - R_MAX) / 5)
    L_2 = L_MAX - space
    L_1 = L_2 - space
    R_1 = L_1 - space
    R_2 = R_1 - space
except configparser.Error as e:
    print(e)
    print("fail to read config.ini")

dll_path = os.path.abspath('hidapi.dll')

LW = "31"
LR = "0"
LG = "5"
LB = "4"

RR = "1"
RG = "16"
RB = "15"
RW = "14"
# 图片配置


key_map = {
    # 索引0
    0: {
        7: LR,  # 左1（第7位）
        2: LG,  # 左2（第2位）
        3: LB,  # 左3（第3位）
        6: RR,  # 右1（第6位）
    },
    # 索引1
    1: {
        7: RG,  # 右2（第7位）
        8: RB,  # 右3（第8位）
        9: RW  # 右侧
    }
}

# 图片配置
IMAGE_MAP = {
    LW: "1_on.png",
    LW + "m": "1.png",

    LR: "2_on.png",
    LR + "m": "2.png",

    LG: "3_on.png",
    LG + "m": "3.png",

    LB: "4_on.png",
    LB + "m": "4.png",

    RR: "5_on.png",
    RR + "m": "5.png",

    RG: "6_on.png",
    RG + "m": "6.png",

    RB: "7_on.png",
    RB + "m": "7.png",

    RW: "8_on.png",
    RW + "m": "8.png",

    "l_lever_0": "l_swing_0.png",
    "l_lever_1": "l_swing_1.png",
    "l_lever_2": "l_swing_2.png",
    "l_lever_-1": "l_swing_-1.png",
    "l_lever_-2": "l_swing_-2.png",
    "r_lever_0": "r_swing_0.png",
    "r_lever_1": "r_swing_1.png",
    "r_lever_2": "r_swing_2.png",
    "r_lever_-1": "r_swing_-1.png",
    "r_lever_-2": "r_swing_-2.png",
}

BACKGROUND_IMAGE = "waiting.png"

# 按钮位置和尺寸配置
# +“m”是手部动作的图片 按键图片和手部图片分别处理
BUTTON_CONFIG = {
    LW: {"x": 0, "y": 0, "width": 400, "height": 300},
    LR: {"x": 0, "y": 0, "width": 400, "height": 300},
    LG: {"x": 0, "y": 0, "width": 400, "height": 300},
    LB: {"x": 0, "y": 0, "width": 400, "height": 300},
    RR: {"x": 0, "y": 0, "width": 400, "height": 300},
    RG: {"x": 0, "y": 0, "width": 400, "height": 300},
    RB: {"x": 0, "y": 0, "width": 400, "height": 300},
    RW: {"x": 0, "y": 0, "width": 400, "height": 300},
    LW + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    LR + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    LG + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    LB + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    RR + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    RG + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    RB + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    RW + "m": {"x": 0, "y": 0, "width": 400, "height": 300},
    "l_lever_0": {"x": 0, "y": 0, "width": 400, "height": 300},  # 从左到右依次-2 -1 0 1 2
    "l_lever_1": {"x": 0, "y": 0, "width": 400, "height": 300},
    "l_lever_2": {"x": 0, "y": 0, "width": 400, "height": 300},
    "l_lever_-1": {"x": 0, "y": 0, "width": 400, "height": 300},
    "l_lever_-2": {"x": 0, "y": 0, "width": 400, "height": 300},
    "r_lever_0": {"x": 0, "y": 0, "width": 400, "height": 300},
    "r_lever_1": {"x": 0, "y": 0, "width": 400, "height": 300},
    "r_lever_2": {"x": 0, "y": 0, "width": 400, "height": 300},
    "r_lever_-1": {"x": 0, "y": 0, "width": 400, "height": 300},
    "r_lever_-2": {"x": 0, "y": 0, "width": 400, "height": 300},
}
