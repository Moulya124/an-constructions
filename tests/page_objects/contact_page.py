from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class ContactPage:

    URL = "https://an-constructions.onrender.com/pages/contact.html"

    NAME = (By.ID, "name")
    EMAIL = (By.ID, "email")
    PHONE = (By.ID, "phone")
    SUBJECT = (By.ID, "subject")
    MESSAGE = (By.ID, "message")
    SUBMIT_BUTTON = (By.ID, "submitBtn")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    def open(self):
        self.driver.get(self.URL)

        self.wait.until(
            lambda d: d.find_element(*self.NAME).is_displayed()
        )

    def name_field(self):
        return self.driver.find_element(*self.NAME)

    def email_field(self):
        return self.driver.find_element(*self.EMAIL)

    def phone_field(self):
        return self.driver.find_element(*self.PHONE)

    def subject_field(self):
        return self.driver.find_element(*self.SUBJECT)

    def message_field(self):
        return self.driver.find_element(*self.MESSAGE)

    def submit_button(self):
        return self.driver.find_element(*self.SUBMIT_BUTTON)

    def enter_name(self, name):
        self.name_field().send_keys(name)

    def enter_email(self, email):
        self.email_field().send_keys(email)

    def enter_phone(self, phone):
        self.phone_field().send_keys(phone)

    def enter_subject(self, subject):
        self.subject_field().send_keys(subject)

    def enter_message(self, message):
        self.message_field().send_keys(message)