from typing import List

from bearlibterminal import terminal

from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys, handle_main_menu, handle_mouse
from loader_functions import get_constants, get_game_variables, load_game, save_game
from menus import message_box, main_menu
from render_functions import render_all


def play_game(player: Entity, entities: List[Entity], game_map: GameMap, message_log: MessageLog,
              game_state: GameStates, constants):
    game_running: bool = True
    fov_recompute: bool = True
    previous_game_state: GameStates = game_state
    targeting_item = None

    while game_running:
        if fov_recompute:
            game_map.compute_fov(
                x=player.x,
                y=player.y,
                radius=constants['fov_radius'],
                light_walls=constants['fov_light_walls'],
                algorithm=constants['fov_algorithm']
            )

        render_all(entities=entities, player=player, game_map=game_map, game_state=game_state, message_log=message_log,
                   constants=constants)

        fov_recompute = False

        terminal.refresh()

        if terminal.has_input():
            terminal_input: int = terminal.read()

            action = handle_keys(key=terminal_input, game_state=game_state)
            mouse_action = handle_mouse(terminal_input)

            drop_inventory = action.get('drop_inventory')
            escape = action.get('escape')
            movement = action.get('movement')
            inventory_index = action.get('inventory_index')
            pickup = action.get('pickup')
            show_inventory = action.get('show_inventory')
            wait = action.get('wait')

            left_click = mouse_action.get('left_click')
            right_click = mouse_action.get('right_click')

            player_turn_results = []

            if escape:
                if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                    game_state = previous_game_state
                elif game_state == GameStates.TARGETING:
                    player_turn_results.append({'targeting_cancelled': True})
                else:
                    save_game(player, entities, game_map, message_log, game_state)

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

            if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                    player.inventory.items):
                item = player.inventory.items[inventory_index]

                if game_state == GameStates.SHOW_INVENTORY:
                    player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=game_map.fov))
                elif game_state == GameStates.DROP_INVENTORY:
                    player_turn_results.extend(player.inventory.drop_item(item))

            if pickup and game_state == GameStates.PLAYERS_TURN:
                for entity in entities:
                    if entity.item and entity.x == player.x and entity.y == player.y:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)

                        break
                else:
                    message_log.add_message('[color=yellow]There is nothing here to pick up.[/color]')

            if show_inventory:
                previous_game_state = game_state
                game_state = GameStates.SHOW_INVENTORY

            if drop_inventory:
                previous_game_state = game_state
                game_state = GameStates.DROP_INVENTORY

            if game_state == GameStates.TARGETING:
                if left_click:
                    target_x, target_y = left_click

                    item_use_results = player.inventory.use(
                        targeting_item,
                        entities=entities,
                        fov_map=game_map.fov,
                        target_x=target_x,
                        target_y=target_y
                    )
                    player_turn_results.extend(item_use_results)
                elif right_click:
                    player_turn_results.append({'targeting_cancelled': True})

            for player_turn_result in player_turn_results:
                dead_entity = player_turn_result.get('dead')
                item_added = player_turn_result.get('item_added')
                item_consumed = player_turn_result.get('consumed')
                item_dropped = player_turn_result.get('item_dropped')
                targeting = player_turn_result.get('targeting')
                targeting_cancelled = player_turn_result.get('targeting_cancelled')
                message = player_turn_result.get('message')

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                if item_added:
                    entities.remove(item_added)

                    game_state = GameStates.ENEMY_TURN

                if item_consumed:
                    game_state = GameStates.ENEMY_TURN

                if item_dropped:
                    entities.append(item_dropped)

                    game_state = GameStates.ENEMY_TURN

                if message:
                    message_log.add_message(message)

                if targeting:
                    previous_game_state = GameStates.PLAYERS_TURN
                    game_state = GameStates.TARGETING

                    targeting_item = targeting

                    message_log.add_message(targeting_item.item.targeting_message)

                if targeting_cancelled:
                    game_state = previous_game_state

                    message_log.add_message('Targeting cancelled')

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai:
                        enemy_turn_results = entity.ai.take_turn(target=player, game_map=game_map, entities=entities)

                        for enemy_turn_result in enemy_turn_results:
                            message = enemy_turn_result.get('message')
                            dead_entity = enemy_turn_result.get('dead')

                            if message:
                                message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, game_state = kill_player(dead_entity)
                                else:
                                    message = kill_monster(dead_entity)

                                message_log.add_message(message)

                                if game_state == GameStates.PLAYER_DEAD:
                                    break

                        if game_state == GameStates.PLAYER_DEAD:
                            break
                else:
                    game_state = GameStates.PLAYERS_TURN

        terminal.clear()


def main():
    constants = get_constants()

    terminal.open()
    terminal.set(f'window: size={constants["screen_width"]}x{constants["screen_height"]}, title="{constants["window_title"]}"; input: filter=[keyboard, mouse+]')

    player: Entity = None
    entities: List[Entity] = []
    game_map: GameMap = None
    message_log: MessageLog = None
    game_state: GameStates = None

    show_main_menu: bool = True
    show_load_error_message: bool = False

    while True:
        if show_main_menu:
            main_menu(screen_width=constants['screen_width'], screen_height=constants['screen_height'])

            if show_load_error_message:
                message_box(
                    header='No saved game to load.',
                    width=50,
                    screen_width=constants['screen_width'],
                    screen_height=constants['screen_height']
                )

            if terminal.has_input():
                terminal_input: int = terminal.read()

                action = handle_main_menu(key=terminal_input)

                new_game = action.get('new_game')
                load_saved_game = action.get('load_saved_game')
                exit_game = action.get('exit_game')

                if show_load_error_message and (new_game or load_saved_game or exit_game):
                    show_load_error_message = False
                elif new_game:
                    player, entities, game_map, message_log, game_state = get_game_variables(constants)
                    game_state = GameStates.PLAYERS_TURN

                    show_main_menu = False
                elif load_saved_game:
                    try:
                        player, entities, game_map, message_log, game_state = load_game()
                        show_main_menu = False
                    except FileNotFoundError:
                        show_load_error_message = True
                elif exit_game:
                    break

            terminal.refresh()

        else:
            play_game(
                player=player,
                entities=entities,
                game_map=game_map,
                message_log=message_log,
                game_state=game_state,
                constants=constants
            )

            show_main_menu = True

        terminal.clear()
    terminal.close()


if __name__ == '__main__':
    main()
