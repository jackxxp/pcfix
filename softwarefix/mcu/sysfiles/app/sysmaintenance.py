import asyncio
import sys
sys.path.append('/sysfiles')
import fileselector

def readbat(file_path, line_number):
    """
    读取指定文件的指定行内容。
    :param file_path: 文件路径
    :param line_number: 要读取的行号（从1开始）
    :return: 指定行的内容
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if 1 <= line_number <= len(lines):
                return lines[line_number - 1].strip()  # 返回指定行的内容
            else:
                return None  # 如果行号超出范围，返回 None
    except FileNotFoundError:
        return "File not found"  # 文件未找到
    except Exception as e:
        return f"Error reading file: {e}"  # 其他错误

    
    

async def apprun(hmi):

    filemodel = fileselector.hmi_fileset(hmi)

    while True:
        batdir = None
        hmi.tx("any", "page app_sysfix")
        hmi.tx("any", f'dir.txt=""')
        hmi.tx("any", f'jbsm.txt="脚本说明\r\n"')
        hmi.tx("any", f'czsm.txt="操作说明\r\n"')
        chaozhuo = 21
        while True:
            key = hmi.get_key()
            if key == "setfile":
                batdir = await filemodel.set_file(dir1="/userfiles/autoprogram/system", filetype="aofs")
                hmi.tx("any", "page app_sysfix")
                hmi.tx("any", f'dir.txt="{batdir}"')
                hmi.tx("any", f'jbsm.txt="脚本说明\r\n"')
                if batdir != None:
                    for i in range(11):
                        line_content = readbat(batdir, i + 1)
                        if line_content is None:
                            hmi.tx("any", f'jbsm.txt+="Line number out of range\r\n"')
                        else:
                            hmi.tx("any", f'jbsm.txt+="{line_content}\r\n"')
                    hmi.tx("any", f'czsm.txt="操作说明\r\n"')
                    line_content = readbat(batdir, 13)
                    if line_content is None:
                        hmi.tx("any", f'czsm.txt+="Line number out of range"')
                    else:
                        hmi.tx("any", f'czsm.txt+="{line_content}"')
            elif key == "start":
                break
            elif key == "appback":
                print("sysmaintenance程序退出")
                hmi.tx("any", "page sys_home")             
                raise asyncio.CancelledError             
            await asyncio.sleep(0.2)
        hmi.tx("any", "page app_sysfix2")
        hmi.tx("any", f'info.txt="运行脚本：{batdir}\r\n"')
        hmi.tx("any", f'ing.txt=""')
        hmi.tx("any", f'jd.val=0')
        for i2 in range(7):
            hmi.tx("any", f'b{i2}.txt=""')
        try:
            while True:
                cz = readbat(batdir, chaozhuo)
                if cz is None:
                    break  # 如果读取到文件末尾或行号超出范围，退出循环
                else:
                    czcmd = cz.strip().split()
                    print(czcmd)
                    if czcmd[0]=="hmi":
                        if czcmd[1]=="info":
                            hmi.tx("any", f'info.txt+="{czcmd[2]}\r\n"')
                            hmi.tx("any", f'info.val_y=maxval_y')                            
                        if czcmd[1]=="ing":
                            hmi.tx("any", f'ing.txt="{czcmd[2]}"')
                        if czcmd[1]=="jd":
                            hmi.tx("any", f'jd.val={czcmd[2]}')
                        if czcmd[1]=="key":
                            hmi.tx("any", f'b{czcmd[2]}.txt="{czcmd[3]}"')
                    if czcmd[0]=="sleep":
                        await asyncio.sleep(int(czcmd[1]))

                chaozhuo += 1
            hmi.tx("any", f'info.txt+="执行完成\n\r"')
            hmi.tx("any", f'info.val_y=maxval_y')
            await asyncio.sleep(0.2)
        except Exception as e:
            hmi.tx("any", f'info.txt+="执行出错 在{chaozhuo}行:{e}"')
            hmi.tx("any", f'info.val_y=maxval_y')
        while True:
            hmi.tx("any", f'b0.txt="返回"')
            key = hmi.get_key()
            if key == "b0" or key == "appback":
                break
            await asyncio.sleep(0.2)

        await asyncio.sleep(0.2)

async def main(hmi):
    apptask = asyncio.create_task(apprun(hmi))
    hmi.set_keyhome(None)
    print("apprun 启动")
    try:
        while True:
            if hmi.get_keyhome() == "apphome":
                print("停止sysmaintenance---")
                apptask.cancel()  # 取消 apprun 协程
                try:
                    await apptask  # 等待 apprun 协程完成
                except asyncio.CancelledError:
                    print("停止sysmaintenance完成")
                hmi.tx("any", "page sys_home")
                break  # 退出 main 协程的循环
            await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        print("sysmaintenance程序强行退出")
