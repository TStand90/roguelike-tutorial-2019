from bearlibterminal import terminal

from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from game_map import GameMap
from game_states import GameStates
from input_handlers import handle_keys
from render_functions import render_all, RenderOrder


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

    fighter_component: Fighter = Fighter(hp=30, defense=2, power=5)
    player: Entity = Entity(
        x=0,
        y=0,
        char='@',
        color=terminal.color_from_argb(0, 255, 255, 255),
        name='Player',
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component
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

        render_all(entities=entities, player=player, game_map=game_map, screen_height=screen_height, colors=colors)

        fov_recompute = False

        terminal.refresh()

        if terminal.has_input():
            terminal_input: int = terminal.read()

            action = handle_keys(terminal_input)

            escape = action.get('escape')
            movement = action.get('movement')
            wait = action.get('wait')

            player_turn_results = []

            if escape:
                game_running = False

            if movement and game_state == GameStates.PLAYERS_TURN:
                dx, dy = movement
                destination_x: int = player.x + dx
                destination_y: int = player.y + dy

                if not game_map.is_blocked(destination_x, destination_y):
                    target: Entity = get_blocking_entities_at_location(entities, destination_x, destination_y)

                    if target:
                        attack_results = player.fighter.attack(target=target)
                        player_turn_results.extend(attack_results)
                    else:
                        player.move(dx, dy)

                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

            if wait:
                game_state = GameStates.ENEMY_TURN

            for player_turn_result in player_turn_results:
                message = player_turn_result.get('message')
                dead_entity = player_turn_result.get('dead')

                if message:
                    print(message)

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                    print(message)

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai:
                        # entity.ai.take_turn(target=player, game_map=game_map, entities=entities)
                        enemy_turn_results = entity.ai.take_turn(target=player, game_map=game_map, entities=entities)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')

                            if message:
                                print(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, game_state = kill_player(dead_entity)
                                else:
                                    message = kill_monster(dead_entity)

                                print(message)

                                if game_state == GameStates.PLAYER_DEAD:
                                    break

                        if game_state == GameStates.PLAYER_DEAD:
                            break
                else:
                    game_state = GameStates.PLAYERS_TURN

        terminal.clear()

    terminal.close()


if __name__ == '__main__':
    main()
