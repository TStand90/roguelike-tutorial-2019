from __future__ import annotations

from enum import auto, Enum
from typing import List, TYPE_CHECKING

from bearlibterminal import terminal

from game_states import GameStates

from menus import inventory_menu

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap
    from game_messages import MessageLog


class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def get_names_under_mouse(entities, fov_map):
    mouse_x: int = terminal.state(terminal.TK_MOUSE_X)
    mouse_y: int = terminal.state(terminal.TK_MOUSE_Y)

    names = [
        entity.name for entity in entities
        if entity.x == mouse_x and entity.y == mouse_y
           and fov_map[mouse_x, mouse_y]
    ]
    names = ', '.join(names)

    return names.capitalize()


def render_bar(x: int, y: int, total_width: int, label: str, current_value: int, maximum_value: int, text_color: str,
               bar_primary_color: str, bar_secondary_color: str):
    bar_primary_width: int = int(float(current_value) / maximum_value * total_width)
    bar_secondary_width: int = total_width - bar_primary_width

    bar_text = format(f'{label}: {current_value:02} / {maximum_value:02}', f'^{total_width}')
    bar_primary_background_text = ' ' * bar_primary_width
    bar_secondary_background_text = ' ' * bar_secondary_width

    terminal.printf(x, y, f'[bkcolor={bar_primary_color}]{bar_primary_background_text}[/bkcolor]')
    terminal.printf(x + bar_primary_width, y,
                    f'[bkcolor={bar_secondary_color}]{bar_secondary_background_text}[/bkcolor]')
    terminal.printf(x, y, bar_text)


def render_all(entities: List[Entity], player: Entity, game_map: GameMap, game_state: GameStates,
               message_log: MessageLog, screen_width: int, screen_height: int, colors):
    # Draw the map
    game_map.render(colors=colors)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        if game_map.fov[entity.x, entity.y]:
            entity.draw()

    render_bar(x=81, y=1, total_width=30, label='HP', current_value=player.fighter.hp,
               maximum_value=player.fighter.max_hp, text_color='white', bar_primary_color='green',
               bar_secondary_color='red')

    message_log.render()

    names_under_mouse = get_names_under_mouse(entities, game_map.fov)

    if names_under_mouse:
        terminal.printf(81, 5, names_under_mouse)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(
            header=inventory_title,
            inventory=player.inventory,
            inventory_width=50,
            screen_width=screen_width,
            screen_height=screen_height
        )
