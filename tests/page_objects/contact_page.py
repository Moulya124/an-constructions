from page_objects.base_page import BasePage
from selenium.webdriver.common.by import By


class ContactPage(BasePage):

    URL = "https://an-constructions.onrender.com/pages/contact.html"

    CONTACT_FORM = (By.ID, "contactForm")

    NAME = (By.ID, "name")
    EMAIL = (By.ID, "email")
    PHONE = (By.ID, "phone")
    SUBJECT = (By.ID, "subject")
    MESSAGE = (By.ID, "message")
    SUBMIT_BUTTON = (By.ID, "submitBtn")

    def open(self):
        self.driver.get(self.URL)

        self.wait_for_visible(self.NAME)

    # ---------- Fields ----------

    def name_field(self):
        return self.find(self.NAME)

    def email_field(self):
        return self.find(self.EMAIL)

    def phone_field(self):
        return self.find(self.PHONE)

    def subject_field(self):
        return self.find(self.SUBJECT)

    def message_field(self):
        return self.find(self.MESSAGE)

    def submit_button(self):
        return self.find(self.SUBMIT_BUTTON)

    # ---------- Enter data ----------

    def enter_name(self, name):
        self.type_text(self.NAME, name)

    def enter_email(self, email):
        self.type_text(self.EMAIL, email)

    def enter_phone(self, phone):
        self.type_text(self.PHONE, phone)

    def enter_subject(self, subject):
        self.type_text(self.SUBJECT, subject)

    def enter_message(self, message):
        self.type_text(self.MESSAGE, message)

    # ---------- Get entered values ----------

    def get_name(self):
        return self.get_value(self.NAME)

    def get_email(self):
        return self.get_value(self.EMAIL)

    def get_phone(self):
        return self.get_value(self.PHONE)

    def get_subject(self):
        return self.get_value(self.SUBJECT)

    def get_message(self):
        return self.get_value(self.MESSAGE)

    # ---------- Required field validation ----------

    def is_name_required(self):
        return self.name_field().get_attribute("required") is not None

    def is_email_required(self):
        return self.email_field().get_attribute("required") is not None

    def is_message_required(self):
        return self.message_field().get_attribute("required") is not None

    # ---------- Browser validation ----------

    def is_form_valid(self):
        return self.driver.execute_script(
            "return arguments[0].checkValidity();",
            self.find(self.CONTACT_FORM)
        )

    def is_email_valid(self):
        return self.driver.execute_script(
            "return arguments[0].checkValidity();",
            self.find(self.EMAIL)
        )