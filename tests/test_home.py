from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def test_homepage_loads(driver):
    driver.get("https://an-constructions.onrender.com")

    WebDriverWait(driver, 30).until(
        lambda d: "A N Constructions" in d.title
    )

    assert "THIS SHOULD FAIL" in driver.title