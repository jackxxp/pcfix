import sys
sys.path.append('/sysfiles')
import asyncio
import battery

async def main():
    while True:
        voltage = battery.battery.get_voltage()
        soc = battery.battery.get_soc()
        charging = battery.battery.is_charging()

        print(f"Voltage: {voltage:.2f}V")
        print(f"SOC: {soc:.2f}%")
        print(f"Charging: {'Yes' if charging else 'No'}")

        await asyncio.sleep(1)

# 运行主函数
asyncio.run(main())