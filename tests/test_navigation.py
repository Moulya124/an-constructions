from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def test_contact_navigation(driver):
    driver.get("https://an-constructions.onrender.com")

    WebDriverWait(driver, 30).until(
        lambda d: d.find_element(
            By.LINK_TEXT, "Contact"
        ).is_displayed()
    )

    contact_link = driver.find_element(
        By.LINK_TEXT, "Contact"
    )

    contact_link.click()

    WebDriverWait(driver, 30).until(
        lambda d: d.find_element(
            By.TAG_NAME, "h1"
        ).is_displayed()
    )

    assert "Contact Us" in driver.page_source