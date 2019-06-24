from bearlibterminal import terminal


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

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
