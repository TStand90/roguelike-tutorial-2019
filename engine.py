from bearlibterminal import terminal

from input_handlers import handle_keys


def main():
    window_title: str = 'Bearlibterm/TCOD Roguelike'

    screen_width: int = 80
    screen_height: int = 25

    game_running: bool = True

    player_x: int = int(screen_width / 2)
    player_y: int = int(screen_height / 2)

    terminal.open()
    terminal.set(f'window: size={screen_width}x{screen_height}, title="{window_title}";')

    while game_running:
        terminal.printf(player_x, player_y, '@')

        terminal.refresh()

        if terminal.has_input():
            terminal_input: int = terminal.read()

            action = handle_keys(terminal_input)

            escape = action.get('escape')
            movement = action.get('movement')

            if escape:
                game_running = False

            if movement:
                dx, dy = movement

                player_x += dx
                player_y += dy

        terminal.clear()

    terminal.close()


if __name__ == '__main__':
    main()
