
import socket
import requests
import psutil
import platform
from datetime import datetime


def get_local_ip():
    """
    获取本机IP地址
    :return:
    """
    # 创建一个临时socket连接获取本机IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_public_ip():
    """
    获取公网IP地址
    :return:
    """
    # 访问公共服务获取公网IP
    res = requests.get('http://httpbin.org/ip')
    ip = res.json()['origin']
    return ip


def get_system_info():
    """
    获取系统资源信息
    :return:
    """
    # 系统信息
    os_info = f"{platform.system()} {platform.release()}"  # 操作系统
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")  # 最后启动时间
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=False)  # 物理核心
    logical_cpu_count = psutil.cpu_count()  # 逻辑核心
    # 内存
    mem = psutil.virtual_memory()
    mem_total = mem.total / (1024 ** 3)  # 转换为GB
    mem_used = mem.used / (1024 ** 3)
    mem_percent = mem.percent
    # 磁盘信息
    disk = psutil.disk_usage('/')
    disk_total = disk.total / (1024 ** 3)  # 转换为GB
    disk_used = disk.used / (1024 ** 3)
    disk_percent = disk.percent
    # 组装成字典
    return {
        "cpu": {
            "percent": cpu_percent,
            "physical_cores": cpu_count,
            "logical_cores": logical_cpu_count
        },
        "memory": {
            "total": round(mem_total, 2),
            "used": round(mem_used, 2),
            "percent": mem_percent
        },
        "disk": {
            "total": round(disk_total, 2),
            "used": round(disk_used, 2),
            "percent": disk_percent
        },
        "system": {
            "os": os_info,
            "boot_time": boot_time
        }
    }


if __name__ == "__main__":
    # 本机IP
    local_ip = get_local_ip()
    print(f"\n📡 本机IP地址: \033[1;34m{local_ip}\033[0m")
    # 公网IP
    public_ip = get_public_ip()
    print(f"🌐 公网IP地址: \033[1;32m{public_ip}\033[0m")
    # 系统信息
    print("\n🔧 系统信息:")
    sys_info = get_system_info()
    print(f"  - 操作系统: {sys_info['system']['os']}")
    print(f"  - 最后启动: {sys_info['system']['boot_time']}")
    # CPU
    cpu = sys_info['cpu']
    print(f"\n💻 CPU使用率: \033[1;33m{cpu['percent']}%\033[0m")
    print(f"  - 物理核心: {cpu['physical_cores']}核")
    print(f"  - 逻辑核心: {cpu['logical_cores']}核")
    # 内存
    mem = sys_info['memory']
    print(f"\n🧠 内存使用: \033[1;33m{mem['percent']}%\033[0m")
    print(f"  - 总量: {mem['total']} GB")
    print(f"  - 已用: {mem['used']} GB")
    # 磁盘
    disk = sys_info['disk']
    print(f"\n💾 磁盘使用: \033[1;33m{disk['percent']}%\033[0m")
    print(f"  - 总量: {disk['total']} GB")
    print(f"  - 已用: {disk['used']} GB")



























