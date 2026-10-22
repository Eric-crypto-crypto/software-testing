import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from test_setup import make_driver

LOGIN_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
ACCOUNT_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=account/account"

# Dedicated test account registered on the demo site for these tests
VALID_EMAIL = "st.test.1792645713@example.com"
VALID_PASSWORD = "Test@12345"

ERROR_MESSAGE = "Warning: No match for E-Mail Address and/or Password."


@pytest.fixture
def driver():
    driver = make_driver()
    yield driver
    driver.quit()


def login(driver, email, password):
    driver.get(LOGIN_URL)
    driver.find_element(By.ID, "input-email").send_keys(email)
    driver.find_element(By.ID, "input-password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()


# Runs before the valid-login test on purpose: the site locks an account after
# several failed attempts, and a successful login resets the counter.
def test_login_with_wrong_password(driver):
    """
    Scenario 2: Login fails with a wrong password
    1. Open the login page.
    2. Enter the registered e-mail address.
    3. Enter an incorrect password.
    4. Click the "Login" button.
    5. Verify the user stays on the login page.
    6. Verify the warning "No match for E-Mail Address and/or Password." is shown.
    """
    login(driver, VALID_EMAIL, "WrongPassword999")

    assert driver.current_url == LOGIN_URL
    alert = driver.find_element(By.CSS_SELECTOR, ".alert-danger")
    assert ERROR_MESSAGE in alert.text


def test_login_with_valid_credentials(driver):
    """
    Scenario 1: Login succeeds with a registered account
    1. Open the login page.
    2. Enter the registered e-mail address.
    3. Enter the correct password.
    4. Click the "Login" button.
    5. Verify the browser is redirected to the "My Account" page.
    6. Verify the page title is "My Account".
    7. Verify a "Logout" link is available.
    """
    login(driver, VALID_EMAIL, VALID_PASSWORD)

    # The redirect after login can finish after click() returns, so wait for it
    WebDriverWait(driver, 10).until(EC.url_to_be(ACCOUNT_URL))
    assert driver.current_url == ACCOUNT_URL
    assert driver.title == "My Account"
    assert len(driver.find_elements(By.LINK_TEXT, "Logout")) > 0


def test_login_with_empty_fields(driver):
    """
    Scenario 3: Login fails when both fields are empty
    1. Open the login page.
    2. Leave the e-mail field empty.
    3. Leave the password field empty.
    4. Click the "Login" button.
    5. Verify the user stays on the login page.
    6. Verify a warning message is shown.
    """
    login(driver, "", "")

    assert driver.current_url == LOGIN_URL
    # The empty e-mail is shared by everyone using this public demo site, so it
    # is often locked out; either "No match..." or a lockout warning is valid.
    alert = driver.find_element(By.CSS_SELECTOR, ".alert-danger")
    assert alert.text.startswith("Warning:")
    assert len(driver.find_elements(By.LINK_TEXT, "Logout")) == 0
