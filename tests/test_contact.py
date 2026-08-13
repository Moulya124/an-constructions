from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def test_contact_form_elements(driver):
    driver.get(
        "https://an-constructions.onrender.com/pages/contact.html"
    )

    WebDriverWait(driver, 30).until(
        lambda d: d.find_element(By.ID, "name").is_displayed()
    )

    name = driver.find_element(By.ID, "name")
    email = driver.find_element(By.ID, "email")
    phone = driver.find_element(By.ID, "phone")
    subject = driver.find_element(By.ID, "subject")
    message = driver.find_element(By.ID, "message")
    submit = driver.find_element(By.ID, "submitBtn")

    assert name.is_displayed()
    assert email.is_displayed()
    assert phone.is_displayed()
    assert subject.is_displayed()
    assert message.is_displayed()
    assert submit.is_displayed()


def test_user_can_enter_contact_details():
    driver = webdriver.Chrome()

    try:
        driver.get(
            "https://an-constructions.onrender.com/pages/contact.html"
        )

        WebDriverWait(driver, 30).until(
            lambda d: d.find_element(By.ID, "name").is_displayed()
        )

        name = driver.find_element(By.ID, "name")
        email = driver.find_element(By.ID, "email")
        message = driver.find_element(By.ID, "message")

        name.send_keys("Selenium Test User")
        email.send_keys("selenium@example.com")
        message.send_keys("This is an automated Selenium test.")

        assert name.get_attribute("value") == "Selenium Test User"
        assert email.get_attribute("value") == "selenium@example.com"
        assert message.get_attribute("value") == (
            "This is an automated Selenium test."
        )

    finally:
        driver.quit()

def test_contact_form_requires_required_fields():
    driver = webdriver.Chrome()

    try:
        driver.get(
            "https://an-constructions.onrender.com/pages/contact.html"
        )

        WebDriverWait(driver, 30).until(
            lambda d: d.find_element(By.ID, "submitBtn").is_displayed()
        )

        name = driver.find_element(By.ID, "name")
        email = driver.find_element(By.ID, "email")
        message = driver.find_element(By.ID, "message")

        assert name.get_attribute("required") is not None
        assert email.get_attribute("required") is not None
        assert message.get_attribute("required") is not None

    finally:
        driver.quit()