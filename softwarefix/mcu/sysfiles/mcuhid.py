import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import time

class HIDController:
    def __init__(self, timeout=1.0):
        self.keyboard = None
        self.mouse = None
        self.consumer_control = None
        self.keyboard_layout = None
        self.initialized = False
        self.error_message = None
        self.timeout = timeout
        self._init_task = None

    async def ensure_initialized(self):
        """确保HID设备已初始化"""
        if self.initialized:
            return True
        if self._init_task is None:
            self._init_task = asyncio.create_task(self._initialize_hid())
        try:
            await asyncio.wait_for(self._init_task, timeout=self.timeout)
            return self.initialized
        except asyncio.TimeoutError:
            self.error_message = "HID initialization timed out"
            return False

    async def _initialize_hid(self):
        """异步初始化HID设备"""
        try:
            start_time = time.monotonic()  # 使用CircuitPython兼容的时间函数
            
            while True:
                try:
                    devices = usb_hid.devices
                    if devices:
                        self.keyboard = Keyboard(devices)
                        self.mouse = Mouse(devices)
                        self.consumer_control = ConsumerControl(devices)
                        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)
                        self.initialized = True
                        self.error_message = None
                        return
                except Exception as e:
                    self.error_message = f"HID init attempt failed: {str(e)}"
                
                # 检查是否超时
                elapsed = time.monotonic() - start_time
                if elapsed > self.timeout:
                    raise asyncio.TimeoutError("HID initialization timeout")
                
                # 非阻塞等待
                await asyncio.sleep(0.1)
        except Exception as e:
            self.error_message = f"HID initialization failed: {str(e)}"
            raise
        finally:
            self._init_task = None

    async def process_command(self, command: bytes):
        """处理输入的命令"""
        if not await self.ensure_initialized():
            return self.error_message
        
        try:
            parts = command.decode().split()
            if not parts:
                return "Empty command"
                
            cmd_type = parts[0]
            
            if cmd_type == "hid":
                if len(parts) < 2:
                    return "Incomplete command"
                
                sub_cmd = parts[1]
                
                # 鼠标移动命令: hid sb m x y wheel
                if sub_cmd == "sb" and len(parts) >= 5 and parts[2] == "m":
                    try:
                        x = int(parts[3])
                        y = int(parts[4])
                        wheel = int(parts[5]) if len(parts) > 5 else 0
                        return await self._move_mouse(x, y, wheel)
                    except ValueError:
                        return "Invalid mouse move parameters"
                
                # 鼠标按键命令: hid sb k [p/r] [l/m/r]
                elif sub_cmd == "sb" and len(parts) >= 5 and parts[2] == "k":
                    action = parts[3]
                    button = parts[4]
                    return await self._mouse_button(action, button)
                
                # 键盘按键命令: hid jp [p/r] key
                elif sub_cmd == "jp" and len(parts) >= 4:
                    action = parts[2]
                    key = parts[3]
                    return await self._key_action(action, key)
                
                else:
                    return f"Unknown sub-command: {sub_cmd}"
            else:
                return f"Unknown command type: {cmd_type}"
        except Exception as e:
            return f"Command processing error: {str(e)}"

    async def _move_mouse(self, x, y, wheel=0):
        """移动鼠标"""
        try:
            self.mouse.move(x=x, y=y, wheel=wheel)
            return f"Mouse moved: x={x}, y={y}, wheel={wheel}"
        except Exception as e:
            return f"Mouse move failed: {str(e)}"

    async def _mouse_button(self, action, button):
        """鼠标按键动作"""
        button_map = {
            "l": Mouse.LEFT_BUTTON,
            "m": Mouse.MIDDLE_BUTTON,
            "r": Mouse.RIGHT_BUTTON
        }
        
        if button not in button_map:
            return f"Invalid mouse button: {button}"
            
        try:
            if action == "p":
                self.mouse.press(button_map[button])
                return f"Mouse {button} pressed"
            elif action == "r":
                self.mouse.release(button_map[button])
                return f"Mouse {button} released"
            else:
                return f"Invalid mouse action: {action}"
        except Exception as e:
            return f"Mouse button action failed: {str(e)}"

    async def _key_action(self, action, key):
        """键盘按键动作"""
        try:
            keycode = getattr(Keycode, key.upper())
            if action == "p":
                self.keyboard.press(keycode)
                return f"Key {key} pressed"
            elif action == "r":
                self.keyboard.release(keycode)
                return f"Key {key} released"
            else:
                return f"Invalid key action: {action}"
        except AttributeError:
            return f"Invalid key: {key}"
        except Exception as e:
            return f"Key action failed: {str(e)}"