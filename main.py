import asyncio
import os
from os import getenv
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

from bot.command_manager.loader import load_all_commands, commands_registry, command_aliases
from bot.command_manager.register import register_event_handlers

# تحميل المتغيرات من ملف .env
load_dotenv("variables.env")
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
SESSION = getenv("SESSION_STRING")
BOT_TOKEN = getenv("BOT_TOKEN")
OWNER_GROUP_ID = int(getenv("OWNER_GROUP_ID"))
BOT_USERNAME = getenv("BOT_USERNAME")

# تجهيز المجلدات الضرورية
os.makedirs("commands", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

# إنشاء جلسات Telethon
client = TelegramClient("bot_session", API_ID, API_HASH)
user_client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# تحميل الأوامر وتسجيل الأحداث
load_all_commands()
register_event_handlers(client)
register_event_handlers(user_client)

# معالجة الأوامر من البوت الرسمي
@client.on(events.NewMessage(incoming=True))
async def dynamic_command_handler_bot(event):
    if not event.raw_text.startswith("."):
        return

    cmd = event.raw_text[1:].split()[0].strip()
    module = commands_registry.get(cmd)

    if module and hasattr(module, "handle"):
        try:
            await module.handle(event)
        except Exception as e:
            await event.respond(f"❌ حدث خطأ أثناء تنفيذ الأمر `.{cmd}`:\n{str(e)}")
    elif cmd in command_aliases:
        await event.respond(f"⚠️ الأمر `.{cmd}` موجود لكن لا يحتوي دالة `handle()`.")

# معالجة الأوامر من الحساب الشخصي
@user_client.on(events.NewMessage(incoming=True))
async def dynamic_command_handler_user(event):
    if not event.raw_text.startswith("."):
        return

    cmd = event.raw_text[1:].split()[0].strip()
    module = commands_registry.get(cmd)

    if module and hasattr(module, "handle"):
        try:
            await module.handle(event)
        except Exception as e:
            await event.respond(f"❌ حدث خطأ أثناء تنفيذ الأمر `.{cmd}`:\n{str(e)}")
    elif cmd in command_aliases:
        await event.respond(f"⚠️ الأمر `.{cmd}` موجود لكن لا يحتوي دالة `handle()`.")

# دالة التشغيل الرئيسية
async def main():
    await client.start(bot_token=BOT_TOKEN)
    await user_client.start()

    # إشعارات التفعيل داخل الجروب المالك
    bot_info = await client.get_me()
    user_info = await user_client.get_me()

    await client.send_message(
        OWNER_GROUP_ID,
        f"✅ تم تفعيل البوت الرسمي: [{bot_info.first_name}](tg://user?id={bot_info.id})"
    )

    await client.send_message(
        OWNER_GROUP_ID,
        f"✅ تم تفعيل الحساب المساعد: [{user_info.first_name}](tg://user?id={user_info.id})"
    )

    await asyncio.gather(
        client.run_until_disconnected(),
        user_client.run_until_disconnected()
    )
@user_client.on(events.CallbackQuery)
async def handle_admin_buttons(event):
    sender = await event.get_sender()
    sender_id = sender.id

    try:
        with open("allowed_users.json", "r", encoding="utf-8") as f:
            allowed = json.load(f)
    except Exception:
        allowed = []

    if sender_id not in allowed:
        await event.answer("🚫 لا تملك صلاحية استخدام الأزرار.", alert=True)
        return

    action = event.data.decode()

    if action == "run_check":
        await event.edit("✅ البوت يعمل بكفاءة، ولا توجد أخطاء حالياً.")

    elif action == "personal_cmds":
        await event.edit("🧾 أوامرك الخاصة:\n▫️ `.نايم`\n▫️ `.فحص`\n▫️ `.اوامر`")

    elif action == "list_users":
        users_text = "\n".join([f"• `{uid}`" for uid in allowed]) or "لا يوجد أي مستخدم مسموح له."
        await event.edit(f"📤 قائمة المسموحين:\n{users_text}")

    elif action == "add_user":
        await event.edit("✏️ أرسل معرف المستخدم المراد إضافته في رسالة جديدة.")

        @user_client.on(events.NewMessage(from_users=sender_id))
        async def add_user_handler(msg):
            try:
                new_uid = int(msg.raw_text.strip())
                if new_uid not in allowed:
                    allowed.append(new_uid)
                    with open("allowed_users.json", "w", encoding="utf-8") as f:
                        json.dump(allowed, f, indent=2)
                    await msg.reply(f"✅ تم إضافة المستخدم `{new_uid}` بنجاح.")
                else:
                    await msg.reply("ℹ️ المستخدم موجود بالفعل في القائمة.")
            except Exception as e:
                await msg.reply(f"❌ خطأ في إضافة المستخدم:\n{str(e)}")

            user_client.remove_event_handler(add_user_handler)

if __name__ == "__main__":
    asyncio.run(main())
