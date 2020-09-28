from string import ascii_lowercase
from shutil import which
from logging import getLogger

from gevent.subprocess import Popen, PIPE

executable = which('insect')

logger = getLogger('insect')

def call_insect(inpt:str):
    if not set(inpt.lower()).intersection(set(ascii_lowercase)):
        return eval(inpt)
    
    if not executable:
        logger.error('Insect is not installed!')
        return 'Insect was not found'

    if any([len(i) > (72 * 3)
            for i in inpt.split('\n')]):
        return 'Lines too long, not allowed!'

    process = Popen(
        [executable],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        encoding='utf-8')

    result = process.communicate(inpt+'\n')

    return result[0] or result[1]
