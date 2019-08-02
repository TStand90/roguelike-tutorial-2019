from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from components.item import Item
    from entity import Entity


class Inventory:
    def __init__(self, capacity: int):
        self.capacity: int = capacity
        self.items: List[Entity] = []

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
            results.append({
                'message': f'[color=yellow]The {item_entity.name} cannot be used.[/color]'
            })
        else:
            kwargs = {**item_component.function_kwargs, **kwargs}
            item_use_results = item_component.use_function(self.owner, **kwargs)

            for item_use_result in item_use_results:
                if item_use_result.get('consumed'):
                    self.remove_item(item_entity)

            results.extend(item_use_results)

        return results
