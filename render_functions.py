from __future__ import annotations

from enum import auto, Enum
from typing import List, TYPE_CHECKING

from bearlibterminal import terminal

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap


class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def render_all(entities: List[Entity], player: Entity, game_map: GameMap, screen_height: int, colors):
    # Draw the map
    game_map.render(colors=colors)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        if game_map.fov[entity.x, entity.y]:
            entity.draw()

    terminal.printf(1, screen_height - 2, f'HP: {player.fighter.hp}/{player.fighter.max_hp}')
