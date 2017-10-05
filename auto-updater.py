import os
import requests

w = requests.get('http://pastebin.com/raw/r2kwMqH3')
code = w.content
w.close()

if os.path.exists('bot.py'):
    f = open('bot.py', 'r')

    if f.read(22).strip() != code[0: 22].strip():
        f.close()
        print 'Downloading new version...'
        f = open('bot.py', 'wb')
        f.write(code)
        f.close()
    else:
        print 'Version check passed.'
        f.close()
else:
    print 'Downloading script...'
    f = open('bot.py', 'wb')
    f.write(code)
    f.close()

execfile('bot.py')