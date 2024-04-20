#!/usr/bin/env python3
import asyncio
import logging
import sys
import subprocess

import click
import uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

import raspberrylock.gpio_tasks
from raspberrylock.ldap_interface import authenticate

__version__ = '2.0.0'

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger("main")

def setup_logging(log_level: str):
    log.debug('Setting up logging ...')


def setup_logging_old(log_level: str):
    global log
    # create console handler and set level to debug
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.getLevelName(log_level))
    # add formatter to ch
    ch.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    # add ch to logger
    log.addHandler(ch)
    log.setLevel(logging.getLevelName(log_level))


door_opener = None   # initialized by init_gpios()
NUMERIC_KEYS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


PLAYER = 'aplay'

STATE = 0
UID = ''
PIN = ''
STALE_TIMEOUT = 30   # seconds
RESET_TIMER = STALE_TIMEOUT
UI_IS_LOCKED = False


log_level = logging.DEBUG

def homepage(request):
    return PlainTextResponse('Hello, world!')

routes = [
    Route('/', homepage),
]

app = Starlette(debug=True, routes=routes)

async def main_loop(log_level, event_queue):
    while True:
        await asyncio.wait_for(event_queue.get(), timeout=1.0)


def reset_state():
    global STATE, UID, PIN
    log.debug("reset state")
    STATE = 0
    UID = ''
    PIN = ''


async def timeout_reset_state():
    """
    Resets the state into its initial state if no keys have been pressed 
    for 30 s (STALE_TIMEOUT).
    """
    reset_state()   # first at the beginning
    global RESET_TIMER
    global UI_IS_LOCKED
    loop = asyncio.get_running_loop()
    while loop.is_running:
        if UI_IS_LOCKED:
            await asyncio.sleep(1.0)
            continue

        RESET_TIMER -= 1
        # logger.debug("timeout in %d" % RESET_TIMER)
        if RESET_TIMER <= 0:
            reset_state()
            RESET_TIMER = STALE_TIMEOUT
        await asyncio.sleep(1.0)


async def open_if_correct(uid, pin):
    """
    BLOCKING! Maybe this function needs to run in an executor thread.
    """
    print('checking ldap ...')
    try:
        if authenticate(uid, pin):
            log.info("Auth works")
            #subprocess.Popen([PLAYER, './themes/%s/success.wav' % THEME],
            #                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #next_theme()
            door_opener.on()
            await asyncio.sleep(1)
            door_opener.off()
            await asyncio.sleep(8)

        else:
            log.info("Auth NO works")
            #subprocess.Popen([PLAYER, './themes/%s/fail.wav' % THEME],
            #                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await asyncio.sleep(2)
    except Exception as error:
        log.error(error)
        # subprocess.Popen([PLAYER, './themes/%s/error.wav' % THEME],
        #                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await asyncio.sleep(2)


async def control_loop(event_queue):
    global RESET_TIMER
    global STATE, UID, PIN
    reset_state()

    # Main state machine.
    # Expects the user to enter her UID, then PIN like this:
    # [A] 2903 [A] 123456 A
    # The first and second 'A' presses are optional and ignored for compatibility with the replicator.
    # The second 'A' would be mandatory for a non-4-digit UID, luckily all c-base UIDs are 4-digit, though.
    loop = asyncio.get_running_loop()
    while loop.is_running:
        key = await event_queue.get()
        log.info('state={}, got symbol {}'.format(STATE, '#'))
        RESET_TIMER = STALE_TIMEOUT
        event_queue.task_done()
        if STATE == 0:
            if key == 'A':
                # print('Enter UID:')
                STATE = 0
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key in NUMERIC_KEYS:
                UID += key
                STATE = 1
                continue
        elif STATE == 1:
            if key in NUMERIC_KEYS:
                if len(UID) < 4:
                    UID += key
                    STATE = 1
                else:
                    PIN += key
                    STATE = 2
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key == 'A':
                STATE = 2
                continue
        elif STATE == 2:
            if key in NUMERIC_KEYS:
                PIN += key
                continue
            elif key == 'C':
                reset_state()
                continue
            elif key == 'A':
                loop = asyncio.get_running_loop()
                # Start the LDAP check
                UI_IS_LOCKED = True
                # log.warning("OPEN IF CORRECT")
                await open_if_correct(UID, PIN)
                UI_IS_LOCKED = False
                reset_state()
                continue




@app.on_event('startup')
async def app_startup():
    global log_level
    setup_logging(log_level)
    event_queue = asyncio.queues.Queue()
    stop_event = asyncio.Event()
    asyncio.create_task(raspberrylock.gpio_tasks.button_ctl(stop_event, event_queue))
    asyncio.create_task(main_loop(log_level, event_queue))
    asyncio.create_task(timeout_reset_state())
    asyncio.create_task(control_loop(event_queue))
    if log_level == 'DEBUG':
        log.debug('DEBUG logging enabled by user.')
    await asyncio.sleep(1.0)


@click.command()
@click.help_option()
@click.version_option(version=__version__, prog_name="raspberrylock-cli")
@click.option("--log-level", 'log_level', 
              default="INFO",
              help="Loging level (DEBUG, INFO, WARNING, ERROR)")
def cli_main(log_level):
    """Simple CLI program to run the raspberrylock"""
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    cli_main()