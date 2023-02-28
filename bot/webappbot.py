#!/usr/bin/env python
# pylint: disable=unused-argument,wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple example of a Telegram WebApp which displays a color picker.
The static website for this website is hosted by the PTB team for your convenience.
Currently only showcases starting the WebApp via a KeyboardButton, as all other methods would
require a bot token.
"""
import json
import logging
import os
import traceback

from telegram import __version__ as TG_VER

try:
	from telegram import __version_info__
except ImportError:
	__version_info__ = (0, 0, 0, 0, 0)	# type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
	raise RuntimeError(
		f"This example is not compatible with your current PTB version {TG_VER}. To view the "
		f"{TG_VER} version of this example, "
		f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
	)
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
	CallbackQueryHandler,
    MessageHandler,
    filters,
)
#from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
#from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext)

# Enable logging
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

try:
	with open('../../tg_key.json','r') as f:
		json_tg_key = json.load(f)
		TOKEN = json_tg_key['key']

except Exception as e:
	print(traceback.format_exc())
	TOKEN = input('Put in token here:')

START, ASK, CONNECT, WAIT = range(4)
db = {}
chats = {}

# Define a `/start` command handler.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	receive_message(update)
	await update.message.reply_text("Welcome to TeleFi")

	# Code some logic to check if the user has to recieve, check if it's screen name instead
	if update.effective_chat.id in db:
		await update.message.reply_text("You have a request from @____ to pay $___")
		# Keyboard here
		return EXIT

	await update.message.reply_text("Type $ amount for payment")
	return START


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	receive_message(update)
	await update.message.reply_text("Ask")
	return ASK


async def wait(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	receive_message(update)
	await update.message.reply_text("Wait")
	return WAIT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	receive_message(update)
	await update.message.reply_text("Wait")
	return WAIT

async def jiggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	receive_message(update)
	await update.message.reply_text("Wait")
	return WAIT

async def connect_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	receive_message(update)
	"""Send a message with a button that opens a the web app."""
	await update.message.reply_text(
		"Please press the button below to choose a color via the WebApp.",
		reply_markup=ReplyKeyboardMarkup.from_button(
			KeyboardButton(
				text="Connect wallet here!",
				web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"),
			)
		),
	)
	return ASK


# Handle incoming WebAppData
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Print the received data and remove the button."""
	print(update)
	# Here we use `json.loads`, since the WebApp sends the data JSON serialized string
	# (see webappbot.html)
	data = json.loads(update.effective_message.web_app_data.data)
	await update.message.reply_html(
		text=f"You selected the color with the HEX value <code>{data['hex']}</code>. The "
		f"corresponding RGB value is <code>{tuple(data['rgb'].values())}</code>.",
		reply_markup=ReplyKeyboardRemove(),
	)

"""
Uses a user's response to get info about that user
"""
def receive_message(update):

    # Getting data from keyboard or message
    if update.callback_query:
        text = update.callback_query.data
    else:
        text = update.message.text.replace('\n','\\n')
    # If this user has been logged in chats
    if update.effective_chat.id in chats:
        user = chats[update.effective_chat.id]
        user.last_seen = datetime.now()
        #.logger.info('Logging - %s - %s received: %s' % (update.effective_chat.id, user.email, text))
        print('Logging - %s received: %s' % (update.effective_chat.id, text))
        return user
    else:
        logger.info('Logging - %s received: %s' % (update.effective_chat.id, text))

def main() -> None:
	"""Start the bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(TOKEN).build()
	# Create the Updater and pass it your bot's token.
	#updater = Updater(telegram_token)

	# Get the dispatcher to register handlers
	#dispatcher = application.dispatcher
	#dispatcher = updater.dispatcher

	# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],
		states={
			START: [MessageHandler(filters.Regex('==$'), ask)],
			#ASK: [MessageHandler(filters.Regex('^(BTC|USDT)$'), ask)],
			ASK: [CallbackQueryHandler(ask), MessageHandler(filters.Command, ask)],
			CONNECT: [MessageHandler(filters.Regex('^(0|[1-9][0-9]*)$'), connect_wallet), connect_wallet],
			WAIT: [MessageHandler(filters.Text, wait)],
		},
		fallbacks=[CommandHandler('cancel', cancel)],allow_reentry=True
	)

	application.add_handler(conv_handler)
	#application.add_handler(CommandHandler("start", start))
	application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

	# Run the bot until the user presses Ctrl-C
	application.run_polling()


if __name__ == "__main__":
	main()
