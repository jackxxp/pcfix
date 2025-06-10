import os
import asyncio

class hmi_fileset:
    def __init__(self, hmi):
        self.hmi = hmi  # 存储 HMI 对象
        print("打开文件选择器")

    @staticmethod
    def get_parent_directory(path):
        """
        返回上一级目录路径。
        :param path: 当前目录路径
        :return: 上一级目录路径
        """
        # 如果当前路径是根目录，则返回当前路径
        if path == "/":
            return path
        # 去掉路径的最后一部分
        parent_path = path.rsplit('/', 1)[0] if '/' in path else path
        return parent_path

    @staticmethod
    def join_paths(base_path, sub_path):
        """
        手动实现 os.path.join 的功能。
        :param base_path: 基础路径
        :param sub_path: 子路径
        :return: 拼接后的路径
        """
        if base_path.endswith('/'):
            return base_path + sub_path
        else:
            return base_path + '/' + sub_path

    def list_files(self, start_path, file_type=None):
        """
        列出指定路径下的所有文件和文件夹，根据文件类型进行筛选。
        :param start_path: 起始路径
        :param file_type: 文件类型（扩展名），如果为空则显示所有文件和文件夹
        :return: 文件和文件夹的路径列表
        """
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

        # 先添加文件夹，再添加文件
        filelist.extend(dirs)
        filelist.extend(files)

        return filelist
    
    async def set_file(self, dir1="/userfiles", filetype=None):
        # 使用 self.hmi 来访问 HMI 对象
        self.hmi.tx("any", "page sys_app_files")
        page = 1
        pagemax = 1
        dirnow = dir1
        noexit=1
        returnfile=None

        while noexit:
            self.hmi.tx("any", f'dir.txt="{dirnow}"')
            self.hmi.tx("any", f'type.txt="{filetype}"')        
            filelist = self.list_files(dirnow, filetype)
            print(filelist)
            pagemax = int((len(filelist) / 8) + 1)
            self.hmi.tx("any", f'page.txt="{str(page)}/{str(pagemax)}"')
            for i in range(8):
                index = i + (page - 1) * 8
                if index < len(filelist):
                    self.hmi.tx("any", f'b{i}.txt="{filelist[index]}"')
                else:
                    self.hmi.tx("any", f'b{i}.txt=""')  # 如果没有更多文件，显示为空

            while True:
                key = self.hmi.get_key() 
                if key == "+":
                    if page < pagemax:
                        page += 1
                        break
                elif key == "-":
                    if page > 1:
                        page -= 1
                        break
                elif key == "backdir":
                    dirnow = self.get_parent_directory(dirnow)
                    page = 1 
                    break
                elif key is not None and key.isdigit() and 0 <= int(key) <= 7:  # 按钮 0-7
                    index = int(key) + (page - 1) * 8
                    if index < len(filelist):
                        selected_item = filelist[index]
                        if selected_item.startswith("dir-"):  # 如果是目录
                            dirnow = self.join_paths(dirnow, selected_item[4:])  # 进入子目录
                            page = 1
                        elif selected_item:  # 如果是文件
                            print(f"Selected file: {selected_item}")
                            returnfile=f"{dirnow}/{selected_item}"
                            noexit=0
                            break
                        else:  # 如果是空
                            pass
                    break
                await asyncio.sleep(0.1)  # 稍微延迟，避免过快的循环
        if noexit==0:
            return returnfile

            await asyncio.sleep(0.1)  # 稍微延迟，避免过快的循环