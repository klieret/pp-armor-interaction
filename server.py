#!/usr/bin/env python3

import json
from typing import Optional, List, Any, Dict
import collections

from browser import document, html
from browser.local_storage import storage

from armor_interaction import (
    DamageCalculator,
    PredefinedArmorDb,
    body_parts,
    damage_types,
    armor_layers_to_string_representation,
    get_armor_layers_from_string_representation,
    DamageResult,
    armor_types,
)

armor_db = PredefinedArmorDb()
armor_db.load_json()
damage_calculator = DamageCalculator()

# Settings that are later written to local storage
settings: Dict[str, Any] = collections.defaultdict(dict)


def calculate_damage(ev=None) -> DamageResult:
    damage = int(document["input_damage"].value)
    penetration = int(document["input_penetration"].value)
    damage_type = get_damage_type()
    if not damage_type:
        return DamageResult(None, "Damage type not set")
    armor, armor_error = get_armor_layers()
    if armor_error:
        document["armor_selection_result"].html = armor_error
        return DamageResult(None, armor_error)
    document[
        "armor_selection_result"
    ].html = armor_layers_to_string_representation(armor)
    assert damage_type
    return damage_calculator.get_damage(
        damage=damage,
        damage_type=damage_type,
        penetration=penetration,
        armor_layers=armor,
        ignored_armor_types=get_ignored_armor_types(),
    )


def update_damage(ev=None):
    print("UPDATING")
    damage = calculate_damage(ev)
    if damage.value is None:
        damage_str = "?"
    else:
        damage_str = str(damage.value)
    document["result"].html = damage_str
    document["explanation"].html = "<br>\n".join(damage.explanation.split("\n"))


def get_damage_type() -> Optional[str]:
    """Returns the damage type that was selected."""
    for damage_type in damage_types:
        if document[f"damage_type_{damage_type}"].checked:
            return damage_type
    return None


def get_ignored_armor_types() -> List[str]:
    return [
        armor_type
        for armor_type in armor_types
        if document[f"ignored_armor_type_{armor_type}"].checked
    ]


def get_armor_layers():
    body_part = get_body_part()
    armor = get_armor_selection()
    settings["armor"] = armor
    custom_armor_input = document["armor_selection_custom_input"].value.strip()
    settings["custom_armor"] = custom_armor_input
    custom_armor = None
    if "custom" in armor:
        try:
            custom_armor = get_armor_layers_from_string_representation(
                custom_armor_input
            )
        except ValueError:
            return None, "Couldn't parse custom armor setting string"
    dump_settings_local_storage()
    return (
        armor_db.get_armor_layers(
            armor, body_part=body_part, custom=custom_armor
        ),
        "",
    )


def setup_damage_types():
    """Sets up radio-buttons for the different damage types"""
    for damage_type, damage_type_full_name in damage_types.items():
        _ = document["damage_type"] <= html.INPUT(
            type="radio",
            id=f"damage_type_{damage_type}",
            name="damage_type",
            value=damage_type,
            checked=damage_type == "b",
        )
        _ = document["damage_type"] <= html.LABEL(
            damage_type_full_name, **{"for": f"damage_type_{damage_type}"}
        )


def get_armor_selection() -> List[str]:
    """Returns the name of the selected pre-configured pieces"""
    return [
        name
        for name in [*list(armor_db), "custom"]
        if document[f"armor_selection_{name}"].checked
    ]


def dump_settings_local_storage():
    storage["main"] = json.dumps(settings)


def restore_from_local_storage():
    """Tries to set things as they were last time"""
    if "main" not in storage:
        print("No local storage settings")
        return
    settings = json.loads(storage["main"])
    print("Restored settings")
    print(storage["main"])
    try:
        for name in settings["armor"]:
            document[f"armor_selection_{name}"].checked = True
        document["armor_selection_custom_input"].value = settings[
            "custom_armor"
        ]
    except Exception as e:
        print(f"Couldn't restore settings: {e}")


def setup_armor_selection():
    """Sets up checkboxes for each pre-configured piece of armor and an
    additional custom field
    """
    for name in [*list(armor_db), "custom"]:
        div = html.DIV(id=f"div_{name}")
        _ = div <= html.INPUT(
            type="checkbox",
            id=f"armor_selection_{name}",
            name="armor_selection",
            value=name,
        )
        _ = div <= html.LABEL(name, **{"for": f"armor_selection_{name}"})
        if name == "custom":
            _ = div <= " "
            _ = div <= html.INPUT(id="armor_selection_custom_input")
        else:
            _ = div <= " "
            _ = div <= html.SPAN(
                id=f"span_{name}", **{"class": ["armor_mirror"]}
            )
        _ = document["armor_selection"] <= div


def update_armor_selection_mirror(*ev):
    """For each of the selectable armors. Updates a small text field that shows
    the actual armor layers that this armor provides at the selected body part
    """
    for name, armor in armor_db.items():
        armor_layer_str = armor_layers_to_string_representation(
            armor.get_layers(body_part=get_body_part())
        )
        document[f"span_{name}"].html = f"({armor_layer_str})"


def get_body_part():
    for body_part in body_parts:
        if document[f"body_part_{body_part}"].checked:
            return body_part


def setup_body_parts():
    for body_part, body_part_full_name in body_parts.items():
        _ = document["body_part"] <= html.INPUT(
            type="radio",
            id=f"body_part_{body_part}",
            name="body_part",
            value=body_part,
            checked=body_part == "body",
        )
        _ = document["body_part"] <= html.LABEL(
            body_part_full_name, **{"for": f"body_part_{body_part}"}
        )


def setup_ignored_armor_types():
    for armor_type, armor_type_desc in armor_types.items():
        _ = document["ignored_armor_types"] <= html.INPUT(
            type="checkbox",
            id=f"ignored_armor_type_{armor_type}",
            name="ignored_armor_type",
            value=armor_type,
            checked=False,
        )
        _ = document["ignored_armor_types"] <= html.LABEL(
            armor_type_desc, **{"for": f"armor_type_{armor_type}"}
        )


def setup_hide_loading_placeholders():
    """Hide 'Loading...' placeholders that show up by default"""
    for item in document.select(".hide_me_after_setup"):
        item.style.display = "none"


def update_damage_slider(ev=None) -> None:
    document["value_input_damage"].html = str(document["input_damage"].value)


def update_penetration_slider(ev=None) -> None:
    document["value_input_penetration"].html = str(
        document["input_penetration"].value
    )


def setup():
    setup_damage_types()
    setup_armor_selection()
    setup_body_parts()
    setup_ignored_armor_types()
    restore_from_local_storage()
    for part in [
        "body_part",
        "armor_selection",
        "damage_type",
        "ignored_armor_types",
    ]:
        document[part].bind("click", update_damage)
    document["body_part"].bind("click", update_armor_selection_mirror)
    for event in ["input", "change"]:
        document["input_damage"].bind(event, update_damage)
        document["input_damage"].bind(event, update_damage_slider)
        document["input_penetration"].bind(event, update_damage)
        document["input_penetration"].bind(event, update_penetration_slider)
    for event in ["keydown", "paste", "input"]:
        document["armor_selection_custom_input"].bind(event, update_damage)
    update_damage_slider()
    update_penetration_slider()
    update_damage()
    update_armor_selection_mirror()


setup()
setup_hide_loading_placeholders()
