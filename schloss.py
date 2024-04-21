

import asyncio
import sys
import os
import time
import random
import subprocess

import uvloop
import gpiozero
from docopt import docopt
from ldap_interface import authenticate


from sanic import Sanic
from sanic.log import logger
from sanic.response import text

__version__ = '2.0.0'



app = Sanic(__name__)


def next_theme():
    """
    Look into themes folder and find all installed themes. Get a random one which is not the current one.
    """
    global THEME
    themes = next(os.walk('./themes/'))[1]
    OLD_THEME = THEME
    while THEME != OLD_THEME:
        THEME = random.choice(themes)


# decode-keypad was here

def decrease_timeouts(timeouts):
    for k, v in timeouts.items():
        if v > 0:
            timeouts[k] = v - 1
    return timeouts


def collect_measurements():
    """
    """
    pin_state = []
    for y_pin in keyboard_rows:
        y_pin.on()
        x_pin_states = []
        for x_pin in keyboard_cols:
            pin_in = x_pin.value
            x_pin_states.append(pin_in)
        y_pin.off()
        pin_state.append(x_pin_states)
    return pin_state


def read_keypad():
    decrease_timeouts(timeouts)
    key = decode_keypad(collect_measurements())
    if key:
        if timeouts[key] > 0:
            return None
        else:
            num = random.randint(0, 9)
            subprocess.Popen([PLAYER, './themes/%s/%s.wav' % (THEME, num)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(PLAYER, './themes/%s/%s.wav' % (THEME, num))
            timeouts[key] = BOUNCE_TIME
            return key
    else:
        return None











@app.add_task
async def keypad_loop():
    global Q
    if not Q:
        Q = asyncio.queues.Queue()
    loop = asyncio.get_running_loop()
    while loop.is_running:
        key = read_keypad()
        if key:
            await Q.put(key)
        await asyncio.sleep(0.1)
    

@app.get("/")
async def hello_world(request):
    return text(f"Next timeout in %d" % RESET_TIMER)
    

if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    try:
        THEME = args['--theme']
        init_gpios()
        app.run(host="0.0.0.0", port=8888, debug=True, access_log=True)
    except KeyboardInterrupt:
        print('quitting')
