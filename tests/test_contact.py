from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from page_objects.contact_page import ContactPage


def test_contact_form_elements(driver):
    contact_page = ContactPage(driver)

    contact_page.open()

    assert contact_page.name_field().is_displayed()
    assert contact_page.email_field().is_displayed()
    assert contact_page.phone_field().is_displayed()
    assert contact_page.subject_field().is_displayed()
    assert contact_page.message_field().is_displayed()
    assert contact_page.submit_button().is_displayed()


def test_user_can_enter_contact_details(driver):
    contact_page = ContactPage(driver)

    contact_page.open()

    contact_page.enter_name("Selenium Test User")
    contact_page.enter_email("selenium@example.com")
    contact_page.enter_message(
        "This is an automated Selenium test."
    )

    assert contact_page.name_field().get_attribute("value") == (
        "Selenium Test User"
    )

    assert contact_page.email_field().get_attribute("value") == (
        "selenium@example.com"
    )

    assert contact_page.message_field().get_attribute("value") == (
        "This is an automated Selenium test."
    )

def test_contact_form_requires_required_fields(driver):
    contact_page = ContactPage(driver)

    contact_page.open()

    assert contact_page.name_field().get_attribute("required") is not None
    assert contact_page.email_field().get_attribute("required") is not None
    assert contact_page.message_field().get_attribute("required") is not None