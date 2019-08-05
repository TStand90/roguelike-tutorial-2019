from typing import TYPE_CHECKING

from equipment_slots import EquipmentSlots

if TYPE_CHECKING:
    from entity import Entity


class Equipment:
    def __init__(self, main_hand: 'Entity' = None, off_hand: 'Entity' = None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    def to_json(self):
        json_data = {}

        if self.main_hand:
            json_data['main_hand'] = self.main_hand.to_json()
        else:
            json_data['main_hand'] = None

        if self.off_hand:
            json_data['off_hand'] = self.off_hand.to_json()
        else:
            json_data['off_hand'] = None

        return json_data

    @classmethod
    def from_json(cls, json_data):
        from entity import Entity

        if json_data.get('main_hand'):
            main_hand = Entity.from_json(json_data['main_hand'])
        else:
            main_hand = None

        if json_data.get('off_hand'):
            off_hand = Entity.from_json(json_data['off_hand'])
        else:
            off_hand = None

        equipment = cls(main_hand=main_hand, off_hand=off_hand)

        return equipment

    @property
    def max_hp_bonus(self) -> int:
        bonus: int = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus

        return bonus

    @property
    def power_bonus(self) -> int:
        bonus: int = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.power_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.power_bonus

        return bonus

    @property
    def defense_bonus(self) -> int:
        bonus: int = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defense_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defense_bonus

        return bonus

    def toggle_equip(self, equippable_entity: 'Entity'):
        results = []

        slot: EquipmentSlots = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.main_hand:
                    results.append({'dequipped': self.main_hand})

                self.main_hand = equippable_entity
                results.append({'equipped': equippable_entity})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({'dequipped': equippable_entity})
            else:
                if self.off_hand:
                    results.append({'dequipped': self.off_hand})

                self.off_hand = equippable_entity
                results.append({'equipped': equippable_entity})

        return results
