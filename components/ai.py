from typing import List

from random import randint


class BasicMonster:
    def take_turn(self, target: 'Entity', game_map: 'GameMap', entities: List['Entity']):
        results = []

        monster = self.owner

        if game_map.fov[monster.x, monster.y]:
            if monster.distance_to(target) >= 2:
                # monster.move_astar(target=target, entities=entities, game_map=game_map)
                monster.move_towards(target_x=target.x, target_y=target.y, game_map=game_map, entities=entities)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target=target)
                results.extend(attack_results)

        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns: int = 10):
        self.previous_ai = previous_ai
        self.number_of_turns: int = number_of_turns

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
