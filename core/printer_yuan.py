import keyboard
from conifg.settings_yuangeki import key_states
import conifg.settings

LW = conifg.settings.LW
LR = conifg.settings.LR
LG = conifg.settings.LG
LB = conifg.settings.LB
RW = conifg.settings.RW
RR = conifg.settings.RR
RG = conifg.settings.RG
RB = conifg.settings.RB


def poll_joystick(self):  # 查询按键情况
    # 安装全局钩子
    keyboard.hook(lambda e: None)

    # 显示左右手背景用
    l_flag = 0
    r_flag = 0
    j = 0

    for key in key_states:
        current_state = keyboard.is_pressed(key)
        # 处理状态变化:
        if current_state != key_states[key]:
            if current_state:
                pressed_key_motion = key + "m"

                # print(f"按下 {key} 键，动作: {pressed_key_motion}")
                diff1 = (self.last_button in self.left_button and pressed_key_motion in self.left_button)
                diff2 = (self.last_button in self.right_button and pressed_key_motion in self.right_button)
                if self.release_button[key] == 1:
                    return
                self.m_press(key, pressed_key_motion, diff1, diff2)

            else:
                # print(f"释放 {key} 键")
                self.m_release(key, key + "m")
            key_states[key] = current_state

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


def m_press(self, pressed_key, pressed_key_motion, diff1, diff2):  # 按下
    self.release_button[pressed_key] = 1
    if pressed_key in (LW, LR, LG, LB):
        self.bg_item_l0.setVisible(False)
    else:
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
