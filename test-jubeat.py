from PIL import Image
from pynput import keyboard
import subprocess
import copy
import time
import threading
import queue
import math
import yaml
import os
import sys

keycontroller= keyboard.Controller()

# 编辑好的图片路径
IMAGE_PATH = "./image/image_monitor.png"
# Android 多点触控数量
MAX_SLOT = 12
# 检测区域的像素值范围
AREA_SCOPE = 50
# 检测区域圆上点的数量
AREA_POINT_NUM = 8
# Android 设备实际屏幕大小 (单位:像素)
ANDROID_ABS_MONITOR_SIZE = [1600, 2560]
# Android 设备触控屏幕大小 (单位:像素)
ANDROID_ABS_INPUT_SIZE = [1600, 2560]
# 是否开启屏幕反转(充电口朝上时开启该配置)
ANDROID_REVERSE_MONITOR = False
# touch_thread 是否启用sleep, 默认关闭, 如果程序 CPU 占用较高则开启, 如果滑动时延迟极大请关闭
TOUCH_THREAD_SLEEP_MODE = False
# 每次 sleep 的延迟, 单位: 微秒, 默认 100 微秒
TOUCH_THREAD_SLEEP_DELAY = 100
# 测试模式,在终端输出所有日志以供调试,默认关闭
DEV_MODE = False

VER = "0.90"

exp_list = [
    ["q", "w", "e", "r", "t", ],
    ["y", "u", "i", "o", "p", ],
    ["a", "s", "d", "f", "g", ],
    ["h", "j", "k", "l", ],
]
exp_image_dict = {'41-65-93': 'q', '87-152-13': 'w', '213-109-81': 'e', '23-222-55': 'r', '69-203-71': 't',
                  '147-253-55': 'y', '77-19-35': 'u', '159-109-79': 'i', '87-217-111': 'o', '149-95-154': 'p',
                  '97-233-9': 'a', '159-27-222': 's', '152-173-186': 'd', '192-185-149': 'f', '158-45-23': 'g',
                  '197-158-219': 'h', '127-144-79': 'j', '242-41-155': 'k', '69-67-213': 'l'}




class JuTouchManager:

    def __init__(self):
        self.settingPacket = bytearray([40, 0, 0, 0, 0, 41])
        self.startUp = False
        self.recvData = ""

        self.touchQueue = queue.Queue()
        self.data_lock = threading.Lock()
        self.touchThread = threading.Thread(target=self.touch_thread)
        self.now_touch_data = b''
        self.now_touch_keys = []
        self.ping_touch_thread()

    def start(self):
        self.touchThread.start()
        print("[TouchThread]运行已开始,您可以启动游戏了")

    def ping_touch_thread(self):
        self.touchQueue.put([1,[]])

    def touch_thread(self):
        beginif = 0
        while True:
            # start_time = time.perf_counter()
            if not self.touchQueue.empty():
                if beginif == 0:
                    s_temp = [1,0]
                    beginif = 1
                # print("touchQueue 不为空，开始执行")
                stempold = s_temp[1]
                s_temp = self.touchQueue.get()
                self.update_touch(s_temp, stempold)
            # 延迟防止消耗 CPU 时间过长
            if TOUCH_THREAD_SLEEP_MODE:
                microsecond_sleep(TOUCH_THREAD_SLEEP_DELAY)
                if DEV_MODE : print("单次响应耗时:", (time.perf_counter() - start_time) * 1e3, "毫秒")

    def destroy(self):
        self.touchThread.join()

    def send_touch(self, ser, data ,stpold):
        if ser == 1:
            if not stpold == 0:
                 for keyold in list(set(stpold) - (set(stpold) & set(data))):
                     keycontroller.release(keyold)
            for key in data:
               keycontroller.press(key)

    # def build_touch_package(self, sl):
    #     sum_list = [0, 0, 0, 0, 0, 0, 0]
    #     for i in range(len(sl)):
    #         for j in range(len(sl[i])):
    #             if sl[i][j] == 1:
    #                 sum_list[i] += (2 ** j)
    #     s = "28 "
    #     for i in sum_list:
    #         s += hex(i)[2:].zfill(2).upper() + " "
    #     s += "29"
    #     # print(s)
    #     return bytes.fromhex(s)

    def build_touch_package(self, sl):
        sum_list = [sum(2 ** j for j, val in enumerate(row) if val == 1) for row in sl]
        hex_list = [hex(i)[2:].zfill(2).upper() for i in sum_list]
        s = "28 " + " ".join(hex_list) + " 29"
        # print(s)
        return bytes.fromhex(s)

    def update_touch(self, s_temp, stpold):
        if DEV_MODE : print("[DEVMODE]old_stemp:",stpold)
        with self.data_lock:
            self.now_touch_data = s_temp[0]
            self.now_touch_keys = s_temp[1]
            self.send_touch(1, s_temp[1], stpold)

        # print("[T_thread]Touch Keys:", s_temp[1])

    def change_touch(self, sl, touch_keys):
        self.touchQueue.put([1, touch_keys])


