import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from test_setup import make_driver

PRODUCT_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=product/product&product_id=40"
CART_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=checkout/cart"
PRODUCT_NAME = "iPhone"

UPDATE_MESSAGE = "Success: You have modified your shopping cart!"
SHIPPING_MESSAGE = "Success: Your shipping estimate has been applied!"
EMPTY_CART_MESSAGE = "Your shopping cart is empty!"


@pytest.fixture
def driver():
    driver = make_driver()
    driver.set_window_size(1400, 1000)
    yield driver
    driver.quit()


@pytest.fixture
def cart_with_product(driver):
    # Each test gets a new browser session, so it starts with its own empty cart
    driver.get(PRODUCT_URL)
    add_button = next(b for b in driver.find_elements(By.CSS_SELECTOR, "button.button-cart") if b.is_displayed())
    add_button.click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "notification-box-top"), "Success: You have added")
    )
    driver.get(CART_URL)
    return driver


def wait_for_success_alert(driver):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#content .alert-success, .alert-success"))
    )


def test_update_product_quantity(cart_with_product):
    """
    Scenario 1: Update the quantity of a product in the cart
    1. Open a product page and click "Add to Cart".
    2. Open the shopping cart page.
    3. Verify the product is listed in the cart with quantity 1.
    4. Change the quantity to 3.
    5. Click the "Update" button.
    6. Verify the message "Success: You have modified your shopping cart!" is shown.
    7. Verify the quantity is 3.
    8. Verify the product total equals the unit price multiplied by 3.
    """
    driver = cart_with_product
    row = driver.find_element(By.CSS_SELECTOR, "#content tbody tr")
    assert PRODUCT_NAME in row.text
    quantity = driver.find_element(By.CSS_SELECTOR, "#content input[name^='quantity']")
    assert quantity.get_attribute("value") == "1"

    quantity.clear()
    quantity.send_keys("3")
    driver.find_element(By.CSS_SELECTOR, "#content button[title='Update']").click()

    alert = wait_for_success_alert(driver)
    assert UPDATE_MESSAGE in alert.text
    quantity = driver.find_element(By.CSS_SELECTOR, "#content input[name^='quantity']")
    assert quantity.get_attribute("value") == "3"

    # Columns: Image, Product Name, Model, Quantity, Unit Price, Total
    cells = driver.find_elements(By.CSS_SELECTOR, "#content tbody tr td")
    unit_price = float(cells[4].text.replace("$", "").replace(",", ""))
    total = float(cells[5].text.replace("$", "").replace(",", ""))
    assert total == pytest.approx(unit_price * 3)


def test_estimate_shipping_and_taxes(cart_with_product):
    """
    Scenario 2: Estimate shipping and taxes for Australia, NSW, 2000
    1. Open a product page and click "Add to Cart".
    2. Open the shopping cart page.
    3. Click "Estimate Shipping & Taxes" to expand the section.
    4. Select "Australia" as the country.
    5. Select "New South Wales" as the region / state.
    6. Enter "2000" as the post code.
    7. Click the "Get Quotes" button.
    8. Verify a pop-up with the shipping methods is shown.
    9. Select the "Flat Shipping Rate" option.
    10. Click the "Apply Shipping" button.
    11. Verify the message "Success: Your shipping estimate has been applied!" is shown.
    12. Verify the cart totals include the "Flat Shipping Rate" line.
    """
    driver = cart_with_product
    driver.find_element(By.CSS_SELECTOR, "[data-target='#collapse-shipping']").click()

    country = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "input-country")))
    Select(country).select_by_visible_text("Australia")
    # The region list is loaded with AJAX after the country changes
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//select[@id='input-zone']/option[text()='New South Wales']"))
    )
    Select(driver.find_element(By.ID, "input-zone")).select_by_visible_text("New South Wales")
    postcode = driver.find_element(By.ID, "input-postcode")
    postcode.clear()
    postcode.send_keys("2000")
    driver.find_element(By.ID, "button-quote").click()

    modal = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "modal-shipping")))
    assert "Flat Shipping Rate" in modal.text
    # The radio is covered by a styled label, so click it with JavaScript
    radio = modal.find_element(By.CSS_SELECTOR, "input[name='shipping_method'][value='flat.flat']")
    driver.execute_script("arguments[0].click();", radio)
    driver.find_element(By.ID, "button-shipping").click()

    alert = wait_for_success_alert(driver)
    assert SHIPPING_MESSAGE in alert.text
    totals = driver.find_elements(By.CSS_SELECTOR, "#content table")[-1]
    assert "Flat Shipping Rate" in totals.text


def test_remove_product_from_cart(cart_with_product):
    """
    Scenario 3: Remove the product and empty the cart
    1. Open a product page and click "Add to Cart".
    2. Open the shopping cart page.
    3. Verify the product is listed in the cart.
    4. Click the "Remove" button of the product.
    5. Verify the message "Your shopping cart is empty!" is shown.
    6. Verify no product rows are left in the cart.
    """
    driver = cart_with_product
    assert PRODUCT_NAME in driver.find_element(By.CSS_SELECTOR, "#content tbody tr").text

    driver.find_element(By.CSS_SELECTOR, "#content button[title='Remove']").click()

    # Remove is done with AJAX and then the page reloads
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "content"), EMPTY_CART_MESSAGE)
    )
    assert len(driver.find_elements(By.CSS_SELECTOR, "#content input[name^='quantity']")) == 0
