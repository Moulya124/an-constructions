from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from page_objects.home_page import HomePage


def test_contact_navigation(driver):
    home_page = HomePage(driver)

    home_page.open()
    home_page.click_contact()

    WebDriverWait(driver, 30).until(
        lambda d: d.find_element(
            By.TAG_NAME, "h1"
        ).is_displayed()
    )

    assert "Contact Us" in driver.page_source