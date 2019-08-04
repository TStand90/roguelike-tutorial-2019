from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity


class Fighter:
    def __init__(self, hp: int, defense: int, power: int, max_hp: int = None):
        self.hp: int = hp
        self.defense: int = defense
        self.power: int = power

        if max_hp:
            self.max_hp = max_hp
        else:
            self.max_hp = hp

    def to_json(self):
        json_data = {
            'max_hp': self.max_hp,
            'hp': self.hp,
            'defense': self.defense,
            'power': self.power
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        fighter = cls(
            hp=json_data['hp'],
            defense=json_data['defense'],
            power=json_data['power'],
            max_hp=json_data['max_hp']
        )

        return fighter

    def attack(self, target: 'Entity'):
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

    def heal(self, amount: int):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def take_damage(self, amount: int):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner})

        return results
