from bearlibterminal import terminal

from entity import Entity, get_blocking_entities_at_location
from game_map import GameMap
from game_states import GameStates
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

    max_monsters_per_room: int = 3

    colors = {
        'dark_wall': terminal.color_from_argb(0, 0, 0, 100),
        'dark_ground': terminal.color_from_argb(0, 50, 50, 150),
        'light_wall': terminal.color_from_argb(0, 255, 255, 255),
        'light_ground': terminal.color_from_argb(0, 255, 255, 255)
    }

    game_running: bool = True

    fov_recompute: bool = True

    player: Entity = Entity(
        x=0,
        y=0,
        char='@',
        color=terminal.color_from_argb(0, 255, 255, 255),
        name='Player',
        blocks=True
    )
    entities = [player]

    game_map: GameMap = GameMap(width=map_width, height=map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                      max_monsters_per_room)

    game_state: GameStates = GameStates.PLAYERS_TURN

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

            if movement and game_state == GameStates.PLAYERS_TURN:
                dx, dy = movement
                destination_x: int = player.x + dx
                destination_y: int = player.y + dy

                if not game_map.is_blocked(destination_x, destination_y):
                    target: Entity = get_blocking_entities_at_location(entities, destination_x, destination_y)

                    if target:
                        print(f'You kick the {target.name} in the shins, much to its annoyance!')
                    else:
                        player.move(dx, dy)

                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity != player:
                        print(f'The {entity.name} ponders the meaning of its existence.')

                game_state = GameStates.PLAYERS_TURN

        terminal.clear()

    terminal.close()


if __name__ == '__main__':
    main()
