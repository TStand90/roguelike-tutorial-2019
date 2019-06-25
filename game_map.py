from random import randint

from bearlibterminal import terminal

from tcod.map import Map


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class GameMap(Map):
    def __init__(self, width, height):
        super().__init__(width=width, height=height, order='F')

        self.transparent[:] = False
        self.walkable[:] = False

    def create_h_tunnel(self, x1, x2, y):
        min_x: int = min(x1, x2)
        max_x: int = max(x1, x2) + 1

        self.walkable[min_x:max_x, y] = True
        self.transparent[min_x:max_x, y] = True

    def create_room(self, room):
        self.walkable[room.x1+1:room.x2, room.y1+1:room.y2] = True
        self.transparent[room.x1+1:room.x2, room.y1+1:room.y2] = True

    def create_v_tunnel(self, y1, y2, x):
        min_y: int = min(y1, y2)
        max_y: int = max(y1, y2) + 1

        self.walkable[x, min_y:max_y] = True
        self.transparent[x, min_y:max_y] = True

    def is_blocked(self, x, y):
        return not self.walkable[x, y]

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player):
        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

    def render(self, colors):
        for y in range(self.height):
            for x in range(self.width):
                wall = self.is_blocked(x, y)

                if wall:
                    terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_wall")}]#[/color]')
                else:
                    terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_ground")}].[/color]')
