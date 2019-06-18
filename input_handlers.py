from bearlibterminal import terminal


def handle_keys(key: int):
    if key == terminal.TK_UP:
        return {'movement': (0, -1)}
    elif key == terminal.TK_DOWN:
        return {'movement': (0, 1)}
    elif key == terminal.TK_LEFT:
        return {'movement': (-1, 0)}
    elif key == terminal.TK_RIGHT:
        return {'movement': (1, 0)}

    if key == terminal.TK_ESCAPE:
        return {'escape': True}

    return {}
