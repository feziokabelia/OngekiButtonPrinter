import pygame
from core.printer import poll_joystick


def try_init_joystick(self):
    if pygame_init(self):  # 如果初始化成功
        try:
            self.timer.timeout.connect(lambda: poll_joystick(self))
        except Exception as e:
            print(e)
        self.init_timer.stop()
        self.timer.start(50)  # 50ms 启动一次计时器


def pygame_init(self):
    try:
        if self.flag:
            self.text.setVisible(False)
        pygame.joystick.quit()
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.text.setVisible(False)
        print(666)
        return True
    except pygame.error:  # 没有连接到手台
        self.text.setVisible(True)
        self.flag = False
        return False
