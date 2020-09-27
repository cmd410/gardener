from logging import getLogger, StreamHandler, basicConfig, DEBUG
from os import getenv
from hashlib import blake2b

from gevent import spawn
from dotenv import load_dotenv

from insect import call_insect
from tapi import *

load_dotenv()

logger = getLogger('MAIN')


def make_responce(text):
    thash = blake2b(text.encode(), digest_size=32).hexdigest()
    return [
        {
            'type': 'article',
            'id': thash,
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
        formated_text = "\n\t".join(msg.text.split("\n"))
        logger.debug(f'Message:\n\t{formated_text}')
        if text.startswith('/'):
            if text.strip() == '/start':
                reply = 'Hello, Im CompXbot\\! I can calculate various things for you using [insect](https://github.com/sharkdp/insect)\\!\n\n'
                reply += 'Just send me some math expression and feel free to use units\\.\n'
                reply += 'I can also work inline, but won\'t recomend that for large expressions\\.'
                reply += '\n\n[Source code](https://github.com/cmd410/gardener)'
                bot.send_message(
                    chat_id=msg.chat.id,
                    text=reply,
                    disable_web_page_preview=True,
                    parse_mode='MarkdownV2'
                    )
            return
        answer = call_insect(text)
        bot.send_message(chat_id=msg.chat.id, text=answer)


@greenlet
@ignore_exc(AttributeError)
def handle_inline(bot, update):
    if (query := update.inline_query):
        qid = query.id
        text = query.query
        if not text:
            return
        logger.debug(f'Inline query: {text}')
        answer = call_insect(text)
        ires = make_responce(f'{text} = {answer}')
        result = bot.answer_inline(
            inline_query_id=qid,
            results=ires
        )

@bot(getenv('TOKEN'))
def mainloop(bot):
    logger.info('Bot started.')
    for updates in bot.updates(timeout=60):
        for update in updates:
            handle_message(bot, update)
            handle_inline(bot, update)


if __name__ == '__main__':
    try:
        from rich.logging import RichHandler
        handler = RichHandler(level=DEBUG)
        formater = '%(message)s'
    except ImportError:
        handler = StreamHandler()
        formater = '[%(asctime)s] [%(levelname)s]\n%(message)s\n'

    basicConfig(level=DEBUG,handlers=[handler], format=formater)
    mainloop()
