from shutil import which

from gevent.subprocess import Popen, PIPE

executable = which('insect')

math_signs = '+-*^ .'

def call_insect(inpt:str):
    test_inpt = inpt
    for i in math_signs:
        test_inpt = test_inpt.replace(i, '')
    if test_inpt.isdigit():
        return eval(inpt)
    
    if not executable:
        return 'Insect was not found'

    if len(lines := inpt.split('\n')) > 1:
        process = Popen(
            [executable],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            encoding='utf-8')
        result = process.communicate(inpt+'\n')
        return result[0] or result[1]

    
    result = Popen([executable, inpt], stdout=PIPE, stderr=PIPE, encoding='utf-8').communicate()
    return result[0] or result[1]
        
