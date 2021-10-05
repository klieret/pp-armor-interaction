#!/usr/bin/env python3

import pandas as pd
import collections
from typing import List, Tuple, Dict
import yaml
from pathlib import Path


def get_predefined_armor(path=Path("data/predefined_armor_pieces.yaml")):
    with path.open() as inf:
        _armor = yaml.load(inf, Loader=yaml.SafeLoader)
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


def get_armor_weapon_interaction_dict(path=Path("data/armor_weapon_interaction.csv")) -> Dict[Tuple[str, str, int], int]:
    df = pd.read_csv(path)
    return {tuple(x[:-1]): x[-1] for x in df.to_numpy()}


armor_weapon_interaction = get_armor_weapon_interaction_dict()


def get_damage(damage: int, damage_type: str, penetration: int, armor_layers: List[Tuple[str, int]]):
    remaining_penetration = penetration
    remaining_damage = damage
    for armor_layer in armor_layers:
        armor_type, armor_points = armor_layer
        print(f"--- {armor_type} armor ({armor_points} AP) ---")
        pen_modifier = armor_weapon_interaction[(damage_type, armor_type, armor_points)]
        print(f"Pen modifier {pen_modifier}")
        remaining_penetration = max(0, remaining_penetration + pen_modifier)
        print(f"Remaining pen after pen modifier {remaining_penetration}")
        remaining_armor_points = max(0, armor_points - remaining_penetration)
        print(f"Remaining armor points {remaining_armor_points}")
        remaining_penetration = max(0, remaining_penetration - armor_points)
        print(f"Remaining pen after armor points {remaining_penetration}")
        damage_modifier = 2*remaining_armor_points
        print(f"Damage modifier {damage_modifier}")
        remaining_damage = max(0, remaining_damage - damage_modifier)
        print(f"Remaining damage {remaining_damage}")
    return remaining_damage
        


print(get_damage(
    15, 
    "p", 
    8, 
    get_armor_layers(
        our_armor,
        [
            "Helmar's Shield of Meginbald",
            "Helmar's Warrior Priest Armour", 
            "Helmar's Warrior Priest Armour (Padded Cap)", 
        ], 
        body_part="left_arm"
    )
))