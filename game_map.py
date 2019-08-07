from random import randint

from bearlibterminal import terminal
import numpy
from tcod.map import Map

from components.ai import BasicMonster
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.fighter import Fighter
from components.item import Item

from entity import Entity

from item_functions import cast_confuse, cast_fireball, cast_lightning, heal

from random_utils import from_dungeon_level, random_choice_from_dict

from render_functions import RenderOrder


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


class GameMapFloor(Map):
    def __init__(self, width: int, height: int, dungeon_level: int = 1):
        super().__init__(width=width, height=height, order='F')

        self.explored = numpy.zeros((width, height), dtype=bool, order='F')
        self.transparent[:] = False
        self.walkable[:] = False
        self.down_stairs = numpy.zeros((width, height), dtype=bool, order='F')
        self.up_stairs = numpy.zeros((width, height), dtype=bool, order='F')

        self.dungeon_level: int = dungeon_level

    def to_json(self):
        json_data = {
            'width': self.width,
            'height': self.height,
            'down_stairs': self.down_stairs.tolist(),
            'dungeon_level': self.dungeon_level,
            'explored': self.explored.tolist(),
            'transparent': self.transparent.tolist(),
            'walkable': self.walkable.tolist(),
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        game_map = cls(width=json_data['width'], height=json_data['height'], dungeon_level=json_data['dungeon_level'])

        for y in range(game_map.height):
            for x in range(game_map.width):
                game_map.down_stairs[x, y] = json_data['down_stairs'][x][y]
                game_map.explored[x, y] = json_data['explored'][x][y]
                game_map.transparent[x, y] = json_data['transparent'][x][y]
                game_map.walkable[x, y] = json_data['walkable'][x][y]

        return game_map

    @property
    def down_stairs_location(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.down_stairs[x, y]:
                    return x, y

        return None

    @property
    def up_stairs_location(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.up_stairs[x, y]:
                    return x, y

        return None

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

    def make_map(self, player, entities, constants):
        rooms = []
        num_rooms = 0

        center_of_first_room_x: int = None
        center_of_first_room_y: int = None
        center_of_last_room_x: int = None
        center_of_last_room_y: int = None

        for r in range(constants['max_rooms']):
            # random width and height
            w = randint(constants['room_min_size'], constants['room_max_size'])
            h = randint(constants['room_min_size'], constants['room_max_size'])
            # random position without going out of the boundaries of the map
            x = randint(0, constants['map_width'] - w - 1)
            y = randint(0, constants['map_height'] - h - 1)

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

                center_of_last_room_x = new_x
                center_of_last_room_y  = new_y

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y

                    center_of_first_room_x = new_x
                    center_of_first_room_y = new_y
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

                self.place_entities(new_room, entities)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        self.down_stairs[center_of_last_room_x, center_of_last_room_y] = True

        if self.dungeon_level != 1 and center_of_first_room_x and center_of_first_room_y:
            print(self.dungeon_level)
            self.up_stairs[center_of_first_room_x, center_of_first_room_y] = True

    # def next_floor(self, player, message_log, constants):
    #     self.dungeon_level += 1
    #     entities = [player]
    #
    #     self.explored = numpy.zeros((self.width, self.height), dtype=bool, order='F')
    #     self.transparent[:] = False
    #     self.walkable[:] = False
    #     self.down_stairs = numpy.zeros((self.width, self.height), dtype=bool, order='F')
    #
    #     self.make_map(player, entities, constants)
    #
    #     player.fighter.heal(player.fighter.max_hp // 2)
    #
    #     message_log.add_message('[color=green]You take a moment to rest, and recover your strength.[/color]')
    #
    #     return entities
    #
    # def previous_floor(self, player, message_log, constants):
    #     self.dungeon_level -= 1
    #     entities = [player]
    #
    #     self.explored = numpy.zeros((self.width, self.height), dtype=bool, order='F')
    #     self.transparent[:] = False
    #     self.walkable[:] = False
    #     self.down_stairs = numpy.zeros((self.width, self.height))
    #
    #     self.make_map(player=player, entities=entities, constants=constants)
    #
    #     message_log.add_message('[color=green]You ascend.[/color]')
    #
    #     return entities

    def place_entities(self, room, entities):
        # Get a random number of monsters
        max_monsters_per_room = from_dungeon_level(table=[[2, 1], [3, 4], [5, 6]], dungeon_level=self.dungeon_level)
        max_items_per_room = from_dungeon_level(table=[[1, 1], [2, 4]], dungeon_level=self.dungeon_level)

        number_of_monsters: int = randint(0, max_monsters_per_room)
        number_of_items: int = randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level(table=[[15, 3], [30, 5], [60, 7]], dungeon_level=self.dungeon_level)
        }
        item_chances = {
            'healing_potion': 35,
            'sword': from_dungeon_level(table=[[5, 4]], dungeon_level=self.dungeon_level),
            'shield': from_dungeon_level(table=[[15, 8]], dungeon_level=self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'orc':
                    fighter_component: Fighter = Fighter(hp=10, base_defense=0, base_power=3)
                    ai_component: BasicMonster = BasicMonster()

                    monster = Entity(
                        x=x,
                        y=y,
                        char='o',
                        color=terminal.color_from_argb(0, 63, 127, 63),
                        name='Orc',
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component
                    )
                else:
                    fighter_component: Fighter = Fighter(hp=16, base_defense=1, base_power=4)
                    ai_component: BasicMonster = BasicMonster()

                    monster = Entity(
                        x=x,
                        y=y,
                        char='T',
                        color=terminal.color_from_argb(0, 0, 127, 0),
                        name='Troll',
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component
                    )

                entities.append(monster)

        for i in range(number_of_items):
            x: int = randint(room.x1 + 1, room.x2 - 1)
            y: int = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == 'healing_potion':
                    item_component = Item(use_function=heal, amount=4)
                    item: Entity = Entity(x=x, y=y, char='!', color=terminal.color_from_argb(0, 238, 130, 238),
                                          name='Healing Potion', render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'sword':
                    equippable_component = Equippable(slot=EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(x=x, y=y, char='/', color=terminal.color_from_argb(0, 153, 204, 255), name='sword',
                                  equippable=equippable_component)
                elif item_choice == 'shield':
                    equippable_component = Equippable(slot=EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x=x, y=y, char='[', color=terminal.color_from_argb(0, 153, 204, 255), name='Shield',
                                  equippable=equippable_component)
                elif item_choice == 'fireball_scroll':
                    item_component = Item(
                        use_function=cast_fireball,
                        targeting=True,
                        targeting_message='[color=blue]Left-click a target tile for the fireball, or right-click to cancel.[/color]',
                        damage=12,
                        radius=3
                    )
                    item = Entity(x=x, y=y, char='~', color=terminal.color_from_argb(0, 255, 0, 0),
                                  name='Fireball Scroll', render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'confusion_scroll':
                    item_component = Item(
                        use_function=cast_confuse,
                        targeting=True,
                        targeting_message='[color=blue]Left-click an enemy to confuse it, or right-click to cancel.[/color]'
                    )
                    item = Entity(x=x, y=y, char='~', color=terminal.color_from_argb(0, 255, 102, 255),
                                  name='Confusion Scroll', render_order=RenderOrder.ITEM, item=item_component)
                else:
                    item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
                    item = Entity(x=x, y=y, char='~', color=terminal.color_from_argb(0, 255, 255, 0),
                                  name='Lightning Scroll', render_order=RenderOrder.ITEM, item=item_component)
                entities.append(item)

    def render(self, colors):
        for y in range(self.height):
            for x in range(self.width):
                down_stairs = self.down_stairs[x, y]
                up_stairs = self.up_stairs[x, y]
                wall = self.is_blocked(x, y)
                visible = self.fov[x, y]

                if visible:
                    if down_stairs:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("light_ground")}]>[/color]')
                    elif up_stairs:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("light_ground")}]<[/color]')
                    elif wall:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("light_wall")}]#[/color]')
                    else:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("light_ground")}].[/color]')

                elif self.explored[x, y]:
                    if down_stairs:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_ground")}]>[/color]')
                    elif up_stairs:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_ground")}]<[/color]')
                    elif wall:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_wall")}]#[/color]')
                    else:
                        terminal.printf(x=x, y=y, s=f'[color={colors.get("dark_ground")}].[/color]')

        self.explored |= self.fov


