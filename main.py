from dotenv import load_dotenv
from os import getenv
from gevent import spawn
from tapi import *

from insect import call_insect

load_dotenv()

def make_responce(text):
    print('text =', text)
    return [
        {
            'type': 'article',
            'id': text,
            'title': text,
            'input_message_content': {
                'message_text': text
            }
        }
    ]

@greenlet
@ignore_exc(AttributeError)
def handle_message(bot, update):
    if (msg := update.message):
        text = msg.text
        if text.startswith('/'):
            if text.strip() == '/start':
                reply = 'Hello, Im insectbot\\! I can calculate various things for you with [insect](https://github.com/sharkdp/insect)\\!\n\n'
                reply += 'Just send me some math expression and feel free to use units\\.\n'
                reply += 'I can also work inline, but won\'t recomend that for large expressions\\.'
                bot.send_message(
                    chat_id=msg.chat.id,
                    text=reply,
                    disable_web_page_preview=True,
                    parse_mode='MarkdownV2'
                    )
            return
        bot.send_message(chat_id=msg.chat.id, text=call_insect(text))


@greenlet
@ignore_exc(AttributeError)
def handle_inline(bot, update):
    if (query := update.inline_query):
        qid = query.id
        text = query.query
        if not text:
            return
        ires = make_responce(f'{text} = {call_insect(text)}')
        result = bot.answer_inline(
            inline_query_id=qid,
            results=ires
        )

@bot(getenv('TOKEN'))
def mainloop(bot):
    for updates in bot.updates(timeout=15):
        for update in updates:
            handle_message(bot, update)
            handle_inline(bot, update)


if __name__ == '__main__':
    mainloop()
