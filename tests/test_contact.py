import pytest

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

    assert contact_page.get_name() == "Selenium Test User"

    assert contact_page.get_email() == "selenium@example.com"

    assert contact_page.get_message() == (
        "This is an automated Selenium test."
    )


def test_contact_form_requires_required_fields(driver):
    contact_page = ContactPage(driver)

    contact_page.open()

    assert contact_page.is_name_required()
    assert contact_page.is_email_required()
    assert contact_page.is_message_required()


def test_contact_form_rejects_invalid_email(driver):
    contact_page = ContactPage(driver)

    contact_page.open()

    contact_page.enter_name("Selenium Test User")
    contact_page.enter_email("not-an-email")
    contact_page.enter_message(
        "Testing invalid email validation."
    )

    assert contact_page.is_email_valid() is False


def test_contact_form_rejects_empty_required_fields(driver):
    contact_page = ContactPage(driver)

    contact_page.open()

    assert contact_page.is_form_valid() is False


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "hello",
        "abc@",
        "@gmail.com",
        "test",
    ],
)
def test_invalid_email_formats(driver, email):
    contact_page = ContactPage(driver)

    contact_page.open()

    contact_page.enter_name("Selenium Test User")
    contact_page.enter_email(email)
    contact_page.enter_message(
        "Testing invalid email formats."
    )

    assert contact_page.is_email_valid() is False