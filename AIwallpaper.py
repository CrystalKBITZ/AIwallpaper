import os
import sys
import ctypes
import winreg
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, font as tkfont
from tkinter import ttk
from pathlib import Path
import webbrowser
from datetime import datetime
from PIL import Image, ImageTk, ImageOps
import threading
import urllib.request
import json
import time
import re
import requests
import io
import tempfile
import random
import shutil
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def check_single_instance():
    mutex_name = "AIwallpaper_SingleInstance_Mutex"
    try:
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == 183:
            return False
        global _mutex_handle
        _mutex_handle = handle
        return True
    except:
        return True


def get_city_by_ip_fast():
    def try_ip_api():
        try:
            url = 'http://ip-api.com/json/'
            response = requests.get(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    city = data.get('city')
                    if city:
                        return city
            return None
        except:
            return None

    for _ in range(3):
        city = try_ip_api()
        if city:
            return city
    return None


# 天气翻译字典
WEATHER_TRANSLATION = {
    'Sunny': '晴', 'Clear': '晴', 'Partly cloudy': '局部多云', 'Cloudy': '多云',
    'Overcast': '阴天', 'Mist': '薄雾', 'Patchy rain possible': '局部可能有雨',
    'Patchy rain nearby': '局部有雨', 'Patchy light rain nearby': '局部有小雨',
    'Patchy moderate rain nearby': '局部有中雨', 'Patchy heavy rain nearby': '局部有大雨',
    'Light rain nearby': '附近有小雨', 'Moderate rain nearby': '附近有中雨',
    'Heavy rain nearby': '附近有大雨', 'Patchy snow possible': '局部可能有雪',
    'Patchy snow nearby': '局部有雪', 'Patchy light snow nearby': '局部有小雪',
    'Patchy moderate snow nearby': '局部有中雪', 'Patchy heavy snow nearby': '局部有大雪',
    'Patchy sleet possible': '局部可能有冻雨', 'Patchy freezing drizzle possible': '局部可能有冻毛毛雨',
    'Thundery outbreaks possible': '可能有雷暴', 'Blowing snow': '吹雪', 'Blizzard': '暴风雪',
    'Fog': '雾', 'Freezing fog': '冻雾', 'Patchy light drizzle': '局部有小毛毛雨',
    'Light drizzle': '小毛毛雨', 'Freezing drizzle': '冻毛毛雨', 'Heavy freezing drizzle': '大冻毛毛雨',
    'Patchy light rain': '局部有小雨', 'Light rain': '小雨', 'Moderate rain at times': '间中有中雨',
    'Moderate rain': '中雨', 'Heavy rain at times': '间中有大雨', 'Heavy rain': '大雨',
    'Light freezing rain': '小冻雨', 'Moderate or heavy freezing rain': '中到大冻雨',
    'Light sleet': '小冻雨', 'Moderate or heavy sleet': '中到大冻雨', 'Patchy light snow': '局部有小雪',
    'Light snow': '小雪', 'Patchy moderate snow': '局部有中雪', 'Moderate snow': '中雪',
    'Patchy heavy snow': '局部有大雪', 'Heavy snow': '大雪', 'Ice pellets': '冰粒',
    'Light rain shower': '小阵雨', 'Moderate or heavy rain shower': '中到大阵雨',
    'Torrential rain shower': '暴雨阵雨', 'Light sleet showers': '小冻雨阵雨',
    'Moderate or heavy sleet showers': '中到大冻雨阵雨', 'Light snow showers': '小阵雪',
    'Moderate or heavy snow showers': '中到大阵雪', 'Light showers of ice pellets': '小冰粒阵雨',
    'Moderate or heavy showers of ice pellets': '中到大冰粒阵雨',
    'Patchy light rain with thunder': '局部小雨伴雷暴', 'Moderate or heavy rain with thunder': '中到大雨伴雷暴',
    'Patchy light snow with thunder': '局部小雪伴雷暴', 'Moderate or heavy snow with thunder': '中到大雪伴雷暴',
    'Patchy light rain in area with thunder': '局部小雨伴雷暴',
    'Patchy light snow in area with thunder': '局部小雪伴雷暴',
    'Moderate or heavy rain in area with thunder': '中到大雨伴雷暴',
}


def translate_weather_en_to_cn(weather_en):
    if not weather_en:
        return '未知'
    if weather_en in WEATHER_TRANSLATION:
        return WEATHER_TRANSLATION[weather_en]
    for key, value in WEATHER_TRANSLATION.items():
        if key.lower() in weather_en.lower() or weather_en.lower() in key.lower():
            return value
    return '未知'


def ReturnTempAndWeather6():
    try:
        city = get_city_by_ip_fast()
        if not city:
            city = "福州"
        weather_url = f"https://wttr.in/{city}?format=j1"
        weather_response = requests.get(weather_url, timeout=10)
        weather_data = weather_response.json()
        current_data = weather_data.get('current_condition', [{}])[0]
        temperature = current_data.get('temp_C', 'N/A')
        weather_en = current_data.get('weatherDesc', [{}])[0].get('value', 'N/A')
        weather_cn = translate_weather_en_to_cn(weather_en)

        CITY_NAME_MAP = {
            'Fuzhou': '福州', 'Xiamen': '厦门', 'Quanzhou': '泉州', 'Zhangzhou': '漳州',
            'Putian': '莆田', 'Ningde': '宁德', 'Longyan': '龙岩', 'Sanming': '三明',
            'Nanping': '南平', 'Beijing': '北京', 'Shanghai': '上海', 'Guangzhou': '广州',
            'Shenzhen': '深圳', 'Hangzhou': '杭州', 'Nanjing': '南京', 'Wuhan': '武汉',
            'Chengdu': '成都', 'Chongqing': '重庆', 'Xi\'an': '西安', 'Tianjin': '天津',
            'Suzhou': '苏州', 'Dongguan': '东莞', 'Foshan': '佛山', 'Ningbo': '宁波',
            'Qingdao': '青岛', 'Changsha': '长沙', 'Zhengzhou': '郑州', 'Jinan': '济南',
            'Hefei': '合肥', 'Kunming': '昆明', 'Guiyang': '贵阳', 'Nanning': '南宁',
            'Haikou': '海口', 'Taipei': '台北', 'Kaohsiung': '高雄', 'Hong Kong': '香港',
            'Macau': '澳门',
        }

        def translate_city_name(en_name):
            if not en_name:
                return en_name
            if en_name in CITY_NAME_MAP:
                return CITY_NAME_MAP[en_name]
            clean_name = en_name.strip()
            if clean_name in CITY_NAME_MAP:
                return CITY_NAME_MAP[clean_name]
            return en_name

        city = translate_city_name(city)
        return [city, temperature, weather_cn]
    except Exception as e:
        print(f"获取信息失败: {e}")
        return ["获取失败", "N/A", "N/A"]


class WallpaperChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("AIwallpaper")
        self.root.withdraw()
        self.bg_color = '#2b2b2b'
        self.default_bg_color = '#2b2b2b'
        self.font_family = 'Arial'
        self.autostart_var = tk.BooleanVar()
        self.autostart_btn = None
        self.announcement_text = (
            "AIwallpaper 功能列表：\n\n"
            "1. 本地壁纸文件夹：选择文件夹后，双击列表图片即可设置桌面壁纸。\n"
            "2. 背景图片：可为软件主界面设置背景图片。\n"
            "3. 在线壁纸：提供自然风光、城市建筑、人物肖像、动物世界、二次元五个分类，点击缩略图即可更换壁纸（有确认提示）。\n"
            "4. 刷新：在线壁纸分类支持刷新获取新壁纸，冷却时间10秒。\n"
            "5. 初始化进度条：首次进入在线壁纸时显示加载进度。\n"
            "6. 临时文件夹管理：可自定义临时文件夹位置，退出时自动清理。\n"
            "7. 开机自启动：可设置是否随系统启动。\n"
            "8. 背景颜色与字体设置：支持界面外观个性化。\n"
            "9. 天气显示：主界面显示当前天气信息。\n"
            "10. 自定义图标：支持选择 ico/png/jpg/bmp/gif 等常见图片作为窗口图标。\n"
            "11. 检查更新：在设置中点击按钮可检查最新版本。\n"
            "12. 仓库地址：可查看 GitHub 和 Gitee 仓库链接，支持复制和跳转。\n"
            "13. 壁纸下载：在线壁纸右键可下载，可自定义默认保存路径。"
        )
        self.check_autostart()

        self.temp_dir_override = None
        self.anime_temp_dir = None
        self._setup_temp_dir()
        atexit.register(self._cleanup_temp)

        self.config = self.load_config()
        custom_icon_path = self.config.get('icon_path')

        if custom_icon_path and os.path.exists(custom_icon_path):
            self._apply_icon(custom_icon_path)
        else:
            default_icon = resource_path("1.ico")
            if os.path.exists(default_icon):
                self._apply_icon(default_icon)

        self.wallpaper_dir = None
        self.current_wallpaper = None
        self.supported_formats = {
            '.jpg', '.jpeg', '.jpe', '.jfif', '.png', '.bmp', '.gif',
            '.tif', '.tiff', '.webp', '.ico', '.cur', '.jp2', '.j2k',
            '.jpf', '.jpx', '.jpm', '.mj2', '.svg', '.heic', '.heif',
            '.avif', '.pbm', '.pgm', '.ppm', '.pnm', '.pcx', '.tga',
            '.dds', '.psd', '.xbm', '.xpm', '.ras', '.exr', '.hdr',
            '.raw', '.cr2', '.nef', '.orf', '.sr2', '.arw', '.dng',
            '.rw2', '.pef', '.raf', '.3fr', '.kdc', '.mef', '.mos',
            '.mrw', '.nrw', '.ptx', '.x3f',
            '.eps', '.ps', '.pdf', '.svgz'
        }

        self.canvas = None
        self.background_photo = None
        self.canvas_image_id = None
        self.bg_image_original = None

        self.time_outline_ids = []
        self.time_text_id = None
        self.date_outline_ids = []
        self.date_text_id = None
        self.weather_outline_ids = []
        self.weather_text_id = None

        self.preview_label = None
        self.preview_photo = None
        self.online_photo_refs = []
        self.current_online_images = []

        self.custom_category_urls = {
            '自然风光': 'https://www.bizhimi.cn/wallpaper/photo/ziran',
            '城市建筑': 'https://www.wallpaperalchemy.com/zh-CN/city/wallpapers',
            '人物肖像': 'https://www.moyubuluo.com/hdwallpapers/renwu/',
            '动物世界': 'https://www.bizhimi.cn/wallpaper/photo/dongwu',
        }

        self.categories = [
            ("自然风光", "nature,landscape"),
            ("城市建筑", "city,architecture"),
            ("人物肖像", "people,portrait"),
            ("动物世界", "animals,wildlife"),
            ("二次元", "anime"),
        ]
        self.current_category = "自然风光"
        self.current_tag = "nature,landscape"
        self.category_buttons = {}
        self.prefetched_images = {}
        self.next_batch_images = {}          # 下一批预取图片
        self.prefetching = set()             # 正在预取的分类
        self.prefetch_semaphore = threading.Semaphore(2)  # 预取并发控制

        self.refresh_cooldown = False
        self.refresh_btn = None
        self.refresh_countdown_label = None
        self.refresh_countdown_after_id = None  # 保存 after ID 用于取消

        self.current_version = "1.0.1"
        self.github_repo = "CrystalKBITZ/AIwallpaper"

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

        self.cached_fonts = None
        self.icon_photo = None

        self.setup_ui()
        self.update_clock()

        threading.Thread(target=self._preload_fonts, daemon=True).start()
        self.weather_update_thread = threading.Thread(target=self.weather_loop, daemon=True)
        self.weather_update_thread.start()

        self.show_splash_animation()
        self.reset_bg_color()

    # ========== 基础方法 ==========
    def _preload_fonts(self):
        self.cached_fonts = sorted(tkfont.families())

    def load_config(self):
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self, config_dict):
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

    def _setup_temp_dir(self):
        if self.temp_dir_override:
            base = Path(self.temp_dir_override)
            base.mkdir(parents=True, exist_ok=True)
            self.anime_temp_dir = base / "aiwallpaper_temp"
        else:
            self.anime_temp_dir = Path(tempfile.mkdtemp(prefix="anime_wallpapers_"))
        self.anime_temp_dir.mkdir(parents=True, exist_ok=True)

    def _cleanup_temp(self):
        try:
            if self.anime_temp_dir and self.anime_temp_dir.exists():
                shutil.rmtree(self.anime_temp_dir)
        except Exception as e:
            print(f"清理临时目录失败: {e}")

    def _apply_icon(self, icon_path):
        try:
            self.current_icon_path = icon_path
            img = Image.open(icon_path)
            if img.mode not in ('RGBA', 'RGB'):
                img = img.convert('RGBA')
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            photos = []
            for size in sizes:
                resized = img.copy()
                resized.thumbnail(size, Image.Resampling.LANCZOS)
                photos.append(ImageTk.PhotoImage(resized))
            self.icon_photo = photos
            self.root.iconphoto(True, *photos)
        except Exception as e:
            print(f"应用图标失败: {e}")
            try:
                if icon_path.lower().endswith('.ico'):
                    self.root.iconbitmap(icon_path)
            except:
                pass

    def _apply_icon_to_window(self, window):
        if not hasattr(self, 'icon_photo') or not self.icon_photo:
            return
        try:
            window.iconphoto(False, *self.icon_photo)
        except Exception as e:
            print(f"应用图标到窗口失败: {e}")

    # ========== UI 构建 ==========
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=5)

        tk.Label(title_frame, text="AIwallpaper", bg=self.bg_color, fg='white',
                 font=(self.font_family, 12, 'bold')).pack(side=tk.LEFT, padx=10)

        announce_btn_frame = tk.Frame(title_frame, bg='#FF9800', cursor='hand2')
        announce_btn_frame.pack(side=tk.RIGHT, padx=10)

        emoji_label = tk.Label(announce_btn_frame, text="📧", bg='#FF9800', fg='white',
                               font=(self.font_family, 20), cursor='hand2')
        emoji_label.pack(side=tk.LEFT)
        text_label = tk.Label(announce_btn_frame, text="公告", bg='#FF9800', fg='white',
                              font=(self.font_family, 10, 'bold'), cursor='hand2')
        text_label.pack(side=tk.LEFT)

        announce_btn_frame.bind("<Button-1>", lambda e: self.show_announcement())
        emoji_label.bind("<Button-1>", lambda e: self.show_announcement())
        text_label.bind("<Button-1>", lambda e: self.show_announcement())

        self.canvas = tk.Canvas(self.root, bg='#1a1a1a', height=220, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=False, padx=20, pady=10)
        self._create_outlined_text('time', font=(self.font_family, 24, 'bold'))
        self._create_outlined_text('date', font=(self.font_family, 12))
        self._create_outlined_text('weather', font=(self.font_family, 10))
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=8, fill=tk.X, padx=20)
        buttons = [
            ("背景图片", self.set_background_image, '#6c757d'),
            ("在线壁纸", self.show_online_wallpaper_entry, '#007acc'),
        ]
        for i, (text, cmd, color) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=cmd, bg=color, fg='white',
                            width=10, height=1, font=(self.font_family, 10))
            btn.grid(row=0, column=i, padx=3, pady=5, sticky='ew')
            btn_frame.grid_columnconfigure(i, weight=1)

        folder_frame = tk.Frame(self.root, bg=self.bg_color)
        folder_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(folder_frame, text="壁纸文件夹:", bg=self.bg_color, fg='white',
                 font=(self.font_family, 10)).pack(side=tk.LEFT)
        self.dir_var = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.dir_var, width=35,
                 font=(self.font_family, 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(folder_frame, text="浏览", command=self.select_folder,
                  font=(self.font_family, 10)).pack(side=tk.LEFT)

        self.status_label = tk.Label(self.root, text="请选择壁纸文件夹",
                                     bg=self.bg_color, fg='yellow', padx=10, pady=5,
                                     font=(self.font_family, 10, 'bold'))
        self.status_label.pack(fill=tk.X, padx=20, pady=5)

        main_area = tk.Frame(self.root, bg=self.bg_color)
        main_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        list_frame = tk.Frame(main_area, bg=self.bg_color)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(list_frame, text="双击图片设置壁纸：", bg=self.bg_color, fg='white',
                 font=(self.font_family, 10)).pack(anchor=tk.W)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                  bg='#3c3c3c', fg='white', height=10,
                                  selectbackground='#007acc',
                                  font=(self.font_family, 10))
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.preview_selected)
        self.listbox.bind('<Double-Button-1>', self.apply_selected_double)

        preview_frame = tk.Frame(main_area, bg=self.bg_color, width=250)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))
        preview_frame.pack_propagate(False)

        preview_header = tk.Frame(preview_frame, bg=self.bg_color)
        preview_header.pack(fill=tk.X)
        tk.Label(preview_header, text="预览", bg=self.bg_color, fg='white',
                 font=(self.font_family, 10, 'bold')).pack(side=tk.LEFT, anchor=tk.W)

        settings_btn_frame = tk.Frame(preview_header, bg=self.bg_color, cursor='hand2')
        settings_btn_frame.pack(side=tk.RIGHT)
        gear_label = tk.Label(settings_btn_frame, text="⚙️", bg=self.bg_color, fg='white',
                              font=(self.font_family, 16), cursor='hand2')
        gear_label.pack(side=tk.LEFT)
        settings_text_label = tk.Label(settings_btn_frame, text="设置", bg=self.bg_color, fg='white',
                                       font=(self.font_family, 10), cursor='hand2')
        settings_text_label.pack(side=tk.LEFT, padx=(2, 0))
        settings_btn_frame.bind("<Button-1>", lambda e: self.show_settings())
        gear_label.bind("<Button-1>", lambda e: self.show_settings())
        settings_text_label.bind("<Button-1>", lambda e: self.show_settings())

        self.preview_label = tk.Label(preview_frame, bg='#1a1a1a', text="选择图片预览",
                                      fg='#666666', width=30, height=12,
                                      font=(self.font_family, 10))
        self.preview_label.pack(fill=tk.BOTH, expand=True)

    # ========== 在线壁纸入口 ==========
    def show_online_wallpaper_entry(self):
        if self.prefetched_images:
            self.show_online_wallpaper_main()
        else:
            self.show_init_window()

    def show_init_window(self):
        self.init_win = tk.Toplevel(self.root)
        win = self.init_win
        win.title("正在初始化在线壁纸")
        win.geometry("500x300")
        win.configure(bg='#2b2b2b')
        win.transient(self.root)
        self._apply_icon_to_window(win)

        tk.Label(win, text="AIwallpaper 在线壁纸初始化", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 14, 'bold')).pack(pady=20)

        self.init_progress = ttk.Progressbar(win, length=400, mode='determinate', maximum=100, value=0)
        self.init_progress.pack(pady=20)

        self.init_status_label = tk.Label(win, text="准备开始...", bg='#2b2b2b', fg='yellow',
                                          font=(self.font_family, 10))
        self.init_status_label.pack(pady=10)

        self.enter_btn = tk.Button(win, text="初始化中...", state=tk.DISABLED,
                                   bg='#4a4a4a', fg='white', width=15,
                                   font=(self.font_family, 10))
        self.enter_btn.pack(pady=20)

        tk.Label(win, text="初始化中，请耐心等待", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 10)).pack(side=tk.BOTTOM, pady=10)

        threading.Thread(target=self._initialize_all_categories, daemon=True).start()

    def _initialize_all_categories(self):
        total = len(self.categories)
        completed = 0

        def worker(cat, tag):
            try:
                urls = self._get_wallpaper_urls(cat, tag)
                images = self._download_images(urls)
                return cat, images
            except Exception as e:
                print(f"初始化 {cat} 失败: {e}")
                return cat, []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(worker, cat, tag): cat for cat, tag in self.categories}
            for future in as_completed(futures):
                cat, images = future.result()
                self.prefetched_images[cat] = images
                completed += 1
                progress_value = int(completed / total * 100)
                self.root.after(0, lambda v=progress_value: self._update_init_progress(v))
        self.root.after(0, self._on_init_complete)

    def _download_images(self, urls):
        def download_single(url):
            try:
                if os.path.exists(url):
                    img = Image.open(url)
                else:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    session = requests.Session()
                    resp = session.get(url, timeout=10, headers=headers)
                    resp.raise_for_status()
                    img = Image.open(io.BytesIO(resp.content))

                if img.width <= img.height:
                    return None

                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                return url, img
            except Exception as e:
                print(f"下载 {url} 失败: {e}")
                return None

        result = []
        with ThreadPoolExecutor(max_workers=16) as executor:  # 提高并发数
            futures = [executor.submit(download_single, url) for url in urls]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    result.append(data)
        return result

    def _update_init_progress(self, value):
        if hasattr(self, 'init_progress'):
            self.init_progress['value'] = value
            if hasattr(self, 'init_status_label'):
                self.init_status_label.config(text=f"加载中... {value}%")

    def _on_init_complete(self):
        if hasattr(self, 'init_progress'):
            self.init_progress['value'] = 100
        if hasattr(self, 'init_status_label'):
            self.init_status_label.config(text="初始化完成！100%")
        if hasattr(self, 'enter_btn'):
            self.enter_btn.config(state=tk.NORMAL, text="进入在线壁纸", bg='#28a745',
                                  command=self._open_online_wallpaper_after_init)

    def _open_online_wallpaper_after_init(self):
        if hasattr(self, 'init_win') and self.init_win.winfo_exists():
            self.init_win.destroy()
        self.show_online_wallpaper_main()

    def _ensure_prefetching(self):
        """确保所有分类都有下一批预取图片（如果没有且未在预取中）"""
        for cat, tag in self.categories:
            if cat in self.next_batch_images or cat in self.prefetching:
                continue
            self._prefetch_next_batch(cat, tag)

    def _prefetch_next_batch(self, category_name, tag):
        """后台预取下一批壁纸，存入 next_batch_images"""
        if category_name in self.prefetching:
            return
        self.prefetching.add(category_name)

        def work():
            with self.prefetch_semaphore:
                try:
                    urls = self._get_wallpaper_urls(category_name, tag)
                    if urls:
                        images = self._download_images(urls)
                        self.next_batch_images[category_name] = images
                except Exception as e:
                    print(f"预取 {category_name} 失败: {e}")
                finally:
                    self.prefetching.discard(category_name)
        threading.Thread(target=work, daemon=True).start()

    # ========== 在线壁纸主界面 ==========
    def show_online_wallpaper_main(self):
        self.online_win = tk.Toplevel(self.root)
        win = self.online_win
        win.title("在线壁纸")
        win.geometry("700x600")
        win.configure(bg='#2b2b2b')
        win.transient(self.root)
        self._apply_icon_to_window(win)

        tk.Label(win, text="在线壁纸 - 点击图片设置为桌面壁纸", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 12, 'bold')).pack(pady=10)

        category_frame = tk.Frame(win, bg='#2b2b2b')
        category_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        self.category_buttons = {}
        for idx, (text, tag) in enumerate(self.categories):
            btn = tk.Button(category_frame, text=text, bg='#4a4a4a', fg='white',
                            font=(self.font_family, 10), relief=tk.RAISED, bd=2,
                            command=lambda t=text, g=tag: self.switch_category(t, g))
            btn.grid(row=0, column=idx, padx=2, pady=2, sticky='ew')
            self.category_buttons[text] = btn
            category_frame.grid_columnconfigure(idx, weight=1)

        refresh_frame = tk.Frame(category_frame, bg='#2b2b2b')
        refresh_frame.grid(row=0, column=len(self.categories), padx=(5,2), pady=2, sticky='ew')
        self.refresh_btn = tk.Button(refresh_frame, text="刷新", bg='#28a745', fg='white',
                                    font=(self.font_family, 10), relief=tk.RAISED, bd=2,
                                    command=self.refresh_current_category)
        self.refresh_btn.pack(side=tk.LEFT)
        self.refresh_countdown_label = tk.Label(refresh_frame, text="", bg='#2b2b2b', fg='white',
                                                font=(self.font_family, 9))
        self.refresh_countdown_label.pack(side=tk.LEFT, padx=(5,0))
        category_frame.grid_columnconfigure(len(self.categories), weight=0)

        self.category_buttons[self.current_category].config(bg='#007acc')

        canvas = tk.Canvas(win, bg='#2b2b2b', highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        self.online_context_menu = tk.Menu(win, tearoff=0)

        def _on_close():
            # 取消刷新倒计时
            if self.refresh_countdown_after_id is not None:
                try:
                    self.root.after_cancel(self.refresh_countdown_after_id)
                except:
                    pass
                self.refresh_countdown_after_id = None
            # 重置状态
            self.refresh_cooldown = False
            # 清理引用
            canvas.unbind("<MouseWheel>")
            scrollable_frame.unbind("<MouseWheel>")
            if hasattr(self, 'online_context_menu'):
                self.online_context_menu.destroy()
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _on_close)

        self.scrollable_frame = scrollable_frame
        self.online_photo_refs = []

        # 进入主界面立即启动10秒冷却
        self.refresh_cooldown = True
        if self.refresh_btn:
            self.refresh_btn.config(state=tk.DISABLED)
        self._update_refresh_countdown(10)

        self.switch_category(self.current_category, self.current_tag)

        # 启动后台预取（如果必要）
        self._ensure_prefetching()

    def switch_category(self, category_name, tag):
        self.current_category = category_name
        self.current_tag = tag

        if not hasattr(self, 'scrollable_frame') or self.scrollable_frame is None:
            return

        for name, btn in self.category_buttons.items():
            btn.config(bg='#4a4a4a')
        self.category_buttons[category_name].config(bg='#007acc')

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        images = self.prefetched_images.get(category_name, [])
        if images:
            self._display_loaded_wallpapers(images)
        else:
            loading_label = tk.Label(self.scrollable_frame, text="正在加载...", bg='#2b2b2b', fg='white',
                                     font=(self.font_family, 12))
            loading_label.pack(pady=50)
            if category_name not in self.prefetched_images:
                threading.Thread(target=self._reload_category_async, args=(category_name, tag), daemon=True).start()

    def _reload_category_async(self, category_name, tag):
        def work():
            urls = self._get_wallpaper_urls(category_name, tag)
            if not urls:
                self.root.after(0, lambda: self._show_load_error(f"加载 {category_name} 失败"))
                return
            images = self._download_images(urls)
            self.prefetched_images[category_name] = images
            self.root.after(0, lambda: self._display_loaded_wallpapers(images))
            # 预取下一批
            self._prefetch_next_batch(category_name, tag)
        threading.Thread(target=work, daemon=True).start()

    def refresh_current_category(self):
        if self.refresh_cooldown:
            return
        self.refresh_cooldown = True
        if self.refresh_btn:
            self.refresh_btn.config(state=tk.DISABLED)
        self._update_refresh_countdown(10)

        category = self.current_category
        # 优先使用预取的下一批
        next_images = self.next_batch_images.pop(category, None)
        if next_images:
            self.prefetched_images[category] = next_images
            self._display_loaded_wallpapers(next_images)
            # 立即预取下一批
            self._prefetch_next_batch(category, self.current_tag)
        else:
            # 没有预取，走正常加载流程
            self.prefetched_images[category] = []
            self.switch_category(category, self.current_tag)
            threading.Thread(target=self._reload_category_async,
                             args=(category, self.current_tag), daemon=True).start()

    def _update_refresh_countdown(self, remaining):
        if remaining > 0:
            if self.refresh_countdown_label:
                self.refresh_countdown_label.config(text=f"{remaining}s")
            self.refresh_countdown_after_id = self.root.after(1000, lambda: self._update_refresh_countdown(remaining - 1))
        else:
            if self.refresh_countdown_label:
                self.refresh_countdown_label.config(text="")
            self.refresh_cooldown = False
            if self.refresh_btn:
                self.refresh_btn.config(state=tk.NORMAL)
            self.refresh_countdown_after_id = None

    def _display_loaded_wallpapers(self, images):
        if not hasattr(self, 'scrollable_frame') or self.scrollable_frame is None:
            return
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.online_photo_refs.clear()
        self.current_online_images = [{'id': idx, 'download_url': url} for idx, (url, _) in enumerate(images)]

        if not images:
            tk.Label(self.scrollable_frame, text="该分区暂无壁纸", bg='#2b2b2b', fg='white').pack()
            return

        row, col = 0, 0
        for idx, (url, pil_img) in enumerate(images):
            photo = ImageTk.PhotoImage(pil_img)
            self.online_photo_refs.append(photo)

            placeholder = tk.Label(self.scrollable_frame, image=photo, bg='#2b2b2b', cursor='hand2')
            placeholder.image = photo
            placeholder.grid(row=row, column=col, padx=10, pady=10)
            placeholder.bind("<Button-1>", lambda e, url=url, id=idx: self.set_online_wallpaper(url, id))
            placeholder.bind("<Button-3>", lambda e, url=url: self.show_online_context_menu(e, url))

            col += 1
            if col >= 3:
                col = 0
                row += 1

        random_btn = tk.Button(self.scrollable_frame, text="随机壁纸", command=self.set_random_online_wallpaper,
                               bg='#007acc', fg='white', font=(self.font_family, 12))
        random_btn.grid(row=row + 1, column=0, columnspan=3, pady=20)

    def _show_load_error(self, msg):
        if not hasattr(self, 'scrollable_frame') or self.scrollable_frame is None:
            return
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        tk.Label(self.scrollable_frame, text=msg, bg='#2b2b2b', fg='red',
                 font=(self.font_family, 12)).pack(pady=50)

    # ========== 右键菜单与下载 ==========
    def show_online_context_menu(self, event, url):
        self.online_context_menu.delete(0, tk.END)
        self.online_context_menu.add_command(label="下载壁纸", command=lambda: self.download_online_wallpaper(url, use_default=True))
        self.online_context_menu.add_command(label="另存为...", command=lambda: self.download_online_wallpaper(url, use_default=False))
        try:
            self.online_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.online_context_menu.grab_release()

    def download_online_wallpaper(self, url, use_default=True):
        if use_default and self.config.get('download_path'):
            save_dir = Path(self.config['download_path'])
            save_dir.mkdir(parents=True, exist_ok=True)
            ext = os.path.splitext(urlparse(url).path)[1]
            if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
                ext = '.jpg'
            filename = f"wallpaper_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100,999)}{ext}"
            file_path = save_dir / filename
        else:
            file_path = filedialog.asksaveasfilename(
                parent=self.online_win,
                title="保存壁纸",
                defaultextension=".jpg",
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("WebP", "*.webp"), ("所有文件", "*.*")]
            )
            if not file_path:
                return

        def download_task():
            try:
                high_res_url = self._enhance_image_url(url)
                headers = {'User-Agent': 'Mozilla/5.0'}
                session = requests.Session()
                try:
                    resp = session.get(high_res_url, timeout=20, headers=headers)
                    resp.raise_for_status()
                except:
                    resp = session.get(url, timeout=20, headers=headers)
                    resp.raise_for_status()

                with open(file_path, 'wb') as f:
                    f.write(resp.content)

                self.root.after(0, lambda: messagebox.showinfo("下载完成", f"壁纸已保存到：\n{file_path}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("下载失败", f"下载失败：{str(e)}"))

        threading.Thread(target=download_task, daemon=True).start()

    # ========== 获取图片URL ==========
    def _save_urls_to_temp(self, category_name, urls):
        if not self.anime_temp_dir:
            return
        try:
            file_path = os.path.join(self.anime_temp_dir, f"{category_name}_urls.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存 URL 失败: {e}")

    def _get_wallpaper_urls(self, category_name, tag):
        if category_name == "二次元":
            urls = self._get_anime_urls()
        else:
            try:
                url = self.custom_category_urls.get(category_name)
                if not url:
                    urls = self._get_loremflickr_urls(tag)
                else:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                    }
                    session = requests.Session()
                    resp = session.get(url, params={'t': int(time.time())}, timeout=15, headers=headers)
                    resp.raise_for_status()
                    if resp.encoding is None or resp.encoding.lower() == 'iso-8859-1':
                        resp.encoding = resp.apparent_encoding
                    html = resp.text
                    img_urls = re.findall(r'(?:src|data-src|data-original|data-lazy-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp))["\']', html, re.I)
                    if not img_urls:
                        img_urls = re.findall(r'https://cdn\.pixabay\.com/photo/[^"\'\s]+\.(?:jpg|jpeg|png)', html)
                    full_urls = []
                    for u in img_urls:
                        if u.startswith('http'):
                            full_urls.append(u)
                        elif u.startswith('//'):
                            full_urls.append('https:' + u)
                        elif u.startswith('/'):
                            parsed = urlparse(url)
                            base = f"{parsed.scheme}://{parsed.netloc}"
                            full_urls.append(base + u)
                        else:
                            full_urls.append(url.rstrip('/') + '/' + u)
                    full_urls = [u for u in full_urls if 'logo' not in u.lower() and 'icon' not in u.lower() and 'avatar' not in u.lower()]
                    seen = set()
                    unique_urls = []
                    for u in full_urls:
                        if u not in seen:
                            seen.add(u)
                            unique_urls.append(u)
                    if unique_urls:
                        random.shuffle(unique_urls)
                        urls = unique_urls[:30]
                    else:
                        urls = self._get_loremflickr_urls(tag)
            except Exception as e:
                print(f"爬取 {category_name} 失败: {e}")
                urls = self._get_loremflickr_urls(tag)

        if urls:
            self._save_urls_to_temp(category_name, urls)
        return urls

    def _get_anime_urls(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            session = requests.Session()
            url = "https://www.wallpaperalchemy.com/zh-CN/blue-archive/wallpapers"
            resp = session.get(url, params={'t': int(time.time())}, timeout=10, headers=headers)
            resp.raise_for_status()
            html = resp.text
            img_urls = re.findall(r'https?://[^\s"\']+\.(?:jpg|jpeg|png|webp)', html)
            seen = set()
            unique_urls = []
            for u in img_urls:
                if u not in seen:
                    seen.add(u)
                    unique_urls.append(u)
            filtered = [u for u in unique_urls if 'logo' not in u.lower() and 'icon' not in u.lower()]
            if filtered:
                unique_urls = filtered
            if unique_urls:
                random.shuffle(unique_urls)
                return unique_urls[:30]
        except Exception as e:
            print(f"二次元爬取失败: {e}")
        return self._get_anime_fallback_urls()

    def _get_anime_fallback_urls(self):
        headers = {'User-Agent': 'Mozilla/5.0'}
        urls = []
        try:
            resp = requests.get("https://nekos.best/api/v2/neko?amount=30", timeout=8, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get('results', []):
                if item.get('url'):
                    urls.append(item['url'])
            if len(urls) >= 30:
                return urls[:30]
        except Exception as e:
            print(f"nekos.best失败: {e}")
        types = ['waifu', 'neko', 'shinobu', 'megumin', 'awoo', 'cuddle', 'kiss', 'pat']
        for t in types:
            try:
                resp = requests.get(f"https://api.waifu.pics/sfw/{t}", timeout=5, headers=headers)
                resp.raise_for_status()
                img_url = resp.json().get('url')
                if img_url:
                    urls.append(img_url)
                if len(urls) >= 30:
                    break
            except:
                continue
        if len(urls) >= 30:
            return urls[:30]
        while len(urls) < 30:
            urls.append(f"https://picsum.photos/id/{random.randint(1000, 2000)}/300/300")
        return urls[:30]

    def _get_loremflickr_urls(self, tag):
        base_seed = random.randint(1, 100000)
        return [f"https://loremflickr.com/300/300/{tag}?lock={base_seed + i}" for i in range(30)]

    # ========== 壁纸设置 ==========
    def set_online_wallpaper(self, url, img_id):
        if not messagebox.askyesno("确认更换", "是否更换壁纸？"):
            return
        self.status_label.config(text="正在下载并设置壁纸...")
        self.root.update_idletasks()

        def download_and_set():
            try:
                if os.path.exists(url):
                    img = Image.open(url)
                else:
                    high_res_url = self._enhance_image_url(url)
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    session = requests.Session()
                    try:
                        resp = session.get(high_res_url, timeout=20, headers=headers)
                        resp.raise_for_status()
                    except Exception:
                        resp = session.get(url, timeout=20, headers=headers)
                        resp.raise_for_status()
                    img = Image.open(io.BytesIO(resp.content))

                if img.mode in ('RGBA', 'P', 'LA'):
                    img = img.convert('RGB')
                screen_w = ctypes.windll.user32.GetSystemMetrics(0)
                screen_h = ctypes.windll.user32.GetSystemMetrics(1)
                img = ImageOps.fit(img, (screen_w, screen_h), Image.Resampling.LANCZOS)
                temp_dir = self.anime_temp_dir
                temp_path = os.path.join(temp_dir, f"online_wallpaper_{img_id}_fitted.bmp")
                img.save(temp_path, "BMP")
                self.root.after(0, lambda: self._finalize_wallpaper_change(temp_path))
            except Exception as e:
                error_msg = str(e)
                print(f"下载壁纸失败: {error_msg}")
                self.root.after(0, lambda: self._show_wallpaper_error(error_msg))

        threading.Thread(target=download_and_set, daemon=True).start()

    def _finalize_wallpaper_change(self, temp_path):
        self.set_wallpaper(Path(temp_path))
        self.status_label.config(text="壁纸已更换！")

    def _show_wallpaper_error(self, msg):
        self.status_label.config(text="壁纸设置失败")
        messagebox.showerror("错误", f"下载壁纸失败：{msg}")

    def _enhance_image_url(self, url):
        if "loremflickr.com" in url:
            return url.replace("/300/300/", "/1920/1080/")
        return url

    def set_random_online_wallpaper(self):
        def choose_and_set():
            try:
                if self.current_online_images:
                    img_info = random.choice(self.current_online_images)
                    url = img_info['download_url']
                    img_id = img_info['id']
                else:
                    if self.current_category == "二次元":
                        urls = self._get_anime_fallback_urls()
                    else:
                        urls = self._get_loremflickr_urls(self.current_tag)
                    if urls:
                        url = urls[0]
                        img_id = 0
                    else:
                        raise Exception("无法获取图片")
                self.root.after(0, lambda: self.set_online_wallpaper(url, img_id))
            except Exception as e:
                error_msg = str(e)
                print(f"下载随机壁纸失败: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("错误", f"下载随机壁纸失败：{error_msg}"))
        threading.Thread(target=choose_and_set, daemon=True).start()

    # ========== 辅助方法 ==========
    def _create_outlined_text(self, which, font):
        offsets = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        if which == 'time':
            self.time_outline_ids = []
            for dx, dy in offsets:
                id_ = self.canvas.create_text(0, 0, text="", fill='black', font=font)
                self.time_outline_ids.append((id_, dx, dy))
            self.time_text_id = self.canvas.create_text(0, 0, text="", fill='white', font=font)
        elif which == 'date':
            self.date_outline_ids = []
            for dx, dy in offsets:
                id_ = self.canvas.create_text(0, 0, text="", fill='black', font=font)
                self.date_outline_ids.append((id_, dx, dy))
            self.date_text_id = self.canvas.create_text(0, 0, text="", fill='white', font=font)
        elif which == 'weather':
            self.weather_outline_ids = []
            for dx, dy in offsets:
                id_ = self.canvas.create_text(0, 0, text="", fill='black', font=font)
                self.weather_outline_ids.append((id_, dx, dy))
            self.weather_text_id = self.canvas.create_text(0, 0, text="天气加载中...", fill='white', font=font)

    def _center_text(self, event=None):
        if not self.canvas:
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        time_center = (w/2, h/2 - 15)
        for id_, dx, dy in self.time_outline_ids:
            self.canvas.coords(id_, time_center[0]+dx, time_center[1]+dy)
        self.canvas.coords(self.time_text_id, time_center[0], time_center[1])
        date_center = (w/2, h/2 + 20)
        for id_, dx, dy in self.date_outline_ids:
            self.canvas.coords(id_, date_center[0]+dx, date_center[1]+dy)
        self.canvas.coords(self.date_text_id, date_center[0], date_center[1])
        weather_center = (w/2, h/2 + 45)
        for id_, dx, dy in self.weather_outline_ids:
            self.canvas.coords(id_, weather_center[0]+dx, weather_center[1]+dy)
        self.canvas.coords(self.weather_text_id, weather_center[0], weather_center[1])

    def translate_weather_desc(self, desc):
        return translate_weather_en_to_cn(desc)

    def ensure_chinese_weather(self, text):
        temp_text = text.replace('°C', '').replace('℃', '')
        english_words = re.findall(r'[A-Za-z]+', temp_text)
        if not english_words:
            return text
        for word in english_words:
            translated = self.translate_weather_desc(word)
            if translated != word:
                text = re.sub(r'\b' + re.escape(word) + r'\b', translated, text)
            else:
                return "今日天气: 获取失败"
        if re.search(r'[A-Za-z]', text.replace('°C', '').replace('℃', '')):
            return "今日天气: 获取失败"
        return text

    def get_city(self):
        city = ""
        try:
            url = "http://ip-api.com/json/?lang=zh-CN"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('status') == 'success':
                    city = data.get('city', '')
                    if not re.search(r'[\u4e00-\u9fff]', city):
                        city = ""
        except:
            pass
        return city

    def update_weather(self):
        weather_info = ReturnTempAndWeather6()
        city, temp, desc = weather_info
        if city == "获取失败" or desc == "N/A" or desc == "未知":
            weather_text = "今日天气: 获取失败"
        else:
            weather_text = f"今日天气: {city} {desc} {temp}°C"
        self.root.after(0, self._set_weather_text, weather_text)

    def _set_weather_text(self, text):
        if self.weather_text_id is not None:
            for id_, _, _ in self.weather_outline_ids:
                self.canvas.itemconfig(id_, text=text)
            self.canvas.itemconfig(self.weather_text_id, text=text)

    def weather_loop(self):
        self.update_weather()
        while True:
            time.sleep(60)
            self.update_weather()

    # ========== 公告 ==========
    def show_announcement(self):
        ann_win = tk.Toplevel(self.root)
        ann_win.title("公告")
        ann_win.geometry("420x400")
        ann_win.configure(bg='#2b2b2b')
        ann_win.transient(self.root)
        self._apply_icon_to_window(ann_win)
        tk.Label(ann_win, text=self.announcement_text, bg='#2b2b2b', fg='white',
                 font=(self.font_family, 10), justify=tk.LEFT, wraplength=380).pack(padx=20, pady=20)
        tk.Button(ann_win, text="关闭", command=ann_win.destroy,
                  bg='#4a4a4a', fg='white', width=10).pack(pady=10)

    # ========== 启动画面 ==========
    def show_splash_animation(self):
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        transparent_color = '#FF00FF'
        splash.configure(bg=transparent_color)
        splash.attributes('-transparentcolor', transparent_color)
        self._apply_icon_to_window(splash)

        w, h = 320, 160
        sw = splash.winfo_screenwidth()
        sh = splash.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        splash.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(splash, width=w, height=h, bg=transparent_color, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        radius = 12
        self.create_round_rectangle(canvas, 2, 2, w-2, h-2, radius, fill='#2b2b2b', outline='white', width=2)

        canvas.create_text(w//2, 25, text="AIwallpaper", fill='#FFFFFF', font=(self.font_family, 13), anchor='center')
        canvas.create_text(w//2, 48, text="感谢使用", fill='#FFFFFF', font=(self.font_family, 10), anchor='center')

        bar_x = 40
        bar_y = 130
        bar_width = 240
        bar_height = 10

        percent_text = canvas.create_text(w//2, 115, text="0%", fill='#FFFFFF', font=(self.font_family, 10), anchor='center')

        self.create_round_rectangle(canvas, bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                                    radius=bar_height//2, fill='#1a1a1a', outline='white', width=1)

        fill_rect = canvas.create_rectangle(bar_x, bar_y, bar_x, bar_y + bar_height,
                                            fill='#4CAF50', outline='')

        # 每25ms增加1，总时长约2.5秒
        self._update_progress(splash, canvas, fill_rect, percent_text,
                              bar_x, bar_y, bar_width, bar_height, current=0, step=1, delay=25)

    def _update_progress(self, splash, canvas, fill_rect, percent_text, bar_x, bar_y, bar_width, bar_height, current=0, step=1, delay=50):
        if current > 100:
            current = 100
        fill_width = int(bar_width * current / 100)
        canvas.coords(fill_rect, bar_x, bar_y, bar_x + fill_width, bar_y + bar_height)
        canvas.itemconfig(percent_text, text=f"{current}%")
        if current < 100:
            splash.after(delay, self._update_progress, splash, canvas, fill_rect, percent_text,
                         bar_x, bar_y, bar_width, bar_height, current + step, step, delay)
        else:
            splash.after(300, lambda: self._finish_splash(splash))

    def create_round_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2,
                  x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        canvas.create_polygon(points, smooth=True, **kwargs)

    def _finish_splash(self, splash):
        splash.destroy()
        self.root.deiconify()
        self.root.lift()

    # ========== 设置窗口 ==========
    def show_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("设置")
        settings_win.geometry("400x580")
        settings_win.configure(bg='#2b2b2b')
        settings_win.transient(self.root)
        self._apply_icon_to_window(settings_win)
        tk.Label(settings_win, text="设置", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 16, 'bold')).pack(pady=(20, 20))
        button_width = 18

        self.autostart_btn = tk.Button(settings_win, text="", command=self.toggle_autostart,
                                       width=button_width, height=1, relief=tk.RAISED, bd=3,
                                       font=(self.font_family, 10, 'bold'))
        self.autostart_btn.pack(pady=5)
        self.update_autostart_button()

        tk.Button(settings_win, text="背景颜色", command=self.choose_bg_color,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="重置背景颜色", command=self.reset_bg_color,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="字体设置", command=self.show_font_settings,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="临时文件夹位置", command=self.choose_temp_dir,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="壁纸保存路径", command=self.choose_download_path,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="自定义图标", command=self.show_icon_window,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="检查更新", command=self.check_for_updates,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="GitHub仓库", command=self.show_repo_window,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="关于", command=self.show_about,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=5)

        tk.Button(settings_win, text="关闭", command=settings_win.destroy,
                  bg='#4a4a4a', fg='white', width=button_width, height=1,
                  font=(self.font_family, 10)).pack(pady=(10, 20))

    def choose_download_path(self):
        folder = filedialog.askdirectory(title="选择壁纸默认保存路径")
        if folder:
            self.config['download_path'] = folder
            self.save_config(self.config)
            messagebox.showinfo("成功", f"壁纸默认保存路径已设置为：\n{folder}")

    def show_repo_window(self):
        repo_win = tk.Toplevel(self.root)
        repo_win.title("仓库地址")
        repo_win.geometry("500x250")
        repo_win.configure(bg='#2b2b2b')
        repo_win.transient(self.root)
        self._apply_icon_to_window(repo_win)

        tk.Label(repo_win, text="仓库地址", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 14, 'bold')).pack(pady=(20, 10))

        github_frame = tk.Frame(repo_win, bg='#2b2b2b')
        github_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(github_frame, text="GitHub:", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 10, 'bold')).pack(side=tk.LEFT)
        github_url = "https://github.com/CrystalKBITZ/AIwallpaper"
        github_label = tk.Label(github_frame, text=github_url, bg='#2b2b2b', fg='#4da6ff',
                                font=(self.font_family, 10, 'underline'), cursor='hand2')
        github_label.pack(side=tk.LEFT, padx=(5, 10))
        github_label.bind("<Button-1>", lambda e: webbrowser.open(github_url))
        tk.Button(github_frame, text="复制", command=lambda: self.copy_to_clipboard(github_url),
                  bg='#4a4a4a', fg='white', font=(self.font_family, 9)).pack(side=tk.RIGHT)

        gitee_frame = tk.Frame(repo_win, bg='#2b2b2b')
        gitee_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(gitee_frame, text="Gitee:", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 10, 'bold')).pack(side=tk.LEFT)
        gitee_url = "https://gitee.com/crystal-void/AIwallpaper"
        gitee_label = tk.Label(gitee_frame, text=gitee_url, bg='#2b2b2b', fg='#4da6ff',
                               font=(self.font_family, 10, 'underline'), cursor='hand2')
        gitee_label.pack(side=tk.LEFT, padx=(5, 10))
        gitee_label.bind("<Button-1>", lambda e: webbrowser.open(gitee_url))
        tk.Button(gitee_frame, text="复制", command=lambda: self.copy_to_clipboard(gitee_url),
                  bg='#4a4a4a', fg='white', font=(self.font_family, 9)).pack(side=tk.RIGHT)

        tk.Button(repo_win, text="关闭", command=repo_win.destroy,
                  bg='#4a4a4a', fg='white', width=10,
                  font=(self.font_family, 10)).pack(pady=20)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("复制成功", "网址已复制到剪贴板")

    # ========== 图标窗口 ==========
    def show_icon_window(self):
        self.icon_win = tk.Toplevel(self.root)
        win = self.icon_win
        win.title("选择图标")
        win.geometry("500x350")
        win.configure(bg='#2b2b2b')
        win.transient(self.root)
        self._apply_icon_to_window(win)

        current_dir = self.config.get('icon_dir', os.path.abspath("."))
        self.current_icon_dir = tk.StringVar(value=current_dir)
        self.preview_photo = None

        top_frame = tk.Frame(win, bg='#2b2b2b')
        top_frame.pack(fill=tk.X, padx=10, pady=(10,5))

        tk.Label(top_frame, text="文件夹:", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 9)).pack(side=tk.LEFT)
        dir_entry = tk.Entry(top_frame, textvariable=self.current_icon_dir, width=35,
                             bg='#3c3c3c', fg='white', insertbackground='white',
                             font=(self.font_family, 9))
        dir_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="浏览", command=self.browse_icon_dir,
                  bg='#4a4a4a', fg='white', font=(self.font_family, 9)).pack(side=tk.LEFT, padx=5)

        main_frame = tk.Frame(win, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))

        list_frame = tk.Frame(main_frame, bg='#2b2b2b')
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="图标文件（单击预览，双击应用）", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 9)).pack(anchor=tk.W)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.icon_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       bg='#3c3c3c', fg='white', height=10,
                                       selectbackground='#007acc',
                                       font=(self.font_family, 9))
        self.icon_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.icon_listbox.yview)

        self.icon_listbox.bind('<<ListboxSelect>>', self.preview_selected_icon)
        self.icon_listbox.bind('<Double-Button-1>', self.apply_selected_icon)

        preview_frame = tk.Frame(main_frame, bg='#2b2b2b', width=180)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5,0))
        preview_frame.pack_propagate(False)

        tk.Label(preview_frame, text="预览", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 9, 'bold')).pack(anchor=tk.W)
        self.icon_preview_label = tk.Label(preview_frame, bg='#1a1a1a', text="选择文件预览",
                                           fg='#666666', width=20, height=7,
                                           font=(self.font_family, 9))
        self.icon_preview_label.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        self.icon_status_label = tk.Label(win, text="", bg='#2b2b2b', fg='lightgreen',
                                          font=(self.font_family, 9))
        self.icon_status_label.pack(side=tk.BOTTOM, pady=5)

        self.load_icon_files_async()

    def browse_icon_dir(self):
        folder = filedialog.askdirectory(initialdir=self.current_icon_dir.get())
        if folder:
            self.current_icon_dir.set(folder)
            self.load_icon_files_async()

    def load_icon_files_async(self):
        directory = self.current_icon_dir.get()
        self.icon_status_label.config(text="加载中...", fg='yellow')

        def worker():
            files = []
            icon_exts = ('.ico', '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp',
                         '.jfif', '.jpe', '.tif', '.cur', '.svg', '.heic', '.heif', '.avif',
                         '.psd', '.tga', '.dds', '.exr', '.hdr', '.pbm', '.pgm', '.ppm',
                         '.pnm', '.pcx', '.xbm', '.xpm')
            try:
                if os.path.isdir(directory):
                    files = [f for f in os.listdir(directory)
                             if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(icon_exts)]
                    files.sort()
            except Exception as e:
                files = None
                error = str(e)
            self.root.after(0, lambda: self._update_icon_list(files, error if files is None else None))

        threading.Thread(target=worker, daemon=True).start()

    def _update_icon_list(self, files, error=None):
        self.icon_listbox.delete(0, tk.END)
        if error:
            self.icon_status_label.config(text=f"读取失败: {error}", fg='red')
            return
        if not files:
            self.icon_status_label.config(text="未找到图标文件", fg='yellow')
            return
        for f in files:
            self.icon_listbox.insert(tk.END, f)
        self.icon_status_label.config(text=f"共 {len(files)} 个文件", fg='white')

    def preview_selected_icon(self, event=None):
        selection = self.icon_listbox.curselection()
        if not selection:
            return
        filename = self.icon_listbox.get(selection[0])
        filepath = os.path.join(self.current_icon_dir.get(), filename)

        def worker():
            try:
                img = Image.open(filepath)
                img.thumbnail((160, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda: self._update_icon_preview(photo))
            except:
                self.root.after(0, lambda: self.icon_preview_label.config(image="", text="无法预览"))
        threading.Thread(target=worker, daemon=True).start()

    def _update_icon_preview(self, photo):
        self.preview_photo = photo
        self.icon_preview_label.config(image=photo, text="")

    def apply_selected_icon(self, event=None):
        selection = self.icon_listbox.curselection()
        if not selection:
            return
        filename = self.icon_listbox.get(selection[0])
        filepath = os.path.join(self.current_icon_dir.get(), filename)

        try:
            self._apply_icon(filepath)
        except Exception as e:
            self.icon_status_label.config(text=f"应用失败: {e}", fg='red')
            return

        self.config['icon_path'] = filepath
        self.config['icon_dir'] = self.current_icon_dir.get()
        self.save_config(self.config)
        self.icon_status_label.config(text=f"已应用: {filename}", fg='lightgreen')
        for win in self.root.winfo_children():
            if isinstance(win, tk.Toplevel):
                self._apply_icon_to_window(win)
        self.root.after(3000, lambda: self.icon_status_label.config(text="") if self.icon_win.winfo_exists() else None)

    # ========== 检查更新 ==========
    def fetch_latest_release_info(self):
        api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        try:
            resp = self.session.get(api_url, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            latest_version = data.get('tag_name', '').lstrip('v')
            assets = data.get('assets', [])
            download_url = None
            for asset in assets:
                if asset['name'].endswith('.exe') or asset['name'].endswith('.zip'):
                    download_url = asset['browser_download_url']
                    break
            if not download_url:
                download_url = data.get('html_url')
            return latest_version, download_url
        except Exception as e:
            print(f"获取更新信息失败: {e}")
            return None, None

    def check_for_updates(self):
        self.status_label.config(text="正在检查更新...")
        self.root.update_idletasks()

        def worker():
            latest_version, download_url = self.fetch_latest_release_info()
            self.root.after(0, lambda: self._on_update_check_done(latest_version, download_url))

        threading.Thread(target=worker, daemon=True).start()

    def _on_update_check_done(self, latest_version, download_url):
        self.status_label.config(text="就绪")
        if not latest_version:
            messagebox.showerror("检查更新", "无法连接更新服务器，请稍后重试。")
            return
        if latest_version > self.current_version:
            msg = f"发现新版本 v{latest_version}\n是否前往下载？"
            if messagebox.askyesno("发现新版本", msg):
                webbrowser.open(download_url)
        else:
            messagebox.showinfo("检查更新", "当前已是最新版本。")

    # ========== 开机自启动 ==========
    def check_autostart(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "CrystalWallpaper")
                self.autostart_var.set(True)
            except FileNotFoundError:
                self.autostart_var.set(False)
            finally:
                winreg.CloseKey(key)
        except:
            self.autostart_var.set(False)

    def set_autostart(self, enabled):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "CrystalWallpaper"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                if getattr(sys, 'frozen', False):
                    app_path = sys.executable
                else:
                    app_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("错误", f"设置开机自启动失败：{e}")

    def toggle_autostart(self):
        new_state = not self.autostart_var.get()
        self.autostart_var.set(new_state)
        self.set_autostart(new_state)
        self.update_autostart_button()

    def update_autostart_button(self):
        if self.autostart_btn is not None:
            if self.autostart_var.get():
                self.autostart_btn.config(text="开机自启动 [关]", bg='#dc3545', fg='white')
            else:
                self.autostart_btn.config(text="开机自启动 [开]", bg='#28a745', fg='white')

    # ========== 背景颜色 ==========
    def choose_bg_color(self):
        color = colorchooser.askcolor(color=self.bg_color, title="选择背景颜色")
        if color[1]:
            self.bg_color = color[1]
            self.apply_bg_color()

    def reset_bg_color(self):
        self.bg_color = self.default_bg_color
        self.apply_bg_color()

    def apply_bg_color(self):
        self.root.configure(bg=self.bg_color)
        for widget in self.root.winfo_children():
            self._update_widget_bg(widget)

    def _update_widget_bg(self, widget):
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.bg_color)
            elif isinstance(widget, tk.Label):
                if widget not in [self.preview_label]:
                    widget.configure(bg=self.bg_color)
        except:
            pass
        for child in widget.winfo_children():
            self._update_widget_bg(child)

    # ========== 字体设置 ==========
    def show_font_settings(self):
        font_win = tk.Toplevel(self.root)
        font_win.title("字体设置")
        font_win.geometry("350x450")
        font_win.configure(bg='#2b2b2b')
        font_win.transient(self.root)
        self._apply_icon_to_window(font_win)
        tk.Label(font_win, text="搜索字体:", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 10)).pack(pady=(10, 5))
        search_var = tk.StringVar()
        search_entry = tk.Entry(font_win, textvariable=search_var,
                                bg='#3c3c3c', fg='white', insertbackground='white',
                                font=(self.font_family, 10))
        search_entry.pack(fill=tk.X, padx=10, pady=5)
        listbox_frame = tk.Frame(font_win, bg='#2b2b2b')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        font_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set,
                                  bg='#3c3c3c', fg='white', selectbackground='#007acc',
                                  font=(self.font_family, 10))
        font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=font_listbox.yview)
        if self.cached_fonts is None:
            all_fonts = sorted(tkfont.families())
        else:
            all_fonts = self.cached_fonts
        for f in all_fonts:
            font_listbox.insert(tk.END, f)
        def filter_fonts(event=None):
            keyword = search_var.get().lower()
            font_listbox.delete(0, tk.END)
            filtered = [f for f in all_fonts if keyword in f.lower()]
            for f in filtered:
                font_listbox.insert(tk.END, f)
        search_entry.bind('<KeyRelease>', filter_fonts)
        def apply_font():
            selection = font_listbox.curselection()
            if selection:
                selected_font = font_listbox.get(selection[0])
                self.font_family = selected_font
                self.update_all_fonts()
                font_win.destroy()
                messagebox.showinfo("成功", f"字体已更改为 {self.font_family}")
        tk.Button(font_win, text="应用", command=apply_font,
                  bg='#28a745', fg='white', width=10,
                  font=(self.font_family, 10)).pack(pady=5)
        tk.Button(font_win, text="取消", command=font_win.destroy,
                  bg='#dc3545', fg='white', width=10,
                  font=(self.font_family, 10)).pack(pady=5)

    def update_all_fonts(self):
        def change_widget_font(widget):
            try:
                current_font = tkfont.Font(font=widget.cget("font"))
                size = current_font.cget("size")
                weight = current_font.cget("weight")
                slant = current_font.cget("slant")
                new_font = (self.font_family, size)
                if weight == 'bold':
                    new_font = (self.font_family, size, 'bold')
                if slant == 'italic':
                    new_font = (*new_font, 'italic')
                widget.config(font=new_font)
            except:
                pass
            for child in widget.winfo_children():
                change_widget_font(child)
        change_widget_font(self.root)

    # ========== 关于 ==========
    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title("关于")
        about_win.geometry("400x400")
        about_win.configure(bg='#2b2b2b')
        about_win.transient(self.root)
        self._apply_icon_to_window(about_win)
        tk.Label(about_win, text="关于", bg='#2b2b2b', fg='white',
                 font=(self.font_family, 16, 'bold')).pack(pady=15)
        about_text = ("AIwallpaper\n\n"
                      "支持静态图片壁纸切换\n\n"
                      "版本：1.0.2\n"
                      "开发者：Crystal空白\n"
                      "开发者QQ：3635835307\n"
                      "开发协助：-呈阶梯状分布-")
        tk.Label(about_win, text=about_text, bg='#2b2b2b', fg='white',
                 font=(self.font_family, 12), justify=tk.LEFT).pack(pady=10)
        def open_bilibili():
            webbrowser.open("https://m.bilibili.com/space/3493260198677093?from=search")
        tk.Button(about_win, text="开发者B站主页", command=open_bilibili,
                  bg='#007acc', fg='white', width=18, height=1,
                  font=(self.font_family, 10), cursor='hand2').pack(pady=10)
        tk.Button(about_win, text="关闭", command=about_win.destroy,
                  bg='#4a4a4a', fg='white', width=10,
                  font=(self.font_family, 10)).pack(pady=10)

    # ========== 临时文件夹 ==========
    def choose_temp_dir(self):
        folder = filedialog.askdirectory(title="选择临时文件夹")
        if folder:
            self.temp_dir_override = folder
            self._cleanup_temp()
            self._setup_temp_dir()
            messagebox.showinfo("成功", f"临时文件夹已更改为：{folder}\n建议重启程序确保所有功能生效。")

    # ========== 本地壁纸设置 ==========
    def set_wallpaper(self, path):
        try:
            test_img = Image.open(path)
            test_img.close()
            return self._set_wallpaper_via_bmp(path)
        except:
            result = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(path), 3)
            if result:
                self.current_wallpaper = path
                self.status_label.config(text=f"当前壁纸: {path.name}")
                return True
            else:
                messagebox.showerror("错误", "该图片格式不受支持或文件损坏")
                return False

    def _set_wallpaper_via_bmp(self, path):
        try:
            img = Image.open(path)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            temp_dir = self.anime_temp_dir
            temp_path = os.path.join(temp_dir, "wallpaper_temp.bmp")
            img.save(temp_path, "BMP")
            result = ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_path, 3)
            if result:
                self.current_wallpaper = path
                self.status_label.config(text=f"当前壁纸: {path.name}")
                return True
            else:
                messagebox.showerror("错误", "无法设置壁纸（系统不支持该图片格式）")
                return False
        except Exception as e:
            messagebox.showerror("错误", f"转换图片失败: {e}")
            return False

    def preview_selected(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            wallpapers = self.get_wallpapers()
            if selection[0] < len(wallpapers):
                self.show_preview(wallpapers[selection[0]])

    def apply_selected_double(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一张壁纸")
            return
        wallpapers = self.get_wallpapers()
        if not wallpapers:
            messagebox.showinfo("提示", "壁纸文件夹为空或未选择")
            return
        index = selection[0]
        if index < len(wallpapers):
            self.set_wallpaper(wallpapers[index])
        else:
            messagebox.showinfo("提示", "所选壁纸不存在")

    def show_preview(self, img_path):
        try:
            img = Image.open(img_path)
            pw = self.preview_label.winfo_width()
            ph = self.preview_label.winfo_height()
            if pw < 50 or ph < 50:
                pw, ph = 220, 160
            img.thumbnail((pw, ph), Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_photo, text="")
        except:
            self.preview_label.config(image="", text="无法预览此图片")

    def set_background_image(self):
        file_path = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[
                ("所有图片文件", "*.jpg *.jpeg *.jpe *.jfif *.png *.bmp *.gif *.tif *.tiff *.webp *.ico *.cur *.jp2 *.j2k *.jpf *.jpx *.jpm *.mj2 *.svg *.heic *.heif *.avif *.pbm *.pgm *.ppm *.pnm *.pcx *.tga *.dds *.psd *.xbm *.xpm *.ras *.exr *.hdr *.raw *.cr2 *.nef *.orf *.sr2 *.arw *.dng *.rw2 *.pef *.raf *.3fr *.kdc *.mef *.mos *.mrw *.nrw *.ptx *.x3f *.eps *.ps *.pdf"),
                ("JPEG", "*.jpg *.jpeg *.jpe *.jfif"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tif *.tiff"),
                ("WebP", "*.webp"),
                ("RAW 格式", "*.raw *.cr2 *.nef *.orf *.sr2 *.arw *.dng *.rw2 *.pef *.raf *.3fr *.kdc *.mef *.mos *.mrw *.nrw *.ptx *.x3f"),
                ("矢量格式", "*.svg *.eps *.ps *.pdf"),
                ("所有文件", "*.*")
            ]
        )
        if not file_path:
            return
        try:
            self.bg_image_original = Image.open(file_path)
            self._update_background_image()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载背景图片：{e}")

    def _update_background_image(self):
        if not hasattr(self, 'bg_image_original') or self.bg_image_original is None:
            return
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 2 or canvas_h < 2:
            return
        resized = self.bg_image_original.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized)
        if self.canvas_image_id:
            self.canvas.itemconfig(self.canvas_image_id, image=self.background_photo)
        else:
            self.canvas_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor='nw')
            self.canvas.tag_lower(self.canvas_image_id)

    def _on_canvas_configure(self, event=None):
        self._update_background_image()
        self._center_text(event)

    def update_clock(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d %A")
        for id_, _, _ in self.time_outline_ids:
            self.canvas.itemconfig(id_, text=time_str)
        self.canvas.itemconfig(self.time_text_id, text=time_str)
        for id_, _, _ in self.date_outline_ids:
            self.canvas.itemconfig(id_, text=date_str)
        self.canvas.itemconfig(self.date_text_id, text=date_str)
        self.root.after(1000, self.update_clock)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.wallpaper_dir = Path(folder)
            self.dir_var.set(str(folder))
            self.load_wallpapers()
            wallpapers = self.get_wallpapers()
            self.status_label.config(text=f"找到 {len(wallpapers)} 张壁纸，双击图片设置")

    def get_wallpapers(self):
        if not self.wallpaper_dir or not self.wallpaper_dir.exists():
            return []
        result = []
        for f in self.wallpaper_dir.iterdir():
            if f.is_file() and f.suffix.lower() in self.supported_formats:
                result.append(f)
        result.sort()
        return result

    def load_wallpapers(self):
        self.listbox.delete(0, tk.END)
        for wp in self.get_wallpapers():
            self.listbox.insert(tk.END, "🖼️ " + wp.name)


def main():
    if not check_single_instance():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("提示", "AIwallpaper 已在运行中，请不要重复打开。")
        root.destroy()
        return

    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.resizable(False, False)
    app = WallpaperChanger(root)
    root.attributes('-topmost', 0)
    root.mainloop()


if __name__ == "__main__":
    main()