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
    while 1:
        helpfiledir = await filemodel.set_file(dir1="/userfiles/helptxt", filetype="txt")
#        helpfiledir = await filemodel.set_file(dir1="/", filetype=None)
        if helpfiledir == None:
            hmi.tx("any", "page sys_home")             
            raise asyncio.CancelledError            
        hang =1
        hmi.tx("any", f'page app_help')   
        hmi.tx("any", f'helptxt.ch=0')             
        hmi.tx("any", f'helptxt.txt="帮助文件：{helpfiledir}\r\n\r\n"')
        try :
            while True:
                txt = readbat(helpfiledir, hang)
                if txt is None:
                    break  # 如果读取到文件末尾或行号超出范围，退出循环
                else:
                    hmi.tx("any", f'helptxt.txt+="{hang} {txt}\r\n"')
                hang += 1
                await asyncio.sleep(0.02)
            hmi.tx("any", f'helptxt.txt+="\r\n----------------------------------------------------------文件结束----------------------------------------------------------"')
        except Exception as e:
            hmi.tx("any", f'helptxt.txt+="打开出错:{e}"') 
        while True:
            key = hmi.get_key()
            if key == "appback":
                break
            await asyncio.sleep(0.2)


async def main(hmi):
    apptask = asyncio.create_task(apprun(hmi))
    hmi.set_keyhome(None)
    print("helpapp 启动")
    try:
        while True:
            if hmi.get_keyhome() == "apphome":
                print("停止helpapp")
                apptask.cancel()  # 取消 apprun 协程
                try:
                    await apptask  # 等待 apprun 协程完成
                except asyncio.CancelledError:
                    print("停止helpapp完成")
                hmi.tx("any", "page sys_home")
                break  # 退出 main 协程的循环
            await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        print("helpapp程序强行退出")
