import asyncio


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


async def button_ctl(button, stop_event):
    while True:
        if button.is_pressed:
            if stop_event.is_set():
               stop_event.clear()
            else:
               stop_event.set()
        else:
            await asyncio.sleep(0.1)



