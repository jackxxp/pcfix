import asyncio
import os


appname="文件管理器"  
appexit=0
    
def get_parent_directory(path):
    if path == "/":
        return path
    parent_path = path.rsplit('/', 1)[0] if '/' in path else path
    return parent_path

def join_paths(base_path, sub_path):
    if base_path.endswith('/'):
        return base_path + sub_path
    else:
        return base_path + '/' + sub_path

def list_files(start_path, file_type=None):
    filelist = []
    try:
        entries = os.listdir(start_path)
    except OSError as e:
        print(f"Error accessing directory {start_path}: {e}")
        return filelist  # 如果无法访问目录，返回空列表

    dirs = []
    files = []
    for entry in entries:
        full_path = f"{start_path}/{entry}"  # 使用字符串拼接构建路径
        try:
            if os.stat(full_path)[0] & 0x4000:  # 如果是目录
                dirs.append(f"dir-{entry}")
            else:
                if file_type is None or entry.endswith(file_type):
                    files.append(entry)
        except OSError as e:
            print(f"Error accessing file {full_path}: {e}")
            continue  # 如果无法访问文件，跳过
    filelist.extend(dirs)
    filelist.extend(files)
    return filelist

async def apprun(hmi,dir1="/userfiles", filetype=None, rootdir="/"):
    global appexit
    try:
        # 使用 hmi 来访问 HMI 对象
        hmi.tx("any", "page app_file")
        page = 1
        pagemax = 1
        dirnow = dir1
        returnfile=None


        while 1:
            joinrun=0
            xuanzhe = None
            hmi.tx("any", f'dir.txt="{dirnow}"')
            hmi.tx("any", f'type.txt="{filetype}"')        
            filelist = list_files(dirnow, filetype)
            print(filelist)
            pagemax = int((len(filelist) / 8) + 1)
            hmi.tx("any", f'page.txt="{str(page)}/{str(pagemax)}"')
            for i in range(8):
                index = i + (page - 1) * 8
                if index < len(filelist):
                    hmi.tx("any", f'b{i}.txt="{filelist[index]}"')
                else:
                    hmi.tx("any", f'b{i}.txt=""')  # 如果没有更多文件，显示为空

            while True:
                key = hmi.get_key() 
                if key == "+":
                    if page < pagemax:
                        page += 1
                        break
                elif key == "-":
                    if page > 1:
                        page -= 1
                        break
                elif key == "backdir":
                    if dirnow!=rootdir:
                        dirnow = get_parent_directory(dirnow)
                        page = 1 
                        break
                elif key == "appback":
                    appexit = 1
                    break
                elif key == "setdir":
                    xuanzhe = "dir"
                    print(f"选择目录：{dirnow}")
                    joinrun =1
                    print(xuanzhe,joinrun)
                    break
                elif key == "newdir":
                    pass                
                elif key is not None and key.isdigit() and 0 <= int(key) <= 7:  # 按钮 0-7
                    index = int(key) + (page - 1) * 8
                    if index < len(filelist):
                        selected_item = filelist[index]
                        if selected_item.startswith("dir-"):  # 如果是目录
                            dirnow = join_paths(dirnow, selected_item[4:])  # 进入子目录
                            page = 1
                        elif selected_item:  # 如果是文件
                            print(f"Selected file: {selected_item}")
                            returnfile=f"{dirnow}/{selected_item}"
                            joinrun=1
                            xuanzhe="file"
                            break
                        else:  # 如果是空
                            pass
                    break
                elif key == "appback":
                    print("文件选择器程序退出")
                    return None       
#                print("文件选择器程序运行")        
                await asyncio.sleep(0.2)  # 稍微延迟，避免过快的循环
            if joinrun==1:
                print(1)
                hmi.tx("any", "page app_file2")
                if xuanzhe== "file":
                    hmi.tx("any", f'info.txt="已选择文件 {returnfile}"')    
                    hmi.tx("any", f'b0.txt="返回"')              
                    while 1:
                        key = hmi.get_key() 
                        if key == "b0" or key== "appback":
                            hmi.tx("any", "page app_file")                        
                            break
                        await asyncio.sleep(0.2)
                elif xuanzhe == "dir":
                    hmi.tx("any", f'info.txt="已选择目录 {dirnow}"')    
                    hmi.tx("any", f'b0.txt="返回"')              
                    while 1:
                        key = hmi.get_key() 
                        if key == "b0" or key== "appback":
                            hmi.tx("any", "page app_file")                        
                            break
                        await asyncio.sleep(0.2)
            await asyncio.sleep(0.2)
        

        await asyncio.sleep(0.1)  # 稍微延迟，避免过快的循环
    except Exception as e:
        print(f"{appname}运行出错：{e}")




async def main(hmi):
    global appexit
    apptask = asyncio.create_task(apprun(hmi))
    hmi.set_keyhome(None)
    print(f"{appname} 启动")
    try:
        while True:
            if hmi.get_keyhome() == "apphome" or appexit==1:
                appexit=0
                print(f"停止{appname}")
                apptask.cancel()  # 取消 apprun 协程
                try:
                    await apptask  # 等待 apprun 协程完成
                except asyncio.CancelledError:
                    print(f"停止{appname}完成")
                hmi.tx("any", "page sys_home")
                break  # 退出 main 协程的循环
            await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        print(f"{appname}程序退出")
