import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from test_setup import make_driver

ARTICLE_URL = "https://ecommerce-playground.lambdatest.io/index.php?route=extension/maza/blog/article&article_id=37"
ARTICLE_TITLE = "amet volutpat consequat mauris nunc congue nisi vitae suscipit tellus"

NAME = "Systems Tester"
EMAIL = "st.test.1792645713@example.com"
COMMENT = "This is an automated Selenium test comment."
REPLY = "This is an automated Selenium test reply."

SUCCESS_MESSAGE = "Thank you for your comment. It has been submitted to the webmaster for approval."
EMPTY_COMMENT_MESSAGE = "Warning: Comment Text must be between 25 and 1000 characters!"


@pytest.fixture
def driver():
    driver = make_driver()
    yield driver
    driver.quit()


def open_article(driver):
    driver.get(ARTICLE_URL)
    assert driver.find_element(By.TAG_NAME, "h1").text == ARTICLE_TITLE


def fill_comment_form(driver, name, email, comment):
    driver.find_element(By.ID, "input-name").send_keys(name)
    driver.find_element(By.ID, "input-email").send_keys(email)
    driver.find_element(By.ID, "input-comment").send_keys(comment)
    driver.find_element(By.ID, "button-comment").click()


def wait_for_success_alert(driver):
    # The comment is posted with AJAX, so wait for the alert instead of sleeping
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )


def test_write_valid_comment(driver):
    """
    Scenario 1: Write a valid comment on an article
    1. Open the blog article page (article_id=37).
    2. Verify the article title is shown.
    3. Enter a name in the "Your Name" field.
    4. Enter an e-mail address in the "Email" field.
    5. Enter a comment of 25-1000 characters in the "Your comment" field.
    6. Click the "Post comment" button.
    7. Verify the message "Thank you for your comment. It has been submitted
       to the webmaster for approval." is shown.
    8. Verify the comment field is cleared.
    """
    open_article(driver)

    fill_comment_form(driver, NAME, EMAIL, COMMENT)

    alert = wait_for_success_alert(driver)
    assert SUCCESS_MESSAGE in alert.text
    assert driver.find_element(By.ID, "input-comment").get_attribute("value") == ""


def test_write_empty_comment(driver):
    """
    Scenario 2: Write an empty comment on an article
    1. Open the blog article page (article_id=37).
    2. Verify the article title is shown.
    3. Enter a name in the "Your Name" field.
    4. Enter an e-mail address in the "Email" field.
    5. Leave the "Your comment" field empty.
    6. Click the "Post comment" button.
    7. Verify the comment field is highlighted as invalid.
    8. Verify the warning "Comment Text must be between 25 and 1000 characters!" is shown.
    9. Verify no success message is shown.
    """
    open_article(driver)

    fill_comment_form(driver, NAME, EMAIL, "")

    comment_box = driver.find_element(By.ID, "input-comment")
    WebDriverWait(driver, 10).until(
        lambda d: "is-invalid" in comment_box.get_attribute("class")
    )
    feedback = driver.find_element(By.XPATH, "//textarea[@id='input-comment']/following-sibling::div[@class='invalid-feedback']")
    assert feedback.is_displayed()
    assert feedback.text == EMPTY_COMMENT_MESSAGE
    assert len(driver.find_elements(By.CSS_SELECTOR, ".alert-success")) == 0


def test_reply_to_existing_comment(driver):
    """
    Scenario 3: Reply to an existing comment
    1. Open the blog article page (article_id=37).
    2. Verify the article title is shown.
    3. Click the "Reply" link of the first comment in the comment list.
    4. Verify the comment form moves under that comment and
       a "Cancel reply" link is shown.
    5. Enter a name in the "Your Name" field.
    6. Enter an e-mail address in the "Email" field.
    7. Enter a reply of 25-1000 characters in the "Your comment" field.
    8. Click the "Post comment" button.
    9. Verify the message "Thank you for your comment. It has been submitted
       to the webmaster for approval." is shown.
    """
    open_article(driver)

    # The comment list is loaded with AJAX after the page opens
    reply_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#comment a.reply"))
    )
    comment_id = reply_link.get_attribute("data-reply_to")
    reply_link.click()

    parent_id = driver.find_element(By.ID, "input-parent-comment-id")
    assert parent_id.get_attribute("value") == comment_id
    form_under_comment = driver.find_elements(By.XPATH, f"//*[@id='comment{comment_id}']//form[@id='form-comment']")
    assert len(form_under_comment) == 1
    assert driver.find_element(By.LINK_TEXT, "CANCEL REPLY").is_displayed()

    fill_comment_form(driver, NAME, EMAIL, REPLY)

    alert = wait_for_success_alert(driver)
    assert SUCCESS_MESSAGE in alert.text
