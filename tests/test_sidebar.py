from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

def test_sidebar_all_items_navigation(logged_in_driver):
    """다른 페이지에서 사이드바 [All Items] 클릭 시 메인 상품 목록으로 이동 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)

    inventory_page.go_to_cart()
    assert "cart.html" in logged_in_driver.current_url

    cart_page.click_all_items()
    assert "inventory.html" in logged_in_driver.current_url
    assert inventory_page.get_title() == "Products"

def test_sidebar_open_and_close(logged_in_driver):
    """사이드바 열기 및 닫기 동작 검증"""
    inventory_page = InventoryPage(logged_in_driver)

    inventory_page.open_sidebar()
    assert inventory_page.is_sidebar_open() is True

    inventory_page.close_sidebar()
    assert inventory_page.is_sidebar_open() is False


