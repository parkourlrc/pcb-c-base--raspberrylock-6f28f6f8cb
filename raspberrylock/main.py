#!/usr/bin/env python3
import asyncio
import logging
import sys

import click
import uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

import raspberrylock.gpio_tasks

__version__ = '2.0.0'

log = logging.getLogger("asyncio")


def setup_logging(log_level: str):
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
keyboard_rows = []
keyboard_cols = []

PLAYER = 'aplay'

MONGO = None

STATE = 0
UID = ''
PIN = ''
STALE_TIMEOUT = 30   # seconds
RESET_TIMER = STALE_TIMEOUT
UI_IS_LOCKED = False


def homepage(request):
    return PlainTextResponse('Hello, world!')

routes = [
    Route('/', homepage),
]

async def main_loop(log_level, event_queue):
    
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
    setup_logging(log_level)
    event_queue = asyncio.queues.Queue()
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.create_task(raspberrylock.gpio_tasks.button_ctl(stop_event, event_queue))
    loop.create_task(main_loop(log_level, event_queue))
    app = Starlette(debug=True, routes=routes)
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    cli_main()