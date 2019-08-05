from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity


class Fighter:
    def __init__(self, hp: int, base_defense: int, base_power: int, base_max_hp: int = None):
        self.hp: int = hp
        self.base_defense: int = base_defense
        self.base_power: int = base_power

        if base_max_hp:
            self.base_max_hp = base_max_hp
        else:
            self.base_max_hp = hp

    def to_json(self):
        json_data = {
            'base_max_hp': self.base_max_hp,
            'hp': self.hp,
            'base_defense': self.base_defense,
            'base_power': self.base_power
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        fighter = cls(
            hp=json_data['hp'],
            base_defense=json_data['base_defense'],
            base_power=json_data['base_power'],
            base_max_hp=json_data['base_max_hp']
        )

        return fighter

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus

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
