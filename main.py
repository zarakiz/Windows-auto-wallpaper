import customtkinter as ctk
import threading
import time
import os
import ctypes
import requests
import json
import sys
import random
import winreg
from PIL import Image, ImageDraw
import pystray

# --- 設定 ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

THEME_OPTIONS = [
    "自然風景 (Nature)", "城市建築 (Architecture)", "璀璨星空 (Space)",
    "賽博龐克 (Cyberpunk)", "可愛動物 (Animals)", "極簡主義 (Minimalist)",
    "日本風情 (Japan)", "深邃海洋 (Ocean)", "汽車超跑 (Cars)",
    "森林秘境 (Forest)", "壯麗山脈 (Mountains)", "迷幻抽象 (Abstract)",
    "唯美夕陽 (Sunset)", "動漫風格 (Anime)"
]

class AutoStartManager:
    def __init__(self, app_name="UnsplashWallpaperPro"):
        self.app_name = app_name
        if getattr(sys, 'frozen', False):
            self.cmd = f'"{sys.executable}"'
        else:
            self.cmd = f'"{sys.executable}" "{os.path.realpath(sys.argv[0])}"'
        self.key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def set_auto_start(self, enabled=True):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self.cmd)
            else:
                try:
                    winreg.DeleteValue(key, self.app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"設置自啟動失敗: {e}")

class ConfigManager:
    def __init__(self, filepath="config_unsplash.json"):
        self.filepath = filepath
        self.data = self.load()

    def load(self):
        default_config = {
            "unsplash_key": "",
            "interval": "60",
            "auto_start": False,
            "selected_themes": ["自然風景 (Nature)"],
            "used_ids": []
        }
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    for key, val in default_config.items():
                        if key not in content:
                            content[key] = val
                    return content
            except: pass
        return default_config

    def save(self, data):
        self.data = data
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

class WallpaperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.auto_start_manager = AutoStartManager()
        
        self.title("Unsplash Pro 4K")
        self.geometry("450x700")
        
        conf = self.config_manager.data
        self.unsplash_key_var = ctk.StringVar(value=conf.get("unsplash_key"))
        self.interval_var = ctk.StringVar(value=conf.get("interval"))
        self.auto_start_var = ctk.BooleanVar(value=conf.get("auto_start"))
        self.theme_vars = {t: ctk.BooleanVar(value=t in conf.get("selected_themes")) for t in THEME_OPTIONS}

        self.is_running = False
        self.tray_icon = None
        self.save_dir = os.path.join(os.getenv('USERPROFILE'), 'Pictures', 'PureWallpapers')
        if not os.path.exists(self.save_dir): os.makedirs(self.save_dir)

        self.create_widgets()
        self.protocol('WM_DELETE_WINDOW', self.hide_window)

        if self.auto_start_var.get() and self.unsplash_key_var.get():
            self.after(2000, self.start_service)

    def create_widgets(self):
        ctk.CTkLabel(self, text="Unsplash 4K 穩定版", font=("Microsoft JhengHei UI", 22, "bold")).pack(pady=15)
        
        frame_key = ctk.CTkFrame(self)
        frame_key.pack(pady=10, padx=25, fill="x")
        ctk.CTkLabel(frame_key, text="Unsplash Access Key:").pack(anchor="w", padx=15, pady=(5,0))
        ctk.CTkEntry(frame_key, textvariable=self.unsplash_key_var, show="*").pack(fill="x", padx=15, pady=(0,10))

        self.scroll_frame = ctk.CTkScrollableFrame(self, height=220, label_text="選擇桌布風格")
        self.scroll_frame.pack(pady=10, padx=25, fill="x")
        for t, v in self.theme_vars.items():
            ctk.CTkCheckBox(self.scroll_frame, text=t, variable=v).pack(anchor="w", padx=10, pady=2)

        frame_set = ctk.CTkFrame(self)
        frame_set.pack(pady=10, padx=25, fill="x")
        ctk.CTkLabel(frame_set, text="分鐘:").pack(side="left", padx=15)
        ctk.CTkEntry(frame_set, textvariable=self.interval_var, width=60).pack(side="left", padx=5)
        ctk.CTkCheckBox(frame_set, text="開機啟動", variable=self.auto_start_var).pack(side="right", padx=15)

        self.label_status = ctk.CTkLabel(self, text="狀態: 準備就緒")
        self.label_status.pack()
        self.label_timer = ctk.CTkLabel(self, text="00:00:00", font=("Consolas", 24, "bold"), text_color="#1E90FF")
        self.label_timer.pack()

        self.btn_start = ctk.CTkButton(self, text="立即開始自動換圖", fg_color="#28a745", height=40, command=self.start_service)
        self.btn_start.pack(pady=(10, 5), padx=25, fill="x")

        self.btn_exit = ctk.CTkButton(self, text="完全退出程式", fg_color="#dc3545", hover_color="#c82333", height=40, command=self.exit_app)
        self.btn_exit.pack(pady=5, padx=25, fill="x")

    def save_current_config(self):
        active_themes = [t for t, v in self.theme_vars.items() if v.get()]
        is_auto = self.auto_start_var.get()
        new_data = self.config_manager.data
        new_data.update({
            "unsplash_key": self.unsplash_key_var.get(),
            "interval": self.interval_var.get(),
            "auto_start": is_auto,
            "selected_themes": active_themes
        })
        self.config_manager.save(new_data)
        self.auto_start_manager.set_auto_start(is_auto)

    def create_tray_icon(self):
        if self.tray_icon: return 
        image = Image.new('RGB', (64, 64), color=(30, 144, 255))
        d = ImageDraw.Draw(image)
        d.ellipse([10, 10, 54, 54], fill=(255, 255, 255))
        menu = pystray.Menu(
            pystray.MenuItem('顯示視窗', self.show_window),
            pystray.MenuItem('結束程式', self.exit_app)
        )
        self.tray_icon = pystray.Icon("WPChanger", image, "桌布管家執行中", menu)

    def hide_window(self):
        self.save_current_config()
        self.withdraw()
        if self.tray_icon is None:
            self.create_tray_icon()
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.after(0, self.deiconify)
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def exit_app(self):
        self.is_running = False
        self.save_current_config()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        # 優雅結束
        sys.exit(0)

    def set_wallpaper(self, path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        self.clean_old_wallpapers(path)

    def clean_old_wallpapers(self, current_path):
        try:
            for file in os.listdir(self.save_dir):
                full_path = os.path.join(self.save_dir, file)
                if full_path != current_path:
                    os.remove(full_path)
        except: pass

    def perform_task(self):
        try:
            active_themes = [t for t, v in self.theme_vars.items() if v.get()]
            if not active_themes: return
            
            used_ids = self.config_manager.data.get("used_ids", [])
            chosen = random.choice(active_themes)
            keyword = chosen.split("(")[-1].replace(")", "") if "(" in chosen else chosen
            
            headers = {"User-Agent": "Mozilla/5.0 WallpaperApp/1.0"}
            img_data = None
            new_id = None
            
            for _ in range(3):
                seed = random.randint(1, 99999)
                url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=landscape&client_id={self.unsplash_key_var.get()}&sig={seed}"
                
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    temp_id = data['id']
                    if temp_id not in used_ids:
                        new_id = temp_id
                        img_url = data['urls']['full']
                        img_data = requests.get(img_url, timeout=30).content
                        break
                else:
                    self.label_status.configure(text="狀態: API 限制或 Key 錯誤")
                    return

            if img_data and new_id:
                path = os.path.join(self.save_dir, f"wp_{int(time.time())}.jpg")
                with open(path, 'wb') as f: 
                    f.write(img_data)
                self.set_wallpaper(path)
                used_ids.append(new_id)
                if len(used_ids) > 100: used_ids.pop(0)
                conf = self.config_manager.data
                conf["used_ids"] = used_ids
                self.config_manager.save(conf)
                self.label_status.configure(text=f"狀態: 更新成功 ({keyword})")
        except Exception as e:
            self.label_status.configure(text=f"狀態: 連線錯誤")

    def service_loop(self):
        while self.is_running:
            self.perform_task()
            try:
                interval = int(self.interval_var.get()) * 60
                if interval < 60: interval = 60 # 最小限制 1 分鐘
            except:
                interval = 3600
            
            target = time.time() + interval
            while time.time() < target and self.is_running:
                rem = int(target - time.time())
                self.label_timer.configure(text=f"{rem//3600:02d}:{(rem%3600)//60:02d}:{rem%60:02d}")
                time.sleep(1)

    def start_service(self):
        if not self.unsplash_key_var.get():
            self.label_status.configure(text="狀態: 請輸入 API Key")
            return
        
        self.save_current_config()
        if not self.is_running:
            self.is_running = True
            self.btn_start.configure(state="disabled", text="服務運行中...")
            threading.Thread(target=self.service_loop, daemon=True).start()

if __name__ == "__main__":
    app = WallpaperApp()
    app.mainloop()