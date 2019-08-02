from entity import Entity


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
