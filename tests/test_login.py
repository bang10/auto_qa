import pytest
from config.config import Config
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

def test_login_success(driver):
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    login_id = Config.STANDARD_USER
    # login_password = Config.PASSWORD
    login_password = "ddddd"
    login_page.load()
    login_page.login(login_id, login_password)

    assert "inventory.html" in driver.current_url, f"로그인에 실패했습니다. id: {login_id}, pw: {login_password}"
    assert inventory_page.get_title() == "Products", f"로그인 성공 후, 메인 화면으로 이동 실패했습니다."

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


