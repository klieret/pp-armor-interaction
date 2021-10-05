#!/usr/bin/env python3


from armor_interaction import get_damage, get_armor_layers, our_armor

print(
    get_damage(
        15,
        "p",
        8,
        get_armor_layers(
            our_armor,
            [
                "Helmar's Shield of Meginbald",
                "Helmar's Warrior Priest Armour",
                "Helmar's Warrior Priest Armour (Padded Cap)",
            ],
            body_part="left_arm",
        ),
    )
)
