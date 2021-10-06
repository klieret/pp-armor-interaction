#!/usr/bin/env python3


from armor_interaction import get_damage, get_armor_layers, our_armor


def test_get_armor_layers():
    assert (
        get_armor_layers(
            our_armor,
            [
                "Helmar's Shield of Meginbald",
                "Helmar's Warrior Priest Armour",
                "Helmar's Warrior Priest Armour (Padded Cap)",
            ],
            body_part="left_arm",
        )
        == [("H", 2), ("M", 1), ("Ls", 2)]
    )


def test_get_damage():
    assert get_damage(15, "p", 8, [("H", 2), ("M", 1), ("Ls", 2)])[0] == 11


def test_get_damage_no_armor():
    assert get_damage(15, "p", 8, [])[0] == 15
    assert get_damage(15, "p", 0, [])[0] == 15
    assert get_damage(15, "x", 0, [])[0] == 15
