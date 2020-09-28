from logging import getLogger
from functools import wraps
from types import SimpleNamespace

import gevent

from .request import make_request

logger = getLogger('bot')


def bot(token):
    def send_message(**kwargs):
        text = kwargs.get("text", "")
        logger.debug(f'''Sending message: {
            text[:32] + "..." if len(text) > 64 else ""}''')

        return  make_request(token, 'sendMessage', kwargs).get()

    def get_updates(**kwargs):
        responce = make_request(token, 'getUpdates', kwargs).get()
        updates = responce.result
        return updates
    
    def answer_inline(**kwargs):
        responce = make_request(token, 'answerInlineQuery', kwargs).get()
        return responce

    def updates(**kwargs):
        modified_kwargs = {'timeout': 30}
        modified_kwargs.update(**kwargs)
        offset = 0
        modified_kwargs.update(offset=offset)
        while True:
            updates = get_updates(**modified_kwargs)
            if updates:
                offset = updates[-1].update_id + 1
                modified_kwargs.update(offset=offset)
            yield updates

    bot = SimpleNamespace(
        send_message=send_message,
        get_updates=get_updates,
        updates=updates,
        answer_inline=answer_inline
        )
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                func(bot, *args, **kwargs)
                gevent.sleep()
        return wrapper
    return decorator