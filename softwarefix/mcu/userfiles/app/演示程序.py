import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import board

# 初始化键盘
kbd = Keyboard(usb_hid.devices)

async def main(hmi):
    # 发送 HMI 命令
    hmi.tx("any", "page sys_app_run")
    hmi.tx("app_title", "维护—系统操作")
    hmi.tx("app_main", "正在加载系统维修程序...")
    await asyncio.sleep(1)
    hmi.tx("app_main", "系统重装 机型——测试电脑")

    # 进入启动项菜单
    hmi.tx("app_main+", "进入启动项菜单")
    for _ in range(40):  # 模拟多次按下 F12
        kbd.send(Keycode.F12)
        await asyncio.sleep(0.1)  # 每次按键间隔 0.1 秒

    await asyncio.sleep(1)
    hmi.tx("app_main+", "选择")
    kbd.send(Keycode.ENTER)
    await asyncio.sleep(1)

    # 启动 PE
    hmi.tx("app_main+", "启动PE0")
    await asyncio.sleep(5)
    hmi.tx("app_main+", "启动PE5")
    await asyncio.sleep(5)
    hmi.tx("app_main+", "启动PE10")
    await asyncio.sleep(5)
    hmi.tx("app_main+", "启动PE15")
    await asyncio.sleep(5)
    hmi.tx("app_main+", "启动PE20")
    await asyncio.sleep(5)
    hmi.tx("app_main+", "启动PE25")
    await asyncio.sleep(5)
    hmi.tx("app_main+", "启动PE30")
    kbd.send(Keycode.ALT, Keycode.ENTER)
    await asyncio.sleep(1)

    # CMD 启动
    hmi.tx("app_main", "CMD启动")
    await asyncio.sleep(3)

    # 设置盘符
    hmi.tx("app_main+", "设置盘符")
    simulate_keyboard_input("PANFU.cmd")
    await asyncio.sleep(1)

    # 打开分区工具
    hmi.tx("app_main+", "打开分区工具")
    simulate_keyboard_input("diskpart")
    await asyncio.sleep(3)

    # 列出所有磁盘
    hmi.tx("app_main+", "列出所有磁盘")
    simulate_keyboard_input("list disk")
    await asyncio.sleep(1)

    # 选择目标系统盘
    hmi.tx("app_main+", "选择目标系统盘")
    simulate_keyboard_input("select disk 0")
    await asyncio.sleep(1)

    # 擦除硬盘
    hmi.tx("app_main+", "擦除硬盘")
    simulate_keyboard_input("clean")
    await asyncio.sleep(5)

    # 建立 GPT 分区表
    hmi.tx("app_main+", "建立 GPT 分区表")
    simulate_keyboard_input("convert gpt")
    await asyncio.sleep(3)

    # 建立 ESP 引导区
    hmi.tx("app_main+", "建立 ESP 引导区")
    simulate_keyboard_input("create partition efi size=100")
    await asyncio.sleep(3)
    simulate_keyboard_input("format quick fs=fat32")
    await asyncio.sleep(3)
    simulate_keyboard_input("assign letter=s")
    await asyncio.sleep(2)

    # 建立 MSR 系统保留区
    hmi.tx("app_main+", "建立 MSR 系统保留区")
    simulate_keyboard_input("create partition msr size=16")
    await asyncio.sleep(3)

    # 建立系统分区
    hmi.tx("app_main+", "建立系统分区")
    simulate_keyboard_input("create partition primary")
    await asyncio.sleep(3)
    simulate_keyboard_input("format quick fs=ntfs")
    await asyncio.sleep(5)
    simulate_keyboard_input("assign letter=c")
    await asyncio.sleep(2)

    # 退出分区工具
    hmi.tx("app_main+", "退出分区工具")
    simulate_keyboard_input("exit")
    await asyncio.sleep(1)

    # 从 U 盘选择 WIM 映像还原至 C 盘
    hmi.tx("app_main+", "从 U 盘选择 WIM 映像还原至 C 盘")
    simulate_keyboard_input("dism /apply-image /imagefile:U:\\Win10lite.wim /index:1 /applydir:C:\\")
    await asyncio.sleep(420)

    # 在 S 盘引导区为 C 盘系统区添加 UEFI 引导
    hmi.tx("app_main+", "在 S 盘引导区为 C 盘系统区添加 UEFI 引导")
    simulate_keyboard_input("bcdboot C:\\Windows /s S: /f UEFI")
    await asyncio.sleep(5)

    # 重新启动系统
    hmi.tx("app_main+", "重新启动系统")
    simulate_keyboard_input("shutdown -r -t 0")
    await asyncio.sleep(1)

