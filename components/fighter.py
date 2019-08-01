from entity import Entity


class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp: int = hp
        self.hp: int = hp
        self.defense: int = defense
        self.power: int = power

    def attack(self, target: Entity):
        results = []

        damage: int = self.power - target.fighter.defense

        if damage > 0:
            results.append(
                {
                    'message': f'{self.owner.name.capitalize()} attacks {target.name} for {damage} hit points.'
                }
            )
            results.extend(target.fighter.take_damage(amount=damage))
        else:
            results.append(
                {
                    'message': f'{self.owner.name.capitalize()} attacks {target.name} but does no damage.'
                }
            )

        return results

    def take_damage(self, amount: int):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner})

        return results
