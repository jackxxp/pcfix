import time
import wifi

class WLANController:
    def __init__(self):
        pass

    def scan_wlan(self):
        """
        扫描附近的 Wi-Fi 网络
        """
        try:
            networks = wifi.radio.start_scanning_networks()
            print("Available networks:")
            for network in networks:
                print(f"{network.ssid},信道{network.rssi},信道{network.channel},加密{network.authmode}")
            wifi.radio.stop_scanning_networks()
        except Exception as e:
            print(f"Error scanning networks: {e}")

    def connect_to_wlan(self, ssid, password):
        """
        连接到指定的 Wi-Fi 网络
        :param ssid: 要连接的 Wi-Fi 网络的 SSID
        :param password: 要连接的 Wi-Fi 网络的密码
        """
        try:
            print(f"Connecting to {ssid}...")
            wifi.radio.connect(ssid, password)
            print("Connected!")
            print(f"IP Address: {wifi.radio.ipv4_address}")
        except Exception as e:
            print(f"Error connecting to {ssid}: {e}")

    def disconnect_wlan(self):
        """
        断开当前的 Wi-Fi 连接
        """
        try:
            wifi.radio.disconnect()
            print("Disconnected from Wi-Fi")
        except Exception as e:
            print(f"Error disconnecting from Wi-Fi: {e}")

    def get_wlan_status(self):
        """
        获取 Wi-Fi 模块的状态
        """
        status = {
            "connected": False,
            "ip_address": "None",
            "ssid": "None"
        }

        if wifi.radio.ipv4_address:
            status["connected"] = True
            status["ip_address"] = wifi.radio.ipv4_address
            status["ssid"] = wifi.radio.ssid

        return status

# 示例用法
if __name__ == "__main__":
    wlan_controller = WLANController()

    # 扫描 Wi-Fi 网络
    wlan_controller.scan_wlan()

    # 连接到 Wi-Fi 网络
    wlan_controller.connect_to_wlan("YourSSID", "YourPassword")

    # 获取 Wi-Fi 模块状态
    status = wlan_controller.get_wlan_status()
    print("Wi-Fi Module Status:")
    print(f"Connected: {status['connected']}")
    print(f"IP Address: {status['ip_address']}")
    print(f"SSID: {status['ssid']}")

    # 断开 Wi-Fi 连接
    wlan_controller.disconnect_wlan()