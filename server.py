#!/usr/bin/env python3

from browser import document, html
from browser.widgets.dialog import InfoDialog

from armor_interaction import (
    damage_types,
    our_armor,
    get_damage,
    get_armor_layers,
    body_parts,
)


def calculate_damage(ev):
    damage = int(document["damage"].value)
    penetration = int(document["penetration"].value)
    damage_type = get_damage_type()
    armor = get_armor_selection()
    print(
        f"damage {damage} penetration {penetration} damage type {damage_type} armor {armor}!"
    )
    result = get_damage(
        damage,
        damage_type,
        penetration,
        get_armor_layers(
            our_armor,
            armor,
            body_part="left_arm",
        ),
    )
    InfoDialog("Resulting damage", str(result))


def get_damage_type():
    for damage_type in damage_types:
        if document[f"damage_type_{damage_type}"].checked:
            return damage_type


def setup_damage_types():
    for damage_type in damage_types:
        document["damage_type"] <= html.INPUT(
            type="radio",
            id=f"damage_type_{damage_type}",
            name="damage_type",
            value=damage_type,
        )
        document["damage_type"] <= damage_type


def get_armor_selection():
    return [
        name
        for name in our_armor
        if document[f"armor_selection_{name}"].checked
    ]


def setup_armor_selection():
    for name in our_armor:
        div = html.DIV()
        div <= html.INPUT(
            type="checkbox",
            id=f"armor_selection_{name}",
            name="armor_selection",
            value=name,
        )
        div <= name
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
        document["body_part"] <= body_part


def setup_hide_loading_placeholders():
    for item in document.select(".hide_me_after_setup"):
        print(item)
        item.style.display = "none"


def setup():
    setup_damage_types()
    setup_armor_selection()
    setup_hide_loading_placeholders()
    setup_body_parts()


setup()
document["evaluate"].bind("click", calculate_damage)
