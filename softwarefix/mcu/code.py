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
import mcuhid
import fileselector

# 初始化 HMI 和电池模块
hmi = uart_hmi.SerialDisplay()
battery_instance = battery.Battery(board.GPIO2, board.GPIO3)
hid = mcuhid.HIDController(timeout=1.0)
# 初始化 AppManager 并传递 hmi 对象
app_manager = app_manager.AppManager(hmi)

# 初始化 HMI 页面
hmi.tx("any", "page boot")
hmi.tx("bootlog", "MCU启动")
time.sleep(1)
hmi.tx("any", "page sys_home")


    
async def hmi_info_send():
    while True:
        hmi.run()
        voltage = battery_instance.get_voltage()
        soc = battery_instance.get_soc()
        charging = battery_instance.is_charging()
        
        # 向屏幕发送电池信息
        hmi.info_set("batv", f"{voltage:.1f}")  # 电池电压，保留1位小数
        hmi.info_set("batn", f"{soc:.0f}")      # 电量百分比，整数
        hmi.info_set("batc", f"{1 if charging else 0}")  # 充电状态，1表示正在充电，0表示未充电
        
        await asyncio.sleep(1)
async def key_scan():
    button = digitalio.DigitalInOut(board.GPIO10)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP  # 启用内部上拉电阻
    while True:
        if not button.value:
            print("POWER Button Pressed!")
            app_manager.stop_app()
            hmi.tx("any","page sys_poweroff")
        await asyncio.sleep(1)

async def main():
    # 创建 hmi_info_send 任务
    hmi_task = asyncio.create_task(hmi_info_send())
    key_task = asyncio.create_task(key_scan())
    
    while True:
            command = hmi.rx()
            if command:
                print(f"Received command: {command}")
                cmd = command.strip().split()  # 按空格分割命令
                print(cmd)
                if not cmd:
                    continue
                # 解码命令列表
                cmd = [part.decode('utf-8') for part in cmd]

                if cmd[0] == "app":
                    if cmd[1] == "run":
                        app_name = cmd[2]
                        await app_manager.run_app(app_name)
                    elif cmd[1] == "tx":
                        hmi.set_key(cmd[2])

                elif cmd[0] == "stop":
                    await app_manager.stop_app()
                elif cmd[0] == "list":
                    if len(cmd) > 1 and cmd[1] == "app":
                        applist = []
                        try:
                            for filename in os.listdir("/userfiles/app"):
                                if filename.endswith(".py"):
                                    file_name_without_extension = filename[:-3]
                                    applist.append(file_name_without_extension)
                            print("找到的 .py 文件名（不含后缀）列表：", applist)
                            if applist:
                                hmi.tx("any", f'b0.txt="{applist[0]}"')
                                hmi.tx("any", f'b1.txt="{applist[1]}"')
                            else:
                                hmi.tx("any", 'b0.txt="No apps found"')
                        except Exception as e:
                            print(f"Error listing apps: {e}")
                    else:
                        print("Error: Invalid list command")
                elif cmd[0] == "mcu":
                    if len(cmd) > 1 and cmd[1] == "reboot":
                        hmi.tx("any", "page boot")
                        microcontroller.reset()
                    else:
                        print("Error: Invalid mcu command")
                elif cmd[0] == "hid":
                    if cmd[1] == "jp":
                        hid.hid_key(dongzuo=cmd[2],anjian=cmd[3])  #p/r zhi  
                    elif cmd[1] == "sb":
                        if cmd[2] !="m":
                            hid.hid_mouse_key(action=cmd[2], button=cmd[3])
                            print(1)
                        else:
                            hid.hid_mouse_move( px=int(cmd[3]), py=int(cmd[4]), wheel=int(cmd[5]))
                                
                else:
                    print(f"Error: Unknown command {cmd[0]}")
            await asyncio.sleep(0.1)  # 调整间隔以适应你的应用

# 运行主函数
asyncio.run(main())