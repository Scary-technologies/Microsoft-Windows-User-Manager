import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import platform
import winreg
import ctypes
import os
import socket
import requests
import getpass

class WindowsControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("کنترل پنل مدیریت ویندوز - کارشناس شبکه")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Check for admin rights
        if not ctypes.windll.shell32.IsUserAnAdmin():
            messagebox.showwarning("هشدار", "برای عملکرد کامل، برنامه را با حقوق مدیر اجرا کنید.")
            self.root.destroy()
            return

        # Initialize status bar first
        self.status_bar = tk.Label(root, text="آماده", bg='#f0f0f0', fg='#333333', relief=tk.FLAT, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Define tab frames
        self.firewall_tab = ttk.Frame(self.notebook)
        self.uac_tab = ttk.Frame(self.notebook)
        self.network_tab = ttk.Frame(self.notebook)
        self.locale_tab = ttk.Frame(self.notebook)
        self.system_tab = ttk.Frame(self.notebook)
        self.av_tab = ttk.Frame(self.notebook)
        self.extra_tab = ttk.Frame(self.notebook)

        # Initialize tabs
        self.create_firewall_tab()
        self.create_uac_tab()
        self.create_network_tab()
        self.create_locale_tab()
        self.create_system_tab()
        self.create_av_tab()
        self.create_extra_tab()

        # Add tabs to notebook
        self.notebook.add(self.firewall_tab, text="مدیریت فایروال")
        self.notebook.add(self.uac_tab, text="مدیریت UAC")
        self.notebook.add(self.network_tab, text="شناسایی شبکه")
        self.notebook.add(self.locale_tab, text="زبان و تاریخ")
        self.notebook.add(self.system_tab, text="نام سیستم")
        self.notebook.add(self.av_tab, text="مدیریت آنتی‌ویروس")
        self.notebook.add(self.extra_tab, text="قابلیت‌های اضافی")

    def update_status(self, message):
        """Update the status bar with a message"""
        self.status_bar.config(text=message)

    ### Firewall Management Tab ###
    def create_firewall_tab(self):
        tk.Label(self.firewall_tab, text="مدیریت فایروال ویندوز", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        self.firewall_status = tk.StringVar()
        self.check_firewall_status()
        tk.Label(self.firewall_tab, textvariable=self.firewall_status, bg='#f0f0f0').pack(pady=5)

        btn_frame = tk.Frame(self.firewall_tab, bg='#f0f0f0')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="فعال کردن", command=self.enable_firewall, bg='#4CAF50', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="غیرفعال کردن", command=self.disable_firewall, bg='#F44336', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="بررسی وضعیت", command=self.check_firewall_status, bg='#2196F3', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

    def check_firewall_status(self):
        try:
            result = subprocess.run(["netsh", "advfirewall", "show", "allprofiles", "state"], capture_output=True, text=True, check=True)
            self.firewall_status.set(f"وضعیت: {result.stdout.strip()}")
            self.update_status("وضعیت فایروال بررسی شد")
        except subprocess.CalledProcessError as e:
            self.firewall_status.set("خطا در بررسی وضعیت")
            self.update_status(f"خطا: {e.stderr}")

    def enable_firewall(self):
        try:
            subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True)
            self.check_firewall_status()
            messagebox.showinfo("موفق", "فایروال فعال شد")
            self.update_status("فایروال فعال شد")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("خطا", f"خطا: {e.stderr}")
            self.update_status("خطا در فعال‌سازی فایروال")

    def disable_firewall(self):
        if messagebox.askyesno("هشدار", "آیا مطمئن هستید؟"):
            try:
                subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "off"], check=True)
                self.check_firewall_status()
                messagebox.showinfo("موفق", "فایروال غیرفعال شد")
                self.update_status("فایروال غیرفعال شد")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("خطا", f"خطا: {e.stderr}")
                self.update_status("خطا در غیرفعال‌سازی فایروال")

    ### UAC Management Tab ###
    def create_uac_tab(self):
        tk.Label(self.uac_tab, text="مدیریت UAC", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        self.uac_level = tk.IntVar(value=self.get_uac_level())
        levels = [(0, "غیرفعال"), (1, "حداقل اعلان"), (2, "پیش‌فرض"), (3, "حداکثر امنیت")]
        for level, desc in levels:
            tk.Radiobutton(self.uac_tab, text=desc, variable=self.uac_level, value=level, bg='#f0f0f0').pack(anchor=tk.W, pady=2)
        tk.Button(self.uac_tab, text="اعمال", command=self.set_uac_level, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=20)

    def get_uac_level(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
            value, _ = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")
            winreg.CloseKey(key)
            return value
        except WindowsError:
            return 2

    def set_uac_level(self):
        level = self.uac_level.get()
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, level)
            winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 1 if level > 1 else 0)
            winreg.CloseKey(key)
            messagebox.showinfo("موفق", "تنظیمات UAC اعمال شد (نیاز به ری‌استارت)")
            self.update_status("تنظیمات UAC اعمال شد")
        except WindowsError as e:
            messagebox.showerror("خطا", f"خطا: {str(e)}")
            self.update_status("خطا در تنظیم UAC")

    ### Network Discovery Tab ###
    def create_network_tab(self):
        tk.Label(self.network_tab, text="شناسایی شبکه", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        self.network_discovery = tk.BooleanVar(value=self.get_network_discovery())
        tk.Checkbutton(self.network_tab, text="فعال کردن شناسایی شبکه", variable=self.network_discovery, bg='#f0f0f0').pack(pady=5)
        tk.Button(self.network_tab, text="اعمال", command=self.set_network_discovery, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=20)
        self.network_info = tk.Text(self.network_tab, height=10, width=80, bg='#ffffff')
        self.network_info.pack(padx=10, pady=5)
        self.network_info.insert(tk.END, self.get_network_info())
        self.network_info.config(state=tk.DISABLED)

    def get_network_discovery(self):
        try:
            result = subprocess.run(["netsh", "advfirewall", "firewall", "show", "rule", "name=\"Network Discovery (LLMNR-UDP)\""], capture_output=True, text=True)
            return "enable=Yes" in result.stdout
        except:
            return False

    def set_network_discovery(self):
        state = "Yes" if self.network_discovery.get() else "No"
        try:
            subprocess.run(["netsh", "advfirewall", "firewall", "set", "rule", "group=\"Network Discovery\"", "new", f"enable={state}"], check=True)
            messagebox.showinfo("موفق", f"شناسایی شبکه {'فعال' if state == 'Yes' else 'غیرفعال'} شد")
            self.update_status(f"شناسایی شبکه {'فعال' if state == 'Yes' else 'غیرفعال'} شد")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("خطا", f"خطا: {e.stderr}")
            self.update_status("خطا در تنظیم شناسایی شبکه")

    def get_network_info(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            interfaces = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
            return f"نام سیستم: {hostname}\nآدرس IP: {ip_address}\n\nجزئیات:\n{interfaces.stdout}"
        except Exception as e:
            return f"خطا: {str(e)}"

    ### Locale and Date Tab ###
    def create_locale_tab(self):
        tk.Label(self.locale_tab, text="زبان و تاریخ", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        self.language_var = tk.StringVar(value="فارسی (Iran)")
        languages = ["فارسی (Iran)", "انگلیسی (US)", "عربی (SA)"]
        tk.OptionMenu(self.locale_tab, self.language_var, *languages).pack(pady=5)
        self.date_format_var = tk.StringVar(value="yyyy/MM/dd")
        date_formats = ["yyyy/MM/dd", "dd/MM/yyyy", "MM/dd/yyyy"]
        tk.OptionMenu(self.locale_tab, self.date_format_var, *date_formats).pack(pady=5)
        tk.Button(self.locale_tab, text="اعمال", command=self.set_locale, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=20)

    def set_locale(self):
        try:
            lang = self.language_var.get()
            date = self.date_format_var.get()
            messagebox.showinfo("موفق", f"زبان: {lang}\nفرمت تاریخ: {date}\n(نیاز به ری‌استارت)")
            self.update_status("تنظیمات زبان و تاریخ اعمال شد")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا: {str(e)}")
            self.update_status("خطا در تنظیم زبان و تاریخ")

    ### System Name Tab ###
    def create_system_tab(self):
        tk.Label(self.system_tab, text="تغییر نام سیستم", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        current_name = socket.gethostname()
        tk.Label(self.system_tab, text=f"نام فعلی: {current_name}", bg='#f0f0f0').pack(pady=5)
        self.new_name_var = tk.StringVar()
        tk.Entry(self.system_tab, textvariable=self.new_name_var, bg='#ffffff').pack(pady=5)
        tk.Button(self.system_tab, text="تغییر نام", command=self.change_computer_name, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=20)

    def change_computer_name(self):
        new_name = self.new_name_var.get().strip()
        if not new_name:
            messagebox.showerror("خطا", "نام معتبر وارد کنید")
            return
        try:
            subprocess.run(["wmic", "computersystem", "where", "name='%COMPUTERNAME%'", "call", "rename", new_name], check=True)
            messagebox.showinfo("موفق", f"نام به '{new_name}' تغییر یافت (نیاز به ری‌استارت)")
            self.update_status("نام سیستم تغییر یافت")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("خطا", f"خطا: {e.stderr}")
            self.update_status("خطا در تغییر نام سیستم")

    ### Antivirus Management Tab ###
    def create_av_tab(self):
        tk.Label(self.av_tab, text="مدیریت آنتی‌ویروس", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        self.exclusions_listbox = tk.Listbox(self.av_tab, width=80, height=10, bg='#ffffff')
        self.exclusions_listbox.pack(pady=5)
        self.refresh_exclusions_list()
        btn_frame = tk.Frame(self.av_tab, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="اضافه کردن", command=self.add_exclusion_path, bg='#4CAF50', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="حذف", command=self.remove_exclusion_path, bg='#F44336', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="بروزرسانی", command=self.refresh_exclusions_list, bg='#2196F3', fg='white', relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

    def refresh_exclusions_list(self):
        self.exclusions_listbox.delete(0, tk.END)
        try:
            result = subprocess.run(["powershell", "-Command", "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"], capture_output=True, text=True)
            paths = [p.strip() for p in result.stdout.split('\n') if p.strip()]
            for path in paths:
                self.exclusions_listbox.insert(tk.END, path)
            self.update_status("لیست استثناها بروزرسانی شد")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("خطا", f"خطا: {e.stderr}")
            self.update_status("خطا در بروزرسانی استثناها")

    def add_exclusion_path(self):
        path = filedialog.askdirectory(title="انتخاب پوشه")
        if path:
            try:
                subprocess.run(["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{path}'"], check=True)
                self.refresh_exclusions_list()
                messagebox.showinfo("موفق", f"مسیر '{path}' اضافه شد")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("خطا", f"خطا: {e.stderr}")

    def remove_exclusion_path(self):
        selection = self.exclusions_listbox.curselection()
        if not selection:
            messagebox.showerror("خطا", "مسیر را انتخاب کنید")
            return
        path = self.exclusions_listbox.get(selection[0])
        if messagebox.askyesno("تأیید", f"حذف '{path}'؟"):
            try:
                subprocess.run(["powershell", "-Command", f"Remove-MpPreference -ExclusionPath '{path}'"], check=True)
                self.refresh_exclusions_list()
                messagebox.showinfo("موفق", f"مسیر '{path}' حذف شد")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("خطا", f"خطا: {e.stderr}")

    ### Extra Features Tab ###
    def create_extra_tab(self):
        tk.Label(self.extra_tab, text="قابلیت‌های اضافی", font=('Tahoma', 12), bg='#f0f0f0').pack(pady=10)
        tk.Button(self.extra_tab, text="نصب AnyDesk", command=self.install_anydesk, bg='#4CAF50', fg='white', relief=tk.FLAT).pack(pady=5)
        tk.Button(self.extra_tab, text="تغییر رمز", command=self.set_password, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=5)
        tk.Button(self.extra_tab, text="دانلود فایل‌ها", command=self.download_files, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=5)
        tk.Button(self.extra_tab, text="نمایش اطلاعات شبکه", command=self.show_network_info, bg='#2196F3', fg='white', relief=tk.FLAT).pack(pady=5)

    def install_anydesk(self):
        try:
            url = "https://download.anydesk.com/AnyDesk.exe"
            response = requests.get(url, timeout=10)
            with open("AnyDesk.exe", "wb") as f:
                f.write(response.content)
            subprocess.run(["AnyDesk.exe", "--silent"], check=True)
            messagebox.showinfo("موفق", "AnyDesk نصب شد")
            self.update_status("AnyDesk نصب شد")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا: {str(e)}")
            self.update_status("خطا در نصب AnyDesk")

    def set_password(self):
        password = tk.simpledialog.askstring("رمز جدید", "رمز جدید را وارد کنید:", show='*')
        if password:
            try:
                username = getpass.getuser()
                subprocess.run(["net", "user", username, password], check=True)
                messagebox.showinfo("موفق", "رمز تغییر یافت")
                self.update_status("رمز کاربر تغییر یافت")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("خطا", f"خطا: {e.stderr}")
                self.update_status("خطا در تغییر رمز")

    def download_files(self):
        if not os.path.exists("LINKS.TXT"):
            messagebox.showerror("خطا", "فایل LINKS.TXT یافت نشد")
            return
        try:
            with open("LINKS.TXT", "r") as f:
                links = [line.strip() for line in f if line.strip()]
            for link in links:
                response = requests.get(link, timeout=10)
                filename = link.split("/")[-1] or "downloaded_file"
                with open(filename, "wb") as f:
                    f.write(response.content)
            messagebox.showinfo("موفق", "فایل‌ها دانلود شدند")
            self.update_status("فایل‌ها دانلود شدند")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا: {str(e)}")
            self.update_status("خطا در دانلود فایل‌ها")

    def show_network_info(self):
        try:
            result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, check=True)
            tk.messagebox.showinfo("اطلاعات شبکه", result.stdout)
            self.update_status("اطلاعات شبکه نمایش داده شد")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("خطا", f"خطا: {e.stderr}")
            self.update_status("خطا در نمایش اطلاعات شبکه")

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsControlPanel(root)
    root.mainloop()