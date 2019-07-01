from typing import List

from bearlibterminal import terminal


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    # def __init__(self, x, y, char, color):
    def __init__(self, x: int, y: int, char: str, color, name: str, blocks: bool = False):
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color = color
        self.name: str = name
        self.blocks: bool = blocks

    def draw(self):
        """
        Draw the entity to the terminal
        """
        terminal.printf(x=self.x, y=self.y, s=f'[color={self.color}]{self.char}[/color]')
        # terminal.printf(x=self.x, y=self.y, s=f'[color=red]{self.char}[/color]')
        # terminal.printf(x=self.x, y=self.y, s=self.char, color=self.color)

    def move(self, dx, dy):
        """
        Move the entity by a given amount
        """
        self.x += dx
        self.y += dy


def get_blocking_entities_at_location(entities: List[Entity], destination_x: int, destination_y: int) -> [Entity, None]:
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
