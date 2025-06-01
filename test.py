#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
کنترل پنل مدیریت ویندوز - کارشناس شبکه
Windows Management Control Panel for Network Specialists

نیازمندی‌ها:
- Python 3.x
- pip install requests

استفاده:
برنامه را با حقوق مدیر اجرا کنید
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import socket
import getpass
import threading
from pathlib import Path
import json
import webbrowser

try:
    import winreg
    import ctypes
    from ctypes import wintypes
    import requests
except ImportError as e:
    print(f"خطا در وارد کردن ماژول: {e}")
    print("لطفاً ماژول‌های مورد نیاز را نصب کنید:")
    print("pip install requests")
    sys.exit(1)

class WindowsControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("کنترل پنل مدیریت ویندوز - کارشناس شبکه")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # بررسی حقوق مدیر
        self.check_admin_rights()
        
        # ایجاد رابط کاربری
        self.create_interface()
        
        # بروزرسانی اولیه اطلاعات
        self.refresh_all_info()
    
    def check_admin_rights(self):
        """بررسی حقوق مدیر"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                messagebox.showwarning(
                    "هشدار",
                    "برای عملکرد کامل برنامه، آن را با حقوق مدیر اجرا کنید.\n"
                    "برخی عملیات ممکن است کار نکنند."
                )
        except:
            pass
    
    def create_interface(self):
        """ایجاد رابط کاربری"""
        # عنوان اصلی
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="کنترل پنل مدیریت ویندوز - کارشناس شبکه",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # ایجاد تب‌ها
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # تب‌های مختلف
        self.create_firewall_tab()
        self.create_uac_tab()
        self.create_network_tab()
        self.create_language_tab()
        self.create_system_name_tab()
        self.create_antivirus_tab()
        self.create_extra_features_tab()
        
        # نوار وضعیت
        self.status_bar = tk.Label(
            self.root,
            text="آماده",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#ecf0f1'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_firewall_tab(self):
        """تب مدیریت فایروال"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="فایروال")
        
        # فریم اصلی
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # عنوان
        title = tk.Label(main_frame, text="مدیریت فایروال ویندوز", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # وضعیت فایروال
        status_frame = tk.Frame(main_frame, bg='white')
        status_frame.pack(pady=10)
        
        tk.Label(status_frame, text="وضعیت فعلی:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        self.firewall_status = tk.Label(status_frame, text="در حال بررسی...", bg='white')
        self.firewall_status.pack(side=tk.LEFT, padx=10)
        
        # دکمه‌ها
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="فعال کردن فایروال", 
                 command=self.enable_firewall, bg='#27ae60', fg='white',
                 font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="غیرفعال کردن فایروال", 
                 command=self.disable_firewall, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="بروزرسانی وضعیت", 
                 command=self.check_firewall_status, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold'), width=15).pack(side=tk.LEFT, padx=5)
        
        # متن اطلاعات
        info_text = scrolledtext.ScrolledText(main_frame, height=8, width=70)
        info_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        info_text.insert(tk.END, "اطلاعات فایروال:\n")
        info_text.insert(tk.END, "• فایروال ویندوز محافظت اولیه سیستم را فراهم می‌کند\n")
        info_text.insert(tk.END, "• غیرفعال کردن فایروال خطرات امنیتی دارد\n")
        info_text.insert(tk.END, "• همیشه از آنتی‌ویروس معتبر استفاده کنید\n")
        info_text.config(state=tk.DISABLED)
    
    def create_uac_tab(self):
        """تب مدیریت UAC"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="UAC")
        
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_frame, text="مدیریت کنترل حساب کاربری (UAC)", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # وضعیت فعلی UAC
        status_frame = tk.Frame(main_frame, bg='white')
        status_frame.pack(pady=10)
        
        tk.Label(status_frame, text="سطح فعلی UAC:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        self.uac_status = tk.Label(status_frame, text="در حال بررسی...", bg='white')
        self.uac_status.pack(side=tk.LEFT, padx=10)
        
        # انتخاب سطح UAC
        level_frame = tk.Frame(main_frame, bg='white')
        level_frame.pack(pady=20)
        
        tk.Label(level_frame, text="انتخاب سطح امنیتی:", font=('Arial', 10, 'bold'), bg='white').pack()
        
        self.uac_var = tk.StringVar(value="2")
        levels = [
            ("هیچ‌گاه اطلاع نده (غیرامن)", "0"),
            ("فقط هنگام تغییرات برنامه‌ها", "1"),
            ("همیشه اطلاع بده (پیشنهادی)", "2"),
            ("همیشه اطلاع بده + تاریک کردن صفحه", "3")
        ]
        
        for text, value in levels:
            tk.Radiobutton(level_frame, text=text, variable=self.uac_var, 
                          value=value, bg='white', font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        
        # دکمه اعمال
        tk.Button(main_frame, text="اعمال تغییرات UAC", 
                 command=self.set_uac_level, bg='#f39c12', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        tk.Button(main_frame, text="بروزرسانی وضعیت", 
                 command=self.check_uac_status, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=5)
    
    def create_network_tab(self):
        """تب شناسایی شبکه"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="شبکه")
        
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_frame, text="مدیریت شناسایی شبکه", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # اطلاعات شبکه
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill=tk.X, pady=10, padx=10)
        
        self.network_info = scrolledtext.ScrolledText(info_frame, height=8, width=70)
        self.network_info.pack(fill=tk.BOTH, expand=True)
        
        # دکمه‌ها
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="فعال کردن شناسایی شبکه", 
                 command=self.enable_network_discovery, bg='#27ae60', fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="غیرفعال کردن شناسایی شبکه", 
                 command=self.disable_network_discovery, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="بروزرسانی اطلاعات شبکه", 
                 command=self.refresh_network_info, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
    
    def create_language_tab(self):
        """تب زبان و تاریخ"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="زبان و تاریخ")
        
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_frame, text="تنظیمات زبان و تاریخ", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # تنظیمات زبان
        lang_frame = tk.LabelFrame(main_frame, text="تنظیمات زبان", bg='white', font=('Arial', 10, 'bold'))
        lang_frame.pack(fill=tk.X, padx=10, pady=10)
        
        languages = [
            ("فارسی", "fa-IR"),
            ("انگلیسی (آمریکا)", "en-US"),
            ("انگلیسی (انگلستان)", "en-GB"),
            ("عربی", "ar-SA")
        ]
        
        self.language_var = tk.StringVar(value="fa-IR")
        for text, value in languages:
            tk.Radiobutton(lang_frame, text=text, variable=self.language_var, 
                          value=value, bg='white').pack(anchor=tk.W, padx=10, pady=2)
        
        tk.Button(lang_frame, text="اعمال زبان", 
                 command=self.set_system_language, bg='#9b59b6', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # تنظیمات تاریخ
        date_frame = tk.LabelFrame(main_frame, text="فرمت تاریخ", bg='white', font=('Arial', 10, 'bold'))
        date_frame.pack(fill=tk.X, padx=10, pady=10)
        
        date_formats = [
            ("شمسی (فارسی)", "persian"),
            ("میلادی (dd/MM/yyyy)", "dmy"),
            ("میلادی (MM/dd/yyyy)", "mdy"),
            ("میلادی (yyyy/MM/dd)", "ymd")
        ]
        
        self.date_var = tk.StringVar(value="persian")
        for text, value in date_formats:
            tk.Radiobutton(date_frame, text=text, variable=self.date_var, 
                          value=value, bg='white').pack(anchor=tk.W, padx=10, pady=2)
        
        tk.Button(date_frame, text="اعمال فرمت تاریخ", 
                 command=self.set_date_format, bg='#34495e', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=10)
    
    def create_system_name_tab(self):
        """تب نام سیستم"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="نام سیستم")
        
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_frame, text="مدیریت نام سیستم", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # نام فعلی
        current_frame = tk.Frame(main_frame, bg='white')
        current_frame.pack(pady=20)
        
        tk.Label(current_frame, text="نام فعلی کامپیوتر:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        self.current_name = tk.Label(current_frame, text="در حال بررسی...", bg='white', fg='#2c3e50')
        self.current_name.pack(side=tk.LEFT, padx=10)
        
        # تغییر نام
        change_frame = tk.Frame(main_frame, bg='white')
        change_frame.pack(pady=20)
        
        tk.Label(change_frame, text="نام جدید:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
        self.new_name_entry = tk.Entry(change_frame, font=('Arial', 10), width=30)
        self.new_name_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(change_frame, text="تغییر نام", 
                 command=self.change_computer_name, bg='#e67e22', fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # راهنما
        help_text = tk.Text(main_frame, height=6, width=70, bg='#ecf0f1')
        help_text.pack(pady=20, padx=10)
        help_text.insert(tk.END, "راهنمای تغییر نام سیستم:\n\n")
        help_text.insert(tk.END, "• نام باید بین 1 تا 15 کاراکتر باشد\n")
        help_text.insert(tk.END, "• از حروف انگلیسی، اعداد و خط تیره استفاده کنید\n")
        help_text.insert(tk.END, "• از کاراکترهای خاص و فاصله استفاده نکنید\n")
        help_text.insert(tk.END, "• پس از تغییر نام، سیستم ریستارت می‌شود\n")
        help_text.config(state=tk.DISABLED)
        
        tk.Button(main_frame, text="بروزرسانی اطلاعات", 
                 command=self.refresh_computer_name, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=10)
    
    def create_antivirus_tab(self):
        """تب مدیریت آنتی‌ویروس"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="آنتی‌ویروس")
        
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_frame, text="مدیریت Windows Defender", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # مدیریت استثناها
        exception_frame = tk.LabelFrame(main_frame, text="مدیریت استثناها", bg='white', font=('Arial', 10, 'bold'))
        exception_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # لیست استثناها
        list_frame = tk.Frame(exception_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(list_frame, text="مسیرهای استثنا:", bg='white', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        self.exception_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.exception_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.exception_listbox.yview)
        
        self.exception_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # کنترل‌ها
        control_frame = tk.Frame(exception_frame, bg='white')
        control_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(control_frame, text="مسیر جدید:", bg='white').pack(side=tk.LEFT)
        self.exception_entry = tk.Entry(control_frame, width=40)
        self.exception_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="افزودن", 
                 command=self.add_exception, bg='#27ae60', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="حذف", 
                 command=self.remove_exception, bg='#e74c3c', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="بروزرسانی", 
                 command=self.refresh_exceptions, bg='#3498db', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
    
    def create_extra_features_tab(self):
        """تب قابلیت‌های اضافی"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="قابلیت‌های اضافی")
        
        main_frame = tk.Frame(tab, bg='white', relief=tk.RAISED, bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_frame, text="قابلیت‌های اضافی", 
                        font=('Arial', 14, 'bold'), bg='white')
        title.pack(pady=10)
        
        # نصب AnyDesk
        anydesk_frame = tk.LabelFrame(main_frame, text="نصب AnyDesk", bg='white', font=('Arial', 10, 'bold'))
        anydesk_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(anydesk_frame, text="نصب خودکار AnyDesk برای اتصال از راه دور", bg='white').pack(pady=5)
        tk.Button(anydesk_frame, text="دانلود و نصب AnyDesk", 
                 command=self.install_anydesk, bg='#8e44ad', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=5)
        
        # تغییر رمز
        password_frame = tk.LabelFrame(main_frame, text="تغییر رمز کاربر", bg='white', font=('Arial', 10, 'bold'))
        password_frame.pack(fill=tk.X, padx=10, pady=10)
        
        pass_input_frame = tk.Frame(password_frame, bg='white')
        pass_input_frame.pack(pady=5)
        
        tk.Label(pass_input_frame, text="رمز جدید:", bg='white').pack(side=tk.LEFT)
        self.new_password_entry = tk.Entry(pass_input_frame, show="*", width=20)
        self.new_password_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(pass_input_frame, text="تغییر رمز", 
                 command=self.change_password, bg='#c0392b', fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # دانلود فایل‌ها
        download_frame = tk.LabelFrame(main_frame, text="دانلود فایل‌ها", bg='white', font=('Arial', 10, 'bold'))
        download_frame.pack(fill=tk.X, padx=10, pady=10)
        
        url_input_frame = tk.Frame(download_frame, bg='white')
        url_input_frame.pack(pady=5)
        
        tk.Label(url_input_frame, text="لینک فایل:", bg='white').pack(side=tk.LEFT)
        self.download_url_entry = tk.Entry(url_input_frame, width=40)
        self.download_url_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(url_input_frame, text="دانلود", 
                 command=self.download_file, bg='#16a085', fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # ابزارهای سیستمی
        tools_frame = tk.LabelFrame(main_frame, text="ابزارهای سیستمی", bg='white', font=('Arial', 10, 'bold'))
        tools_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tools_button_frame = tk.Frame(tools_frame, bg='white')
        tools_button_frame.pack(pady=5)
        
        tk.Button(tools_button_frame, text="مدیریت دستگاه‌ها", 
                 command=lambda: self.run_command("devmgmt.msc"), bg='#7f8c8d', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        
        tk.Button(tools_button_frame, text="مدیریت خدمات", 
                 command=lambda: self.run_command("services.msc"), bg='#7f8c8d', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        
        tk.Button(tools_button_frame, text="مدیریت کاربران", 
                 command=lambda: self.run_command("lusrmgr.msc"), bg='#7f8c8d', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
        
        tk.Button(tools_button_frame, text="رجیستری", 
                 command=lambda: self.run_command("regedit"), bg='#7f8c8d', fg='white',
                 font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)
    
    # متدهای عملیاتی
    def update_status(self, message):
        """بروزرسانی نوار وضعیت"""
        self.status_bar.config(text=message)
        self.root.update()
    
    def run_command(self, command, shell=True, capture_output=True):
        """اجرای دستور سیستمی"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=shell, capture_output=True, text=True)
                return result
            else:
                subprocess.Popen(command, shell=shell)
                return None
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در اجرای دستور: {str(e)}")
            return None
    
    def check_firewall_status(self):
        """بررسی وضعیت فایروال"""
        self.update_status("بررسی وضعیت فایروال...")
        try:
            result = self.run_command('netsh advfirewall show allprofiles state')
            if result and result.returncode == 0:
                output = result.stdout
                if "ON" in output.upper():
                    self.firewall_status.config(text="فعال", fg="green")
                else:
                    self.firewall_status.config(text="غیرفعال", fg="red")
            else:
                self.firewall_status.config(text="نامشخص", fg="orange")
        except Exception as e:
            self.firewall_status.config(text="خطا در بررسی", fg="red")
        self.update_status("آماده")
    
    def enable_firewall(self):
        """فعال کردن فایروال"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید فایروال را فعال کنید؟"):
            self.update_status("فعال کردن فایروال...")
            result = self.run_command('netsh advfirewall set allprofiles state on')
            if result and result.returncode == 0:
                messagebox.showinfo("موفقیت", "فایروال با موفقیت فعال شد")
                self.check_firewall_status()
            else:
                messagebox.showerror("خطا", "خطا در فعال کردن فایروال")
            self.update_status("آماده")
    
    def disable_firewall(self):
        """غیرفعال کردن فایروال"""
        if messagebox.askyesno("هشدار", "غیرفعال کردن فایروال خطرات امنیتی دارد. ادامه می‌دهید؟"):
            self.update_status("غیرفعال کردن فایروال...")
            result = self.run_command('netsh advfirewall set allprofiles state off')
            if result and result.returncode == 0:
                messagebox.showinfo("موفقیت", "فایروال با موفقیت غیرفعال شد")
                self.check_firewall_status()
            else:
                messagebox.showerror("خطا", "خطا در غیرفعال کردن فایروال")
            self.update_status("آماده")
    
    def check_uac_status(self):
        """بررسی وضعیت UAC"""
        self.update_status("بررسی وضعیت UAC...")
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System") as key:
                value, _ = winreg.QueryValueEx(key, "ConsentPromptBehaviorAdmin")
                level_text = {
                    0: "هیچ‌گاه اطلاع نده",
                    1: "فقط هنگام تغییرات برنامه‌ها", 
                    2: "همیشه اطلاع بده",
                    3: "همیشه اطلاع بده + تاریک کردن صفحه"
                }.get(value, "نامشخص")
                self.uac_status.config(text=level_text)
                self.uac_var.set(str(value))
        except Exception as e:
            self.uac_status.config(text="خطا در بررسی")
        self.update_status("آماده")
    
    def set_uac_level(self):
        """تنظیم سطح UAC"""
        level = int(self.uac_var.get())
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید سطح UAC را تغییر دهید؟"):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                                  0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, level)
                messagebox.showinfo("موفقیت", "تنظیمات UAC تغییر یافت. برای اعمال کامل ریستارت کنید.")
                self.check_uac_status()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در تنظیم UAC: {str(e)}")
    
    def enable_network_discovery(self):
        """فعال کردن شناسایی شبکه"""
        self.update_status("فعال کردن شناسایی شبکه...")
        commands = [
            'netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes',
            'netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes'
        ]
        
        success = True
        for cmd in commands:
            result = self.run_command(cmd)
            if not result or result.returncode != 0:
                success = False
                break
        
        if success:
            messagebox.showinfo("موفقیت", "شناسایی شبکه فعال شد")
        else:
            messagebox.showerror("خطا", "خطا در فعال کردن شناسایی شبکه")
        
        self.refresh_network_info()
        self.update_status("آماده")
    
    def disable_network_discovery(self):
        """غیرفعال کردن شناسایی شبکه"""
        self.update_status("غیرفعال کردن شناسایی شبکه...")
        commands = [
            'netsh advfirewall firewall set rule group="Network Discovery" new enable=No',
            'netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=No'
        ]
        
        success = True
        for cmd in commands:
            result = self.run_command(cmd)
            if not result or result.returncode != 0:
                success = False
                break
        
        if success:
            messagebox.showinfo("موفقیت", "شناسایی شبکه غیرفعال شد")
        else:
            messagebox.showerror("خطا", "خطا در غیرفعال کردن شناسایی شبکه")
        
        self.refresh_network_info()
        self.update_status("آماده")
    
    def refresh_network_info(self):
        """بروزرسانی اطلاعات شبکه"""
        self.update_status("بروزرسانی اطلاعات شبکه...")
        self.network_info.delete(1.0, tk.END)
        
        try:
            # نام کامپیوتر
            computer_name = socket.gethostname()
            self.network_info.insert(tk.END, f"نام کامپیوتر: {computer_name}\n\n")
            
            # آدرس IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.network_info.insert(tk.END, f"آدرس IP محلی: {local_ip}\n\n")
            
            # اطلاعات شبکه
            result = self.run_command('ipconfig /all')
            if result and result.returncode == 0:
                self.network_info.insert(tk.END, "اطلاعات کامل شبکه:\n")
                self.network_info.insert(tk.END, "=" * 50 + "\n")
                self.network_info.insert(tk.END, result.stdout)
            
        except Exception as e:
            self.network_info.insert(tk.END, f"خطا در دریافت اطلاعات شبکه: {str(e)}")
        
        self.update_status("آماده")
    
    def set_system_language(self):
        """تنظیم زبان سیستم"""
        language = self.language_var.get()
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید زبان سیستم را تغییر دهید؟"):
            try:
                # تنظیم زبان در رجیستری
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"Control Panel\International", 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "LocaleName", 0, winreg.REG_SZ, language)
                
                messagebox.showinfo("موفقیت", "زبان سیستم تغییر یافت. برای اعمال کامل ریستارت کنید.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در تنظیم زبان: {str(e)}")
    
    def set_date_format(self):
        """تنظیم فرمت تاریخ"""
        date_format = self.date_var.get()
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید فرمت تاریخ را تغییر دهید؟"):
            try:
                format_map = {
                    "persian": "yyyy/MM/dd",
                    "dmy": "dd/MM/yyyy", 
                    "mdy": "MM/dd/yyyy",
                    "ymd": "yyyy/MM/dd"
                }
                
                format_str = format_map.get(date_format, "yyyy/MM/dd")
                
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"Control Panel\International", 0,
                                  winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "sShortDate", 0, winreg.REG_SZ, format_str)
                
                messagebox.showinfo("موفقیت", "فرمت تاریخ تغییر یافت.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در تنظیم فرمت تاریخ: {str(e)}")
    
    def refresh_computer_name(self):
        """بروزرسانی نام کامپیوتر"""
        try:
            computer_name = socket.gethostname()
            self.current_name.config(text=computer_name)
        except Exception as e:
            self.current_name.config(text="خطا در دریافت نام")
    
    def change_computer_name(self):
        """تغییر نام کامپیوتر"""
        new_name = self.new_name_entry.get().strip()
        
        if not new_name:
            messagebox.showerror("خطا", "لطفاً نام جدید را وارد کنید")
            return
        
        if len(new_name) > 15:
            messagebox.showerror("خطا", "نام باید کمتر از 15 کاراکتر باشد")
            return
        
        if not new_name.replace('-', '').replace('_', '').isalnum():
            messagebox.showerror("خطا", "نام باید شامل حروف، اعداد و خط تیره باشد")
            return
        
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید نام کامپیوتر را به '{new_name}' تغییر دهید؟\nسیستم ریستارت خواهد شد."):
            try:
                # تغییر نام کامپیوتر
                result = self.run_command(f'wmic computersystem where name="%computername%" call rename name="{new_name}"')
                
                if result and result.returncode == 0:
                    if messagebox.askyesno("موفقیت", "نام کامپیوتر تغییر یافت. آیا می‌خواهید اکنون ریستارت کنید؟"):
                        self.run_command('shutdown /r /t 10', capture_output=False)
                else:
                    messagebox.showerror("خطا", "خطا در تغییر نام کامپیوتر")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در تغییر نام: {str(e)}")
    
    def refresh_exceptions(self):
        """بروزرسانی لیست استثناها"""
        self.exception_listbox.delete(0, tk.END)
        try:
            result = self.run_command('powershell "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"')
            if result and result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                for path in paths:
                    if path.strip():
                        self.exception_listbox.insert(tk.END, path.strip())
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت استثناها: {str(e)}")
    
    def add_exception(self):
        """افزودن استثنا به Windows Defender"""
        path = self.exception_entry.get().strip()
        if not path:
            messagebox.showerror("خطا", "لطفاً مسیر را وارد کنید")
            return
        
        try:
            result = self.run_command(f'powershell "Add-MpPreference -ExclusionPath \\"{path}\\""')
            if result and result.returncode == 0:
                messagebox.showinfo("موفقیت", "استثنا اضافه شد")
                self.exception_entry.delete(0, tk.END)
                self.refresh_exceptions()
            else:
                messagebox.showerror("خطا", "خطا در افزودن استثنا")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا: {str(e)}")
    
    def remove_exception(self):
        """حذف استثنا از Windows Defender"""
        selection = self.exception_listbox.curselection()
        if not selection:
            messagebox.showerror("خطا", "لطفاً یک استثنا را انتخاب کنید")
            return
        
        path = self.exception_listbox.get(selection[0])
        
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید این استثنا را حذف کنید؟\n{path}"):
            try:
                result = self.run_command(f'powershell "Remove-MpPreference -ExclusionPath \\"{path}\\""')
                if result and result.returncode == 0:
                    messagebox.showinfo("موفقیت", "استثنا حذف شد")
                    self.refresh_exceptions()
                else:
                    messagebox.showerror("خطا", "خطا در حذف استثنا")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا: {str(e)}")
    
    def install_anydesk(self):
        """نصب AnyDesk"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید AnyDesk را دانلود و نصب کنید؟"):
            def download_and_install():
                try:
                    self.update_status("دانلود AnyDesk...")
                    
                    # URL دانلود AnyDesk
                    url = "https://download.anydesk.com/AnyDesk.exe"
                    
                    # دانلود فایل
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    
                    # ذخیره فایل
                    file_path = os.path.join(os.path.expanduser("~"), "Downloads", "AnyDesk.exe")
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.update_status("نصب AnyDesk...")
                    
                    # اجرای فایل نصب
                    self.run_command(f'"{file_path}" --install --start-with-win --silent', capture_output=False)
                    
                    messagebox.showinfo("موفقیت", "AnyDesk با موفقیت نصب شد")
                    self.update_status("آماده")
                    
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در نصب AnyDesk: {str(e)}")
                    self.update_status("آماده")
            
            # اجرای دانلود در thread جداگانه
            threading.Thread(target=download_and_install, daemon=True).start()
    
    def change_password(self):
        """تغییر رمز کاربر فعلی"""
        new_password = self.new_password_entry.get()
        
        if not new_password:
            messagebox.showerror("خطا", "لطفاً رمز جدید را وارد کنید")
            return
        
        current_user = getpass.getuser()
        
        if messagebox.askyesno("تأیید", f"آیا می‌خواهید رمز کاربر '{current_user}' را تغییر دهید؟"):
            try:
                result = self.run_command(f'net user "{current_user}" "{new_password}"')
                if result and result.returncode == 0:
                    messagebox.showinfo("موفقیت", "رمز با موفقیت تغییر یافت")
                    self.new_password_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("خطا", "خطا در تغییر رمز")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا: {str(e)}")
    
    def download_file(self):
        """دانلود فایل از URL"""
        url = self.download_url_entry.get().strip()
        
        if not url:
            messagebox.showerror("خطا", "لطفاً آدرس فایل را وارد کنید")
            return
        
        def download():
            try:
                self.update_status("در حال دانلود...")
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # تشخیص نام فایل
                filename = url.split('/')[-1]
                if not filename or '.' not in filename:
                    filename = "downloaded_file"
                
                # مسیر ذخیره
                save_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
                
                # دانلود
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                messagebox.showinfo("موفقیت", f"فایل با موفقیت دانلود شد:\n{save_path}")
                self.download_url_entry.delete(0, tk.END)
                self.update_status("آماده")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در دانلود: {str(e)}")
                self.update_status("آماده")
        
        # اجرای دانلود در thread جداگانه
        threading.Thread(target=download, daemon=True).start()
    
    def refresh_all_info(self):
        """بروزرسانی تمام اطلاعات"""
        self.check_firewall_status()
        self.check_uac_status()
        self.refresh_network_info()
        self.refresh_computer_name()
        self.refresh_exceptions()

def main():
    """تابع اصلی برنامه"""
    try:
        # بررسی سیستم عامل
        if os.name != 'nt':
            messagebox.showerror("خطا", "این برنامه فقط برای ویندوز طراحی شده است")
            return
        
        # ایجاد پنجره اصلی
        root = tk.Tk()
        
        # تنظیم آیکون (اختیاری)
        try:
            root.iconbitmap(default='icon.ico')  # در صورت وجود فایل آیکون
        except:
            pass
        
        # ایجاد برنامه
        app = WindowsControlPanel(root)
        
        # اجرای برنامه
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("خطای کلی", f"خطا در اجرای برنامه: {str(e)}")

if __name__ == "__main__":
    main()