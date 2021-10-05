from typing import List, Tuple, Dict
import json
import csv


body_parts = [
    "head",
    "body",
    "left_arm",
    "right_arm",
    "left_leg",
    "right_leg",
]


def get_predefined_armor(path="data/predefined_armor_pieces.json"):
    with open(path) as inf:
        _armor = json.load(inf)
    return {armor["name"]: armor for armor in _armor}


our_armor = get_predefined_armor()


def resolve_layer(layer_code: str):
    if layer_code.endswith("2"):
        return layer_code[:-1], 2
    else:
        return layer_code, 1


def get_armor_layer(armor_dict, name: str, body_part="default"):
    armor = armor_dict[name]
    if body_part not in armor["armor"]:
        body_part = "default"
    return [resolve_layer(layer) for layer in armor["armor"][body_part]]


def get_armor_layers(armor_dict, names: List[str], body_part="default"):
    layers = []
    for name in names:
        layers.extend(get_armor_layer(armor_dict, name, body_part=body_part))
    return layers


def get_armor_weapon_interaction_dict(
    path="data/armor_weapon_interaction.csv",
) -> Dict[Tuple[str, str, int], int]:
    dct = {}
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for irow, row in enumerate(reader):
            if irow == 0:
                # skip header
                continue
            assert len(row) == 4
            key = (row[0], row[1], int(row[2]))
            value = int(row[3])
            dct[key] = value
    return dct  # type: ignore


armor_weapon_interaction = get_armor_weapon_interaction_dict()
damage_types = sorted(set([x[0] for x in armor_weapon_interaction.keys()]))
armor_types = sorted(set([x[1] for x in armor_weapon_interaction.keys()]))


def get_damage(
    damage: int,
    damage_type: str,
    penetration: int,
    armor_layers: List[Tuple[str, int]],
):
    remaining_penetration = penetration
    remaining_damage = damage
    for armor_layer in armor_layers:
        armor_type, armor_points = armor_layer
        print(f"--- {armor_type} armor ({armor_points} AP) ---")
        pen_modifier = armor_weapon_interaction[
            (damage_type, armor_type, armor_points)
        ]
        print(f"Pen modifier {pen_modifier}")
        remaining_penetration = max(0, remaining_penetration + pen_modifier)
        print(f"Remaining pen after pen modifier {remaining_penetration}")
        remaining_armor_points = max(0, armor_points - remaining_penetration)
        print(f"Remaining armor points {remaining_armor_points}")
        remaining_penetration = max(0, remaining_penetration - armor_points)
        print(f"Remaining pen after armor points {remaining_penetration}")
        damage_modifier = 2 * remaining_armor_points
        print(f"Damage modifier {damage_modifier}")
        remaining_damage = max(0, remaining_damage - damage_modifier)
        print(f"Remaining damage {remaining_damage}")
    return remaining_damage
