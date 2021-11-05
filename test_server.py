#!/usr/bin/env python3

# 3rd
from selenium import webdriver
import pytest


@pytest.fixture(scope="session")
def driver():
    return webdriver.Chrome()


@pytest.fixture
def session(driver):
    driver.get("http://0.0.0.0:8000/")
    return driver


def get_result(driver) -> str:
    return driver.find_element_by_id("result").text


def get_input_damage(driver) -> str:
    return driver.find_element_by_id("input_damage").get_property("value")


def toggle_helmars_warrior_priest_armour(driver) -> None:
    driver.find_element_by_id(
        "armor_selection_Helmar's Warrior Priest Armour"
    ).click()


def test_initial_state(session):
    assert get_input_damage(session) == "10"
    assert get_result(session) == "10"


def test_helmar(session):
    toggle_helmars_warrior_priest_armour(session)
    assert get_result(session) == "0"


if __name__ == "__main__":
    _driver = webdriver.Chrome()
    _driver.get("http://0.0.0.0:8000/")
