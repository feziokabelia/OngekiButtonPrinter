from pynput import mouse
import time

# 初始化变量记录鼠标位置范围
min_x = float('inf')
max_x = 0
min_y = float('inf')
max_y = 0


def on_move(x, y):
    global min_x, max_x, min_y, max_y

    # 更新范围
    min_x = min(min_x, x)
    max_x = max(max_x, x)
    min_y = min(min_y, y)
    max_y = max(max_y, y)

    print(x)
    # 打印当前范围
    print(f"X范围: {min_x}-{max_x}, Y范围: {min_y}-{max_y}", end='\r')
    return True


print("开始检测鼠标移动范围(按Ctrl+C停止)...")

# 创建监听器
listener = mouse.Listener(on_move=on_move)
listener.start()

try:
    while True:
        print(f"X范围: {min_x}-{max_x}, Y范围: {min_y}-{max_y}", end='\r')
        time.sleep(1)
except KeyboardInterrupt:
    listener.stop()
    with open('mouselimit.txt', 'w') as f:
        f.writelines(f"X: {min_x}  -  {max_x} \n")
        f.writelines(f"Y: {min_y}  -  {max_y} \n")
        f.writelines(f"{max_x - min_x}x{max_y - min_y}")
    print("\n检测结束")
    print(f"最终X范围: {min_x}-{max_x}")
    print(f"最终Y范围: {min_y}-{max_y}")
    print(f"移动区域大小: {max_x - min_x}x{max_y - min_y}")
