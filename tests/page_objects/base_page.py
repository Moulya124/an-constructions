from selenium.webdriver.support.ui import WebDriverWait


class BasePage:

    TIMEOUT = 30

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    def find(self, locator):
        return self.driver.find_element(*locator)

    def wait_for_visible(self, locator):
        return self.wait.until(
            lambda d: d.find_element(*locator).is_displayed()
        )

    def click(self, locator):
        self.wait_for_visible(locator)
        self.find(locator).click()

    def type_text(self, locator, text):
        self.wait_for_visible(locator)
        self.find(locator).send_keys(text)

    def get_value(self, locator):
        return self.find(locator).get_attribute("value")