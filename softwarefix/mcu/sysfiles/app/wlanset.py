import asyncio
async def main(hmi):
    await asyncio.sleep(0.1)
    hmi.tx("any", 'wlan_info.txt+="正在获取信息\r\n"')

