from typing import List, TYPE_CHECKING

from random import randint


if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap


class BasicMonster:
    def to_json(self):
        json_data = {
            'name': self.__class__.__name__
        }

        return json_data

    @classmethod
    def from_json(cls, json_data, owner):
        basic_monster = cls()

        basic_monster.owner = owner

        return basic_monster

    def take_turn(self, target: 'Entity', game_map: 'GameMap', entities: List['Entity']):
        results = []

        monster = self.owner

        if game_map.current_floor.fov[monster.x, monster.y]:
            if monster.distance_to(target) >= 2:
                monster.move_towards(target_x=target.x, target_y=target.y, game_map=game_map, entities=entities)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target=target)
                results.extend(attack_results)

        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns: int = 10):
        self.previous_ai = previous_ai
        self.number_of_turns: int = number_of_turns

    def to_json(self):
        json_data = {
            'name': self.__class__.__name__,
            'ai_data': {
                'previous_ai': self.previous_ai.__class__.__name__,
                'number_of_turns': self.number_of_turns
            }
        }

        return json_data

    @classmethod
    def from_json(cls, json_data, owner):
        previous_ai_name = json_data.get('previous_ai')
        number_of_turns = json_data.get('number_of_turns')

        if previous_ai_name == 'BasicMonster':
            previous_ai = BasicMonster()
            previous_ai.owner = owner
        else:
            previous_ai = None

        confused_monster = cls(previous_ai=previous_ai, number_of_turns=number_of_turns)
        confused_monster.owner = owner

        return confused_monster

    def take_turn(self, target, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map=game_map, entities=entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({
                'message': f'[color=red]The {self.owner.name} is no longer confused.[/color]'
            })

        return results
