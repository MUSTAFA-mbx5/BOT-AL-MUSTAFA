import subprocess
import sys
import importlib.util
import os
from telethon import TelegramClient

# تحميل المتغيرات من environment أو ملف خارجي
from dotenv import load_dotenv
load_dotenv("variables.env")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("BOT_STARTUP_CHAT_ID", "-1001234567890"))

# قائمة المكتبات المطلوبة
required_libs = [
    ("telethon", "telethon"),
    ("fitz", "PyMuPDF"),
    ("docx", "python-docx"),
    ("pptx", "python-pptx"),
    ("win32print", "pywin32"),
    ("aiohttp", "aiohttp"),
    ("nest_asyncio", "nest_asyncio"),
]

def is_installed(module_name):
    return importlib.util.find_spec(module_name) is not None

# تثبيت المكتبات الناقصة
for module_name, package_name in required_libs:
    if not is_installed(module_name):
        print(f"[+] تثبيت: {package_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# تشغيل البوت + إرسال إشعار للكروب
async def main():
    client = TelegramClient("installer", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    await client.send_message(CHAT_ID, "✅ تم تفعيل البوت بنجاح على الجهاز.")
    print("[+] تشغيل البوت...")
    os.system("python bot/main.py")

import asyncio
asyncio.run(main())