import os
import shutil
import sys
import asyncio
import time

import psutil
from database import db
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from .utils import STS

main_buttons = [[
    InlineKeyboardButton(
        '📜 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/+mCdsJ7mjeBEyZWQ1'),
    InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇᴅ ᴄʜᴀɴɴᴇʟ ', url='https://t.me/Kdramaland')
], [
    InlineKeyboardButton('❗️ʜᴇʟᴘ❗', callback_data='help')
], [
    InlineKeyboardButton('💳 ᴅᴏɴᴀᴛᴇ', callback_data='donate')
]]

# ===================Start Function===================#


@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await client.send_message(
        chat_id=message.chat.id,
        reply_markup=reply_markup,
        text=Translation.START_TXT.format(
            user.mention))

# ===================Donate Function===================#


@Client.on_message(filters.private & filters.command('donate'))
async def func_donate(client, message):
    user = message.from_user
    buttons = [[InlineKeyboardButton('❄️ ѕησωвαℓℓ', url='https://t.me/Snowball_Official'),
                InlineKeyboardButton('✘ ᴄʟᴏsᴇ', callback_data='close')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(chat_id=user.id, text=Translation.DONATE, reply_markup=reply_markup)

# ==================Restart Function==================#


@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER_ID))
async def restart(client, message:Message):
    await message.reply_text(
        text="<i>Trying to restarting.....</i>"
    )
    os.execl(sys.executable, sys.executable, *sys.argv)

# ==================Ping Function==================#


@Client.on_message(filters.private & filters.command(["ping", "p"]))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("Pinging....", quote=True)
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Ping 🔥!\n{time_taken_s:.3f} ms")
    return time_taken_s

# ==================Callback Functions==================#


@Client.on_callback_query(filters.regex("^help"))
async def help_cb(bot, query):
    buttons = [
        [
            InlineKeyboardButton('• ᴜsᴀɢᴇ ɢᴜɪᴅᴇ •', callback_data='how_to_use')
        ],
        [
            InlineKeyboardButton('• ᴀʙᴏᴜᴛ •', callback_data='about'),
            InlineKeyboardButton('• sᴛᴀᴛs •', callback_data='status'),
        ], [
            InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='back'),
            InlineKeyboardButton(
                '• sᴇᴛᴛɪɴɢs • ', callback_data='settings#main')
        ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.HELP_TXT,
        reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^how_to_use"))
async def how_to_use(bot, query):
    buttons = [[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.HOW_USE_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex("^back"))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await query.message.edit_text(
        reply_markup=reply_markup,
        text=Translation.START_TXT.format(
            query.from_user.first_name))


@Client.on_callback_query(filters.regex("^about"))
async def about(bot, query):
    buttons = [[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.ABOUT_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("^donate"))
async def donate(bot, query):
    buttons = [[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='back'), InlineKeyboardButton('✘ ᴄʟᴏsᴇ', callback_data='close')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.DONATE,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex("^status"))
async def status(bot, query):
    users_count, bots_count = await db.total_users_bots_count()
    buttons = [[InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='help'), InlineKeyboardButton(
        '• sᴇʀᴠᴇʀ sᴛᴀᴛᴜs', callback_data='server_status')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.STATUS_TXT.format(
            users_count, bots_count, abs(temp.forwardings)),
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex('^server_status'))
async def server_status(bot, query):
    buttons = [[InlineKeyboardButton(
        '• ʙᴀᴄᴋ', callback_data='status'), InlineKeyboardButton('⟲ ʀᴇʟᴏᴀᴅ', callback_data='server_status')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(
        time.time() - Config.BOT_START_TIME))
    total, used, free = shutil.disk_usage(".")
    total = STS.humanbytes(total)
    used = STS.humanbytes(used)
    free = STS.humanbytes(free)
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    await query.message.edit_text(
        text=Translation.SERVER_STATUS.format(
            currentTime, total, used, disk_usage, free, cpu_usage, ram_usage),
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex('^close'))
async def close(bot, query):
    await query.message.delete()
    await query.message.reply_to_message.delete()
    await query.message.continue_propagation()
