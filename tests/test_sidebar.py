from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

def test_sidebar_all_items_navigation(logged_in_driver):
    """다른 페이지에서 사이드바 [All Items] 클릭 시 메인 상품 목록으로 이동 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)

    inventory_page.go_to_cart()
    assert "cart.html" in logged_in_driver.current_url, "장바구니로 이동하지 않습니다."

    cart_page.click_all_items()
    assert "inventory.html" in logged_in_driver.current_url, "카테고리 > [All Items] 선택 시, 전체 상품 화면으로 진입하지 않습니다."
    assert inventory_page.get_title() == "Products", "카테고리 > [All Items] 선택 시, 전체 상품 화면으로 진입하지 않습니다."

def test_sidebar_open_and_close(logged_in_driver):
    """사이드바 열기 및 닫기 동작 검증"""
    inventory_page = InventoryPage(logged_in_driver)

    inventory_page.open_sidebar()
    assert inventory_page.is_sidebar_open() is True, "[메뉴열기] 버튼 선택 시, 네비게이션 바가 노출되지 않습니다. "

    inventory_page.close_sidebar()
    assert inventory_page.is_sidebar_open() is False, "[메뉴닫기] 버튼 선택 시, 네비게이션 바가 닫히지 않습니다. "


