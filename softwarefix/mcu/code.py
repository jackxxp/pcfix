import asyncio
import sys
import board
import time
import os
import digitalio
import microcontroller
sys.path.append('/sysfiles')
import uart_hmi
import battery
import app_manager
from mcuhid import HIDController

# 初始化各个模块
async def initialize_system():
    # 初始化HMI串口显示
    hmi = uart_hmi.SerialDisplay()
    
    # 初始化电池监测
    battery_instance = battery.Battery(board.GPIO2, board.GPIO3)
    
    # 初始化App管理器
    app_mgr = app_manager.AppManager(hmi)
    
    # 显示启动页面
    hmi.tx("any", "page boot")
    hmi.tx("bootlog", "MCU启动中...")
    
    # 初始化HID控制器
    hmi.tx("bootlog", "初始化HID设备")
    hid = HIDController(timeout=1.0)
    
    # 切换到主页面
    hmi.tx("any", "page sys_home")
    
    return hmi, battery_instance, app_mgr, hid

# 电池信息发送任务
async def battery_info_task(hmi, battery_instance):
    while True:
        try:
            voltage = battery_instance.get_voltage()
            soc = battery_instance.get_soc()
            charging = battery_instance.is_charging()
            
            # 更新HMI显示
            hmi.info_set("batv", f"{voltage:.1f}")
            hmi.info_set("batn", f"{soc:.0f}")
            hmi.info_set("batc", "1" if charging else "0")
            
        except Exception as e:
            print(f"电池信息更新错误: {e}")
        
        await asyncio.sleep(1)

# 按键扫描任务
async def key_scan_task(hmi, app_mgr):
    button = digitalio.DigitalInOut(board.GPIO10)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    
    last_state = button.value
    debounce_time = 0
    
    while True:
        current_state = button.value
        now = time.monotonic()
        
        # 按键状态变化且消抖时间已过
        if current_state != last_state and (now - debounce_time) > 0.05:
            last_state = current_state
            debounce_time = now
            
            # 按键按下(低电平)
            if not current_state:
                print("电源按键按下")
                await app_mgr.stop_app()
                hmi.tx("any", "page sys_poweroff")
                
        await asyncio.sleep(0.01)

# 命令处理函数
async def handle_hid_command(hid, command):
    try:
        # 确保是字节类型
        if isinstance(command, str):
            command = command.encode()
            
        result = await hid.process_command(command)
        print(f"HID命令结果: {result}")
        return result
    except Exception as e:
        print(f"命令处理异常: {e}")
        return None

# 主消息循环
async def main_loop(hmi, hid):
    while True:
        # 检查HMI接收
        command = hmi.rx()
        if command:
            print(f"收到命令: {command}")
            
            # 如果是HID命令
            if command.startswith(b"hid "):
                await handle_hid_command(hid, command)
            # 其他系统命令可以在这里添加...
            
        await asyncio.sleep(0.05)

# 主函数
async def main():
    try:
        # 初始化系统
        hmi, battery_instance, app_mgr, hid = await initialize_system()
        
        # 创建后台任务
        battery_task = asyncio.create_task(battery_info_task(hmi, battery_instance))
        key_task = asyncio.create_task(key_scan_task(hmi, app_mgr))
        
        # 运行主循环
        await main_loop(hmi, hid)
        
    except Exception as e:
        print(f"系统错误: {e}")
        microcontroller.reset()

# 启动程序
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"致命错误: {e}")
        microcontroller.reset()