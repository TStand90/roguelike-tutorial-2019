from bearlibterminal import terminal

import tcod
from tcod.map import Map


class GameMap(Map):
    def __init__(self, width, height):
        super().__init__(width=width, height=height, order='F')

        self.transparent[:] = True
        self.walkable[:] = True

        self.walkable[30:33,8] = False

    def is_blocked(self, x, y):
        return not self.walkable[x, y]

    def render(self, colors):
        for y in range(self.height):
            for x in range(self.width):
                wall = self.is_blocked(x, y)

                if wall:
                    # console.print(x=x, y=y, string=' ', bg=colors.get('dark_wall'))
                    terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_wall")}]#[/color]')
                else:
                    # console.print(x=x, y=y, string=' ', bg=colors.get('dark_ground'))
                    terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_ground")}].[/color]')
