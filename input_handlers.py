from bearlibterminal import terminal

from game_states import GameStates


KEY_MAPPINGS = {
    'drop_inventory': (terminal.TK_D,),
    'escape': (terminal.TK_ESCAPE,),
    'move_north': (terminal.TK_UP, terminal.TK_K),
    'move_south': (terminal.TK_DOWN, terminal.TK_J,),
    'move_east': (terminal.TK_RIGHT, terminal.TK_L),
    'move_west': (terminal.TK_LEFT, terminal.TK_H,),
    'move_northeast': (terminal.TK_U,),
    'move_northwest': (terminal.TK_Y,),
    'move_southeast': (terminal.TK_N,),
    'move_southwest': (terminal.TK_B,),
    'pickup': (terminal.TK_G,),
    'show_inventory': (terminal.TK_I,),
    'wait': (terminal.TK_PERIOD,),
}


def handle_keys(key: int, game_state: GameStates):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)

    return {}


def handle_inventory_keys(key):
    index = int(key) - 4

    if index in range(26):
        return {'inventory_index': index}

    if key in KEY_MAPPINGS['escape']:
        return {'escape': True}

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

    if key in KEY_MAPPINGS['escape']:
        return {'escape': True}

    return {}
