import math
import os
import struct
import sys
from ctypes import cdll

import pygame
import config.settings_Oncontroller_HID

LW = config.settings_Oncontroller_HID.LW
LR = config.settings_Oncontroller_HID.LR
LG = config.settings_Oncontroller_HID.LG
LB = config.settings_Oncontroller_HID.LB
RW = config.settings_Oncontroller_HID.RW
RR = config.settings_Oncontroller_HID.RR
RG = config.settings_Oncontroller_HID.RG
RB = config.settings_Oncontroller_HID.RB
L_MAX = config.settings_Oncontroller_HID.L_MAX
L_1 = config.settings_Oncontroller_HID.L_1
L_2 = config.settings_Oncontroller_HID.L_2
R_MAX = config.settings_Oncontroller_HID.R_MAX
R_1 = config.settings_Oncontroller_HID.R_1
R_2 = config.settings_Oncontroller_HID.R_2
VENDOR_ID = config.settings_Oncontroller_HID.VENDOR_ID
PRODUCT_ID = config.settings_Oncontroller_HID.PRODUCT_ID
key_map = config.settings_Oncontroller_HID.key_map
dll_path = config.settings_Oncontroller_HID.dll_path

OUTPUT_T_FORMAT = '<8h 4h 2B 2B 2H 2B 29x'  # 小端字节序，2B 2B 表示 2个 coin_data_t（每个2字节）
STRUCT_SIZE = struct.calcsize(OUTPUT_T_FORMAT)

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


def get_pos(position):
    pos_image = ""
    if L_MAX + 20 > position >= L_2:
        pos_image = "lever_-2"
    if L_2 > position >= L_1:
        pos_image = "lever_-1"
    if L_1 > position >= R_1:
        pos_image = "lever_0"
    if R_1 > position >= R_2:
        pos_image = "lever_1"
    if R_2 > position > R_MAX - 20:
        pos_image = "lever_2"
    return pos_image


