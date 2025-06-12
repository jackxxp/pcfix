import asyncio

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

    

async def main(hmi):
    try :
        hang=1
        hmi.tx("any", f'info.txt=""')
        while True:
            txt = readbat("/sysfiles/conf/about.txt", hang)
            if txt is None:
                break  # 如果读取到文件末尾或行号超出范围，退出循环
            else:
                hmi.tx("any", f'info.txt+="{txt}\r\n"')
            hang += 1
            await asyncio.sleep(0.02)
    except Exception as e:
        hmi.tx("any", f'info.txt+="打开出错:{e}"') 