class GameMap():
    def __init__(self, width: int, height: int, current_floor_number: int = 1, number_of_floors: int = 10,
                 floors = None):
        self.width: int = width
        self.height: int = height
        self.current_floor_number: int = current_floor_number

        if floors:
            self.floors = floors
        else:
            self.floors = []

            for i in range(number_of_floors):
                self.floors.append(GameMapFloor(width=width, height=height, dungeon_level=i+1))

    def to_json(self):
        json_data = {
            'width': self.width,
            'height': self.height,
            'current_floor_number': self.current_floor_number,
            'floors': [floor.to_json() for floor in self.floors],
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        json_floors = json_data.get('floors', [])
        floors = []

        for json_floor in json_floors:
            floors.append(GameMapFloor.from_json(json_floor))

        game_map = cls(
            width=json_data['width'],
            height=json_data['height'],
            current_floor_number=json_data['current_floor_number'],
            number_of_floors=len(floors),
            floors=floors
        )

        return game_map

    @property
    def current_floor(self) -> GameMapFloor:
        return self.floors[self.current_floor_number - 1]

    def ascend(self):
        self.current_floor_number -= 1

    def descend(self):
        self.current_floor_number += 1

    def next_floor(self, player, message_log, constants):
        self.current_floor_number += 1
        entities = [player]

        self.current_floor.explored = numpy.zeros((self.width, self.height), dtype=bool, order='F')
        self.current_floor.transparent[:] = False
        self.current_floor.walkable[:] = False
        self.current_floor.down_stairs = numpy.zeros((self.width, self.height), dtype=bool, order='F')

        self.current_floor.make_map(player, entities, constants)

        player.x, player.y = self.current_floor.up_stairs_location
        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message('[color=green]You take a moment to rest, and recover your strength.[/color]')

        return entities

    def previous_floor(self, player, message_log, constants):
        self.current_floor_number -= 1
        entities = [player]

        self.current_floor.explored = numpy.zeros((self.width, self.height), dtype=bool, order='F')
        self.current_floor.transparent[:] = False
        self.current_floor.walkable[:] = False
        self.current_floor.down_stairs = numpy.zeros((self.width, self.height), dtype=bool, order='F')

        self.current_floor.make_map(player, entities, constants)

        player.x, player.y = self.current_floor.down_stairs_location
        message_log.add_message('[color=green]You ascend.[/color]')

        return entities
