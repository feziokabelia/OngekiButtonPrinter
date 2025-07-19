# 31 0 5 4 | 1 16 15 14 ←从左到右是左侧键到右侧键
LW = "31"
LR = "0"
LG = "5"
LB = "4"

RR = "1"
RG = "16"
RB = "15"
RW = "14"
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
}

