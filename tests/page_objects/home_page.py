from page_objects.base_page import BasePage
from selenium.webdriver.common.by import By


class HomePage(BasePage):

    URL = "https://an-constructions.onrender.com"

    CONTACT_LINK = (By.LINK_TEXT, "Contact")

    def open(self):
        self.driver.get(self.URL)

        self.wait_for_visible(self.CONTACT_LINK)

    def click_contact(self):
        self.click(self.CONTACT_LINK)