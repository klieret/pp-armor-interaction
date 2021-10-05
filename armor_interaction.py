import pandas as pd
import collections
from typing import List, Tuple
import yaml
from pathlib import Path

df = pd.read_csv("data/armor_weapon_interaction.csv")

with Path("data/predefined_armor_pieces.yaml").open() as inf:
    _our_armor = yaml.load(inf, Loader=yaml.SafeLoader)
our_armor = {armor["name"]: armor for armor in _our_armor}


def resolve_layer(layer_code: str):
    if layer_code.endswith("2"):
        return layer_code[:-1], 2
    else:
        return layer_code, 1


def get_armor_layer(name: str, body_part="default"):
    armor = our_armor[name]
    if body_part not in armor["armor"]:
        body_part = "default"
    return [resolve_layer(layer) for layer in armor["armor"][body_part]]


def get_armor_layers(names: List[str], body_part="default"):
    layers = []
    for name in names:
        layers.extend(get_armor_layer(name, body_part=body_part))
    return layers


armor_weapon_interaction = {tuple(x[:-1]): x[-1] for x in df.to_numpy()}


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
        [
            "Helmar's Shield of Meginbald",
            "Helmar's Warrior Priest Armour", 
            "Helmar's Warrior Priest Armour (Padded Cap)", 
        ], 
        body_part="left_arm"
    )
))
