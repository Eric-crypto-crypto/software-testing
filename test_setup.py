from selenium import webdriver
from selenium.webdriver.common.by import By


def make_driver():
    options = webdriver.ChromeOptions()
    # Codespace has no display, so run Chrome headless
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def test_locators():
    driver = make_driver()
    try:
        driver.get("https://www.selenium.dev/selenium/web/locators_tests/locators.html")

        first_name = driver.find_element(By.CSS_SELECTOR, "#fname")
        assert first_name.get_attribute("value") == "Jane"

        last_name = driver.find_element(By.ID, "lname")
        assert last_name.get_attribute("value") == "Doe"

        fradio = driver.find_element(By.XPATH, "//input[@value='f']")
        assert fradio.get_attribute("type") == "radio"
    finally:
        driver.quit()
