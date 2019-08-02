import math
from typing import List

from bearlibterminal import terminal
import tcod
import tcod.path

from render_functions import RenderOrder


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    # def __init__(self, x, y, char, color):
    def __init__(self, x: int, y: int, char: str, color, name: str, blocks: bool = False,
                 render_order: RenderOrder = RenderOrder.CORPSE, ai=None, fighter=None, inventory=None, item=None):
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color = color
        self.name: str = name
        self.blocks: bool = blocks
        self.render_order = render_order

        self.ai = ai
        self.fighter = fighter
        self.inventory = inventory
        self.item = item

        if self.ai:
            self.ai.owner = self

        if self.fighter:
            self.fighter.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.item:
            self.item.owner = self

    def distance(self, target_x, target_y):
        return math.sqrt((target_x - self.x) ** 2 + (target_y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(dx ** 2 + dy ** 2)

    def draw(self):
        """
        Draw the entity to the terminal
        """
        terminal.printf(x=self.x, y=self.y, s=f'[color={self.color}]{self.char}[/color]')

    def move(self, dx, dy):
        """
        Move the entity by a given amount
        """
        self.x += dx
        self.y += dy

    def move_astar(self, target, entities, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = tcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                tcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight, not game_map.tiles[x1][y1].blocked)

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                tcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

            # Delete the path to free memory
        tcod.path_delete(my_path)

    def move_towards(self, target_x, target_y, game_map, entities):
        astar = tcod.path.AStar(game_map.walkable, diagonal=1.41)
        path = astar.get_path(self.x, self.y, target_x, target_y)

        if path:
            dx = path[0][0] - self.x
            dy = path[0][1] - self.y

            if game_map.walkable[path[0][0], path[0][1]] and not get_blocking_entities_at_location(entities,
                                                                                                   self.x + dx,
                                                                                                   self.y + dy):
                self.move(dx, dy)


def get_blocking_entities_at_location(entities: List[Entity], destination_x: int, destination_y: int) -> [Entity, None]:
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
