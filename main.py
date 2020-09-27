from dotenv import load_dotenv
from os import getenv
from gevent import spawn
from tapi import *

load_dotenv()

@greenlet
@ignore_exc(AttributeError)
def handle_message(bot, update):
    if (msg := update.message):
        bot.send_message(chat_id=msg.chat.id, text='hello')

@bot(getenv('TOKEN'))
def mainloop(bot):
    for updates in bot.updates(timeout=15):
        for update in updates:
            handle_message(bot, update)

if __name__ == '__main__':
    mainloop()
