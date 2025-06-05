
async def main(hmi):
    hmi.tx("any", "page sys_app_run")
    hmi.tx("app_title", "test111")
    hmi.tx("app_main+", "要发送的文字")
