import asyncio
import logging

import gpiozero

log = logging.getLogger('asyncio')
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

ROWS = [17, 4, 3, 2]
COLS = [23, 18, 15, 14]
OPEN_PIN = 26

def init_gpios():
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setup(OPEN_PIN, GPIO.OUT)
    global door_opener
    door_opener = gpiozero.LED(OPEN_PIN)
    door_opener.off()

    for pin in ROWS:
        out_pin = gpiozero.LED(pin)
        out_pin.off()
        keyboard_rows.append(out_pin)
    for pin in COLS:
        in_pin = gpiozero.Button(pin, pull_up=False)
        keyboard_cols.append(in_pin)


def decrease_timeouts(timeouts):
    for k, v in timeouts.items():
        if v > 0:
            timeouts[k] = v - 1
    return timeouts


def decode_keypad(measurements):
    """
    x1 = (0,0,1,0)
    """
    layout = [['C', 'D', 'E', 'F'], ['B', '9', '6', '3'],
              ['0', '8', '5', '2'], ['A', '7', '4', '1']]
    for y_index, y_row in enumerate(measurements):
        for x_index, x_state in enumerate(y_row):
            if x_state > 0:
                return layout[y_index][x_index]
    return None   # No key pressed


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


async def button_ctl(button, stop_event):
    init_gpios()
    while not stop_event.is_set():
        measured = collect_measurements()
        is_pressed = decode_keypad(measured)
        if is_pressed:
            log.debug("Pressed: %s" % is_pressed)
        else:
            await asyncio.sleep(0.1)



