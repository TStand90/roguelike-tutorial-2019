from typing import TYPE_CHECKING

from components.ai import ConfusedMonster

if TYPE_CHECKING:
    from entity import Entity


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not fov_map[target_x, target_y]:
        results.append({
            'consumed': False,
            'message': '[color=yellow]You cannot target a tile outside your field of view.[/color]'
        })

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({
                'consumed': True,
                'message': f'[color=purple]The eyes of the {entity.name} look vacant, as he starts to stumble around![/color]'
            })

            break
    else:
        results.append({
            'consumed': False,
            'message': '[color=yellow]There is no targetable enemy at that location.[/color]'
        })

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not fov_map[target_x, target_y]:
        results.append({
            'consumed': False,
            'message': '[color=yellow]You cannot target a tile outside your field of view.[/color]'
        })
        return results

    results.append({
        'consumed': True,
        'message': f'[color=orange]The fireball explodes, burning everything within {radius} tiles![/color]'
    })

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({
                'message': f'[color=orange]The {entity.name} gets burned for {damage} hit points.[/color]'
            })
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_lightning(*args, **kwargs):
    caster: Entity = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target: Entity = None
    closest_distance: int = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and fov_map[entity.x, entity.y]:
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({
            'consumed': True,
            'target': target,
            'message': f'A lighting bolt strikes the {target.name} with a loud thunder! The damage is {damage}.'
        })
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({
            'consumed': False,
            'target': None,
            'message': '[color=red]No enemy is close enough to strike.[/color]'
        })

    return results


def heal(*args, **kwargs):
    entity: Entity = args[0]
    amount: int = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({
            'consumed': False,
            'message': '[color=yellow]You are already at full health.[/color]'
        })
    else:
        entity.fighter.heal(amount)
        results.append({
            'consumed': True,
            'message': '[color=green]Your wounds start to feel better![/color]'
        })

    return results
