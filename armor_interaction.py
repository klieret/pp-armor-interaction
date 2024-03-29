from typing import List, Tuple, Dict, NamedTuple, Optional
import json

# todo: use enums

body_parts = {
    "head": "head",
    "body": "body",
    "left_arm": "left arm",
    "right_arm": "right arm",
    "left_leg": "left leg",
    "right_leg": "right leg",
}

armor_types = {
    "Ls": "Soft light",
    "Lh": "Hard light",
    "M": "Medium",
    "H": "Heavy",
}

damage_types = {
    "b": "bludgeoning",
    "e": "explosive",
    "p": "piercing",
    "s": "slicing",
    "x": "energy",
}


class ArmorLayer:
    def __init__(self, armor_type: str, armor_points: int):
        self.armor_type = armor_type
        self.armor_points = armor_points

    @classmethod
    def from_string(cls, layer_code: str):
        for armor_type in armor_types:
            for ap in range(1, len(layer_code) // len(armor_type) + 1):
                if layer_code == armor_type * ap:
                    return cls(armor_type=armor_type, armor_points=ap)
        raise ValueError(f"Doesn't seem like a valid armor code: {layer_code}")

    def __repr__(self):
        return self.armor_type * self.armor_points

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class PredefinedArmor:
    def __init__(
        self, name: str, bodypart_to_layers: Dict[str, List[ArmorLayer]]
    ):
        self.name = name
        self._bodypart_to_layers = bodypart_to_layers

    def get_layers(self, body_part: str) -> List[ArmorLayer]:
        if body_part not in self._bodypart_to_layers:
            body_part = "default"
        return self._bodypart_to_layers[body_part]


def armor_layers_to_string_representation(layers: List[ArmorLayer]) -> str:
    if layers:
        return " ".join([str(layer) for layer in layers])
    else:
        return "No layers."


def get_armor_layers_from_string_representation(
    string: str,
) -> List[ArmorLayer]:
    return [
        ArmorLayer.from_string(ls) for ls in string.replace(",", " ").split()
    ]


class PredefinedArmorDb:
    def __init__(self):
        self._armor_dict: Dict[str, PredefinedArmor] = {}

    def load_json(self, path="data/predefined_armor_pieces.json"):
        """Load armor configuration from json file and add it to the available
        armors.
        """
        with open(path) as inf:
            _armor = json.load(inf)
        print("Loaded")
        for a in _armor:
            bodypart_to_layers = {}
            for body_part, layer_codes in a["armor"].items():
                if layer_codes == "empty":
                    layer_codes = []
                armor_layers = [
                    ArmorLayer.from_string(lc) for lc in layer_codes
                ]
                bodypart_to_layers[body_part] = armor_layers
            _new_armor = PredefinedArmor(
                name=a["name"], bodypart_to_layers=bodypart_to_layers
            )
            self._armor_dict[_new_armor.name] = _new_armor

    def get_armor_layers(
        self,
        names: List[str],
        body_part="default",
        custom=None,
    ) -> List[ArmorLayer]:
        """Get armor layers provided by a list of armor elements at a specific
        body part.

        Args:
            names: Names of armors
            body_part:
            custom: Replace the name "custom" with this value

        Returns:
            list of armor layers
        """
        layers = []
        for name in names:
            if name == "custom" and custom is not None:
                layers.extend(custom)
            else:
                layers.extend(self[name].get_layers(body_part=body_part))
        return layers

    def __iter__(self):
        return iter(self._armor_dict)

    def __getitem__(self, item):
        return self._armor_dict[item]

    def items(self):
        return self._armor_dict.items()


class DamageResult(NamedTuple):
    value: Optional[int]
    explanation: str


class DamageCalculator:
    def __init__(
        self, armor_interaction_path="data/armor_weapon_interaction.csv"
    ):
        self.armor_weapon_interaction: Dict[Tuple[str, str, int], int] = {}
        with open(armor_interaction_path) as csvfile:
            for iline, line in enumerate(csvfile):
                if iline == 0:
                    # skip header
                    continue
                if not line.split():
                    continue
                row = [x.strip() for x in line.split(",")]
                assert len(row) == 4
                key = (row[0], row[1], int(row[2]))
                value = int(row[3])
                self.armor_weapon_interaction[key] = value

    def get_damage(
        self,
        damage: int,
        damage_type: str,
        penetration: int,
        armor_layers: List[ArmorLayer],
        ignored_armor_types: Optional[List[str]] = None,
    ) -> DamageResult:
        if ignored_armor_types is None:
            ignored_armor_types = []
        remaining_pen = penetration
        remaining_dam = damage
        explanation_lines = []
        for armor_layer in armor_layers:
            at = armor_layer.armor_type
            ap = armor_layer.armor_points
            explanation_lines.append(f"--- {at} armor ({ap} AP) ---")
            if at in ignored_armor_types:
                explanation_lines.append(f"Armor type {at} is ignored")
                continue
            pen_modifier = self.armor_weapon_interaction[(damage_type, at, ap)]
            explanation_lines.append(f"Pen modifier {pen_modifier}")
            remaining_pen = max(0, remaining_pen + pen_modifier)
            explanation_lines.append(
                f"Remaining pen after pen modifier {remaining_pen}"
            )
            remaining_armor_points = max(0, ap - remaining_pen)
            explanation_lines.append(
                f"Remaining armor points {remaining_armor_points}"
            )
            remaining_pen = max(0, remaining_pen - ap)
            explanation_lines.append(
                f"Remaining pen after armor points {remaining_pen}"
            )
            damage_modifier = 2 * remaining_armor_points
            explanation_lines.append(f"Damage modifier {damage_modifier}")
            remaining_dam = max(0, remaining_dam - damage_modifier)
            explanation_lines.append(f"Remaining damage {remaining_dam}")
        return DamageResult(
            value=remaining_dam, explanation="\n".join(explanation_lines)
        )
