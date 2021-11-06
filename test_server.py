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
    options.headless = True
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


def select_damage_type(driver, damage_type: str) -> None:
    driver.find_element_by_id(f"damage_type_{damage_type}").click()


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
    assert get_result(session) == "0"
    toggle_armor(session, h)
    assert get_result(session) == "10"
    toggle_armor(session, h)
    set_penetration(session, 3)
    assert get_result(session) == "2"


def test_initial_state(session):
    assert get_input_damage(session) == "10"
    assert (
        session.find_element_by_id("input_penetration").get_property("value")
        == "0"
    )
    assert get_result(session) == "10"
    select_damage_type(session, "e")
    assert get_result(session) == "10"


if __name__ == "__main__":
    _driver = webdriver.Chrome()
    _driver.get("http://0.0.0.0:8000/")
