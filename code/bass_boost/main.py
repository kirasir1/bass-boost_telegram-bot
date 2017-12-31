# -*- coding: utf-8 -*-
import requests
from flask import Flask, url_for
from luckydonaldUtils.logger import logging
from pydub import AudioSegment
from pytgbot import Bot
from pytgbot.api_types.receivable.media import Audio
from pytgbot.api_types.receivable.peer import Chat, User
from pytgbot.api_types.receivable.updates import Message, Update
from pytgbot.api_types.sendable.files import InputFile
from pytgbot.exceptions import TgApiServerException
from teleflask.messages import HTMLMessage

from bass_boost.boost import boost
from .langs import l
from .secrets import API_KEY, URL_HOSTNAME, URL_PATH
from luckydonaldUtils.exceptions import assert_type_or_raise
import re
from html import escape
from io import BytesIO

POSSIBLE_CHAT_TYPES = ("supergroup", "group", "channel")
SEND_BACKOFF = 5

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)
logging.add_colored_handler(level=logging.DEBUG)

from teleflask import Teleflask
app = Flask(__name__)

# sentry = add_error_reporting(app)
bot = Teleflask(API_KEY, hostname=URL_HOSTNAME, hostpath=URL_PATH, hookpath="/income/{API_KEY}")
bot.init_app(app)

assert_type_or_raise(bot.bot, Bot)
AT_ADMIN_REGEX = re.compile(".*([^\\w]|^)@(admins?|{bot})(\\W|$).*".format(bot=bot.username))


@app.errorhandler(404)
def url_404(error):
    return "Nope.", 404
# end def


@app.route("/", methods=["GET","POST"])
def url_root():
    return "Yep."
# end def


@app.route("/test", methods=["GET","POST"])
def url_test():
    return "Success", 200
# end def

@app.route("/healthcheck")
def url_healthcheck():
    return '[ OK ]', 200
    #return '[FAIL]', 500
# end def



@bot.command("start")
def cmd_start(update, text):
    return HTMLMessage(l(update.message.from_peer.language_code).start_message)
# end def


@bot.command("help")
def cmd_start(update, text):
    return HTMLMessage(l(update.message.from_peer.language_code).help_message)
# end def


AUDIO_FORMATS = {
    "audio/mpeg3": "mp3",
    "audio/x-mpeg-3": "mp3",
    "audio/mpeg": "mp3",
}

from .langs import l
@bot.on_message("audio")
def msg_audio(update, msg):
    assert isinstance(msg, Message)
    assert isinstance(msg.audio, Audio)
    assert isinstance(msg.from_peer, User)
    process_audio(
        audio=msg.audio,
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        file_id=msg.audio.file_id,
        language_code=msg.from_peer.language_code
    )
# end def

def process_audio(audio, chat_id, message_id, file_id, language_code):
    assert isinstance(audio, Audio)
    assert isinstance(bot.bot, Bot)
    ln = l(language_code)
    progress = bot.bot.send_message(
        chat_id=chat_id, text=ln.progress0, disable_web_page_preview=True,
        disable_notification=False, reply_to_message_id=message_id
    )
    file_in = bot.bot.get_file(file_id)
    url = bot.bot.get_download_url(file_in)
    r = requests.get(url, stream=True)
    fake_file_in = BytesIO(r.content)
    fake_file_out = BytesIO()
    if audio.mime_type not in AUDIO_FORMATS:
        return ln.format_unsupported
    # end if
    audio_format = AUDIO_FORMATS[audio.mime_type]
    audio_in = AudioSegment.from_file(fake_file_in, format=audio_format)
    audio_out = None
    for step in boost(audio_in):
        if isinstance(step, int):
            text = getattr(ln, "progress" + str(step+1))
            try:
                bot.bot.edit_message_text(
                    text, chat_id, progress.message_id, disable_web_page_preview=True
                )
            except TgApiServerException:
                logger.exception("Editing status message failed")
            # end try
        # end if
        else:
            audio_out = step
        # end for
        bot.bot.send_chat_action(chat_id, "record_audio")
    # end def
    assert_type_or_raise(audio_out, AudioSegment)
    assert isinstance(audio_out, AudioSegment)
    bot.bot.send_chat_action(chat_id, "upload_audio")
    bot_link = "https://t.me/{bot}".format(bot=bot.username)
    tags = {
        "composer": bot_link,
        "service_name": bot_link,
        "comment": "TEST°!!!",
        "genre": "BOOSTED BASS",
        "encoder": "Horseapples 1.2 - {bot_link} (littlepip is best pony/)".format(bot_link=bot_link),
        "encoded_by": bot_link
    }
    if audio.title:
        tags["title"] = audio.title
    # end if
    if audio.artist:
        tags["artist"] = audio.performer
    # end if
    audio_out.export(fake_file_out, format="mp3",tags=tags)
    file_out = InputFile(
        fake_file_out.getvalue(), file_mime="audio/mpeg",
        file_name="bass boosted by @{bot}.mp3".format(bot=bot.username),
    )
    bot.bot.send_chat_action(chat_id, "upload_audio")
    caption = ln.caption.format(bot=bot.username)
    bot.bot.send_audio(
        chat_id, file_out,
        caption=caption, duration=audio.duration,
        performer=audio.performer, title=audio.title,
        disable_notification=False, reply_to_message_id=message_id
    )
    bot.bot.delete_message(chat_id, progress.message_id)
# end def
