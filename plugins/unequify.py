import re
import asyncio
import sys
from database import db
from config import temp
from .test import CLIENT, start_clone_bot
from translation import Translation
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()
COMPLETED_BTN = InlineKeyboardMarkup([
    [InlineKeyboardButton('💟 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💟', url='https://t.me/+mCdsJ7mjeBEyZWQ1'), 
    [InlineKeyboardButton('💠 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 💠', url='https://t.me/Kdramaland')]]])

CANCEL_BTN = InlineKeyboardMarkup(
    [[InlineKeyboardButton('• ᴄᴀɴᴄᴇʟ', 'terminate_frwd')]])


@Client.on_message(filters.command("unequify") & filters.private)
async def unequify(client, message):
    user_id = message.from_user.id
    temp.CANCEL[user_id] = False

    if temp.lock.get(user_id) and str(temp.lock.get(user_id)) == "True":
        return await message.reply("**please wait until previous task complete**")

    _bot = await db.get_user(user_id)

    if not _bot or _bot['is_bot']:
        return await message.reply("<b>Need userbot to do this process. Please add a userbot using /settings</b>")

    target = await client.ask(user_id, text="**Forward the last message from target chat or send last message link.**\n/cancel - `cancel this process`")

    try:
        if target.text.startswith("/"):
            return await message.reply("**process cancelled !**")
    except:
        try:
            if target.forward_from_chat.type in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP]:
                chat_id = target.forward_from_chat.username or target.forward_from_chat.id
        except:
            try:
                if target.text:
                    regex = re.compile(
                        "(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
                    match = regex.match(target.text.replace("?single", ""))

                    if not match:
                        return await message.reply('**Invalid link**')

                    chat_id = match.group(4)

                    if chat_id.isnumeric():
                        chat_id = int(("-100" + chat_id))
            except:
                return await message.reply_text("**invalid !**")

    confirm = await client.ask(user_id, text="**send /yes to start the process and /no to cancel this process**")

    if confirm.text.lower() == '/no':
        return await confirm.reply("**process cancelled !**")

    sts = await confirm.reply("**processing..**")

    try:
        bot = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e:
        return await sts.edit(e)

    try:
        k = await bot.send_message(chat_id, text="testing")
        await k.delete()
    except:
        await sts.edit(f"**please make your [userbot](t.me/{_bot['username']}) admin in target chat with full permissions**")
        return await bot.stop()

    MESSAGES = []
    DUPLICATE = []
    total = deleted = 0
    temp.lock[user_id] = True

    try:
        await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "ᴘʀᴏɢʀᴇssɪɴɢ"), reply_markup=CANCEL_BTN)

        async for message in bot.search_messages(chat_id=chat_id, filter=enums.MessagesFilter.DOCUMENT):
            if temp.CANCEL.get(user_id) == True:
                await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "ᴄᴀɴᴄᴇʟʟᴇᴅ"), reply_markup=COMPLETED_BTN)
                return await bot.stop()

            file = message.document
            file_id = file.file_id  # Use an alternative way to get the file ID

            if file_id in MESSAGES:
                DUPLICATE.append(message.id)
            else:
                MESSAGES.append(file_id)

            total += 1

            if total % 10000 == 0:
                await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "ᴘʀᴏɢʀᴇssɪɴɢ"), reply_markup=CANCEL_BTN)

            if len(DUPLICATE) >= 100:
                await bot.delete_messages(chat_id, DUPLICATE)
                deleted += 100
                await sts.edit(Translation.DUPLICATE_TEXT.format(total, deleted, "ᴘʀᴏɢʀᴇssɪɴɢ"), reply_markup=CANCEL_BTN)
                DUPLICATE = []
    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        await sts.edit(e)
