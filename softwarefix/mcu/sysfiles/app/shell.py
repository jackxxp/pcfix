import asyncio
async def main(hmi):
    hmi.tx("any", "page sys_shell")