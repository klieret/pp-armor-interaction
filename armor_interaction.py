from typing import List, Tuple, Dict, Any
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

armor_types = ["Ls", "Lh", "M", "H"]


class PredefinedArmorDb:
    def __init__(self):
        self.armor_dict: Dict[str, Any] = {}

    def load_json(self, path="data/predefined_armor_pieces.json"):
        with open(path) as inf:
            _armor = json.load(inf)
        self.armor_dict = {
            **self.armor_dict,
            **{armor["name"]: armor for armor in _armor},
        }

    @staticmethod
    def _resolve_layer(layer_code: str) -> Tuple[str, int]:
        for armor_type in armor_types:
            for ap in range(1, len(layer_code) // len(armor_type) + 1):
                if layer_code == armor_type * ap:
                    return (armor_type, ap)
        raise ValueError(f"Doesn't seem like a valid armor code: {layer_code}")

    def _get_armor_layers(
        self, name: str, body_part="default"
    ) -> List[Tuple[str, int]]:
        armor = self.armor_dict[name]
        if body_part not in armor["armor"]:
            body_part = "default"
        return [
            self._resolve_layer(layer) for layer in armor["armor"][body_part]
        ]

    def get_armor_layers(
        self, names: List[str], body_part="default"
    ) -> List[Tuple[str, int]]:
        """

        Args:
            names: Names of armors
            body_part:

        Returns:

        """
        layers = []
        for name in names:
            layers.extend(
                self._get_armor_layers(name=name, body_part=body_part)
            )
        return layers

    def __iter__(self):
        return iter(self.armor_dict)


class DamageCalculator:
    def __init__(
        self, armor_interaction_path="data/armor_weapon_interaction.csv"
    ):
        self.armor_weapon_interaction: Dict[Tuple[str, str, int], int] = {}
        with open(armor_interaction_path) as csvfile:
            reader = csv.reader(csvfile)
            for irow, row in enumerate(reader):
                if irow == 0:
                    # skip header
                    continue
                assert len(row) == 4
                key = (row[0], row[1], int(row[2]))
                value = int(row[3])
                self.armor_weapon_interaction[key] = value
        self.damage_types = sorted(
            set([x[0] for x in self.armor_weapon_interaction.keys()])
        )
        self.armor_types = sorted(
            set([x[1] for x in self.armor_weapon_interaction.keys()])
        )

    def get_damage(
        self,
        damage: int,
        damage_type: str,
        penetration: int,
        armor_layers: List[Tuple[str, int]],
    ) -> Tuple[int, str]:
        remaining_penetration = penetration
        remaining_damage = damage
        explanation_lines = []
        for armor_layer in armor_layers:
            armor_type, armor_points = armor_layer
            explanation_lines.append(
                f"--- {armor_type} armor ({armor_points} AP) ---"
            )
            pen_modifier = self.armor_weapon_interaction[
                (damage_type, armor_type, armor_points)
            ]
            explanation_lines.append(f"Pen modifier {pen_modifier}")
            remaining_penetration = max(0, remaining_penetration + pen_modifier)
            explanation_lines.append(
                f"Remaining pen after pen modifier {remaining_penetration}"
            )
            remaining_armor_points = max(
                0, armor_points - remaining_penetration
            )
            explanation_lines.append(
                f"Remaining armor points {remaining_armor_points}"
            )
            remaining_penetration = max(0, remaining_penetration - armor_points)
            explanation_lines.append(
                f"Remaining pen after armor points {remaining_penetration}"
            )
            damage_modifier = 2 * remaining_armor_points
            explanation_lines.append(f"Damage modifier {damage_modifier}")
            remaining_damage = max(0, remaining_damage - damage_modifier)
            explanation_lines.append(f"Remaining damage {remaining_damage}")
        return remaining_damage, "\n".join(explanation_lines)
