import storage
import os

# 禁用默认的 CIRCUITPY 驱动器
# storage.disable_usb_drive()

# 确保 /userfiles 路径存在
try:
    os.listdir("/userfiles")
except OSError:
    os.mkdir("/userfiles")

# 重新挂载根目录为可读写
storage.remount("/", readonly=False)

# 挂载 /userfiles 为可读写
storage.remount("/userfiles", readonly=False)