def restart_script():
    python = sys.executable
    script = os.path.abspath(sys.argv[0])
    os.execv(python, [python, script])


def microsecond_sleep(sleep_time):
    end_time = time.perf_counter() + (sleep_time - 1.0) / 1e6  # 1.0是时间补偿，需要根据自己PC的性能去实测
    while time.perf_counter() < end_time:
        pass


# 采集9个判定点
def get_colors_in_area(x, y):
    colors = set()  # 使用集合来存储颜色值，以避免重复
    num_points = AREA_POINT_NUM  # 要获取的点的数量
    angle_increment = 360.0 / num_points  # 角度增量
    cos_values = [math.cos(math.radians(i * angle_increment)) for i in range(num_points)]
    sin_values = [math.sin(math.radians(i * angle_increment)) for i in range(num_points)]
    # 处理中心点
    if 0 <= x < exp_image_width and 0 <= y < exp_image_height:
        colors.add(get_color_name(exp_image.getpixel((x, y))))
    # 处理圆上的点
    for i in range(num_points):
        dx = int(AREA_SCOPE * cos_values[i])
        dy = int(AREA_SCOPE * sin_values[i])
        px = x + dx
        py = y + dy
        if 0 <= px < exp_image_width and 0 <= py < exp_image_height:
            colors.add(get_color_name(exp_image.getpixel((px, py))))
    return list(colors)


def get_color_name(pixel):
    return str(pixel[0]) + "-" + str(pixel[1]) + "-" + str(pixel[2])


def convert(touch_data):
    copy_exp_list = copy.deepcopy(exp_list)
    touch_keys = {exp_image_dict[rgb_str] for i in touch_data if i["p"] for rgb_str in
                  get_colors_in_area(i["x"], i["y"]) if
                  rgb_str in exp_image_dict}
    if DEV_MODE : print("[DEVMODE]Touch Keys:", touch_keys)
    touched = sum(1 for i in touch_data if i["p"])
    if DEV_MODE : print("[DEVMODE]Touched:", touched)
    touch_keys_list = list(touch_keys)
    copy_exp_list = [[1 if item in touch_keys_list else 0 for item in sublist] for sublist in copy_exp_list]
    if DEV_MODE : print("[DEVMODE]copy_exp_list:",copy_exp_list)
    JuTouch_manager.change_touch(copy_exp_list, touch_keys_list)

