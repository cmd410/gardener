from shutil import which

from gevent.subprocess import Popen, PIPE

executable = which('insect')

def call_insect(inpt:str):
    if executable:
        result = Popen([executable, inpt], stdout=PIPE, stderr=PIPE, encoding='utf-8').communicate()
        return result[0] or result[1]
    else:
        return 'Insect was not found'
