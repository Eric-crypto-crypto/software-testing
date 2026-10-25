import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from test_setup import make_driver

PRODUCT_URL = "https://opencart.abstracta.us/index.php?route=product/product&product_id=40"
PRODUCT_NAME = "iPhone"

NAME = "Systems Tester"
REVIEW = "This is an automated Selenium test review."
RATING = "5"

SUCCESS_MESSAGE = "Thank you for your review. It has been submitted to the webmaster for approval."
EMPTY_REVIEW_MESSAGE = "Warning: Review Text must be between 25 and 1000 characters!"
NO_RATING_MESSAGE = "Warning: Please select a review rating!"


@pytest.fixture
def driver():
    driver = make_driver()
    driver.set_window_size(1400, 1000)
    yield driver
    driver.quit()


def open_review_tab(driver):
    driver.get(PRODUCT_URL)
    assert driver.find_element(By.CSS_SELECTOR, "#content h1").text == PRODUCT_NAME
    driver.find_element(By.CSS_SELECTOR, "a[href='#tab-review']").click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "form-review")))


def fill_review_form(driver, name, review, rating):
    driver.find_element(By.ID, "input-name").send_keys(name)
    driver.find_element(By.ID, "input-review").send_keys(review)
    if rating:
        driver.find_element(By.CSS_SELECTOR, f"input[name='rating'][value='{rating}']").click()
    driver.find_element(By.ID, "button-review").click()


def wait_for_alert(driver, alert_class):
    # The review is posted with AJAX, so wait for the alert instead of sleeping
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, f"#form-review .{alert_class}"))
    )


def test_write_valid_review(driver):
    """
    Scenario 1: Write a valid review for a product
    1. Open the product page (iPhone, product_id=40).
    2. Verify the product name is shown.
    3. Click the "Reviews" tab.
    4. Enter a name in the "Your Name" field.
    5. Enter a review of 25-1000 characters in the "Your Review" field.
    6. Select a rating of 5.
    7. Click the "Continue" button.
    8. Verify the message "Thank you for your review. It has been submitted
       to the webmaster for approval." is shown.
    9. Verify the review field is cleared.
    """
    open_review_tab(driver)

    fill_review_form(driver, NAME, REVIEW, RATING)

    alert = wait_for_alert(driver, "alert-success")
    assert SUCCESS_MESSAGE in alert.text
    assert driver.find_element(By.ID, "input-review").get_attribute("value") == ""


def test_write_empty_review(driver):
    """
    Scenario 2: Write an empty review for a product
    1. Open the product page (iPhone, product_id=40).
    2. Verify the product name is shown.
    3. Click the "Reviews" tab.
    4. Enter a name in the "Your Name" field.
    5. Leave the "Your Review" field empty.
    6. Select a rating of 5.
    7. Click the "Continue" button.
    8. Verify the warning "Review Text must be between 25 and 1000 characters!" is shown.
    9. Verify no success message is shown.
    """
    open_review_tab(driver)

    fill_review_form(driver, NAME, "", RATING)

    alert = wait_for_alert(driver, "alert-danger")
    assert alert.text.startswith(EMPTY_REVIEW_MESSAGE)
    assert len(driver.find_elements(By.CSS_SELECTOR, "#form-review .alert-success")) == 0


def test_write_review_without_rating(driver):
    """
    Scenario 3: Write a review without selecting a rating
    1. Open the product page (iPhone, product_id=40).
    2. Verify the product name is shown.
    3. Click the "Reviews" tab.
    4. Enter a name in the "Your Name" field.
    5. Enter a review of 25-1000 characters in the "Your Review" field.
    6. Do not select a rating.
    7. Click the "Continue" button.
    8. Verify the warning "Please select a review rating!" is shown.
    9. Verify the review text is kept in the form.
    """
    open_review_tab(driver)

    fill_review_form(driver, NAME, REVIEW, None)

    alert = wait_for_alert(driver, "alert-danger")
    assert alert.text.startswith(NO_RATING_MESSAGE)
    assert driver.find_element(By.ID, "input-review").get_attribute("value") == REVIEW
