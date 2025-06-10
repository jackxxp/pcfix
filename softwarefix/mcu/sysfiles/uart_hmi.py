import board
import busio
import time

class SerialDisplay:
    def __init__(self):
        """
        初始化 SerialDisplay 类
        - 配置 UART 串口通信
        - 初始化设备状态信息
        """
        # 初始化 UART 串口，配置波特率、数据位、奇偶校验、停止位以及 TX 和 RX 引脚
        self.uart = busio.UART(board.GPIO40, board.GPIO39, baudrate=921600, bits=8, parity=None, stop=1)
        # 初始化设备状态信息
        self.info_bat_v = "0.0"  # 电池电压
        self.info_bat_n = "0"    # 电池电量百分比
        self.info_batc = "0"     # 电池充电状态
        self.info_usb = "0"      # USB 连接状态
        self.info_wlan = "0"     # WLAN 连接状态
        # 初始化缓冲区，用于存储未处理的串口数据
        self.buffer = b""
        # 初始化按键状态变量
        self.key = None
        self.keyhome = None

    def run(self):
        """
        更新串口屏显示信息
        - 将设备状态信息发送到串口屏
        """
        # 定义要发送的命令列表
        commands = [
            f'sys_core.bat_v.txt="{self.info_bat_v}"',  # 设置电池电压显示
            f'sys_core.bat_n.txt="{self.info_bat_n}"',   # 设置电池电量百分比显示
            f'sys_core.info_batc.txt="{self.info_batc}"',# 设置电池充电状态显示
            f'sys_core.info_usb.txt="{self.info_usb}"',  # 设置 USB 连接状态显示
            f'sys_core.info_wlan.txt="{self.info_wlan}"',# 设置 WLAN 连接状态显示
            'sys_core.info_mcu.txt="1"'                  # 设置 MCU 状态显示
        ]
        # 遍历命令列表，逐条发送命令
        for command in commands:
            # 将命令转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(command.encode() + b'\xff\xff\xff')
            # 短暂延时，确保命令发送完成
            time.sleep(0.1)

    def info_set(self, info, num):
        """
        设置设备状态信息
        :param info: 信息类型（如 "batv" 表示电池电压）
        :param num: 信息值
        """
        # 根据信息类型，更新对应的设备状态
        if info == "batv":
            self.info_bat_v = str(num)
        elif info == "batn":
            self.info_bat_n = str(num)
        elif info == "batc":
            self.info_batc = str(num)
        elif info == "usb":
            self.info_usb = str(num)
        elif info == "wlan":
            self.info_wlan = str(num)

    def tx(self, place, info, addinfo=None):
        """
        发送自定义信息到串口屏
        :param place: 信息发送位置（目前支持 "any" 和 "bootlog"）
        :param info: 要发送的信息
        """
        # 如果 place 为 "any"，则直接发送信息
        if place == "any":
            # 将信息转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(info.encode() + b'\xff' * 3)
        # 如果 place 为 "bootlog"，则按照指定格式发送日志信息
        elif place == "bootlog":
            # 构造 bootlog 格式：boot.bootlog.txt+="\r\n日志内容"
            bootlog_command = f'boot.bootlog.txt+="\r\n{info}"'
            # 将命令转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(bootlog_command.encode() + b'\xff' * 3)
        elif place == "app_title":
            bootlog_command = f't_title.txt="{info}"'
            # 将命令转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(bootlog_command.encode() + b'\xff' * 3)
        elif place == "app_main":
            bootlog_command = f'display.txt="{info}"'
            # 将命令转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(bootlog_command.encode() + b'\xff' * 3)
        elif place == "app_main+":
            bootlog_command = f'display.txt+="\r\n{info}"'
            # 将命令转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(bootlog_command.encode() + b'\xff' * 3)
        elif place == "app_b":
            bootlog_command = f'b{addinfo}.txt="{info}"'
            # 将命令转换为字节类型，并添加结束符 \xff\xff\xff
            self.uart.write(bootlog_command.encode() + b'\xff' * 3)

    def rx(self):
        """
        接收串口屏发来的命令
        - 每次只提取一条以 'cmd' 开头、以 'end' 结尾的命令
        :return: 提取的命令（字节类型），如果没有完整命令则返回 None
        """
        # 如果有可用的串口数据
        if self.uart.in_waiting > 0:
            # 读取所有可用的串口数据，并追加到缓冲区
            self.buffer += self.uart.read(self.uart.in_waiting)

        # 定义命令的起始和结束标记
        start_marker = b"cmd"
        end_marker = b"end"
        # 查找起始标记和结束标记的位置
        start = self.buffer.find(start_marker)
        end = self.buffer.find(end_marker)

        # 如果找到完整的命令
        if start != -1 and end != -1 and end > start:
            # 提取命令内容（从起始标记后到结束标记前）
            command = self.buffer[start + len(start_marker):end]
            # 移除缓冲区中已处理的命令部分（包括起始标记和结束标记）
            self.buffer = self.buffer[end + len(end_marker):]
            # 返回提取的命令
            return command
        # 如果没有找到完整的命令，返回 None
        return None

    def set_key(self, key1):
        self.key = key1

    def get_key(self):
        key2 = self.key
        self.key = None  # 清除按键变量
        return key2
    def set_keyhome(self, key1):
        self.keyhome = key1

    def get_keyhome(self):
        key2 = self.keyhome
        self.keyhome = None  # 清除按键变量
        return key2