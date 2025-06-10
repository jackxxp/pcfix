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
                return "Line number out of range"  # 行号超出范围
    except FileNotFoundError:
        return "File not found"  # 文件未找到
    except Exception as e:
        return f"Error reading file: {e}"  # 其他错误

async def main(hmi):
    batdir = None
    # 发送 HMI 命令
    hmi.tx("any", "page app_sysfix")
    filemodel = fileselector.hmi_fileset(hmi)
    while True:
        await asyncio.sleep(0.2)  # 调整间隔以适应你的应用
        key = hmi.get_key()
        if key == "setfile":
            batdir = await filemodel.set_file(dir1="/userfiles/autoprogram/system", filetype="aof")
            hmi.tx("any", "page app_sysfix")
            hmi.tx("any", f'dir.txt="{batdir}"')
            hmi.tx("any", f'jbsm.txt="{readbat(batdir, 1) }"')
            hmi.tx("any", f'czsm.txt="{readbat(batdir, 2) }"')
