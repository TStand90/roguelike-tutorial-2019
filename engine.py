from typing import List

from bearlibterminal import terminal

from entity import Entity
from game_map import GameMap
from input_handlers import handle_keys
from render_functions import render_all


def main():
    window_title: str = 'Bearlibterm/TCOD Roguelike'

    screen_width: int = 80
    screen_height: int = 25
    map_width: int = 80
    map_height: int = 20

    colors = {
        'dark_wall': terminal.color_from_argb(0, 0, 0, 100),
        'dark_ground': terminal.color_from_argb(0, 50, 50, 150)
    }

    game_running: bool = True

    game_map: GameMap = GameMap(width=map_width, height=map_height)

    player: Entity = Entity(
        x=int(screen_width / 2),
        y=int(screen_height / 2),
        char='@',
        color=terminal.color_from_argb(0, 255, 255, 255)
    )
    npc: Entity = Entity(
        x=int(screen_width / 2) + 2,
        y=int(screen_height / 2),
        char='@',
        color=terminal.color_from_argb(0, 255, 255, 0)
    )
    entities: List[Entity] = [npc, player]

    terminal.open()
    terminal.set(f'window: size={screen_width}x{screen_height}, title="{window_title}";')

    while game_running:
        render_all(entities=entities, game_map=game_map, colors=colors)

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

                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    player.move(dx, dy)

        terminal.clear()

    terminal.close()


if __name__ == '__main__':
    main()
