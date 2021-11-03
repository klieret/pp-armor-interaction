#!/usr/bin/env python3

import time

from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://0.0.0.0:8000/")

time.sleep(5)


def get_result():
    return driver.find_element_by_id("result").text


assert driver.find_element_by_id("input_damage").get_property("value") == "10"

assert get_result() == "10", get_result()


helmar_armor = driver.find_element_by_id(
    "armor_selection_Helmar's Warrior Priest Armour"
)
helmar_armor.click()
assert get_result() == "0", get_result()
