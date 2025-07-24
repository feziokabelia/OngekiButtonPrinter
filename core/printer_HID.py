import math
import os
import struct
import sys
from ctypes import cdll

import pygame
import config.settings_HID

LW = config.settings_HID.LW
LR = config.settings_HID.LR
LG = config.settings_HID.LG
LB = config.settings_HID.LB
RW = config.settings_HID.RW
RR = config.settings_HID.RR
RG = config.settings_HID.RG
RB = config.settings_HID.RB
L_MAX = config.settings_HID.L_MAX
L_1 = config.settings_HID.L_1
L_2 = config.settings_HID.L_2
R_MAX = config.settings_HID.R_MAX
R_1 = config.settings_HID.R_1
R_2 = config.settings_HID.R_2
VENDOR_ID = config.settings_HID.VENDOR_ID
PRODUCT_ID = config.settings_HID.PRODUCT_ID
key_map = config.settings_HID.key_map
dll_path = config.settings_HID.dll_path

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


def parse_output_t(data: bytes):
    """解析输出数据，仅提取指定字段"""
    unpacked = struct.unpack(OUTPUT_T_FORMAT, data)
    return {
        'rotary': unpacked[8:12],  # 后续4个int16_t (旋转编码器)
        'switches': unpacked[16:18],  # 2个uint16_t (开关状态)
        'system_status': unpacked[18]  # uint8_t (系统状态)
    }


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


