from bearlibterminal import terminal

from components.inventory import Inventory


def inventory_menu(header: str, inventory: Inventory, inventory_width: int, screen_width: int, screen_height: int):
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(header=header, options=options, width=inventory_width, screen_width=screen_width, screen_height=screen_height)


def main_menu(screen_width: int, screen_height: int):
    menu(
        header='',
        options=['Play a new game', 'Continue last game', 'Quit'],
        width=24,
        screen_width=screen_width,
        screen_height=screen_height
    )


def menu(header: str, options, width: int, screen_width: int, screen_height: int):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    terminal.layer = 10

    _, header_height = terminal.measuref(header)
    height = len(options) + header_height

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    letter_index = ord('a')

    terminal.printf(x, y, header)

    y += 1

    for option_text in options:
        text = f'({chr(letter_index)}) {option_text}'
        terminal.printf(x, y, text)

        y += 1
        letter_index += 1

    terminal.layer = 0


def message_box(header: str, width: int, screen_width: int, screen_height: int):
    menu(
        header=header,
        options=[],
        width=width,
        screen_width=screen_width,
        screen_height=screen_height
    )
