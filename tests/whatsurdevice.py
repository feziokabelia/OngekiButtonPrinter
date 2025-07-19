import pygame


#  检测手台按键
def detect():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"按钮 {event.button} 按下")
            elif event.type == pygame.JOYBUTTONUP:
                print(f"按钮 {event.button} 释放")


if __name__ == "__main__":
    pygame.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        detect()
    else:
        print("未检测到手台")
