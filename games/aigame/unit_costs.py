unit_costs = {
    "gatherer": {
        'wood': 5,
        'metal': 5
    },
    "attacker": {
        'wood': 5,
        'metal': 5
    }
}

unit_stats = {
    "gatherer": dict(
        speed=10,
        health=10,
        attack=0,
        defense=5,
        attack_range=0,
        view_range=None,
        collect_amount=3,
    ),
    "attacker": dict(
        speed=10,
        health=15,
        attack=5,
        defense=10,
        attack_range=15,
        view_range=None,
        collect_amount=0,
    )
}