def simulate_keyboard_input(command):
    for char in command:
        if char.isalpha():
            kbd.send(getattr(Keycode, char.upper()))
        elif char.isdigit():
            kbd.send(getattr(Keycode, f"ZERO" if char == "0" else f"ONE" if char == "1" else f"TWO" if char == "2" else f"THREE" if char == "3" else f"FOUR" if char == "4" else f"FIVE" if char == "5" else f"SIX" if char == "6" else f"SEVEN" if char == "7" else f"EIGHT" if char == "8" else f"NINE"))
        elif char == " ":
            kbd.send(Keycode.SPACE)
        elif char == ".":
            kbd.send(Keycode.PERIOD)
        elif char == "\\":
            kbd.send(Keycode.BACKSLASH)
        elif char == "/":
            kbd.send(Keycode.FORWARD_SLASH)
        elif char == ":":
            kbd.send(Keycode.SHIFT, Keycode.SEMICOLON)  # 冒号是 Shift + ;
        elif char == "-":
            kbd.send(Keycode.MINUS)
        elif char == "_":
            kbd.send(Keycode.SHIFT, Keycode.MINUS)  # 下划线是 Shift + -
        elif char == "=":
            kbd.send(Keycode.EQUALS)
        elif char == "[":
            kbd.send(Keycode.LEFT_BRACKET)
        elif char == "]":
            kbd.send(Keycode.RIGHT_BRACKET)
        elif char == "{":
            kbd.send(Keycode.SHIFT, Keycode.LEFT_BRACKET)  # 左大括号是 Shift + [
        elif char == "}":
            kbd.send(Keycode.SHIFT, Keycode.RIGHT_BRACKET)  # 右大括号是 Shift + ]
        elif char == ";":
            kbd.send(Keycode.SEMICOLON)
        elif char == "'":
            kbd.send(Keycode.QUOTE)
        elif char == ",":
            kbd.send(Keycode.COMMA)
        elif char == "<":
            kbd.send(Keycode.SHIFT, Keycode.COMMA)  # 小于号是 Shift + ,
        elif char == ">":
            kbd.send(Keycode.SHIFT, Keycode.PERIOD)  # 大于号是 Shift + .
        elif char == "?":
            kbd.send(Keycode.SHIFT, Keycode.FORWARD_SLASH)  # 问号是 Shift + /
        elif char == "!":
            kbd.send(Keycode.SHIFT, Keycode.ONE)  # 感叹号是 Shift + 1
        elif char == "@":
            kbd.send(Keycode.SHIFT, Keycode.TWO)  # @ 是 Shift + 2
        elif char == "#":
            kbd.send(Keycode.SHIFT, Keycode.THREE)  # # 是 Shift + 3
        elif char == "$":
            kbd.send(Keycode.SHIFT, Keycode.FOUR)  # $ 是 Shift + 4
        elif char == "%":
            kbd.send(Keycode.SHIFT, Keycode.FIVE)  # % 是 Shift + 5
        elif char == "^":
            kbd.send(Keycode.SHIFT, Keycode.SIX)  # ^ 是 Shift + 6
        elif char == "&":
            kbd.send(Keycode.SHIFT, Keycode.SEVEN)  # & 是 Shift + 7
        elif char == "*":
            kbd.send(Keycode.SHIFT, Keycode.EIGHT)  # * 是 Shift + 8
        elif char == "(":
            kbd.send(Keycode.SHIFT, Keycode.NINE)  # ( 是 Shift + 9
        elif char == ")":
            kbd.send(Keycode.SHIFT, Keycode.ZERO)  # ) 是 Shift + 0
        elif char == "+":
            kbd.send(Keycode.SHIFT, Keycode.EQUALS)  # + 是 Shift + =
        elif char == "|":
            kbd.send(Keycode.SHIFT, Keycode.BACKSLASH)  # | 是 Shift + \
        elif char == "~":
            kbd.send(Keycode.SHIFT, Keycode.GRAVE_ACCENT)  # ~ 是 Shift + `
        elif char == "`":
            kbd.send(Keycode.GRAVE_ACCENT)
        elif char == '"':
            kbd.send(Keycode.SHIFT, Keycode.QUOTE)  # 双引号是 Shift + '
        else:
            print(f"Unknown character: {char}")
    kbd.send(Keycode.ENTER)