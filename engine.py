from bearlibterminal import terminal

from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse
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
    max_items_per_room: int = 20

    message_log_location_x: int = 0
    message_log_location_y: int = map_height
    message_log_width: int = screen_width
    message_log_height: int = 5

    colors = {
        'dark_wall': terminal.color_from_argb(0, 0, 0, 100),
        'dark_ground': terminal.color_from_argb(0, 50, 50, 150),
        'light_wall': terminal.color_from_argb(0, 255, 255, 255),
        'light_ground': terminal.color_from_argb(0, 255, 255, 255)
    }

    game_running: bool = True

    fov_recompute: bool = True

    fighter_component: Fighter = Fighter(hp=30, defense=2, power=5)
    inventory_component: Inventory = Inventory(capacity=26)

    player: Entity = Entity(
        x=0,
        y=0,
        char='@',
        color=terminal.color_from_argb(0, 255, 255, 255),
        name='Player',
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component,
        inventory=inventory_component
    )
    entities = [player]

    game_map: GameMap = GameMap(width=map_width, height=map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                      max_monsters_per_room, max_items_per_room=max_items_per_room)

    game_state: GameStates = GameStates.PLAYERS_TURN
    previous_game_state: GameStates = game_state

    targeting_item = None

    message_log: MessageLog = MessageLog()

    terminal.open()
    terminal.set(f'window: size={screen_width}x{screen_height}, title="{window_title}"; input: filter=[keyboard, mouse+]')

    while game_running:
        if fov_recompute:
            game_map.compute_fov(
                x=player.x,
                y=player.y,
                radius=fov_radius,
                light_walls=fov_light_walls,
                algorithm=fov_algorithm
            )

        render_all(entities=entities, player=player, game_map=game_map, game_state=game_state, message_log=message_log,
                   screen_width=screen_width, screen_height=screen_height, colors=colors)

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
                        # entity.ai.take_turn(target=player, game_map=game_map, entities=entities)
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

    terminal.close()


if __name__ == '__main__':
    main()
