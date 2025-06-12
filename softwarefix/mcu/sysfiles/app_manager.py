import sys
import asyncio

class AppManager:
    def __init__(self, hmi):
        self.current_task = None  # 当前正在运行的应用程序任务
        self.app_paths = ['/sysfiles/app', '/userfiles/app','/sysfiles/app/yuzhuangapp']  # 应用程序路径
        self.hmi = hmi  # 存储 HMI 对象

    async def run_app(self, app_name):
        """运行应用程序"""
        if self.current_task:
            # 如果已经有应用程序在运行，先停止它
            await self.stop_app()

        app_module = None
        for path in self.app_paths:
            try:
                # 将应用程序路径添加到 sys.path
                if path not in sys.path:
                    sys.path.append(path)
                
                # 动态导入应用程序模块
                app_module = __import__(app_name)
                print(f"Application '{app_name}' loaded successfully from {path}.")
                break
            except ImportError:
                continue
            except Exception as e:
                print(f"Error loading application '{app_name}': {e}")
                return
        if app_module is None:
            print(f"Failed to load application '{app_name}'.")
            return

        if hasattr(app_module, 'main'):
            # 创建并启动应用程序任务
            self.current_task = asyncio.create_task(app_module.main(self.hmi))  # 传递 hmi 对象
            print(f"Application '{app_name}' started.")
        else:
            print(f"Application '{app_name}' does not have a 'main' function.")

    async def stop_app(self):
        """停止当前正在运行的应用程序"""
        if self.current_task:
            task = self.current_task
            task.cancel()  # 取消任务
            try:
                await task  # 等待任务完成
            except asyncio.CancelledError:
                pass
            self.current_task = None
            print("Current application stopped.")
        else:
            print("No application is running.")

# 创建 AppManager 实例
app_manager = None