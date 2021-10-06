#!/usr/bin/env python3

from typing import Optional, Tuple, List

from browser import document, html

from armor_interaction import (
    DamageCalculator,
    PredefinedArmorDb,
    body_parts,
)

armor_db = PredefinedArmorDb()
armor_db.load_json()
damage_calculator = DamageCalculator()


def calculate_damage(ev=None) -> Tuple[Optional[int], str]:
    damage = int(document["input_damage"].value)
    penetration = int(document["input_penetration"].value)
    damage_type = get_damage_type()
    if not damage_type:
        return None, "Damage type not set"
    body_part = get_body_part()
    if not body_part:
        return None, "body part not set"
    armor = get_armor_selection()
    print(
        f"damage {damage} penetration {penetration} damage type {damage_type} armor {armor}!"
    )
    assert damage_type
    assert body_part
    result, explanation_lines = damage_calculator.get_damage(
        damage,
        damage_type,
        penetration,
        armor_db.get_armor_layers(
            armor,
            body_part=body_part,
        ),
    )
    return result, explanation_lines


def update_damage(ev=None):
    print("UPDATING")
    damage, explanation = calculate_damage(ev)
    if damage is None:
        damage_str = f"Invalid ({explanation})"
    else:
        damage_str = str(damage)
    document["result"].html = damage_str
    document["explanation"].html = "<br>\n".join(explanation.split("\n"))


def get_damage_type() -> Optional[str]:
    for damage_type in damage_calculator.damage_types:
        if document[f"damage_type_{damage_type}"].checked:
            return damage_type
    return None


def setup_damage_types():
    for damage_type in damage_calculator.damage_types:
        document["damage_type"] <= html.INPUT(
            type="radio",
            id=f"damage_type_{damage_type}",
            name="damage_type",
            value=damage_type,
        )
        document["damage_type"] <= html.LABEL(
            damage_type, **{"for": f"damage_type_{damage_type}"}
        )


def get_armor_selection() -> List[str]:
    return [
        name for name in armor_db if document[f"armor_selection_{name}"].checked
    ]


def setup_armor_selection():
    for name in armor_db:
        div = html.DIV()
        div <= html.INPUT(
            type="checkbox",
            id=f"armor_selection_{name}",
            name="armor_selection",
            value=name,
        )
        div <= html.LABEL(name, **{"for": f"armor_selection_{name}"})
        document["armor_selection"] <= div


def get_body_part():
    for body_part in body_parts:
        if document[f"body_part_{body_part}"].checked:
            return body_part


def setup_body_parts():
    for body_part in body_parts:
        document["body_part"] <= html.INPUT(
            type="radio",
            id=f"body_part_{body_part}",
            name="body_part",
            value=body_part,
        )
        document["body_part"] <= html.LABEL(
            body_part, **{"for": f"body_part_{body_part}"}
        )


def setup_hide_loading_placeholders():
    for item in document.select(".hide_me_after_setup"):
        print(item)
        item.style.display = "none"


def update_damage_slider(ev=None) -> None:
    print("update slider")
    document["value_input_damage"].html = str(document["input_damage"].value)


def update_penetration_slider(ev=None) -> None:
    print("update slider")
    document["value_input_penetration"].html = str(
        document["input_penetration"].value
    )


def setup():
    setup_damage_types()
    setup_armor_selection()
    setup_body_parts()
    for part in [
        "input_damage",
        "input_penetration",
        "body_part",
        "armor_selection",
        "damage_type",
    ]:
        document[part].bind("click", update_damage)
    document["input_damage"].bind("input", update_damage_slider)
    document["input_penetration"].bind("input", update_penetration_slider)
    update_damage_slider()
    update_penetration_slider()
    update_damage()
    setup_hide_loading_placeholders()


setup()
