import json
import os
from typing import List

from bearlibterminal import terminal

from components.fighter import Fighter
from components.inventory import Inventory

from entity import Entity
from game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from render_functions import RenderOrder


def get_constants():
    window_title: str = 'Bearlibterm/TCOD Roguelike'

    screen_width: int = 120
    screen_height: int = 45
    map_width: int = 80
    map_height: int = 40

    room_max_size: int = 10
    room_min_size: int = 6
    max_rooms: int = 30

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    max_monsters_per_room: int = 3
    max_items_per_room: int = 2

    message_log_location_x: int = 0
    message_log_location_y: int = map_height
    message_log_width: int = screen_width
    message_log_height: int = 5

    colors = {
        'dark_wall': terminal.color_from_argb(0, 0, 0, 100),
        'dark_ground': terminal.color_from_argb(0, 50, 50, 150),
        'light_wall': terminal.color_from_argb(0, 255, 255, 255),
        'light_ground': terminal.color_from_argb(0, 255, 255, 255)
    }

    constants = {
        'colors': colors,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'map_height': map_height,
        'map_width': map_width,
        'max_items_per_room': max_items_per_room,
        'max_monsters_per_room': max_monsters_per_room,
        'max_rooms': max_rooms,
        'message_log_height': message_log_height,
        'message_log_location_x': message_log_location_x,
        'message_log_location_y': message_log_location_y,
        'message_log_width': message_log_width,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'screen_height': screen_height,
        'screen_width': screen_width,
        'window_title': window_title,
    }

    return constants


def get_game_variables(constants):
    fighter_component: Fighter = Fighter(hp=30, defense=2, power=5)
    inventory_component: Inventory = Inventory(capacity=26)

    player: Entity = Entity(
        x=0,
        y=0,
        char='@',
        color=terminal.color_from_argb(0, 255, 255, 255),
        name='Player',
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component,
        inventory=inventory_component
    )
    entities = [player]

    game_map: GameMap = GameMap(width=constants['map_width'], height=constants['map_height'])
    game_map.make_map(
        player=player,
        entities=entities,
        constants=constants
    )

    message_log: MessageLog = MessageLog()

    game_state: GameStates = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state


def load_game():
    if not os.path.isfile('save_game.json'):
        raise FileNotFoundError

    with open('save_game.json') as save_file:
        json_data = json.load(save_file)

    entities = [Entity.from_json(json_data=entity_json_data) for entity_json_data in json_data['entities']]
    player = entities[json_data['player_index']]

    game_map = GameMap.from_json(json_data['game_map'])
    message_log = MessageLog.from_json(json_data['message_log'])
    game_state = GameStates(json_data['game_state'])

    return player, entities, game_map, message_log, game_state


def save_game(player: Entity, entities: List[Entity], game_map: GameMap, message_log: MessageLog,
              game_state: GameStates):
    player_index = entities.index(player)
    entities_json_data = [entity.to_json() for entity in entities]
    game_map_json_data = game_map.to_json()
    message_log_json_data = message_log.to_json()
    game_state_json_data = game_state.value

    json_data = {
        'player_index': player_index,
        'entities': entities_json_data,
        'game_map': game_map_json_data,
        'message_log': message_log_json_data,
        'game_state': game_state_json_data
    }

    with open('save_game.json', 'w') as save_file:
        json.dump(json_data, save_file, indent=4)
