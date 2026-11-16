from pages.inventory_page import InventoryPage
from pages.inventory_detail_page import InventoryDetailPage

def test_back_to_products(logged_in_driver):
    """제품 상세 화면에서 뒤로 가기"""
    inventory_page = InventoryPage(logged_in_driver)
    inventroy_detail_page = InventoryDetailPage(logged_in_driver)

    target_product = "Sauce Labs Backpack"
    inventory_page.click_product_by_name(target_product)

    inventroy_detail_page.back_to_products()
    assert "inventory.html" in logged_in_driver.current_url

