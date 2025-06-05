import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

class HIDModule:
    def __init__(self):
        self.keyboard = None
        self.mouse = None
        self.consumer_control = None
        self.keyboard_layout = None
        self.initialized = False
        self.error_message = None
        self.timeout = 5  # 设置超时时间为5秒

        try:
            self.keyboard = Keyboard(usb_hid.devices)
            self.mouse = Mouse(usb_hid.devices)
            self.consumer_control = ConsumerControl(usb_hid.devices)
            self.keyboard_layout = KeyboardLayoutUS(self.keyboard)
            self.initialized = True
        except Exception as e:
            self.error_message = f"Initialization failed: {e}"

    def hid_mouse_move(self, px, py, wheel=0):
        """模拟鼠标移动和滚轮操作
        px: 水平方向移动的像素值（正数向右，负数向左）
        py: 垂直方向移动的像素值（正数向下，负数向上）
        wheel: 滚轮滚动值（正数向上，负数向下）
        """
        if not self.initialized:
            return self.error_message

        try:
            self.mouse.move(x=px, y=py, wheel=wheel)
            return "Mouse moved and scrolled successfully"
        except Exception as e:
            return f"Error moving or scrolling mouse: {e}"

    def hid_mouse_key(self, action, button):
        """模拟鼠标按键操作
        action: 'press' 或 'release'
        button: 'left', 'middle', 'right'
        """
        if not self.initialized:
            return self.error_message

        try:
            if button == "left":
                button_code = Mouse.LEFT_BUTTON
            elif button == "middle":
                button_code = Mouse.MIDDLE_BUTTON
            elif button == "right":
                button_code = Mouse.RIGHT_BUTTON
            else:
                return "Invalid button"

            if action == "press":
                self.mouse.press(button_code)
            elif action == "release":
                self.mouse.release(button_code)
            else:
                return "Invalid action"

            return "Mouse button action performed successfully"
        except Exception as e:
            return f"Error performing mouse button action: {e}"

    def hid_key(self, dongzuo, anjian):
        """模拟键盘操作，dongzuo是按下还是释放，anjian是按键"""
        if not self.initialized:
            return self.error_message

        try:
            if dongzuo == "press":
                self.keyboard.press(getattr(Keycode, anjian.upper()))
            elif dongzuo == "release":
                self.keyboard.release(getattr(Keycode, anjian.upper()))
            else:
                return "Invalid action"
            return "Key action performed successfully"
        except Exception as e:
            return f"Error performing key action: {e}"

    def hid_input(self, str, huanghang):
        """输入字符串，huanghang是是否在末尾加上回车"""
        if not self.initialized:
            return self.error_message

        try:
            self.keyboard_layout.write(str)
            if huanghang:
                self.keyboard.send(Keycode.ENTER)
            return "String input successful"
        except Exception as e:
            return f"Error inputting string: {e}"

    def hid_zhj(self, zhuhejian):
        """模拟组合键操作，zhuhejian是组合键"""
        if not self.initialized:
            return self.error_message

        try:
            keys = zhuhejian.split("+")
            keycodes = [getattr(Keycode, key.upper()) for key in keys]
            self.keyboard.send(*keycodes)
            return "Combination key pressed successfully"
        except Exception as e:
            return f"Error pressing combination key: {e}"

    def hid_any(self, zhi):
        """模拟自定义键值操作，zhi是键值"""
        if not self.initialized:
            return self.error_message

        try:
            self.keyboard.send(int(zhi, 16))  # 将十六进制字符串转换为整数
            return "Custom key value sent successfully"
        except Exception as e:
            return f"Error sending custom key value: {e}"

    def check_hid(self):
        """检查HID设备是否连接"""
        if not self.initialized:
            return self.error_message

        try:
            # 检查设备是否仍然连接
            if not self.keyboard or not self.mouse or not self.consumer_control:
                return "HID devices disconnected"
            return "HID devices connected"
        except Exception as e:
            return f"Error checking HID devices: {e}"
        

