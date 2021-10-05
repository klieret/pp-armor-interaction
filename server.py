#!/usr/bin/env python3

from browser import document, html
from browser.widgets.dialog import InfoDialog

from armor_interaction import damage_types


def echo(ev):
    InfoDialog(
        "Hello",
        f"damage {document['damage'].value} penetration {document['penetration'].value} damage type {get_damage_type()}!",
    )


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


def setup_hide_loading_placeholders():
    for item in document.select(".hide_me_after_setup"):
        print(item)
        item.style.display = "none"


def setup():
    setup_damage_types()
    setup_hide_loading_placeholders()


setup()
document["evaluate"].bind("click", echo)