def get_sub_position(rotary0, rotary1):
    total_range = 65536  # 32768 - (-32768)
    sub_range_size = total_range / 20  # 3276.8
    sub_pos = int((rotary0 + 32768) // sub_range_size)  # 映射到0~19
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
        index = 0
        key_data = [[0 for _ in range(16)] for _ in range(2)]
        for switch_idx, switch in enumerate(data_hid.get("key")):
            bits = switch[2:]  # 去掉 '0b' 前缀
            for bit_pos in range(16):
                bit_value = bits[bit_pos]  # 从左到右依次为 Bit0 → Bit15
                key_data[index][bit_pos] = bit_value
            index = index + 1
    # 显示摇杆
    result = show_lever(self, data_hid, key_data, pressed_keys)
    pressed_keys = result[0]
    pos_image = result[1]

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
            m_press(self, pressed_key, pressed_key_motion, diff1, diff2, pos_image)
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
    data = self.device.read(STRUCT_SIZE)
    if not data:
        return None
    current_data = parse_output_t(bytes(data))
    switches_str = [f"0b{s:016b}" for s in current_data['switches']]
    op = {
        "sub_pos": current_data['rotary'][0],  # int
        "pos": current_data['rotary'][1],  # int
        "key": switches_str,  # list
        "lw": current_data['system_status']  # int
    }
    return op

def show_lever(self, data_hid, key_data, pressed_keys):
    result = []
    # 显示摇杆
    position = data_hid.get("pos")  # 摇杆位置
    pos_image = get_pos(position)
    sub_pos = get_sub_position(data_hid.get("sub_pos"), data_hid.get("pos"))
    # print(sub_pos)

    if math.copysign(1, data_hid.get("sub_pos")) == 1:
        analog = True
    else:
        analog = False
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
    # print(f"{is_l_buttons}    {is_r_buttons}")
    # print(is_l_buttons and not is_r_buttons)
    # print(self.release_button.values())
    # print(f"{is_l_buttons}    {is_r_buttons}")
    # print("------------------------")
    # print(f"{is_l_buttons != self.prev_l_buttons}  {is_r_buttons != self.prev_r_buttons}")
    # print("*********************************")
    if (is_l_buttons != self.prev_l_buttons) or (is_r_buttons != self.prev_r_buttons):
        status = True  # 任意一个按钮状态变化，status 设为 True
    else:
        status = False
    if is_l_buttons and is_l_buttons:
        status = True
    # print((is_l_buttons != self.prev_l_buttons) or (is_r_buttons != self.prev_r_buttons))
    self.prev_l_buttons = is_l_buttons
    self.prev_r_buttons = is_l_buttons
    # print(f"{is_l_buttons}  {is_r_buttons}")
    # print(status)
    # 第一版 self.last_lever_pos != pos_image
    if self.last_lever_pos != position:  # 左侧有按键则不显示摇杆 右侧同
        if self.last_lever_pos != "":
            self.button_items["l_" + str(get_pos(self.last_lever_pos))].setVisible(False)
            self.button_items["r_" + str(get_pos(self.last_lever_pos))].setVisible(False)
        # print(f"{is_l_buttons}  {is_r_buttons}")
        if is_l_buttons and is_r_buttons:  # 情况1 左右两侧都有按键
            # print("情况1")
            self.button_items["l_" + pos_image].setVisible(False)
            self.button_items["r_" + pos_image].setVisible(False)
            self.bg_item_swing.setVisible(True)
        else:
            self.bg_item_swing.setVisible(False)
        if is_l_buttons and not is_r_buttons:  # 情况2 左侧有 右侧没有
            # print("情况2")
            # print("l_" + pos_image)
            self.is_show_bg_l0 = True
            self.is_left = False
            self.button_items["l_" + pos_image].setVisible(True)
            self.button_items["r_" + pos_image].setVisible(False)
        else:
            self.is_show_bg_l0 = False
        if not is_l_buttons and is_r_buttons:  # 情况3 右侧有 左侧没有
            # print("情况3")
            self.is_show_bg_r0 = True
            self.is_left = True
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
                self.button_items["r_" + pos_image].setVisible(True)  # 换默认右
            else:
                # print("换左")
                self.is_show_bg_l0 = True
                self.button_items["l_" + pos_image].setVisible(True)  # 换默认左
        self.last_lever_pos = position
        self.last_ana = analog
        self.first_down = True
    elif self.last_lever_pos == position:  # 摇杆不动 手放下
        if self.last_subpos == sub_pos:
            self.bg_item_swing.setVisible(True)
            self.is_show_bg_r0 = True
            self.is_show_bg_l0 = True
            self.button_items["l_" + str(get_pos(self.last_lever_pos))].setVisible(False)
            self.button_items["r_" + str(get_pos(self.last_lever_pos))].setVisible(False)
        self.last_subpos = sub_pos

    # print("l_" + pos_image)
    for switch_idx in range(2):  # 遍历左/右开关
        for bit_pos in range(16):  # 检查每一位
            new_state = int(key_data[switch_idx][bit_pos])  # 注意：bits[0]是MSB（Bit15）
            if switch_idx == 1 and bit_pos == 9:
                if new_state == 0:
                    new_state = 1
                else:
                    new_state = 0
            if new_state == 1:
                if switch_idx == 0:
                    key_map_l = key_map.get(switch_idx)
                    for i in key_map_l.keys():
                        if bit_pos == i:
                            pressed_keys.append(key_map_l.get(i))
                else:
                    key_map_r = key_map.get(switch_idx)
                    for i in key_map_r.keys():
                        if bit_pos == i:
                            pressed_keys.append(key_map_r.get(i))
    if data_hid.get("lw") == 0:
        pressed_keys.append(LW)
    result.append(pressed_keys)
    result.append(pos_image)
    return result


def m_press(self, pressed_key, pressed_key_motion, diff1, diff2, pos_image):  # 按下
    self.release_button[pressed_key] = 1
    if pressed_key in (LW, LR, LG, LB):
        self.button_items["r_" + pos_image].setVisible(False)
        self.bg_item_l0.setVisible(False)
    else:
        self.button_items["l_" + pos_image].setVisible(False)
        self.bg_item_r0.setVisible(False)

    if pressed_key in self.button_items:
        # print(f"press = {pressed_key}")
        # print(f"release = {released_key}")
        self.button_items[pressed_key].setVisible(True)
        self.button_items[pressed_key_motion].setVisible(True)  # motion True
        # print(f"{pressed_key} 显示")

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
        # self.last_button = pressed_key_motion

        if pressed_key_motion in self.left_button:
            # arr = self.last_left_button_arr
            # self.last_left_button_arr[self.last_left_button_i] = pressed_key
            for k in range(len(self.last_left_button_arr)):
                if self.last_left_button_arr[k] == "":
                    self.last_left_button_arr[k] = pressed_key
                    break
            # self.last_left_button_i = self.last_left_button_i + 1
        else:
            # arr = self.last_right_button_arr
            for k in range(len(self.last_right_button_arr)):
                if self.last_right_button_arr[k] == "":
                    self.last_right_button_arr[k] = pressed_key
                    break


def m_release(self, pressed_key, pressed_key_motion):
    null_count = 0  # 记录last_button_arr有多少“”
    if pressed_key in self.button_items:
        if self.release_button[pressed_key] == 1:
            # print(f"{pressed_key} 释放")
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
