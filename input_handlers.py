from bearlibterminal import terminal


KEY_MAPPINGS = {
    'move_north': (terminal.TK_UP, terminal.TK_K),
    'move_south': (terminal.TK_DOWN, terminal.TK_J,),
    'move_east': (terminal.TK_RIGHT, terminal.TK_L),
    'move_west': (terminal.TK_LEFT, terminal.TK_H,),
    'move_northeast': (terminal.TK_U,),
    'move_northwest': (terminal.TK_Y,),
    'move_southeast': (terminal.TK_N,),
    'move_southwest': (terminal.TK_B,),
    'wait': (terminal.TK_PERIOD,),
}


def handle_keys(key: int):
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

    if key == terminal.TK_ESCAPE:
        return {'escape': True}

    return {}
