from ctypes import cdll
import os
import configparser
import struct
from enum import IntEnum

dll_path = os.path.abspath('hidapi.dll')  # 查找hidapi.dll
with open("error.txt", "w") as f:
    f.write(dll_path)
try:
    cdll.LoadLibrary(dll_path)  # 使用绝对路径
    import hid

    print("load hidapi successfully!")
    print("加载hidapi成功！")
except Exception as e:
    print(f"fail to load hidapi: {e}")
    print(f"加载失败: {e}")
    print(f"check your hidapi.dll")
    print("查看hidapi.dll是否在当前文件夹")

config = configparser.ConfigParser()
try:
    config.read('config.ini')
    VENDOR_ID = config.get('deviceid', 'VENDOR_ID')
    PRODUCT_ID = config.get('deviceid', 'PRODUCT_ID')
    print(f"VENDOR_ID = {VENDOR_ID}")
    print(f"PRODUCT_ID = {PRODUCT_ID}")
except configparser.Error as e:
    print(e)
    print("fail to read config.ini")


class CoinCondition(IntEnum):
    NORMAL = 0x0
    JAM = 0x1
    DISCONNECT = 0x2
    BUSY = 0x3


# 定义 output_t 的解析格式（小端字节序）
OUTPUT_T_FORMAT = '<8h 4h 2B 2B 2H 2B 29x'  # 小端字节序，2B 2B 表示 2个 coin_data_t（每个2字节）
STRUCT_SIZE = struct.calcsize(OUTPUT_T_FORMAT)
# print(f"Struct size: {STRUCT_SIZE} bytes")  # 应输出 63
output_count = 0

last_Analog = [0, 0]


def parse_output_t(data: bytes):
    unpacked = struct.unpack(OUTPUT_T_FORMAT, data)
    return {
        'analog': unpacked[:8],
        'rotary': unpacked[8:12],
        'coin': [
            {'condition': CoinCondition(unpacked[12]), 'count': unpacked[13]},
            {'condition': CoinCondition(unpacked[14]), 'count': unpacked[15]}
        ],
        'switches': unpacked[16:18],
        'system_status': unpacked[18],
        'usb_status': unpacked[19],
    }


def data_changed(old, new):
    if old is None:
        print("detect swing limit")
        print("测试摇杆范围")
        return True  # 第一次总是输出
    return (
            old['analog'] != new['analog'] or
            old['rotary'] != new['rotary'] or
            old['coin'] != new['coin'] or
            old['switches'] != new['switches'] or
            old['system_status'] != new['system_status'] or
            old['usb_status'] != new['usb_status']
    )


def read_hid_device():
    global output_count
    last_data = None  # 缓存上一次的数据
    # device = hid.Device(vendor_id, product_id)
    device = hid.device()
    device.open(int(VENDOR_ID, 0), int(PRODUCT_ID, 0))
    while True:
        data = device.read(STRUCT_SIZE)
        if not data:
            continue

        current_data = parse_output_t(bytes(data))
        # print(current_data['rotary'])

        # 仅当数据变化时输出
        if data_changed(last_data, current_data):
            print(f"rotary  : {current_data['rotary']}")
            last_data = current_data  # 更新缓存


if __name__ == "__main__":
    # devices = hid.enumerate()
    try:
        read_hid_device()
    except Exception as e:
        print("")
        print(e)
