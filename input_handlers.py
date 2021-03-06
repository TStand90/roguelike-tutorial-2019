from bearlibterminal import terminal

from game_states import GameStates


KEY_MAPPINGS = {
    'drop_inventory': (terminal.TK_D,),
    'escape': (terminal.TK_ESCAPE,),
    'exit_game': (terminal.TK_C, terminal.TK_ESCAPE,),
    'load_saved_game': (terminal.TK_B,),
    'move_north': (terminal.TK_UP, terminal.TK_K),
    'move_south': (terminal.TK_DOWN, terminal.TK_J,),
    'move_east': (terminal.TK_RIGHT, terminal.TK_L),
    'move_west': (terminal.TK_LEFT, terminal.TK_H,),
    'move_northeast': (terminal.TK_U,),
    'move_northwest': (terminal.TK_Y,),
    'move_southeast': (terminal.TK_N,),
    'move_southwest': (terminal.TK_B,),
    'new_game': (terminal.TK_A,),
    'pickup': (terminal.TK_G,),
    'show_inventory': (terminal.TK_I,),
    'take_stairs': (terminal.TK_ENTER,),
    'wait': (terminal.TK_PERIOD,),
}


def handle_keys(key: int, game_state: GameStates):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)

    return {}


def handle_inventory_keys(key):
    index = int(key) - 4

    if index in range(26):
        return {'inventory_index': index}

    if key in KEY_MAPPINGS['escape']:
        return {'escape': True}

    return {}


def handle_main_menu(key):
    if key in KEY_MAPPINGS['new_game']:
        return {'new_game': True}
    elif key in KEY_MAPPINGS['load_saved_game']:
        return {'load_saved_game': True}
    elif key in KEY_MAPPINGS['exit_game']:
        return {'exit_game': True}

    return {}


def handle_mouse(mouse_input):
    mouse_x: int = terminal.state(terminal.TK_MOUSE_X)
    mouse_y: int = terminal.state(terminal.TK_MOUSE_Y)

    if mouse_input == terminal.TK_MOUSE_LEFT:
        return {'left_click': (mouse_x, mouse_y)}
    elif mouse_input == terminal.TK_MOUSE_RIGHT:
        return {'right_click': (mouse_x, mouse_y)}

    return {}


def handle_player_dead_keys(key: int):
    if key in KEY_MAPPINGS['show_inventory']:
        return {'show_inventory': True}
    elif key in KEY_MAPPINGS['escape']:
        return {'escape': True}

    return {}


def handle_player_turn_keys(key: int):
    if key in KEY_MAPPINGS['move_north']:
        return {'movement': (0, -1)}
    elif key in KEY_MAPPINGS['move_south']:
        return {'movement': (0, 1)}
    elif key in KEY_MAPPINGS['move_east']:
        return {'movement': (1, 0)}
    elif key in KEY_MAPPINGS['move_west']:
        return {'movement': (-1, 0)}
    elif key in KEY_MAPPINGS['move_northeast']:
        return {'movement': (1, -1)}
    elif key in KEY_MAPPINGS['move_northwest']:
        return {'movement': (-1, -1)}
    elif key in KEY_MAPPINGS['move_southeast']:
        return {'movement': (1, 1)}
    elif key in KEY_MAPPINGS['move_southwest']:
        return {'movement': (-1, 1)}
    elif key in KEY_MAPPINGS['wait']:
        return {'wait': True}

    if key in KEY_MAPPINGS['pickup']:
        return {'pickup': True}
    elif key in KEY_MAPPINGS['drop_inventory']:
        return {'drop_inventory': True}
    elif key in KEY_MAPPINGS['show_inventory']:
        return {'show_inventory': True}

    if key in KEY_MAPPINGS['take_stairs']:
        return {'take_stairs': True}

    if key in KEY_MAPPINGS['escape']:
        return {'escape': True}

    return {}


def handle_targeting_keys(key):
    if key in KEY_MAPPINGS['escape']:
        return {'exit': True}

    return {}
