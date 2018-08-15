import logging
import telegram
import threading
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters
from telegram import KeyboardButton
import parser
from parser import getNearestAtms


lock = threading.Lock()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '697931558:AAFTBIorcFD5l6n2kFI-lHGALTD_jlamDA4'

def get_location(bot, update):
	location_keyboard = KeyboardButton(text="send location",  request_location=True)           #creating location button object
	custom_keyboard = [[ location_keyboard]] #creating keyboard object
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)                                                                                  
	update.message.reply_text("This bot requires to know your location before continuing", reply_markup=reply_markup)


def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="This bot will help you find the nearest ATM to your location\n Type /help in order to get information about the commands")

def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Commands:\n /start - Get welcome message \n /link - Get nearest LINK ATMs \n /banelco - Get nearest BANELCO ATMs \n ""\n This bot only shows the 3 nearest ATMs within 500metre radius \n ""\n This bot requieres access to your location" )


def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"' % (update, error))

# Write your handlers here
def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command. \n Type \help to get a list of possible commands.")

def link_atms(bot, update, chat_data):
	chat_data['red'] = 'LINK'
	get_location(bot, update)



def banelco_atms(bot, update, chat_data):
	chat_data['red'] = 'BANELCO'
	get_location(bot, update)



def parseLocation(bot, update, chat_data):
	reply_markup = telegram.ReplyKeyboardRemove()
	lock.acquire()
	if not'red' in chat_data or chat_data['red']=='NONE':
		bot.send_message(chat_id=update.message.chat_id, text="To get the nearest ATMs type /banelco or /link", reply_markup=reply_markup)
	else:
		bankingNetwork = chat_data['red']
		chat_data['red'] = 'NONE'
		msgAndURL = getNearestAtms(update.message.location, bankingNetwork)
		listOfAtms = msgAndURL[0]
		url = msgAndURL[1]
		print (url)
		if len(listOfAtms) == 0:
			bot.send_message(chat_id=update.message.chat_id, text="There are no nearby " + bankingNetwork +" ATMs", reply_markup=reply_markup)
		else:
			msg = "Nearby " + bankingNetwork + " ATMs \n"
			msg += listOfAtms
			bot.send_message(chat_id=update.message.chat_id, text=msg)
			bot.send_photo(chat_id=update.message.chat_id, photo=url)
	lock.release()
	

def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
    	bot = Bot(TOKEN)
    	update_queue = Queue()
    	dp = Dispatcher(bot, update_queue)
    else:
    	updater = Updater(TOKEN)
    	bot = updater.bot
    	dp = updater.dispatcher
    	dp.add_handler(CommandHandler("start", start))
    	dp.add_handler(CommandHandler("help", help))
        # log all errors
    	dp.add_error_handler(error)
    	# Add your handlers here
    	dp.add_handler(CommandHandler('link', link_atms, pass_chat_data=True))
    	dp.add_handler(CommandHandler('banelco', banelco_atms, pass_chat_data=True))
    	dp.add_handler(MessageHandler(Filters.command, unknown))
    	dp.add_handler(MessageHandler(Filters.location, parseLocation, pass_chat_data=True))
    if webhook_url:
    	bot.set_webhook(webhook_url=webhook_url)
    	thread = Thread(target=dp.start, name='dispatcher')
    	thread.start()
    	return update_queue, bot
    else:
    	bot.set_webhook()  # Delete webhook
    	updater.start_polling()
    	updater.idle()


if __name__ == '__main__':
	setup()