def get_sub_position(rotary0):
    total_range = 255
    sub_range_size = total_range / 20  # 3276.8
    sub_pos = int(rotary0 // sub_range_size)  # 映射到0~19
    return min(max(sub_pos, 0), 19)  # 限制在0~19


def poll_joystick(self):  # 查询按键情况
    try:
        # self.device = hid.Device(VENDOR_ID, PRODUCT_ID)
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        self.device = device
        self.relink_timer.stop()
    except Exception:
        self.text.setPlainText("等待连接中……")
        self.timer.stop()
        self.relink()
    # 显示左右手背景用
    l_flag = 0
    r_flag = 0
    j = 0

    pressed_keys = []
    try:
        data_hid = read_hid(self)
        self.relink_timer.stop()
    except Exception:
        self.text.setPlainText("等待连接中……")
        self.timer.stop()
        self.relink()
        return
    if data_hid is None:
        return
    else:
        key_data = data_hid.get("key")
    # 显示摇杆
    result = show_lever(self, data_hid, key_data, pressed_keys)
    pressed_keys = result[0]
    last_lever_pos = result[1]
    for i in (LW, LR, LG, LB, RR, RG, RW, RB):
        current = False
        for ind in range(len(pressed_keys)):
            if pressed_keys[ind] == i:
                # print(data_hid)
                current = True
        pressed_key = str(i)
        pressed_key_motion = pressed_key + "m"  # 手部图片

        # 判断是否同侧
        diff1 = (self.last_button in self.left_button and pressed_key_motion in self.left_button)
        diff2 = (self.last_button in self.right_button and pressed_key_motion in self.right_button)

        if not (pressed_key in (LW, LR, LG, LB, RR, RG, RB, RW)):  # 不在这8个键不会反应
            continue

        if current:
            if self.release_button[pressed_key] == 1:
                continue
            m_press(self, pressed_key, pressed_key_motion, diff1, diff2, last_lever_pos)
        else:
            m_release(self, pressed_key, pressed_key_motion)

    # 判断左边右边分别有多少按键
    for i in self.release_button.keys():
        if j < 4:
            l_flag = l_flag + self.release_button[i]
        else:
            r_flag = r_flag + self.release_button[i]
        j = j + 1
    if l_flag == 0:
        self.bg_item_l0.setVisible(True)
    if r_flag == 0:
        self.bg_item_r0.setVisible(True)
    if not self.is_show_bg_l0:
        self.bg_item_l0.setVisible(False)
    if not self.is_show_bg_r0:
        self.bg_item_r0.setVisible(False)


def read_hid(self):
    current_data = self.device.read(5)
    if not current_data:
        return None
    op = {
        "sub_pos": current_data[2],  # int
        "pos": current_data[1],  # int
        "key": f"{current_data[3]:08b}",  # str
    }
    return op


def show_lever(self, data_hid, key_data, pressed_keys):
    result = []
    # 显示摇杆
    position = data_hid.get("pos")  # 摇杆位置
    pos_image = get_pos(position)
    sub_pos = get_sub_position(data_hid.get("sub_pos"))
    # print(sub_pos)

    is_l_buttons = False
    is_r_buttons = False
    release_button_i = 0

    for i in (LW, LR, LG, LB, RR, RG, RB, RW):
        if release_button_i < 4:  # 左侧
            if self.release_button[i] == 1:
                is_l_buttons = True
        else:
            if self.release_button[i] == 1:
                # print("右侧有键")
                is_r_buttons = True
        release_button_i = release_button_i + 1
    last_lever_pos = self.last_lever_pos
    if self.last_lever_pos != position:  # 左侧有按键则不显示摇杆 右侧同
        self.close_swing()
        if self.last_lever_pos != "":
            self.button_items["l_" + str(get_pos(self.last_lever_pos))].setVisible(False)
            self.button_items["r_" + str(get_pos(self.last_lever_pos))].setVisible(False)
        # print(f"{is_l_buttons}  {is_r_buttons}")
        if self.last_button != "":
            self.button_items[self.last_button].setVisible(False)
        if is_l_buttons and is_r_buttons:  # 情况1 左右两侧都有按键
            # print("情况1")
            self.button_items["l_" + pos_image].setVisible(False)
            self.button_items["r_" + pos_image].setVisible(False)
            self.button_items[pos_image].setVisible(True)
            # self.bg_item_swing.setVisible(True)
        else:
            self.bg_item_swing.setVisible(False)
        if is_l_buttons and not is_r_buttons:  # 情况2 左侧有 右侧没有
            # print("情况2")
            # print("l_" + pos_image)
            self.is_show_bg_l0 = True
            self.is_left = False
            self.button_items[pos_image].setVisible(False)
            self.button_items["l_" + pos_image].setVisible(True)
            self.button_items["r_" + pos_image].setVisible(False)
        else:
            self.is_show_bg_l0 = False
        if not is_l_buttons and is_r_buttons:  # 情况3 右侧有 左侧没有
            # print("情况3")
            self.is_show_bg_r0 = True
            self.is_left = True
            self.button_items[pos_image].setVisible(False)
            self.button_items["l_" + pos_image].setVisible(False)
            self.button_items["r_" + pos_image].setVisible(True)
        else:
            self.is_show_bg_r0 = False
        if not is_l_buttons and not is_r_buttons:  # 情况4 都没有
            # print("情况4")
            # print(self.is_left)
            if self.is_left:
                # print("换右")
                self.is_show_bg_r0 = True
                self.button_items[pos_image].setVisible(False)
                self.button_items["r_" + pos_image].setVisible(True)  # 换默认右
            else:
                # print("换左")
                self.is_show_bg_l0 = True
                self.button_items[pos_image].setVisible(False)
                self.button_items["l_" + pos_image].setVisible(True)  # 换默认左
        self.last_lever_pos = position
        self.first_down = True
    elif self.last_lever_pos == position:  # 摇杆不动 手放下
        if self.last_subpos == sub_pos:
            # self.bg_item_swing.setVisible(True)
            self.button_items[pos_image].setVisible(True)
            self.is_show_bg_r0 = True
            self.is_show_bg_l0 = True
            self.button_items["l_" + str(get_pos(self.last_lever_pos))].setVisible(False)
            self.button_items["r_" + str(get_pos(self.last_lever_pos))].setVisible(False)
        self.last_subpos = sub_pos
    # print("l_" + pos_image)

    for bit_pos in range(len(key_data)):  # 检查每一位
        new_state = int(key_data[bit_pos])
        if new_state == 1:
            for i in key_map.keys():
                if bit_pos == i:
                    print(i)
                    pressed_keys.append(key_map.get(i))
    result.append(pressed_keys)
    result.append(last_lever_pos)
    return result


def m_press(self, pressed_key, pressed_key_motion, diff1, diff2, last_lever_pos):  # 按下
    self.release_button[pressed_key] = 1
    if pressed_key in (LW, LR, LG, LB):
        self.button_items["r_" + str(get_pos(self.last_lever_pos))].setVisible(False)
        self.bg_item_l0.setVisible(False)
    else:
        self.button_items["l_" + str(get_pos(self.last_lever_pos))].setVisible(False)
        self.bg_item_r0.setVisible(False)

    if pressed_key in self.button_items:
        self.button_items[pressed_key].setVisible(True)
        self.button_items[pressed_key_motion].setVisible(True)  # motion True

        # 动作图片隐藏的逻辑判断
        if pressed_key in (LW, LR, LG, LB):
            self.left_show = pressed_key_motion
            for le in reversed(range(len(self.last_left_button_arr))):
                if self.last_left_button_arr[le] != "":
                    self.button_items[self.last_left_button_arr[le] + "m"].setVisible(False)
        else:
            self.right_show = pressed_key_motion
            for r in reversed(range(len(self.last_right_button_arr))):
                if self.last_right_button_arr[r] != "":
                    self.button_items[self.last_right_button_arr[r] + "m"].setVisible(False)
        if not self.last_button == "":
            if self.last_button != pressed_key_motion:
                # 同在左 或 同在右
                if diff1 or diff2:  # 不同边
                    self.button_items[self.last_button].setVisible(False)  # motion False

        if pressed_key_motion in self.left_button:
            for k in range(len(self.last_left_button_arr)):
                if self.last_left_button_arr[k] == "":
                    self.last_left_button_arr[k] = pressed_key
                    break
        else:
            for k in range(len(self.last_right_button_arr)):
                if self.last_right_button_arr[k] == "":
                    self.last_right_button_arr[k] = pressed_key
                    break


def m_release(self, pressed_key, pressed_key_motion):
    null_count = 0  # 记录last_button_arr有多少“”
    if pressed_key in self.button_items:
        if self.release_button[pressed_key] == 1:
            left = pressed_key_motion in self.left_button

            if left:
                button_arr = self.last_left_button_arr
                show = self.left_show  # 上一个显示的动作图片
            else:
                button_arr = self.last_right_button_arr
                show = self.right_show  # 同上

            # if left:
            # self.last_left_button_i = self.last_left_button_i - 1
            # else:
            # self.last_right_button_i = self.last_right_button_i - 1

            k = 0  # 当last_button_arr内只有一个按键，记录其下标
            for a in range(len(button_arr)):
                # print(f"数组{i}  {button_arr[i]}")
                if pressed_key == button_arr[a]:
                    # print(f"释放 {button_arr[i]}")
                    if a > 0:
                        # print(f"i {i}")
                        # print(f"该 {button_arr[a-1]} 显示")
                        # print(f"松开前显示的是{show}")

                        # 动作图片显示逻辑判断
                        if button_arr[a - 1] != "":
                            if show != (button_arr[a - 1] + "m") and show != "":
                                # print(f"{button_arr[a - 1]} 显示")
                                self.button_items[show].setVisible(False)
                                self.button_items[button_arr[a - 1] + "m"].setVisible(True)
                                if left:
                                    self.left_show = button_arr[a - 1] + "m"
                                else:
                                    self.right_show = button_arr[a - 1] + "m"
                                if button_arr[a] != "":
                                    self.button_items[button_arr[a] + "m"].setVisible(False)
                                    button_arr[a] = ""
                                break
                    else:
                        for b in reversed(range(len(button_arr))):
                            if button_arr[b] != "":
                                self.button_items[button_arr[b] + "m"].setVisible(True)
                                break
                    button_arr[a] = ""

                else:
                    self.release_button[pressed_key] = 0
                    self.button_items[pressed_key].setVisible(False)
                    self.button_items[pressed_key_motion].setVisible(False)
            for h in range(len(button_arr)):
                if button_arr[h] == "":
                    # print(f"空的位置 {h}")
                    null_count = null_count + 1
                else:
                    # print(f"k = {k}")
                    k = h
            if null_count == 3:
                # print(k)
                # print(f"数组唯一的值 {button_arr[k]}")
                self.button_items[button_arr[k] + "m"].setVisible(True)
