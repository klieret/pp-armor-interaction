#!/usr/bin/env python3

# 3rd
from selenium import webdriver
import pytest
from math import fabs
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException


@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


@pytest.fixture
def session(driver):
    driver.delete_all_cookies()
    try:
        driver.execute_script("window.localStorage.clear();")
    except WebDriverException:
        # won't work before the first .get
        pass
    driver.get("http://0.0.0.0:8000/")
    return driver


def get_result(driver) -> str:
    return driver.find_element_by_id("result").text


def get_input_damage(driver) -> str:
    return driver.find_element_by_id("input_damage").get_property("value")


def toggle_armor(driver, armor: str) -> None:
    driver.find_element_by_id(f"armor_selection_{armor}").click()


def toggle_ignored_armor_type(driver, armor: str) -> None:
    driver.find_element_by_id(f"ignored_armor_type_{armor}").click()


def select_damage_type(driver, damage_type: str) -> None:
    driver.find_element_by_id(f"damage_type_{damage_type}").click()


def select_body_part(driver, body_part: str) -> None:
    driver.find_element_by_id(f"body_part_{body_part}").click()


def get_armor_selection_result(driver) -> str:
    return driver.find_element_by_id("armor_selection_result").text


def set_custom_armor(driver, armor: str) -> None:
    driver.find_element_by_id("armor_selection_custom_input").send_keys("LsLs")


def set_int_slider(driver, slider_name: str, target: int) -> None:
    slider = driver.find_element_by_id(slider_name)
    now = int(slider.get_property("value"))
    difference = now - target
    if difference == 0:
        return
    for i in range(int(fabs(difference))):
        if difference < 0:
            slider.send_keys(Keys.RIGHT)
        else:
            slider.send_keys(Keys.LEFT)
    assert int(slider.get_property("value")) == target


def set_penetration(driver, penetration: int) -> None:
    set_int_slider(
        slider_name="input_penetration", driver=driver, target=penetration
    )


def set_input_damage(driver, damage: int) -> None:
    set_int_slider(slider_name="input_damage", driver=driver, target=damage)


def test_set_input_damage(session) -> None:
    for value in [1, 5, 10, 15]:
        set_input_damage(session, value)
        assert get_input_damage(session) == str(value)


def test_helmar(session):
    h = "Helmar's Warrior Priest Armour"
    toggle_armor(session, h)
    assert get_armor_selection_result(session) == "HH M LsLs"
    assert get_result(session) == "0"
    select_body_part(session, "head")
    assert get_result(session) == "10"
    select_body_part(session, "body")
    toggle_armor(session, h)
    assert get_result(session) == "10"
    toggle_armor(session, h)
    set_penetration(session, 3)
    assert get_result(session) == "2"


def test_initial_state(session):
    assert get_armor_selection_result(session) == "No layers."
    assert get_input_damage(session) == "10"
    assert (
        session.find_element_by_id("input_penetration").get_property("value")
        == "0"
    )
    assert get_result(session) == "10"
    select_damage_type(session, "e")
    assert get_result(session) == "10"


def test_custom_armor(session):
    set_custom_armor(session, "LsLs")
    assert get_result(session) == "10"
    toggle_armor(session, "custom")
    assert get_result(session) == "6"


def test_custom_and_shield(session):
    toggle_armor(session, "Helmar's Shield of Meginbald")
    set_custom_armor(session, "LsLs")
    toggle_armor(session, "custom")
    assert get_armor_selection_result(session) == "HH LsLs"
    assert get_result(session) == "2"


def test_ignored_armor_type(session):
    toggle_armor(session, "Helmar's Warrior Priest Armour")
    toggle_ignored_armor_type(session, "Ls")
    assert get_result(session) == "4"
    toggle_ignored_armor_type(session, "M")
    assert get_result(session) == "6"
    toggle_ignored_armor_type(session, "H")
    assert get_result(session) == "10"


if __name__ == "__main__":
    _driver = webdriver.Chrome()
    _driver.get("http://0.0.0.0:8000/")
