#!/usr/bin/env python3
import asyncio
import logging
import sys

import click
"""
raspberrylock

Usage:
  raspberrylock [--theme <theme>]
  raspberrylock (-h | --help)
  raspberrylock --version

Options:
  -h --help        Show this screen.
  --version        Show version.
  --theme=<theme>  Sound theme [default: default].
"""

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

# GPIO.setwarnings(False)

NUMERIC_KEYS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

BOUNCE_TIME = 2  # in milliseconds
STALE_TIMEOUT = 30  # in seconds
timeouts = {'1': BOUNCE_TIME, '2': BOUNCE_TIME, '3': BOUNCE_TIME, '4': BOUNCE_TIME,
            '5': BOUNCE_TIME, '6': BOUNCE_TIME, '7': BOUNCE_TIME, '8': BOUNCE_TIME,
            '9': BOUNCE_TIME, '0': BOUNCE_TIME, 'A': BOUNCE_TIME, 'B': BOUNCE_TIME,
            'C': BOUNCE_TIME, 'D': BOUNCE_TIME, 'E': BOUNCE_TIME, 'F': BOUNCE_TIME}

Q = None
# Q = asyncio.queues.Queue()
# LOCK = RLock()

# ROWS and COLS for keyboard at HW lager
# ROWS = [24, 3, 5, 7]
# COLS = [15, 13, 11, 22]
# OPEN_PIN = 26

# Default ROWS, COLS and OPEN_PIN for all others
# ROWS = [11, 7, 5, 3]
# COLS = [16, 12, 10, 8]
ROWS = [17, 4, 3, 2]
COLS = [23, 18, 15, 14]
OPEN_PIN = 26



door_opener = None   # initialized by init_gpios()
keyboard_rows = []
keyboard_cols = []

PLAYER = 'aplay'

MONGO = None

STATE = 0
UID = ''
PIN = ''
RESET_TIMER = STALE_TIMEOUT
UI_IS_LOCKED = False


async def main(log_level):
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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(log_level))


if __name__ == '__main__':
    cli_main()