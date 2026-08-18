from selenium.webdriver.common.by import By

from config import BASE_URL
from page_objects.base_page import BasePage


class HomePage(BasePage):

    URL = BASE_URL

    CONTACT_LINK = (By.LINK_TEXT, "Contact")

    def open(self):
        self.driver.get(self.URL)

        self.wait_for_visible(self.CONTACT_LINK)

    def click_contact(self):
        self.click(self.CONTACT_LINK)