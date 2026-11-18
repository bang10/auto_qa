import pytest
from config.config import Config
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

def test_login_success(driver):
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    login_page.load()
    login_page.login(Config.STANDARD_USER, Config.PASSWORD)

    assert "inventory.html" in driver.current_url
    assert inventory_page.get_title() == "Products"

@pytest.mark.parametrize("username, password, expected_error", [
    (Config.LOCKED_OUT_USER, Config.PASSWORD, "Sorry, this user has been locked out."),
    ("invalid_user", "wrong_pass", "Username and password do not match"),
    ("", "secret_sauce", "Username is required"),
    (Config.STANDARD_USER, "", "Password is required")
])
def test_login_fail(driver, username, password, expected_error):
    login_page = LoginPage(driver)

    login_page.load()
    login_page.login(username, password)

    assert expected_error in login_page.get_error_message()
