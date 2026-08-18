import os

import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()

    # Run Chrome without a graphical desktop.
    # Required for GitHub Actions / Linux CI environments.
    options.add_argument("--headless=new")

    # Prevent Chrome sandbox issues in CI.
    options.add_argument("--no-sandbox")

    # Prevent shared-memory problems in containers/CI.
    options.add_argument("--disable-dev-shm-usage")

    # Give the browser a consistent viewport.
    options.add_argument("--window-size=1920,1080")

    browser = webdriver.Chrome(options=options)

    yield browser

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")

        if driver:
            os.makedirs("screenshots", exist_ok=True)

            screenshot_path = (
                f"screenshots/{item.name}.png"
            )

            driver.save_screenshot(screenshot_path)

            print(
                f"\nScreenshot saved: {screenshot_path}"
            )