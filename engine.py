from typing import List

from bearlibterminal import terminal

from entity import Entity
from game_map import GameMap
from input_handlers import handle_keys
from render_functions import render_all


def main():
    window_title: str = 'Bearlibterm/TCOD Roguelike'

    screen_width: int = 120
    screen_height: int = 45
    map_width: int = 80
    map_height: int = 40

    room_max_size: int = 10
    room_min_size: int = 6
    max_rooms: int = 30

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    colors = {
        'dark_wall': terminal.color_from_argb(0, 0, 0, 100),
        'dark_ground': terminal.color_from_argb(0, 50, 50, 150),
        'light_wall': terminal.color_from_argb(0, 255, 255, 255),
        'light_ground': terminal.color_from_argb(0, 255, 255, 255)
    }

    game_running: bool = True

    fov_recompute: bool = True

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

    game_map: GameMap = GameMap(width=map_width, height=map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    terminal.open()
    terminal.set(f'window: size={screen_width}x{screen_height}, title="{window_title}";')

    while game_running:
        if fov_recompute:
            game_map.compute_fov(
                x=player.x,
                y=player.y,
                radius=fov_radius,
                light_walls=fov_light_walls,
                algorithm=fov_algorithm
            )

        render_all(entities=entities, game_map=game_map, colors=colors)

        fov_recompute = False

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

                    fov_recompute = True

        terminal.clear()

    terminal.close()


if __name__ == '__main__':
    main()
