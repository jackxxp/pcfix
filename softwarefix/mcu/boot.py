import storage
import board
import digitalio
import time

# 定义按键引脚（根据你的硬件连接修改）
BUTTON_PIN = board.GPIO0  # 假设按键连接到 GPIO0

# 初始化按键引脚
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # 假设按键按下时接地

time.sleep(1)

# 检测按键是否按下（按下时为低电平）
if not button.value:
    # 如果按键按下，启用 USB 存储设备
    print("按键按下，启用 USB 存储设备")
    storage.enable_usb_drive()
else:
    # 如果按键未按下，禁用 USB 存储设备
    print("按键未按下，禁用 USB 存储设备")
    storage.disable_usb_drive()