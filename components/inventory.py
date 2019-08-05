from typing import List, TYPE_CHECKING

from components.item import Item


class Inventory:
    def __init__(self, capacity: int, items: List['Entity'] = None):
        self.capacity: int = capacity

        if items:
            self.items = items
        else:
            self.items = []

    def to_json(self):
        json_data = {
            'capacity': self.capacity,
            'items': [item.to_json() for item in self.items]
        }

        return json_data

    @classmethod
    def from_json(cls, json_data):
        from entity import Entity

        items = [Entity.from_json(item_json_data) for item_json_data in json_data['items']]

        inventory = cls(capacity=json_data['capacity'], items=items)

        return inventory

    def add_item(self, item: 'Entity'):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': '[color=yellow]You cannot carry any more, your inventory is full.[/color]'
            })
        else:
            results.append({
                'item_added': item,
                'message': f'You pick up the [color=blue]{item.name}[/color]'
            })

            self.items.append(item)

        return results

    def drop_item(self, item: 'Entity'):
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({
            'item_dropped': item,
            'message': f'[color=yellow]You drop the {item.name}[/color]'
        })

        return results

    def remove_item(self, item: 'Entity'):
        self.items.remove(item)

    def use(self, item_entity: 'Entity', **kwargs):
        results = []

        item_component: Item = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({'equip': item_entity})
            else:
                results.append({
                    'message': f'[color=yellow]The {item_entity.name} cannot be used.[/color]'
                })
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results
