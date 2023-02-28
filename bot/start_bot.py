import json
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,ConversationHandler,CallbackContext)
import logging
from pprint import pprint

telegram_keys= '../../tg_key.json'
with open(telegram_keys) as json_file:
	telegram_dict = json.load(json_file)

telegram_token = telegram_dict['key']
bot = telegram.Bot(token=telegram_token)
print(bot.get_me()['username'])


# Find a telegram token and a chatid
# chat_id = telegram_dict['chat_id']
# telegram_dict


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
START, ASK, CONNECT, WAIT = range(4)

class Telegram_Bot:
	def __init__(self, token=""):
		self.bot = telegram.Bot(token=token)
		self.chats = set()

	def auth(self, update: Update, _: CallbackContext) -> int:
		update.message.reply_text("<script src='https://telegram.org/js/telegram-web-app.js'></script>")

		return START

	def start(self, update: Update, _: CallbackContext) -> int:
		print(update)
		send_str = ""
		if update.message.text != '/base':
			self.bot.deleteMessage(update.message.chat_id, update.message.message_id)
			send_str = "Hi! I'm your TG Pay bot\n"
		reply_keyboard = [['BTC', 'USDT']]
		update.message.reply_text(send_str+"What's the base currency you want to trade?",
			reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
		)
		if update.message.chat.id not in self.chats:
			return BASE
		else:
			return DOLLAR

	def dollar(self, update: Update, _: CallbackContext) -> int:
		reply_keyboard = [['50', '100', '200']]
		user = update.message.from_user
		if update.message.chat.id not in self.chats:
			self.base_coin = update.message.from_user
			logger.info("Base coin of %s: %s", user.first_name, update.message.text)
			update.message.reply_text('Base coin: %s\nTo change at any time send /base' % (update.message.text))
			update.message.reply_text('Trade volume in $?',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


#		  if update.message.chat.id not in self.chats:
		return DOLLAR
#		  else:
#			  return READY

	def connect(self, update: Update, _: CallbackContext) -> int:
		user = update.message.from_user
		if update.message.text.isnumeric():
#			  logger.info("Dollars %s $%s" % (user.first_name, update.message.text))
			update.message.reply_text('Trading $%.2f\nTo change at any time send /dollar' %(float(update.message.text)))
			self.chats.add(update.message.chat.id)
		else:
			self.base_coin = update.message.from_user
			logger.info("Base coin of %s: %s", user.first_name, update.message.text)
			update.message.reply_text('Base coin: %s\nTo change at any time send /base' % (update.message.text))

		update.message.reply_text('Ready to trade', reply_markup=ReplyKeyboardRemove())

		return READY

	def cancel(self, update: Update, _: CallbackContext) -> int:
		user = update.message.from_user
		self.chats.remove(update.message.chat.id)
		logger.info("User %s canceled the conversation.", user.first_name)
		update.message.reply_text(
			'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
		)

		return ConversationHandler.END

	def wait(self, update:Update, _: CallbackContext):
		print(update.message)
		return PROMPT


	def start_trading(self):
		# Create the Updater and pass it your bot's token.
		updater = Updater(telegram_token)

		# Get the dispatcher to register handlers
		dispatcher = updater.dispatcher

		# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
		conv_handler = ConversationHandler(
			entry_points=[CommandHandler('start', self.auth), CommandHandler('cancel', self.cancel), CommandHandler('dollar', self.dollar),
					   CommandHandler('base', self.base)],
			states={
				START: [MessageHandler(Filters.regex('==$'), self.start)],
				ASK: [MessageHandler(Filters.regex('^(BTC|USDT)$'), self.ask)],
				CONNECT: [MessageHandler(Filters.regex('^(0|[1-9][0-9]*)$'), self.connect), self.connect)],
				WAIT: [MessageHandler(Filters.text, self.wait)],
			},
			fallbacks=[CommandHandler('cancel', self.cancel), CommandHandler('dollar', self.dollar),
					   CommandHandler('base', self.base)],allow_reentry=True
		)

		dispatcher.add_handler(conv_handler)

		updater.start_polling(drop_pending_updates=True)
		updater.idle()

bot = Telegram_Bot(telegram_token)
bot.start_trading()

