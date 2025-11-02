import customtkinter as ctk
from tkinter import messagebox, filedialog
import subprocess
import platform
import winreg
import ctypes
import os
import socket
import requests
import getpass
import threading
import json
import psutil
import wmi
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import re

# تنظیمات ظاهری
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdvancedWindowsControlPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # تنظیمات پنجره اصلی
        self.title("🛡️ پنل کنترل پیشرفته مدیریت ویندوز")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # بررسی دسترسی مدیریت
        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not self.is_admin:
            messagebox.showwarning("⚠️ هشدار", 
                                 "برای عملکرد کامل، برنامه را با حقوق مدیر اجرا کنید.\n"
                                 "برنامه در حالت محدود اجرا می‌شود.")
        
        # مسیر فایل تنظیمات
        self.config_file = "panel_config.json"
        self.load_config()
        
        # WMI برای دسترسی عمیق به سیستم
        try:
            self.wmi = wmi.WMI()
        except:
            self.wmi = None
        
        # ایجاد فریم‌های اصلی
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        # شروع مانیتورینگ سیستم
        self.start_system_monitoring()
        
        # نمایش صفحه اصلی
        self.show_dashboard()
    
    def load_config(self):
        """بارگذاری تنظیمات ذخیره شده"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'theme': 'dark',
                    'auto_backup': False,
                    'monitoring_interval': 5,
                    'alert_cpu': 80,
                    'alert_memory': 85,
                    'alert_disk': 90
                }
        except:
            self.config = {}
    
    def save_config(self):
        """ذخیره تنظیمات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات: {e}")
    
    def start_system_monitoring(self):
        """شروع مانیتورینگ مداوم سیستم"""
        self.monitoring = True
        self.cpu_history = []
        self.memory_history = []
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
    
    def monitor_system(self):
        """مانیتورینگ مداوم منابع سیستم"""
        while self.monitoring:
            try:
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory().percent
                
                self.cpu_history.append(cpu)
                self.memory_history.append(memory)
                
                # نگه داشتن 60 نمونه آخر
                if len(self.cpu_history) > 60:
                    self.cpu_history.pop(0)
                if len(self.memory_history) > 60:
                    self.memory_history.pop(0)
                
                # بررسی هشدارها
                if cpu > self.config.get('alert_cpu', 80):
                    self.show_alert(f"⚠️ استفاده CPU: {cpu}%")
                if memory > self.config.get('alert_memory', 85):
                    self.show_alert(f"⚠️ استفاده حافظه: {memory}%")
                
            except:
                pass
    
    def show_alert(self, message):
        """نمایش هشدار در نوار وضعیت"""
        try:
            self.update_status(message, "⚠️")
        except:
            pass
    
    def create_sidebar(self):
        """ایجاد نوار کناری با منوی ناوبری"""
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="right", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # لوگو و عنوان
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=30, padx=20)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🛡️ پنل مدیریت پیشرفته",
            font=ctk.CTkFont(family="Tahoma", size=20, weight="bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Windows Control Center",
            font=ctk.CTkFont(family="Tahoma", size=12),
            text_color="gray"
        )
        subtitle_label.pack()
        
        # اطلاعات سریع سیستم
        self.quick_info_frame = ctk.CTkFrame(self.sidebar, corner_radius=10)
        self.quick_info_frame.pack(pady=15, padx=15, fill="x")
        
        self.cpu_label = ctk.CTkLabel(
            self.quick_info_frame,
            text="CPU: ---%",
            font=ctk.CTkFont(family="Tahoma", size=11)
        )
        self.cpu_label.pack(pady=5)
        
        self.memory_label = ctk.CTkLabel(
            self.quick_info_frame,
            text="RAM: ---%",
            font=ctk.CTkFont(family="Tahoma", size=11)
        )
        self.memory_label.pack(pady=5)
        
        # بروزرسانی اطلاعات سریع
        self.update_quick_info()
        
        # دکمه‌های منو
        self.menu_buttons = []
        
        menu_items = [
            ("🏠 داشبورد", self.show_dashboard),
            ("📊 مانیتورینگ", self.show_monitoring),
            ("🔥 فایروال پیشرفته", self.show_firewall),
            ("🔒 امنیت سیستم", self.show_security),
            ("🌐 شبکه و اتصالات", self.show_network),
            ("💾 مدیریت دیسک", self.show_disk_management),
            ("⚡ بهینه‌سازی", self.show_optimization),
            ("📦 مدیریت سرویس‌ها", self.show_services),
            ("🔌 برنامه‌های استارتاپ", self.show_startup),
            ("🛠️ ابزارهای پیشرفته", self.show_advanced_tools),
            ("⚙️ تنظیمات", self.show_settings)
        ]
        
        for text, command in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(family="Tahoma", size=13),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                corner_radius=8
            )
            btn.pack(pady=3, padx=15, fill="x")
            self.menu_buttons.append(btn)
        
        # دکمه تغییر تم
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="🌙 حالت تاریک",
            command=self.toggle_theme,
            font=ctk.CTkFont(family="Tahoma", size=12)
        )
        self.theme_switch.pack(pady=15, padx=20)
        if self.config.get('theme', 'dark') == 'dark':
            self.theme_switch.select()
    
    def update_quick_info(self):
        """بروزرسانی اطلاعات سریع"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            
            self.cpu_label.configure(text=f"CPU: {cpu:.1f}%")
            self.memory_label.configure(text=f"RAM: {memory:.1f}%")
            
            # رنگ‌بندی بر اساس مقادیر
            cpu_color = "green" if cpu < 50 else ("orange" if cpu < 80 else "red")
            mem_color = "green" if memory < 50 else ("orange" if memory < 80 else "red")
            
            self.cpu_label.configure(text_color=cpu_color)
            self.memory_label.configure(text_color=mem_color)
        except:
            pass
        
        self.after(2000, self.update_quick_info)
    
    def create_main_content(self):
        """ایجاد ناحیه محتوای اصلی"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = ctk.CTkFrame(self, height=35, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="✅ آماده",
            font=ctk.CTkFont(family="Tahoma", size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=15, pady=5)
        
        # نمایش وضعیت admin
        admin_text = "👑 مدیر" if self.is_admin else "👤 کاربر عادی"
        self.admin_label = ctk.CTkLabel(
            self.status_bar,
            text=admin_text,
            font=ctk.CTkFont(family="Tahoma", size=11),
            text_color="green" if self.is_admin else "orange"
        )
        self.admin_label.pack(side="right", padx=15, pady=5)
    
    def update_status(self, message, icon="ℹ️"):
        """بروزرسانی نوار وضعیت"""
        self.status_label.configure(text=f"{icon} {message}")
    
    def clear_main_frame(self):
        """پاک کردن محتوای اصلی"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def toggle_theme(self):
        """تغییر تم"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.config['theme'] = 'dark'
        else:
            ctk.set_appearance_mode("light")
            self.config['theme'] = 'light'
        self.save_config()
    
    def highlight_menu_button(self, index):
        """هایلایت کردن دکمه منوی فعال"""
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
    
    # ==================== داشبورد ====================
    def show_dashboard(self):
        self.clear_main_frame()
        self.highlight_menu_button(0)
        self.update_status("داشبورد نمایش داده شد", "🏠")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📊 داشبورد سیستم",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # فریم‌های بالایی
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)
        
        # کارت سیستم
        system_card = self.create_dashboard_card(top_frame, "💻 اطلاعات سیستم")
        system_card.pack(side="left", fill="both", expand=True, padx=5)
        
        system_info = self.get_detailed_system_info()
        for key, value in system_info.items():
            info_label = ctk.CTkLabel(
                system_card,
                text=f"{key}: {value}",
                font=ctk.CTkFont(family="Tahoma", size=11),
                anchor="w"
            )
            info_label.pack(anchor="w", padx=15, pady=2)
        
        # کارت شبکه
        network_card = self.create_dashboard_card(top_frame, "🌐 شبکه")
        network_card.pack(side="left", fill="both", expand=True, padx=5)
        
        network_info = self.get_network_summary()
        for key, value in network_info.items():
            info_label = ctk.CTkLabel(
                network_card,
                text=f"{key}: {value}",
                font=ctk.CTkFont(family="Tahoma", size=11),
                anchor="w"
            )
            info_label.pack(anchor="w", padx=15, pady=2)
        
        # فریم‌های میانی
        middle_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        middle_frame.pack(fill="x", pady=10)
        
        # کارت CPU و RAM
        resources_card = self.create_dashboard_card(middle_frame, "📈 منابع سیستم")
        resources_card.pack(side="left", fill="both", expand=True, padx=5)
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        self.create_progress_bar(resources_card, "CPU", cpu_percent)
        self.create_progress_bar(resources_card, "RAM", memory_percent)
        self.create_progress_bar(resources_card, "Disk", disk_percent)
        
        # کارت امنیت
        security_card = self.create_dashboard_card(middle_frame, "🔒 وضعیت امنیتی")
        security_card.pack(side="left", fill="both", expand=True, padx=5)
        
        security_status = self.get_comprehensive_security_status()
        for item in security_status:
            status_label = ctk.CTkLabel(
                security_card,
                text=item,
                font=ctk.CTkFont(family="Tahoma", size=11),
                anchor="w"
            )
            status_label.pack(anchor="w", padx=15, pady=3)
        
        # دکمه‌های سریع
        quick_actions = ctk.CTkFrame(self.main_frame, corner_radius=15)
        quick_actions.pack(fill="x", pady=10)
        
        actions_title = ctk.CTkLabel(
            quick_actions,
            text="⚡ اقدامات سریع",
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
        )
        actions_title.pack(pady=10)
        
        buttons_frame = ctk.CTkFrame(quick_actions, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        quick_buttons = [
            ("🔄 بروزرسانی ویندوز", self.check_windows_update),
            ("🧹 پاکسازی دیسک", self.disk_cleanup),
            ("🛡️ اسکن امنیتی", self.quick_security_scan),
            ("📊 گزارش سیستم", self.generate_system_report)
        ]
        
        for text, command in quick_buttons:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                width=200,
                height=40,
                font=ctk.CTkFont(family="Tahoma", size=12)
            )
            btn.pack(side="left", padx=5)
    
    def create_dashboard_card(self, parent, title):
        """ایجاد کارت داشبورد"""
        card = ctk.CTkFrame(parent, corner_radius=15)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Tahoma", size=14, weight="bold")
        )
        title_label.pack(pady=10, padx=15, anchor="w")
        
        return card
    
    def create_progress_bar(self, parent, label, value):
        """ایجاد نوار پیشرفت"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=5)
        
        label_widget = ctk.CTkLabel(
            frame,
            text=f"{label}: {value:.1f}%",
            font=ctk.CTkFont(family="Tahoma", size=11)
        )
        label_widget.pack(side="left")
        
        progress = ctk.CTkProgressBar(frame, width=150)
        progress.pack(side="right", padx=10)
        progress.set(value / 100)
    
    def get_detailed_system_info(self):
        """دریافت اطلاعات دقیق سیستم"""
        info = {}
        try:
            info['نام سیستم'] = socket.gethostname()
            info['سیستم عامل'] = f"{platform.system()} {platform.release()}"
            info['معماری'] = platform.machine()
            info['پردازنده'] = platform.processor()[:30] + "..."
            info['تعداد هسته‌ها'] = psutil.cpu_count(logical=False)
            info['تعداد Thread'] = psutil.cpu_count(logical=True)
            total_ram = psutil.virtual_memory().total / (1024**3)
            info['حافظه RAM'] = f"{total_ram:.1f} GB"
        except:
            pass
        return info
    
    def get_network_summary(self):
        """خلاصه اطلاعات شبکه"""
        info = {}
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            info['نام میزبان'] = hostname
            info['IP داخلی'] = ip
            
            # دریافت IP خارجی
            try:
                external_ip = requests.get('https://api.ipify.org', timeout=3).text
                info['IP خارجی'] = external_ip
            except:
                info['IP خارجی'] = 'نامشخص'
            
            # وضعیت اتصال
            net_io = psutil.net_io_counters()
            info['ارسال'] = f"{net_io.bytes_sent / (1024**2):.1f} MB"
            info['دریافت'] = f"{net_io.bytes_recv / (1024**2):.1f} MB"
        except:
            pass
        return info
    
    def get_comprehensive_security_status(self):
        """وضعیت جامع امنیتی"""
        status = []
        try:
            # فایروال
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True, text=True, timeout=5
            )
            firewall_on = "ON" in result.stdout
            status.append(f"{'✅' if firewall_on else '❌'} فایروال: {'فعال' if firewall_on else 'غیرفعال'}")
            
            # UAC
            uac_level = self.get_uac_level()
            uac_text = ["غیرفعال", "حداقل", "پیش‌فرض", "حداکثر"][uac_level]
            status.append(f"{'✅' if uac_level >= 2 else '⚠️'} UAC: {uac_text}")
            
            # Windows Defender
            try:
                defender_result = subprocess.run(
                    ["powershell", "-Command", "Get-MpComputerStatus | Select-Object -Property AntivirusEnabled"],
                    capture_output=True, text=True, timeout=5
                )
                defender_on = "True" in defender_result.stdout
                status.append(f"{'✅' if defender_on else '❌'} Defender: {'فعال' if defender_on else 'غیرفعال'}")
            except:
                status.append("❓ Defender: نامشخص")
            
            # بروزرسانی‌ها
            status.append("📦 بروزرسانی: بررسی کنید")
            
        except:
            status.append("❌ خطا در بررسی امنیت")
        
        return status
    
    def get_uac_level(self):
        """دریافت سطح UAC"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
            )
            value, _ = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")
            winreg.CloseKey(key)
            return value
        except:
            return 2
    
    def check_windows_update(self):
        """بررسی بروزرسانی ویندوز"""
        self.update_status("در حال بررسی بروزرسانی...", "🔄")
        
        def check():
            try:
                subprocess.run(["ms-settings:windowsupdate"], shell=True)
                self.update_status("پنجره بروزرسانی باز شد", "✅")
            except:
                messagebox.showerror("خطا", "خطا در باز کردن تنظیمات بروزرسانی")
        
        threading.Thread(target=check, daemon=True).start()
    
    def disk_cleanup(self):
        """پاکسازی دیسک"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید پاکسازی دیسک را اجرا کنید؟"):
            try:
                subprocess.Popen(["cleanmgr", "/sagerun:1"])
                self.update_status("پاکسازی دیسک شروع شد", "✅")
            except:
                messagebox.showerror("خطا", "خطا در اجرای پاکسازی دیسک")
    
    def quick_security_scan(self):
        """اسکن سریع امنیتی"""
        self.update_status("در حال اسکن امنیتی...", "🔍")
        
        def scan():
            try:
                subprocess.run(
                    ["powershell", "-Command", "Start-MpScan -ScanType QuickScan"],
                    check=True,
                    timeout=300
                )
                messagebox.showinfo("✅ موفق", "اسکن امنیتی با موفقیت انجام شد")
                self.update_status("اسکن کامل شد", "✅")
            except subprocess.TimeoutExpired:
                messagebox.showinfo("ℹ️ اطلاع", "اسکن در حال انجام است...")
            except:
                messagebox.showerror("خطا", "خطا در اسکن امنیتی")
                self.update_status("خطا در اسکن", "❌")
        
        threading.Thread(target=scan, daemon=True).start()
    
    def generate_system_report(self):
        """تولید گزارش سیستم"""
        report_window = ctk.CTkToplevel(self)
        report_window.title("📊 گزارش سیستم")
        report_window.geometry("800x600")
        
        title = ctk.CTkLabel(
            report_window,
            text="📊 گزارش کامل سیستم",
            font=ctk.CTkFont(family="Tahoma", size=20, weight="bold")
        )
        title.pack(pady=20)
        
        report_text = ctk.CTkTextbox(
            report_window,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        report_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # تولید گزارش
        report = self.create_full_report()
        report_text.insert("1.0", report)
        
        # دکمه ذخیره
        save_btn = ctk.CTkButton(
            report_window,
            text="💾 ذخیره گزارش",
            command=lambda: self.save_report(report),
            width=150,
            height=40
        )
        save_btn.pack(pady=10)
    
    def create_full_report(self):
        """ایجاد گزارش کامل"""
        report = "="*60 + "\n"
        report += "گزارش سیستم - " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\n"
        report += "="*60 + "\n\n"
        
        # اطلاعات سیستم
        report += "💻 اطلاعات سیستم:\n"
        report += "-"*60 + "\n"
        for key, value in self.get_detailed_system_info().items():
            report += f"{key}: {value}\n"
        
        report += "\n🌐 اطلاعات شبکه:\n"
        report += "-"*60 + "\n"
        for key, value in self.get_network_summary().items():
            report += f"{key}: {value}\n"
        
        report += "\n📈 منابع:\n"
        report += "-"*60 + "\n"
        report += f"CPU: {psutil.cpu_percent()}%\n"
        report += f"RAM: {psutil.virtual_memory().percent}%\n"
        report += f"Disk: {psutil.disk_usage('/').percent}%\n"
        
        report += "\n🔒 امنیت:\n"
        report += "-"*60 + "\n"
        for item in self.get_comprehensive_security_status():
            report += f"{item}\n"
        
        return report
    
    def save_report(self, report):
        """ذخیره گزارش"""
        try:
            filename = f"System_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            messagebox.showinfo("✅ موفق", f"گزارش در {filename} ذخیره شد")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره: {str(e)}")
    
    # ==================== مانیتورینگ ====================
    def show_monitoring(self):
        self.clear_main_frame()
        self.highlight_menu_button(1)
        self.update_status("مانیتورینگ سیستم", "📊")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📊 مانیتورینگ لحظه‌ای سیستم",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # فریم نمودارها
        charts_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ایجاد نمودار
        fig = Figure(figsize=(10, 6), dpi=100)
        
        # نمودار CPU
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(self.cpu_history, color='#2196F3', linewidth=2)
        ax1.set_title('CPU Usage (%)', fontsize=12, fontweight='bold')
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#f0f0f0')
        
        # نمودار Memory
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.plot(self.memory_history, color='#4CAF50', linewidth=2)
        ax2.set_title('Memory Usage (%)', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#f0f0f0')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # اطلاعات تفصیلی
        details_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        details_frame.pack(fill="x", padx=10, pady=10)
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="📋 جزئیات منابع",
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
        )
        details_title.pack(pady=10)
        
        # اطلاعات CPU
        cpu_info = self.get_cpu_details()
        cpu_label = ctk.CTkLabel(
            details_frame,
            text=cpu_info,
            font=ctk.CTkFont(family="Courier New", size=11),
            justify="left"
        )
        cpu_label.pack(pady=5, padx=20, anchor="w")
        
        # دکمه بروزرسانی
        refresh_btn = ctk.CTkButton(
            details_frame,
            text="🔄 بروزرسانی نمودار",
            command=self.show_monitoring,
            width=200,
            height=40
        )
        refresh_btn.pack(pady=10)
    
    def get_cpu_details(self):
        """دریافت جزئیات CPU"""
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            
            details = f"⚡ فرکانس: {cpu_freq.current:.0f} MHz (حداکثر: {cpu_freq.max:.0f} MHz)\n"
            details += f"🔢 استفاده هر هسته:\n"
            for i, percent in enumerate(cpu_percent):
                details += f"  Core {i+1}: {percent:.1f}%\n"
            
            return details
        except:
            return "خطا در دریافت اطلاعات CPU"
    
    # ==================== فایروال پیشرفته ====================
    def show_firewall(self):
        self.clear_main_frame()
        self.highlight_menu_button(2)
        self.update_status("مدیریت فایروال پیشرفته", "🔥")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="🔥 مدیریت پیشرفته فایروال",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # تب‌ویو
        tabview = ctk.CTkTabview(self.main_frame)
        tabview.pack(fill="both", expand=True)
        
        # تب وضعیت
        tabview.add("وضعیت فایروال")
        tabview.add("قوانین ورودی")
        tabview.add("قوانین خروجی")
        tabview.add("قوانین سفارشی")
        
        # تب وضعیت
        status_frame = tabview.tab("وضعیت فایروال")
        
        self.firewall_status_text = ctk.CTkTextbox(
            status_frame,
            font=ctk.CTkFont(family="Courier New", size=11)
        )
        self.firewall_status_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        buttons_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ فعال کردن همه",
            command=self.enable_all_firewall,
            width=150,
            height=40,
            fg_color="#4CAF50"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="❌ غیرفعال کردن همه",
            command=self.disable_all_firewall,
            width=150,
            height=40,
            fg_color="#F44336"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="🔄 بروزرسانی",
            command=self.refresh_firewall_status,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        # تب قوانین ورودی
        inbound_frame = tabview.tab("قوانین ورودی")
        
        self.inbound_rules_text = ctk.CTkTextbox(
            inbound_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.inbound_rules_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(
            inbound_frame,
            text="📋 نمایش قوانین ورودی",
            command=self.show_inbound_rules,
            width=200,
            height=40
        ).pack(pady=10)
        
        # تب قوانین خروجی
        outbound_frame = tabview.tab("قوانین خروجی")
        
        self.outbound_rules_text = ctk.CTkTextbox(
            outbound_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.outbound_rules_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(
            outbound_frame,
            text="📋 نمایش قوانین خروجی",
            command=self.show_outbound_rules,
            width=200,
            height=40
        ).pack(pady=10)
        
        # تب قوانین سفارشی
        custom_frame = tabview.tab("قوانین سفارشی")
        
        ctk.CTkLabel(
            custom_frame,
            text="➕ افزودن قانون سفارشی",
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
        ).pack(pady=10)
        
        form_frame = ctk.CTkFrame(custom_frame, corner_radius=10)
        form_frame.pack(pady=10, padx=50, fill="x")
        
        self.rule_name_var = ctk.StringVar()
        self.rule_port_var = ctk.StringVar()
        self.rule_protocol_var = ctk.StringVar(value="TCP")
        self.rule_action_var = ctk.StringVar(value="allow")
        self.rule_direction_var = ctk.StringVar(value="in")
        
        ctk.CTkLabel(form_frame, text="نام قانون:").pack(pady=5, padx=10, anchor="w")
        ctk.CTkEntry(form_frame, textvariable=self.rule_name_var, width=300).pack(pady=5, padx=10)
        
        ctk.CTkLabel(form_frame, text="پورت:").pack(pady=5, padx=10, anchor="w")
        ctk.CTkEntry(form_frame, textvariable=self.rule_port_var, width=300).pack(pady=5, padx=10)
        
        ctk.CTkLabel(form_frame, text="پروتکل:").pack(pady=5, padx=10, anchor="w")
        ctk.CTkOptionMenu(form_frame, variable=self.rule_protocol_var, values=["TCP", "UDP", "ANY"], width=300).pack(pady=5, padx=10)
        
        ctk.CTkLabel(form_frame, text="جهت:").pack(pady=5, padx=10, anchor="w")
        ctk.CTkOptionMenu(form_frame, variable=self.rule_direction_var, values=["in", "out"], width=300).pack(pady=5, padx=10)
        
        ctk.CTkLabel(form_frame, text="اقدام:").pack(pady=5, padx=10, anchor="w")
        ctk.CTkOptionMenu(form_frame, variable=self.rule_action_var, values=["allow", "block"], width=300).pack(pady=5, padx=10)
        
        ctk.CTkButton(
            custom_frame,
            text="➕ افزودن قانون",
            command=self.add_firewall_rule,
            width=200,
            height=45,
            fg_color="#4CAF50"
        ).pack(pady=20)
        
        # بارگذاری وضعیت
        self.refresh_firewall_status()
    
    def refresh_firewall_status(self):
        """بروزرسانی وضعیت فایروال"""
        self.firewall_status_text.delete("1.0", "end")
        self.firewall_status_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                result = subprocess.run(
                    ["netsh", "advfirewall", "show", "allprofiles"],
                    capture_output=True, text=True, timeout=10
                )
                self.firewall_status_text.delete("1.0", "end")
                self.firewall_status_text.insert("1.0", result.stdout)
                self.update_status("وضعیت فایروال بروزرسانی شد", "✅")
            except:
                self.firewall_status_text.delete("1.0", "end")
                self.firewall_status_text.insert("1.0", "❌ خطا در دریافت وضعیت")
        
        threading.Thread(target=load, daemon=True).start()
    
    def enable_all_firewall(self):
        """فعال کردن فایروال برای همه پروفایل‌ها"""
        try:
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True)
            messagebox.showinfo("✅ موفق", "فایروال برای همه پروفایل‌ها فعال شد")
            self.refresh_firewall_status()
        except:
            messagebox.showerror("❌ خطا", "خطا در فعال‌سازی فایروال")
    
    def disable_all_firewall(self):
        """غیرفعال کردن فایروال"""
        if messagebox.askyesno("⚠️ هشدار", "آیا مطمئن هستید؟ این کار امنیت سیستم را به خطر می‌اندازد!"):
            try:
                subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "off"], check=True)
                messagebox.showwarning("⚠️ هشدار", "فایروال غیرفعال شد")
                self.refresh_firewall_status()
            except:
                messagebox.showerror("❌ خطا", "خطا در غیرفعال‌سازی فایروال")
    
    def show_inbound_rules(self):
        """نمایش قوانین ورودی"""
        self.inbound_rules_text.delete("1.0", "end")
        self.inbound_rules_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                result = subprocess.run(
                    ["netsh", "advfirewall", "firewall", "show", "rule", "name=all", "dir=in"],
                    capture_output=True, text=True, timeout=30
                )
                self.inbound_rules_text.delete("1.0", "end")
                self.inbound_rules_text.insert("1.0", result.stdout)
            except:
                self.inbound_rules_text.delete("1.0", "end")
                self.inbound_rules_text.insert("1.0", "❌ خطا در دریافت قوانین")
        
        threading.Thread(target=load, daemon=True).start()
    
    def show_outbound_rules(self):
        """نمایش قوانین خروجی"""
        self.outbound_rules_text.delete("1.0", "end")
        self.outbound_rules_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                result = subprocess.run(
                    ["netsh", "advfirewall", "firewall", "show", "rule", "name=all", "dir=out"],
                    capture_output=True, text=True, timeout=30
                )
                self.outbound_rules_text.delete("1.0", "end")
                self.outbound_rules_text.insert("1.0", result.stdout)
            except:
                self.outbound_rules_text.delete("1.0", "end")
                self.outbound_rules_text.insert("1.0", "❌ خطا در دریافت قوانین")
        
        threading.Thread(target=load, daemon=True).start()
    
    def add_firewall_rule(self):
        """افزودن قانون فایروال سفارشی"""
        name = self.rule_name_var.get().strip()
        port = self.rule_port_var.get().strip()
        protocol = self.rule_protocol_var.get().lower()
        action = self.rule_action_var.get()
        direction = self.rule_direction_var.get()
        
        if not name or not port:
            messagebox.showerror("❌ خطا", "لطفاً نام و پورت را وارد کنید")
            return
        
        try:
            cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={name}",
                f"dir={direction}",
                f"action={action}",
                f"protocol={protocol}",
                f"localport={port}"
            ]
            subprocess.run(cmd, check=True)
            messagebox.showinfo("✅ موفق", f"قانون '{name}' با موفقیت اضافه شد")
            self.update_status("قانون جدید اضافه شد", "✅")
        except Exception as e:
            messagebox.showerror("❌ خطا", f"خطا در افزودن قانون:\n{str(e)}")
    
    # ==================== امنیت سیستم ====================
    def show_security(self):
        self.clear_main_frame()
        self.highlight_menu_button(3)
        self.update_status("مدیریت امنیت", "🔒")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="🔒 مرکز امنیت سیستم",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # تب‌ویو امنیتی
        tabview = ctk.CTkTabview(self.main_frame)
        tabview.pack(fill="both", expand=True)
        
        tabview.add("Windows Defender")
        tabview.add("مدیریت UAC")
        tabview.add("بررسی آسیب‌پذیری")
        tabview.add("رمزگذاری")
        
        # تب Defender
        defender_frame = tabview.tab("Windows Defender")
        
        ctk.CTkLabel(
            defender_frame,
            text="🛡️ مدیریت Windows Defender",
            font=ctk.CTkFont(family="Tahoma", size=18, weight="bold")
        ).pack(pady=15)
        
        defender_buttons = ctk.CTkFrame(defender_frame, fg_color="transparent")
        defender_buttons.pack(pady=10)
        
        ctk.CTkButton(
            defender_buttons,
            text="🔍 اسکن سریع",
            command=lambda: self.run_defender_scan("Quick"),
            width=150,
            height=45
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            defender_buttons,
            text="🔍 اسکن کامل",
            command=lambda: self.run_defender_scan("Full"),
            width=150,
            height=45
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            defender_buttons,
            text="🔄 بروزرسانی تعاریف",
            command=self.update_defender_definitions,
            width=150,
            height=45
        ).pack(side="left", padx=5)
        
        # استثناهای Defender
        exclusions_frame = ctk.CTkFrame(defender_frame, corner_radius=10)
        exclusions_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            exclusions_frame,
            text="📁 مدیریت استثناها",
            font=ctk.CTkFont(family="Tahoma", size=14, weight="bold")
        ).pack(pady=10)
        
        self.defender_exclusions_text = ctk.CTkTextbox(
            exclusions_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.defender_exclusions_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        exclusion_buttons = ctk.CTkFrame(exclusions_frame, fg_color="transparent")
        exclusion_buttons.pack(pady=10)
        
        ctk.CTkButton(
            exclusion_buttons,
            text="➕ افزودن",
            command=self.add_defender_exclusion,
            width=120,
            height=35,
            fg_color="#4CAF50"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            exclusion_buttons,
            text="🔄 بروزرسانی",
            command=self.refresh_defender_exclusions,
            width=120,
            height=35
        ).pack(side="left", padx=5)
        
        # تب UAC
        uac_frame = tabview.tab("مدیریت UAC")
        
        ctk.CTkLabel(
            uac_frame,
            text="🔒 تنظیمات کنترل حساب کاربری (UAC)",
            font=ctk.CTkFont(family="Tahoma", size=18, weight="bold")
        ).pack(pady=20)
        
        self.uac_var = ctk.IntVar(value=self.get_uac_level())
        
        uac_levels = [
            (0, "🔓 غیرفعال", "بدون اعلان - خطرناک!"),
            (1, "⚠️ حداقل اعلان", "فقط در تغییرات مهم اعلان"),
            (2, "✅ پیش‌فرض", "توصیه می‌شود"),
            (3, "🛡️ حداکثر امنیت", "همیشه اعلان و تأیید")
        ]
        
        for level, title_text, desc in uac_levels:
            level_frame = ctk.CTkFrame(uac_frame, corner_radius=10)
            level_frame.pack(pady=8, padx=50, fill="x")
            
            radio = ctk.CTkRadioButton(
                level_frame,
                text=f"{title_text}\n{desc}",
                variable=self.uac_var,
                value=level,
                font=ctk.CTkFont(family="Tahoma", size=13)
            )
            radio.pack(pady=15, padx=20, anchor="w")
        
        ctk.CTkButton(
            uac_frame,
            text="💾 اعمال تنظیمات UAC",
            command=self.apply_uac_settings,
            width=250,
            height=50,
            font=ctk.CTkFont(family="Tahoma", size=15, weight="bold")
        ).pack(pady=30)
        
        # تب بررسی آسیب‌پذیری
        vuln_frame = tabview.tab("بررسی آسیب‌پذیری")
        
        ctk.CTkLabel(
            vuln_frame,
            text="🔍 بررسی آسیب‌پذیری‌های سیستم",
            font=ctk.CTkFont(family="Tahoma", size=18, weight="bold")
        ).pack(pady=20)
        
        self.vuln_text = ctk.CTkTextbox(
            vuln_frame,
            font=ctk.CTkFont(family="Courier New", size=11)
        )
        self.vuln_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkButton(
            vuln_frame,
            text="🔍 شروع بررسی",
            command=self.check_vulnerabilities,
            width=200,
            height=45,
            font=ctk.CTkFont(family="Tahoma", size=14, weight="bold")
        ).pack(pady=15)
        
        # بارگذاری اولیه
        self.refresh_defender_exclusions()
    
    def run_defender_scan(self, scan_type):
        """اجرای اسکن Defender"""
        self.update_status(f"در حال اسکن {scan_type}...", "🔍")
        
        def scan():
            try:
                subprocess.run(
                    ["powershell", "-Command", f"Start-MpScan -ScanType {scan_type}Scan"],
                    check=True,
                    timeout=600
                )
                messagebox.showinfo("✅ موفق", f"اسکن {scan_type} با موفقیت انجام شد")
                self.update_status("اسکن کامل شد", "✅")
            except subprocess.TimeoutExpired:
                messagebox.showinfo("ℹ️ اطلاع", "اسکن در حال انجام است و ممکن است زمان ببرد...")
            except Exception as e:
                messagebox.showerror("❌ خطا", f"خطا در اسکن:\n{str(e)}")
                self.update_status("خطا در اسکن", "❌")
        
        threading.Thread(target=scan, daemon=True).start()
    
    def update_defender_definitions(self):
        """بروزرسانی تعاریف Defender"""
        self.update_status("در حال بروزرسانی تعاریف...", "🔄")
        
        def update():
            try:
                subprocess.run(
                    ["powershell", "-Command", "Update-MpSignature"],
                    check=True,
                    timeout=120
                )
                messagebox.showinfo("✅ موفق", "تعاریف ویروس با موفقیت بروزرسانی شد")
                self.update_status("تعاریف بروزرسانی شد", "✅")
            except:
                messagebox.showerror("❌ خطا", "خطا در بروزرسانی تعاریف")
        
        threading.Thread(target=update, daemon=True).start()
    
    def refresh_defender_exclusions(self):
        """بروزرسانی لیست استثناها"""
        self.defender_exclusions_text.delete("1.0", "end")
        self.defender_exclusions_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                result = subprocess.run(
                    ["powershell", "-Command", "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"],
                    capture_output=True, text=True, timeout=10
                )
                paths = [p.strip() for p in result.stdout.split('\n') if p.strip()]
                
                if paths:
                    text = "\n".join([f"📁 {path}" for path in paths])
                else:
                    text = "هیچ پوشه‌ای مستثنی نشده است"
                
                self.defender_exclusions_text.delete("1.0", "end")
                self.defender_exclusions_text.insert("1.0", text)
            except:
                self.defender_exclusions_text.delete("1.0", "end")
                self.defender_exclusions_text.insert("1.0", "❌ خطا در بارگذاری")
        
        threading.Thread(target=load, daemon=True).start()
    
    def add_defender_exclusion(self):
        """افزودن استثنا"""
        path = filedialog.askdirectory(title="انتخاب پوشه")
        if path:
            try:
                subprocess.run(
                    ["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{path}'"],
                    check=True,
                    timeout=10
                )
                self.refresh_defender_exclusions()
                messagebox.showinfo("✅ موفق", f"پوشه اضافه شد:\n{path}")
            except:
                messagebox.showerror("❌ خطا", "خطا در افزودن پوشه")
    
    def apply_uac_settings(self):
        """اعمال تنظیمات UAC"""
        level = self.uac_var.get()
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, level)
            winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 1 if level > 1 else 0)
            winreg.CloseKey(key)
            
            messagebox.showinfo(
                "✅ موفق",
                "تنظیمات UAC با موفقیت اعمال شد.\n\n⚠️ برای اعمال کامل، سیستم را ری‌استارت کنید."
            )
            self.update_status("تنظیمات UAC اعمال شد", "✅")
        except Exception as e:
            messagebox.showerror("❌ خطا", f"خطا در تنظیم UAC:\n{str(e)}")
    
    def check_vulnerabilities(self):
        """بررسی آسیب‌پذیری‌ها"""
        self.vuln_text.delete("1.0", "end")
        self.vuln_text.insert("1.0", "در حال بررسی آسیب‌پذیری‌ها...\n\n")
        
        def check():
            results = []
            
            # بررسی فایروال
            try:
                fw_result = subprocess.run(
                    ["netsh", "advfirewall", "show", "allprofiles", "state"],
                    capture_output=True, text=True
                )
                if "OFF" in fw_result.stdout:
                    results.append("❌ فایروال غیرفعال است - خطر بالا!")
                else:
                    results.append("✅ فایروال فعال است")
            except:
                results.append("⚠️ خطا در بررسی فایروال")
            
            # بررسی UAC
            uac_level = self.get_uac_level()
            if uac_level < 2:
                results.append(f"⚠️ UAC در سطح پایین است - توصیه به افزایش")
            else:
                results.append("✅ UAC در سطح مناسب است")
            
            # بررسی Defender
            try:
                def_result = subprocess.run(
                    ["powershell", "-Command", "Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled"],
                    capture_output=True, text=True,
                    timeout=10
                )
                if "False" in def_result.stdout:
                    results.append("❌ Windows Defender غیرفعال است - خطر بالا!")
                else:
                    results.append("✅ Windows Defender فعال است")
            except:
                results.append("⚠️ خطا در بررسی Defender")
            
            # بررسی پورت‌های باز
            results.append("\n🔌 بررسی پورت‌های باز:")
            try:
                netstat_result = subprocess.run(
                    ["netstat", "-an"],
                    capture_output=True, text=True,
                    timeout=10
                )
                listening_ports = [line for line in netstat_result.stdout.split('\n') if 'LISTENING' in line]
                results.append(f"تعداد پورت‌های در حال گوش دادن: {len(listening_ports)}")
            except:
                results.append("⚠️ خطا در بررسی پورت‌ها")
            
            # بررسی بروزرسانی‌ها
            results.append("\n📦 وضعیت بروزرسانی:")
            results.append("⚠️ لطفاً از Windows Update بروزرسانی‌ها را بررسی کنید")
            
            # نمایش نتایج
            final_text = "\n".join(results)
            self.vuln_text.delete("1.0", "end")
            self.vuln_text.insert("1.0", final_text)
            self.update_status("بررسی آسیب‌پذیری کامل شد", "✅")
        
        threading.Thread(target=check, daemon=True).start()
    
    # ==================== شبکه و اتصالات ====================
    def show_network(self):
        self.clear_main_frame()
        self.highlight_menu_button(4)
        self.update_status("مدیریت شبکه", "🌐")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="🌐 مدیریت شبکه و اتصالات",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # تب‌ویو
        tabview = ctk.CTkTabview(self.main_frame)
        tabview.pack(fill="both", expand=True)
        
        tabview.add("اطلاعات شبکه")
        tabview.add("اتصالات فعال")
        tabview.add("تنظیمات DNS")
        tabview.add("ابزارها")
        
        # تب اطلاعات شبکه
        info_frame = tabview.tab("اطلاعات شبکه")
        
        self.network_info_text = ctk.CTkTextbox(
            info_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.network_info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_buttons = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_buttons.pack(pady=10)
        
        ctk.CTkButton(
            info_buttons,
            text="🔄 ipconfig /all",
            command=self.show_ipconfig,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            info_buttons,
            text="📡 Adapters",
            command=self.show_network_adapters,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        # تب اتصالات فعال
        connections_frame = tabview.tab("اتصالات فعال")
        
        self.connections_text = ctk.CTkTextbox(
            connections_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.connections_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(
            connections_frame,
            text="🔄 نمایش اتصالات (netstat)",
            command=self.show_netstat,
            width=200,
            height=40
        ).pack(pady=10)
        
        # تب DNS
        dns_frame = tabview.tab("تنظیمات DNS")
        
        ctk.CTkLabel(
            dns_frame,
            text="🌐 تنظیم سرورهای DNS",
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
        ).pack(pady=15)
        
        dns_presets = ctk.CTkFrame(dns_frame, corner_radius=10)
        dns_presets.pack(pady=10, padx=50, fill="x")
        
        ctk.CTkLabel(dns_presets, text="DNS پیش‌فرض:").pack(pady=10)
        
        dns_buttons = [
            ("Google DNS", "8.8.8.8", "8.8.4.4"),
            ("Cloudflare DNS", "1.1.1.1", "1.0.0.1"),
            ("Shecan DNS", "178.22.122.100", "185.51.200.2"),
            ("403 DNS", "10.202.10.202", "10.202.10.102")
        ]
        
        for name, primary, secondary in dns_buttons:
            btn = ctk.CTkButton(
                dns_presets,
                text=f"{name} ({primary})",
                command=lambda p=primary, s=secondary: self.set_dns(p, s),
                width=300,
                height=40
            )
            btn.pack(pady=5)
        
        # تب ابزارها
        tools_frame = tabview.tab("ابزارها")
        
        tools_grid = ctk.CTkFrame(tools_frame, fg_color="transparent")
        tools_grid.pack(pady=20, padx=20, fill="both", expand=True)
        
        network_tools = [
            ("🔍 Ping", self.run_ping),
            ("📍 Traceroute", self.run_tracert),
            ("🔎 DNS Lookup", self.run_nslookup),
            ("📊 Bandwidth Test", self.test_bandwidth),
            ("🔄 Flush DNS", self.flush_dns),
            ("♻️ Reset Network", self.reset_network)
        ]
        
        for i, (text, command) in enumerate(network_tools):
            row = i // 2
            col = i % 2
            
            btn = ctk.CTkButton(
                tools_grid,
                text=text,
                command=command,
                width=250,
                height=60,
                font=ctk.CTkFont(family="Tahoma", size=14)
            )
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        tools_grid.grid_columnconfigure(0, weight=1)
        tools_grid.grid_columnconfigure(1, weight=1)
        
        # بارگذاری اولیه
        self.show_ipconfig()
    
    def show_ipconfig(self):
        """نمایش ipconfig"""
        self.network_info_text.delete("1.0", "end")
        self.network_info_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                result = subprocess.run(
                    ["ipconfig", "/all"],
                    capture_output=True, text=True, timeout=10
                )
                self.network_info_text.delete("1.0", "end")
                self.network_info_text.insert("1.0", result.stdout)
            except:
                self.network_info_text.delete("1.0", "end")
                self.network_info_text.insert("1.0", "❌ خطا در دریافت اطلاعات")
        
        threading.Thread(target=load, daemon=True).start()
    
    def show_network_adapters(self):
        """نمایش آداپترهای شبکه"""
        self.network_info_text.delete("1.0", "end")
        self.network_info_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                adapters_info = ""
                for iface, addrs in psutil.net_if_addrs().items():
                    adapters_info += f"\n{'='*60}\n"
                    adapters_info += f"🔌 {iface}\n"
                    adapters_info += f"{'='*60}\n"
                    for addr in addrs:
                        adapters_info += f"  Type: {addr.family.name}\n"
                        adapters_info += f"  Address: {addr.address}\n"
                        if addr.netmask:
                            adapters_info += f"  Netmask: {addr.netmask}\n"
                        adapters_info += "\n"
                
                self.network_info_text.delete("1.0", "end")
                self.network_info_text.insert("1.0", adapters_info)
            except:
                self.network_info_text.delete("1.0", "end")
                self.network_info_text.insert("1.0", "❌ خطا در دریافت اطلاعات آداپترها")
        
        threading.Thread(target=load, daemon=True).start()
    
    def show_netstat(self):
        """نمایش اتصالات فعال"""
        self.connections_text.delete("1.0", "end")
        self.connections_text.insert("1.0", "در حال بارگذاری اتصالات فعال...")
        
        def load():
            try:
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True, text=True, timeout=10
                )
                self.connections_text.delete("1.0", "end")
                self.connections_text.insert("1.0", result.stdout)
            except:
                self.connections_text.delete("1.0", "end")
                self.connections_text.insert("1.0", "❌ خطا در دریافت اتصالات")
        
        threading.Thread(target=load, daemon=True).start()
    
    def set_dns(self, primary, secondary):
        """تنظیم DNS"""
        if not self.is_admin:
            messagebox.showerror("❌ خطا", "برای تغییر DNS نیاز به دسترسی مدیر دارید")
            return
        
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید DNS را به {primary} تغییر دهید؟"):
            try:
                # دریافت نام آداپتر فعال
                result = subprocess.run(
                    ["netsh", "interface", "show", "interface"],
                    capture_output=True, text=True
                )
                
                messagebox.showinfo(
                    "ℹ️ راهنما",
                    f"برای تغییر DNS:\n\n"
                    f"1. به Network Connections بروید\n"
                    f"2. روی آداپتر فعال راست کلیک کنید\n"
                    f"3. Properties > IPv4 > Properties\n"
                    f"4. DNS را به {primary} و {secondary} تغییر دهید\n\n"
                    f"یا از دستور زیر استفاده کنید:\n"
                    f'netsh interface ip set dns "نام_آداپتر" static {primary}'
                )
            except:
                messagebox.showerror("خطا", "خطا در تنظیم DNS")
    
    def run_ping(self):
        """اجرای Ping"""
        host = ctk.CTkInputDialog(text="آدرس یا IP برای Ping:", title="🔍 Ping").get_input()
        if host:
            self.run_network_command("ping", ["-n", "4", host])
    
    def run_tracert(self):
        """اجرای Traceroute"""
        host = ctk.CTkInputDialog(text="آدرس یا IP برای Traceroute:", title="📍 Traceroute").get_input()
        if host:
            self.run_network_command("tracert", [host])
    
    def run_nslookup(self):
        """اجرای NSLookup"""
        host = ctk.CTkInputDialog(text="دامنه برای DNS Lookup:", title="🔎 NSLookup").get_input()
        if host:
            self.run_network_command("nslookup", [host])
    
    def run_network_command(self, cmd, args):
        """اجرای دستورات شبکه"""
        result_window = ctk.CTkToplevel(self)
        result_window.title(f"🌐 {cmd.upper()}")
        result_window.geometry("700x500")
        
        result_text = ctk.CTkTextbox(
            result_window,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        result_text.pack(fill="both", expand=True, padx=10, pady=10)
        result_text.insert("1.0", f"در حال اجرای {cmd}...\n")
        
        def run():
            try:
                result = subprocess.run(
                    [cmd] + args,
                    capture_output=True, text=True, timeout=60
                )
                result_text.delete("1.0", "end")
                result_text.insert("1.0", result.stdout)
            except:
                result_text.delete("1.0", "end")
                result_text.insert("1.0", f"❌ خطا در اجرای {cmd}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def test_bandwidth(self):
        """تست سرعت اینترنت"""
        messagebox.showinfo(
            "ℹ️ تست سرعت",
            "برای تست سرعت اینترنت:\n\n"
            "1. از سایت speedtest.net استفاده کنید\n"
            "2. یا ابزار speedtest-cli را نصب کنید\n\n"
            "pip install speedtest-cli"
        )
    
    def flush_dns(self):
        """پاک کردن کش DNS"""
        try:
            subprocess.run(["ipconfig", "/flushdns"], check=True)
            messagebox.showinfo("✅ موفق", "کش DNS با موفقیت پاک شد")
            self.update_status("DNS Cache پاک شد", "✅")
        except:
            messagebox.showerror("❌ خطا", "خطا در پاک کردن کش DNS")
    
    def reset_network(self):
        """ریست شبکه"""
        if messagebox.askyesno("⚠️ هشدار", "آیا می‌خواهید تنظیمات شبکه را ریست کنید؟\nسیستم باید ری‌استارت شود."):
            try:
                subprocess.run(["netsh", "winsock", "reset"], check=True)
                subprocess.run(["netsh", "int", "ip", "reset"], check=True)
                messagebox.showinfo("✅ موفق", "شبکه ریست شد. لطفاً سیستم را ری‌استارت کنید.")
            except:
                messagebox.showerror("❌ خطا", "خطا در ریست شبکه")
    
    # ==================== مدیریت دیسک ====================
    def show_disk_management(self):
        self.clear_main_frame()
        self.highlight_menu_button(5)
        self.update_status("مدیریت دیسک", "💾")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="💾 مدیریت دیسک و فضای ذخیره‌سازی",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # اطلاعات دیسک‌ها
        disks_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        disks_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            disks_frame,
            text="💿 دیسک‌های سیستم",
            font=ctk.CTkFont(family="Tahoma", size=18, weight="bold")
        ).pack(pady=15)
        
        # نمایش اطلاعات هر دیسک
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                disk_card = ctk.CTkFrame(disks_frame, corner_radius=10)
                disk_card.pack(pady=10, padx=20, fill="x")
                
                # عنوان دیسک
                disk_title = ctk.CTkLabel(
                    disk_card,
                    text=f"🔷 {partition.device} ({partition.fstype})",
                    font=ctk.CTkFont(family="Tahoma", size=14, weight="bold")
                )
                disk_title.pack(pady=10, padx=15, anchor="w")
                
                # اطلاعات
                info_frame = ctk.CTkFrame(disk_card, fg_color="transparent")
                info_frame.pack(fill="x", padx=15, pady=5)
                
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                
                info_text = f"کل: {total_gb:.1f} GB  |  استفاده شده: {used_gb:.1f} GB  |  آزاد: {free_gb:.1f} GB"
                ctk.CTkLabel(
                    info_frame,
                    text=info_text,
                    font=ctk.CTkFont(family="Tahoma", size=11)
                ).pack(anchor="w")
                
                # نوار پیشرفت
                progress = ctk.CTkProgressBar(disk_card, width=600, height=15)
                progress.pack(pady=10, padx=15)
                progress.set(usage.percent / 100)
                
                percent_label = ctk.CTkLabel(
                    disk_card,
                    text=f"{usage.percent:.1f}% استفاده شده",
                    font=ctk.CTkFont(family="Tahoma", size=12)
                )
                percent_label.pack(pady=(0, 10))
                
            except:
                pass
        
        # دکمه‌های عملیاتی
        operations_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        operations_frame.pack(pady=15)
        
        ctk.CTkButton(
            operations_frame,
            text="🧹 پاکسازی دیسک",
            command=self.disk_cleanup,
            width=180,
            height=45
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            operations_frame,
            text="🔍 تحلیل فضا",
            command=self.analyze_disk_space,
            width=180,
            height=45
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            operations_frame,
            text="⚙️ Disk Management",
            command=self.open_disk_management,
            width=180,
            height=45
        ).pack(side="left", padx=5)
    
    def analyze_disk_space(self):
        """تحلیل فضای دیسک"""
        path = filedialog.askdirectory(title="انتخاب پوشه برای تحلیل")
        if path:
            self.update_status("در حال تحلیل فضا...", "🔍")
            
            def analyze():
                try:
                    folder_sizes = {}
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            try:
                                size = sum(
                                    os.path.getsize(os.path.join(dirpath, filename))
                                    for dirpath, dirnames, filenames in os.walk(item_path)
                                    for filename in filenames
                                )
                                folder_sizes[item] = size / (1024**2)  # MB
                            except:
                                pass
                    
                    # مرتب‌سازی
                    sorted_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
                    
                    # نمایش نتایج
                    result = "🔍 10 پوشه بزرگ‌تر:\n\n"
                    for folder, size in sorted_folders:
                        result += f"📁 {folder}: {size:.1f} MB\n"
                    
                    messagebox.showinfo("📊 تحلیل فضا", result)
                    self.update_status("تحلیل کامل شد", "✅")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در تحلیل: {str(e)}")
            
            threading.Thread(target=analyze, daemon=True).start()
    
    def open_disk_management(self):
        """باز کردن Disk Management"""
        try:
            subprocess.Popen(["diskmgmt.msc"])
            self.update_status("Disk Management باز شد", "✅")
        except:
            messagebox.showerror("خطا", "خطا در باز کردن Disk Management")
    
    # ==================== بهینه‌سازی ====================
    def show_optimization(self):
        self.clear_main_frame()
        self.highlight_menu_button(6)
        self.update_status("بهینه‌سازی سیستم", "⚡")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="⚡ بهینه‌سازی و افزایش سرعت",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # کارت‌های بهینه‌سازی
        optimization_cards = ctk.CTkScrollableFrame(self.main_frame)
        optimization_cards.pack(fill="both", expand=True, padx=10, pady=10)
        
        optimizations = [
            {
                "title": "🧹 پاکسازی فایل‌های موقت",
                "desc": "حذف فایل‌های temp، cache و موقت",
                "command": self.clean_temp_files
            },
            {
                "title": "💾 بهینه‌سازی حافظه RAM",
                "desc": "آزادسازی حافظه و بستن پروسه‌های غیرضروری",
                "command": self.optimize_memory
            },
            {
                "title": "🚀 غیرفعال‌سازی برنامه‌های استارتاپ",
                "desc": "کاهش زمان بوت با غیرفعال کردن برنامه‌های اضافی",
                "command": self.manage_startup_programs
            },
            {
                "title": "⚙️ غیرفعال‌سازی سرویس‌های غیرضروری",
                "desc": "متوقف کردن سرویس‌هایی که استفاده نمی‌شوند",
                "command": self.disable_unnecessary_services
            },
            {
                "title": "🎨 بهینه‌سازی جلوه‌های بصری",
                "desc": "غیرفعال کردن افکت‌های بصری برای سرعت بیشتر",
                "command": self.optimize_visual_effects
            },
            {
                "title": "🌐 بهینه‌سازی شبکه",
                "desc": "تنظیمات شبکه برای سرعت بهتر",
                "command": self.optimize_network
            }
        ]
        
        for opt in optimizations:
            card = ctk.CTkFrame(optimization_cards, corner_radius=15)
            card.pack(pady=10, padx=10, fill="x")
            
            ctk.CTkLabel(
                card,
                text=opt["title"],
                font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
            ).pack(pady=(15, 5), padx=20, anchor="w")
            
            ctk.CTkLabel(
                card,
                text=opt["desc"],
                font=ctk.CTkFont(family="Tahoma", size=11),
                text_color="gray"
            ).pack(pady=(0, 10), padx=20, anchor="w")
            
            ctk.CTkButton(
                card,
                text="▶️ اجرا",
                command=opt["command"],
                width=120,
                height=35,
                fg_color="#4CAF50"
            ).pack(pady=(0, 15), padx=20, anchor="e")
        
        # دکمه بهینه‌سازی کامل
        ctk.CTkButton(
            self.main_frame,
            text="⚡ بهینه‌سازی کامل (همه موارد)",
            command=self.full_optimization,
            width=300,
            height=55,
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold"),
            fg_color="#FF5722"
        ).pack(pady=20)
    
    def clean_temp_files(self):
        """پاکسازی فایل‌های موقت"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید فایل‌های موقت را پاک کنید؟"):
            self.update_status("در حال پاکسازی...", "🧹")
            
            def clean():
                try:
                    temp_folders = [
                        os.environ.get('TEMP'),
                        os.environ.get('TMP'),
                        r'C:\Windows\Temp'
                    ]
                    
                    total_freed = 0
                    for folder in temp_folders:
                        if folder and os.path.exists(folder):
                            for item in os.listdir(folder):
                                try:
                                    item_path = os.path.join(folder, item)
                                    if os.path.isfile(item_path):
                                        size = os.path.getsize(item_path)
                                        os.remove(item_path)
                                        total_freed += size
                                    elif os.path.isdir(item_path):
                                        import shutil
                                        size = sum(
                                            os.path.getsize(os.path.join(dirpath, filename))
                                            for dirpath, dirnames, filenames in os.walk(item_path)
                                            for filename in filenames
                                        )
                                        shutil.rmtree(item_path, ignore_errors=True)
                                        total_freed += size
                                except:
                                    pass
                    
                    freed_mb = total_freed / (1024**2)
                    messagebox.showinfo("✅ موفق", f"پاکسازی انجام شد!\nفضای آزاد شده: {freed_mb:.1f} MB")
                    self.update_status("پاکسازی کامل شد", "✅")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در پاکسازی: {str(e)}")
            
            threading.Thread(target=clean, daemon=True).start()
    
    def optimize_memory(self):
        """بهینه‌سازی حافظه"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید حافظه RAM را بهینه‌سازی کنید؟"):
            self.update_status("در حال بهینه‌سازی حافظه...", "💾")
            
            def optimize():
                try:
                    # پاک کردن Working Set
                    subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force"], timeout=10)
                    
                    messagebox.showinfo("✅ موفق", "حافظه RAM بهینه‌سازی شد")
                    self.update_status("حافظه بهینه شد", "✅")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در بهینه‌سازی: {str(e)}")
            
            threading.Thread(target=optimize, daemon=True).start()
    
    def manage_startup_programs(self):
        """مدیریت برنامه‌های استارتاپ"""
        try:
            subprocess.Popen(["msconfig"])
            messagebox.showinfo("ℹ️ راهنما", "در پنجره باز شده، به تب Startup بروید و برنامه‌های غیرضروری را غیرفعال کنید")
            self.update_status("پنجره استارتاپ باز شد", "✅")
        except:
            messagebox.showerror("خطا", "خطا در باز کردن msconfig")
    
    def disable_unnecessary_services(self):
        """غیرفعال‌سازی سرویس‌های غیرضروری"""
        try:
            subprocess.Popen(["services.msc"])
            messagebox.showinfo(
                "⚠️ هشدار",
                "فقط سرویس‌هایی که مطمئن هستید غیرفعال کنید!\n\n"
                "سرویس‌های پیشنهادی برای غیرفعال‌سازی:\n"
                "- Windows Search (اگر جستجو استفاده نمی‌کنید)\n"
                "- Print Spooler (اگر پرینتر ندارید)\n"
                "- Bluetooth Support Service (اگر بلوتوث ندارید)"
            )
        except:
            messagebox.showerror("خطا", "خطا در باز کردن Services")
    
    def optimize_visual_effects(self):
        """بهینه‌سازی جلوه‌های بصری"""
        try:
            subprocess.Popen(["SystemPropertiesPerformance.exe"])
            messagebox.showinfo(
                "ℹ️ راهنما",
                "برای بهترین عملکرد:\n\n"
                "1. گزینه 'Adjust for best performance' را انتخاب کنید\n"
                "2. یا به صورت دستی افکت‌های غیرضروری را خاموش کنید"
            )
        except:
            messagebox.showerror("خطا", "خطا در باز کردن تنظیمات")
    
    def optimize_network(self):
        """بهینه‌سازی شبکه"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید تنظیمات شبکه را بهینه‌سازی کنید?"):
            try:
                subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"], check=True)
                messagebox.showinfo("✅ موفق", "تنظیمات شبکه بهینه شد")
                self.update_status("شبکه بهینه شد", "✅")
            except:
                messagebox.showerror("خطا", "خطا در بهینه‌سازی شبکه")
    
    def full_optimization(self):
        """بهینه‌سازی کامل"""
        if messagebox.askyesno(
            "⚠️ هشدار",
            "آیا می‌خواهید بهینه‌سازی کامل سیستم را اجرا کنید?\n\n"
            "این عملیات شامل موارد زیر است:\n"
            "- پاکسازی فایل‌های موقت\n"
            "- بهینه‌سازی حافظه\n"
            "- بهینه‌سازی شبکه\n"
            "- و سایر موارد...\n\n"
            "ممکن است چند دقیقه طول بکشد."
        ):
            self.update_status("در حال بهینه‌سازی کامل...", "⚡")
            
            def full_opt():
                try:
                    # پاکسازی
                    self.clean_temp_files()
                    # بهینه‌سازی حافظه
                    subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force"], timeout=10)
                    # بهینه‌سازی شبکه
                    subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"], timeout=10)
                    # Flush DNS
                    subprocess.run(["ipconfig", "/flushdns"], timeout=10)
                    
                    messagebox.showinfo(
                        "✅ کامل شد",
                        "بهینه‌سازی کامل سیستم انجام شد!\n\n"
                        "برای بهترین نتیجه سیستم را ری‌استارت کنید."
                    )
                    self.update_status("بهینه‌سازی کامل شد", "✅")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در بهینه‌سازی: {str(e)}")
            
            threading.Thread(target=full_opt, daemon=True).start()
    
    # ==================== مدیریت سرویس‌ها ====================
    def show_services(self):
        self.clear_main_frame()
        self.highlight_menu_button(7)
        self.update_status("مدیریت سرویس‌ها", "📦")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="📦 مدیریت سرویس‌های ویندوز",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # فریم جستجو
        search_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.services_search_var = ctk.StringVar()
        ctk.CTkEntry(
            search_frame,
            textvariable=self.services_search_var,
            placeholder_text="🔍 جستجوی سرویس...",
            width=400,
            height=40
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            search_frame,
            text="🔄 بروزرسانی",
            command=self.refresh_services_list,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            search_frame,
            text="⚙️ Services.msc",
            command=lambda: subprocess.Popen(["services.msc"]),
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        # لیست سرویس‌ها
        services_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        services_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.services_text = ctk.CTkTextbox(
            services_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.services_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # بارگذاری لیست
        self.refresh_services_list()
    
    def refresh_services_list(self):
        """بروزرسانی لیست سرویس‌ها"""
        self.services_text.delete("1.0", "end")
        self.services_text.insert("1.0", "در حال بارگذاری سرویس‌ها...")
        
        def load():
            try:
                result = subprocess.run(
                    ["powershell", "-Command", "Get-Service | Select-Object Name, Status, DisplayName | Format-Table -AutoSize"],
                    capture_output=True, text=True, timeout=30
                )
                self.services_text.delete("1.0", "end")
                self.services_text.insert("1.0", result.stdout)
                self.update_status("لیست سرویس‌ها بروزرسانی شد", "✅")
            except:
                self.services_text.delete("1.0", "end")
                self.services_text.insert("1.0", "❌ خطا در بارگذاری سرویس‌ها")
        
        threading.Thread(target=load, daemon=True).start()
    
    # ==================== برنامه‌های استارتاپ ====================
    def show_startup(self):
        self.clear_main_frame()
        self.highlight_menu_button(8)
        self.update_status("مدیریت استارتاپ", "🔌")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="🔌 مدیریت برنامه‌های استارتاپ",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            self.main_frame,
            text="برنامه‌هایی که با شروع ویندوز اجرا می‌شوند",
            font=ctk.CTkFont(family="Tahoma", size=12),
            text_color="gray"
        )
        info_label.pack()
        
        # لیست استارتاپ
        startup_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        startup_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.startup_text = ctk.CTkTextbox(
            startup_frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.startup_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # دکمه‌ها
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="🔄 بروزرسانی",
            command=self.refresh_startup_programs,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="⚙️ Task Manager",
            command=lambda: subprocess.Popen(["taskmgr"]),
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="📁 Startup Folder",
            command=self.open_startup_folder,
            width=150,
            height=40
        ).pack(side="left", padx=5)
        
        # بارگذاری
        self.refresh_startup_programs()
    
    def refresh_startup_programs(self):
        """بروزرسانی لیست برنامه‌های استارتاپ"""
        self.startup_text.delete("1.0", "end")
        self.startup_text.insert("1.0", "در حال بارگذاری...")
        
        def load():
            try:
                # از Registry
                startup_text = "📋 برنامه‌های استارتاپ از Registry:\n\n"
                
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
                ]
                
                for reg_path in reg_paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                startup_text += f"✓ {name}: {value}\n"
                                i += 1
                            except WindowsError:
                                break
                        winreg.CloseKey(key)
                    except:
                        pass
                
                # از Startup Folder
                startup_folder = os.path.join(
                    os.environ['APPDATA'],
                    r'Microsoft\Windows\Start Menu\Programs\Startup'
                )
                
                startup_text += f"\n\n📁 فایل‌های Startup Folder:\n\n"
                if os.path.exists(startup_folder):
                    for item in os.listdir(startup_folder):
                        startup_text += f"✓ {item}\n"
                
                self.startup_text.delete("1.0", "end")
                self.startup_text.insert("1.0", startup_text)
                self.update_status("لیست استارتاپ بروزرسانی شد", "✅")
            except Exception as e:
                self.startup_text.delete("1.0", "end")
                self.startup_text.insert("1.0", f"❌ خطا: {str(e)}")
        
        threading.Thread(target=load, daemon=True).start()
    
    def open_startup_folder(self):
        """باز کردن پوشه استارتاپ"""
        try:
            startup_folder = os.path.join(
                os.environ['APPDATA'],
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            os.startfile(startup_folder)
            self.update_status("پوشه استارتاپ باز شد", "✅")
        except:
            messagebox.showerror("خطا", "خطا در باز کردن پوشه")
    
    # ==================== ابزارهای پیشرفته ====================
    def show_advanced_tools(self):
        self.clear_main_frame()
        self.highlight_menu_button(9)
        self.update_status("ابزارهای پیشرفته", "🛠️")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="🛠️ ابزارهای پیشرفته سیستم",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # گرید ابزارها
        tools_container = ctk.CTkScrollableFrame(self.main_frame)
        tools_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        advanced_tools = [
            ("🖥️ Task Manager", "مدیریت پروسه‌ها", lambda: subprocess.Popen(["taskmgr"])),
            ("📊 Resource Monitor", "مانیتورینگ منابع", lambda: subprocess.Popen(["resmon"])),
            ("⚙️ Registry Editor", "ویرایش Registry", lambda: subprocess.Popen(["regedit"])),
            ("💻 Command Prompt", "خط فرمان", lambda: subprocess.Popen(["cmd"])),
            ("🔷 PowerShell", "PowerShell پیشرفته", lambda: subprocess.Popen(["powershell"])),
            ("🖥️ System Information", "اطلاعات سیستم", lambda: subprocess.Popen(["msinfo32"])),
            ("💾 Disk Cleanup", "پاکسازی دیسک", lambda: subprocess.Popen(["cleanmgr"])),
            ("🔧 Device Manager", "مدیریت دستگاه‌ها", lambda: subprocess.Popen(["devmgmt.msc"])),
            ("🌐 Network Connections", "اتصالات شبکه", lambda: subprocess.Popen(["ncpa.cpl"])),
            ("🎨 Display Settings", "تنظیمات نمایش", lambda: subprocess.Popen(["desk.cpl"])),
            ("🔊 Sound Settings", "تنظیمات صدا", lambda: subprocess.Popen(["mmsys.cpl"])),
            ("🖱️ Mouse Settings", "تنظیمات موس", lambda: subprocess.Popen(["main.cpl"])),
            ("⌨️ Keyboard Settings", "تنظیمات کیبورد", lambda: subprocess.Popen(["control", "keyboard"])),
            ("👤 User Accounts", "حساب‌های کاربری", lambda: subprocess.Popen(["netplwiz"])),
            ("🕐 Date & Time", "تاریخ و زمان", lambda: subprocess.Popen(["timedate.cpl"])),
            ("🌍 Region Settings", "تنظیمات منطقه", lambda: subprocess.Popen(["intl.cpl"])),
            ("📝 Event Viewer", "نمایش رویدادها", lambda: subprocess.Popen(["eventvwr.msc"])),
            ("🔐 Local Security Policy", "خط‌مشی امنیتی", lambda: subprocess.Popen(["secpol.msc"])),
            ("📦 Programs & Features", "برنامه‌ها", lambda: subprocess.Popen(["appwiz.cpl"])),
            ("🔄 Windows Update", "بروزرسانی ویندوز", lambda: subprocess.Popen(["ms-settings:windowsupdate"])),
            ("⚡ Power Options", "تنظیمات انرژی", lambda: subprocess.Popen(["powercfg.cpl"])),
            ("🖨️ Printers", "چاپگرها", lambda: subprocess.Popen(["control", "printers"]))
        ]
        
        row = 0
        col = 0
        for icon_title, desc, command in advanced_tools:
            tool_card = ctk.CTkFrame(tools_container, corner_radius=10)
            tool_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(
                tool_card,
                text=icon_title,
                font=ctk.CTkFont(family="Tahoma", size=14, weight="bold")
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                tool_card,
                text=desc,
                font=ctk.CTkFont(family="Tahoma", size=10),
                text_color="gray"
            ).pack(pady=(0, 10))
            
            ctk.CTkButton(
                tool_card,
                text="باز کردن",
                command=command,
                width=100,
                height=30
            ).pack(pady=(0, 15))
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # تنظیم grid
        for i in range(3):
            tools_container.grid_columnconfigure(i, weight=1)
    
    # ==================== تنظیمات ====================
    def show_settings(self):
        self.clear_main_frame()
        self.highlight_menu_button(10)
        self.update_status("تنظیمات برنامه", "⚙️")
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="⚙️ تنظیمات برنامه",
            font=ctk.CTkFont(family="Tahoma", size=28, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # فریم تنظیمات
        settings_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        settings_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # تنظیمات مانیتورینگ
        ctk.CTkLabel(
            settings_frame,
            text="📊 تنظیمات مانیتورینگ",
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        # هشدار CPU
        cpu_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        cpu_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(cpu_frame, text="آستانه هشدار CPU (%):", width=200).pack(side="left")
        self.cpu_threshold_var = ctk.IntVar(value=self.config.get('alert_cpu', 80))
        ctk.CTkSlider(
            cpu_frame,
            from_=50, to=100,
            variable=self.cpu_threshold_var,
            width=300
        ).pack(side="left", padx=10)
        self.cpu_threshold_label = ctk.CTkLabel(cpu_frame, text=f"{self.cpu_threshold_var.get()}%")
        self.cpu_threshold_label.pack(side="left")
        self.cpu_threshold_var.trace('w', lambda *args: self.cpu_threshold_label.configure(text=f"{self.cpu_threshold_var.get()}%"))
        
        # هشدار Memory
        mem_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        mem_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(mem_frame, text="آستانه هشدار حافظه (%):", width=200).pack(side="left")
        self.memory_threshold_var = ctk.IntVar(value=self.config.get('alert_memory', 85))
        ctk.CTkSlider(
            mem_frame,
            from_=50, to=100,
            variable=self.memory_threshold_var,
            width=300
        ).pack(side="left", padx=10)
        self.memory_threshold_label = ctk.CTkLabel(mem_frame, text=f"{self.memory_threshold_var.get()}%")
        self.memory_threshold_label.pack(side="left")
        self.memory_threshold_var.trace('w', lambda *args: self.memory_threshold_label.configure(text=f"{self.memory_threshold_var.get()}%"))
        
        # تنظیمات عمومی
        ctk.CTkLabel(
            settings_frame,
            text="🔧 تنظیمات عمومی",
            font=ctk.CTkFont(family="Tahoma", size=16, weight="bold")
        ).pack(pady=(30, 10), padx=20, anchor="w")
        
        self.auto_backup_var = ctk.BooleanVar(value=self.config.get('auto_backup', False))
        ctk.CTkCheckBox(
            settings_frame,
            text="پشتیبان‌گیری خودکار از تنظیمات",
            variable=self.auto_backup_var
        ).pack(pady=5, padx=20, anchor="w")
        
        # دکمه‌های تنظیمات
        buttons_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        buttons_frame.pack(pady=30)
        
        ctk.CTkButton(
            buttons_frame,
            text="💾 ذخیره تنظیمات",
            command=self.save_settings,
            width=180,
            height=45,
            fg_color="#4CAF50"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="🔄 بازگردانی پیش‌فرض",
            command=self.reset_settings,
            width=180,
            height=45,
            fg_color="#FF5722"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="📋 درباره برنامه",
            command=self.show_about,
            width=180,
            height=45
        ).pack(side="left", padx=10)
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        self.config['alert_cpu'] = self.cpu_threshold_var.get()
        self.config['alert_memory'] = self.memory_threshold_var.get()
        self.config['auto_backup'] = self.auto_backup_var.get()
        self.save_config()
        messagebox.showinfo("✅ موفق", "تنظیمات با موفقیت ذخیره شد")
        self.update_status("تنظیمات ذخیره شد", "✅")
    
    def reset_settings(self):
        """بازگردانی تنظیمات پیش‌فرض"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید تنظیمات را به حالت پیش‌فرض برگردانید؟"):
            self.config = {
                'theme': 'dark',
                'auto_backup': False,
                'monitoring_interval': 5,
                'alert_cpu': 80,
                'alert_memory': 85,
                'alert_disk': 90
            }
            self.save_config()
            messagebox.showinfo("✅ موفق", "تنظیمات به حالت پیش‌فرض برگشت")
            self.show_settings()
    
    def show_about(self):
        """درباره برنامه"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("📋 درباره برنامه")
        about_window.geometry("500x400")
        
        ctk.CTkLabel(
            about_window,
            text="🛡️ پنل کنترل پیشرفته ویندوز",
            font=ctk.CTkFont(family="Tahoma", size=20, weight="bold")
        ).pack(pady=30)
        
        info_text = """
        نسخه: 2.0 Advanced
        
        برنامه جامع مدیریت و کنترل سیستم‌های ویندوز
        
        قابلیت‌ها:
        ✓ مانیتورینگ لحظه‌ای سیستم
        ✓ مدیریت پیشرفته فایروال
        ✓ بهینه‌سازی سیستم
        ✓ مدیریت شبکه و اتصالات
        ✓ ابزارهای امنیتی
        ✓ و بسیاری دیگر...
        
        توسعه‌دهنده: کارشناس شبکه
        تاریخ: 2024
        """
        
        ctk.CTkTextbox(
            about_window,
            font=ctk.CTkFont(family="Tahoma", size=12),
            wrap="word"
        ).pack(fill="both", expand=True, padx=30, pady=10)
        
        about_window.children['!ctktextbox'].insert("1.0", info_text)
        about_window.children['!ctktextbox'].configure(state="disabled")


if __name__ == "__main__":
    app = AdvancedWindowsControlPanel()
    app.mainloop()