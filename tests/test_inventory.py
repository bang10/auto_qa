import pytest
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.inventory_detail_page import InventoryDetailPage
from config.config import Config

def test_back_to_products(logged_in_driver):
    """제품 상세 화면에서 뒤로 가기"""
    inventory_page = InventoryPage(logged_in_driver)
    inventroy_detail_page = InventoryDetailPage(logged_in_driver)

    target_product = "Sauce Labs Backpack"
    inventory_page.click_product_by_name(target_product)

    inventroy_detail_page.back_to_products()
    assert "inventory.html" in logged_in_driver.current_url, "제품 상세에 뒤로 가기 시, 홈 화면으로 이동하지 않습니다."

EXPECTED_PRODUCT_THUMBNAILS = {
    "Sauce Labs Backpack": "sauce-backpack-1200x1500",
    "Sauce Labs Bike Light": "bike-light-1200x1500",
    "Sauce Labs Bolt T-Shirt": "bolt-shirt-1200x1500",
    "Sauce Labs Fleece Jacket": "sauce-pullover-1200x1500",
    "Sauce Labs Onesie": "red-onesie-1200x1500",
    "Test.allTheThings() T-Shirt (Red)": "red-tatt-1200x1500",
}
def test_product_thumbnails_match_expected_baseline(logged_in_driver):
    inventory_page = InventoryPage(logged_in_driver)

    actual_thumbnails = inventory_page.get_product_thumbnail_map()
    mismatched_products = []

    for product_name, expected_keyword in EXPECTED_PRODUCT_THUMBNAILS.items():
        actual_src = actual_thumbnails.get(product_name, "")
        if expected_keyword not in actual_src:
            mismatched_products.append(
                f"- {product_name}: 기대값('{expected_keyword}') != 실제값('{actual_src}')"
            )

    assert not mismatched_products, (
        f"정상 기준선과 다른 상품 썸네일이 {len(mismatched_products)}건 검출되었습니다:\n"
        + "\n".join(mismatched_products)
    )