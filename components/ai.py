from typing import List


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