def getevent():
    # 存储多点触控数据的列表
    touch_data = [{"p": False, "x": 0, "y": 0} for _ in range(MAX_SLOT)]
    # 记录当前按下的触控点数目
    touch_sum = 0
    # 记录当前选择的 SLOT 作为索引
    touch_index = 0

    # 通过 adb shell getevent 命令监控触摸事件
    process = subprocess.Popen(['adb', 'shell', 'getevent', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    key_is_changed = False

    # 读取命令输出
    for line in iter(process.stdout.readline, b''):
        try:
            
            event = line.decode('utf-8').strip()
            parts = event.split()

            # 垃圾过滤器,过滤无用数据
            if len(parts) < 4:
                continue
            
            event_type = parts[2]
            event_value_hex = parts[3]
            event_value = int(event_value_hex, 16)

            if event_type == 'ABS_MT_POSITION_X':
                key_is_changed = True
                touch_data[touch_index]["x"] = (ANDROID_ABS_MONITOR_SIZE[0] - event_value * abs_multi_x) if ANDROID_REVERSE_MONITOR else event_value * abs_multi_x

            elif event_type == 'ABS_MT_POSITION_Y':
                key_is_changed = True
                touch_data[touch_index]["y"] = (ANDROID_ABS_MONITOR_SIZE[1] - event_value * abs_multi_y) if ANDROID_REVERSE_MONITOR else event_value * abs_multi_y

            elif event_type == 'SYN_REPORT':
                if key_is_changed:
                    convert(touch_data)
                    key_is_changed = False

            elif event_type == 'ABS_MT_SLOT':
                key_is_changed = True
                touch_index = event_value
                if touch_index >= touch_sum:
                    touch_sum = touch_index + 1

            elif event_type == 'ABS_MT_TRACKING_ID':
                key_is_changed = True
                if event_value_hex == "ffffffff":
                    touch_data[touch_index]['p'] = False
                    touch_sum = max(0, touch_sum - 1)
                else:
                    touch_data[touch_index]['p'] = True
                    touch_sum += 1

        except Exception as e:
            event_error_output = line.decode('utf-8')
            if "name" not in event_error_output:
                continue
            print(event_error_output)


if __name__ == "__main__":
    print("[Main]AndUbeat -Controller- 版本%s"%VER)
    print("[Msg]本窗口是AUC的终端窗口,确认工作正常后您可以将本窗口最小化")
    print("[Warning]请务必以管理员身份运行本程序!")
    yaml_file_path = 'config.yaml'
    if len(sys.argv) > 1:
        yaml_file_path = sys.argv[1]
    if os.path.isfile(yaml_file_path):
        print("[Main]正在使用配置文件:", yaml_file_path)
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            c = yaml.safe_load(file)
        IMAGE_PATH = c["IMAGE_PATH"]
        MAX_SLOT = c["MAX_SLOT"]
        AREA_SCOPE = c["AREA_SCOPE"]
        AREA_POINT_NUM = c["AREA_POINT_NUM"]
        ANDROID_ABS_MONITOR_SIZE = c["ANDROID_ABS_MONITOR_SIZE"]
        ANDROID_ABS_INPUT_SIZE = c["ANDROID_ABS_INPUT_SIZE"]
        ANDROID_REVERSE_MONITOR = c["ANDROID_REVERSE_MONITOR"]
        TOUCH_THREAD_SLEEP_MODE = c["TOUCH_THREAD_SLEEP_MODE"]
        TOUCH_THREAD_SLEEP_DELAY = c["TOUCH_THREAD_SLEEP_DELAY"]
        DEV_MODE = c["DEV_MODE"]
        exp_image_dict = c["exp_image_dict"]
    else:
        print("[ERROR]未找到配置文件,载入默认配置")

    exp_image = Image.open(IMAGE_PATH)
    exp_image_width, exp_image_height = exp_image.size
    abs_multi_x = ANDROID_ABS_MONITOR_SIZE[0] / ANDROID_ABS_INPUT_SIZE[0]
    abs_multi_y = ANDROID_ABS_MONITOR_SIZE[1] / ANDROID_ABS_INPUT_SIZE[1]
    print("[Main]当前触控区域X轴放大倍数:", abs_multi_x)
    print("[Main]当前触控区域Y轴放大倍数:", abs_multi_y)
    print("[Main]" + ('已' if ANDROID_REVERSE_MONITOR else '未') + "开启屏幕反转")
    if ANDROID_REVERSE_MONITOR : print("[Warning]屏幕反转 在Android14设备上测试出现问题,若程序未正确响应触摸事件,请关闭此功能.(测试设备:Xiaomi Pad 6SPRO)")
    if DEV_MODE : print("[Warning]测试模式已启动,将输出全部日志,建议在调试结束后关闭此功能以节省资源#Config")
    JuTouch_manager = JuTouchManager()
    JuTouch_manager.start()
    threading.Thread(target=getevent).start()
