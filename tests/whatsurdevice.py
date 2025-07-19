import pygame

output_file = "log_device.log"
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

    try:
        pygame.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            detect()
        else:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("未检测到手台")
    except pygame.error as e:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(str(e))


