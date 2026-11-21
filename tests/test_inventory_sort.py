import pytest
from pages.inventory_page import InventoryPage

@pytest.mark.parametrize("option_value, is_reverse", [
    ("az", False),
    ("za", True),
])
def test_sort_products_by_name(logged_in_driver, option_value, is_reverse):
    """이름순 정렬, A > Z / Z > A"""
    inventory_page = InventoryPage(logged_in_driver)

    inventory_page.select_sort_option(option_value)
    displayed_names = inventory_page.get_all_product_names()

    assert displayed_names == sorted(displayed_names, reverse=is_reverse), "상품이 이름순으로 정렬되지 않습니다."

@pytest.mark.parametrize("option_value, is_reverse", [
    ("lohi", False),
    ("hilo", True),
])
def test_sort_products_by_price(logged_in_driver, option_value, is_reverse):
    """가격순 정렬, 낮은 가격 > 높은 가격 / 높은 가격 > 낮은 가격"""
    inventory_page = InventoryPage(logged_in_driver)

    inventory_page.select_sort_option(option_value)
    displayed_prices = inventory_page.get_all_product_prices()

    assert displayed_prices == sorted(displayed_prices, reverse=is_reverse), "상품이 가격순으로 정렬되지 않습니다."

    
    