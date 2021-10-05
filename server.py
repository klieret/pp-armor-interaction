#!/usr/bin/env python3

from browser import document, html
from browser.widgets.dialog import InfoDialog

from armor_interaction import damage_types


def echo(ev):
    InfoDialog(
        "Hello",
        f"damage {document['damage'].value} penetration {document['penetration'].value} !",
    )


def setup():
    for damage_type in damage_types:
        document["damage_type"] <= html.DIV(damage_type)


setup()
document["evaluate"].bind("click", echo)
