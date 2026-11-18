from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from config.config import Config

def test_logout_from_sidebar(logged_in_driver):
    """사이드바 메뉴에서 Logout 클릭 시 로그인 페이지 복귀 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    login_page = LoginPage(logged_in_driver)

    inventory_page.click_logout()

    # 로그인 페이지 URL 및 로그인 버튼 노출 여부 검증
    assert logged_in_driver.current_url == login_page.URL
    assert login_page.is_displayed(login_page.LOGIN_BUTTON) is True

def test_block_direct_access_after_logout(logged_in_driver):
    """로그아웃 후 직접 URL 접근 차단 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    login_page = LoginPage(logged_in_driver)

    inventory_page.click_logout()
    assert login_page.is_displayed(login_page.LOGIN_BUTTON) is True

    logged_in_driver.get(Config.INVENTORY_URL)

    assert logged_in_driver.current_url == login_page.URL
    assert "You can only access '/inventory.html' when you are logged in." in login_page.get_error_message()