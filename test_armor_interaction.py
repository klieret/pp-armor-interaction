#!/usr/bin/env python3

import pytest

from armor_interaction import PredefinedArmorDb, DamageCalculator, ArmorLayer


@pytest.fixture
def armor_db() -> PredefinedArmorDb:
    db = PredefinedArmorDb()
    db.load_json()
    return db


@pytest.fixture
def damage_calculator() -> DamageCalculator:
    return DamageCalculator()


def test_armor_layer_serialization():
    test_cases = ["HH", "Ls", "H"]
    for test_case in test_cases:
        armor_layer = ArmorLayer.from_string(test_case)
        assert str(armor_layer) == test_case
        assert ArmorLayer.from_string(str(armor_layer)) == armor_layer


def test_get_armor_layers(armor_db: PredefinedArmorDb):
    assert (
        armor_db.get_armor_layers(
            [
                "Helmar's Shield of Meginbald",
                "Helmar's Warrior Priest Armour",
                "Helmar's Warrior Priest Armour (Padded Cap)",
            ],
            body_part="left_arm",
        )
        == [ArmorLayer("H", 2), ArmorLayer("M", 1), ArmorLayer("Ls", 2)]
    )


def test_get_damage(damage_calculator: DamageCalculator):
    assert (
        damage_calculator.get_damage(
            15,
            "p",
            8,
            [ArmorLayer("H", 2), ArmorLayer("M", 1), ArmorLayer("Ls", 2)],
        )[0]
        == 11
    )
    assert (
        damage_calculator.get_damage(
            10,
            "p",
            4,
            [ArmorLayer("H", 2)],
        )[0]
        == 8
    )


def test_get_damage_no_armor(damage_calculator: DamageCalculator):
    assert damage_calculator.get_damage(15, "p", 8, [])[0] == 15
    assert damage_calculator.get_damage(15, "p", 0, [])[0] == 15
    assert damage_calculator.get_damage(15, "x", 0, [])[0] == 15
