# Software Testing Project

This project uses **Selenium** and **pytest** to test a website automatically.
The website is a demo online shop: <https://opencart.abstracta.us>.
The tests open a Chrome browser (with no window), click buttons, fill in forms, and then check that the results are correct.

## How to Run

1. Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Run all tests:

   ```bash
   pytest
   ```

   Or run only one file, for example:

   ```bash
   pytest test_login.py
   ```

> You need Chrome installed and an internet connection.

## What Each File Does

### `test_setup.py` — Set up the browser

- `make_driver()`: Opens a Chrome browser. The Codespace has no screen, so Chrome runs in "headless" mode (no window). All other test files use this function to open the browser.
- `test_locators()`: A simple practice test. It opens a Selenium sample page, finds items on the page in three ways (CSS, ID, and XPath), and checks their values.

### `test_login.py` — Test the login page

There are 3 tests:

| Test | What it does | Expected result |
| --- | --- | --- |
| `test_login_with_wrong_password` | Log in with the right email and a wrong password | Stays on the login page and shows an error |
| `test_login_with_valid_credentials` | Log in with the right email and the right password | Goes to the "My Account" page and shows "Logout" |
| `test_login_with_empty_fields` | Log in with both fields empty | Stays on the login page and shows a warning |

### `test_edit_cart.py` — Test the shopping cart

Each test first adds a product (iPhone) to the cart, then opens the cart page. Every test uses a new browser, so the cart always starts empty. There are 3 tests:

| Test | What it does | Expected result |
| --- | --- | --- |
| `test_update_product_quantity` | Change the quantity from 1 to 3 and click "Update" | Shows a success message, quantity is 3, total = unit price × 3 |
| `test_estimate_shipping_and_taxes` | Choose Australia, New South Wales, post code 2000, and get shipping quotes | Shows shipping options; after choosing "Flat Shipping Rate", shows a success message |
| `test_remove_product_from_cart` | Click "Remove" to delete the product | Shows "Your shopping cart is empty!" and no products are left |

### `test_product_review.py` — Test product reviews

Each test opens the iPhone product page and clicks the "Reviews" tab. There are 3 tests:

| Test | What it does | Expected result |
| --- | --- | --- |
| `test_write_valid_review` | Enter a name, write a review, choose 5 stars, and submit | Shows a thank-you message and the review box is cleared |
| `test_write_empty_review` | Enter a name and choose 5 stars, but leave the review empty | Shows a warning: the review must be 25 to 1000 characters |
| `test_write_review_without_rating` | Enter a name and write a review, but do not choose a rating | Shows a warning to choose a rating; the review text is kept |

## Other Files

- `requirements.txt`: The Python packages to install (`selenium` and `pytest`).
- `.gitignore`: Tells Git which files not to track.
