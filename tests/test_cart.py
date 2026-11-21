from pages.inventory_page import InventoryPage
from pages.inventory_detail_page import InventoryDetailPage
from pages.cart_page import CartPage

def test_navigate_to_product_detail(logged_in_driver):
    """메인화면에서 상품 상세 페이지 진입 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    detail_page = InventoryDetailPage(logged_in_driver)

    target_product = "Sauce Labs Backpack"
    inventory_page.click_product_by_name(target_product)

    detail_page_product_name = detail_page.get_product_name()
    assert "inventory-item.html" in logged_in_driver.current_url, "메인화면 > 상품 상세 페이지에 진입하지 못했습니다."
    assert detail_page_product_name == target_product, f"메인화면 > 선택한 상품명과 상세 페이지의 상품명이 일치하지 않습니다. 선택한 상품명: {target_product}, 노출되는 상품명: {detail_page_product_name}"
    assert detail_page.get_product_price() == "$29.99", f"메인화면 > 선택한 상품의 가격과 상세 페이지의 가격이 일치하지 않습니다. 선택한 상품명: {target_product}, 노출되는 상품명: {detail_page_product_name}"

def test_add_to_cart_from_main_page(logged_in_driver):
    """메인화면에서 장바구니 담기 및 장바구니 페이지 진입"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)

    target_product = "Sauce Labs Bike Light"
    inventory_page.add_to_cart_by_name(target_product)

    # remove로 변경되는지 확인
    assert inventory_page.is_remove_button_displayed(target_product) is True, "메인화면 > 장바구니 선택 후, remove로 변경되지 않습니다."
    # 장바구니 뱃지 반영되는지 
    assert inventory_page.get_cart_badge_count() == 1, "메인화면 > 장바구니에 추가 후 장바구니 뱃지에 반영되지 않습니다."

    # 장바구니에 해당 상품이 있는지 확인
    inventory_page.go_to_cart()
    assert cart_page.get_title() == "Your Cart", "메인화면 > 장바구니 진입에 실패했습니다. "
    assert target_product in cart_page.get_cart_item_names(), "메인화면 > 선택한 상품이 노출되지 않습니다."

def test_add_to_cart_from_detail_page(logged_in_driver):
    """상품 상세 화면에서 장바구니 담기 및 장바구니 페이지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    detail_page = InventoryDetailPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)

    target_product = "Sauce Labs Bolt T-Shirt"
    inventory_page.click_product_by_name(target_product)

    # 상세 페이지에서 담기 후 버튼이 remove로 변경되는지 확인
    detail_page.add_to_cart()
    assert detail_page.is_remove_button_displayed() is True, "상세화면 > 장바구니 추가 후, remove로 변경되지 않습니다."
    assert inventory_page.get_cart_badge_count() == 1, "상세화면 > 장바구니 추가 후, 장바구니 뱃지에 반영되지 않습니다."

    # 장바구니 페이지 이동 후 상품 존재 여부 확인
    detail_page.go_to_cart()
    assert cart_page.get_title() == "Your Cart", "상세화면 > 장바구니 진입에 실패했습니다."
    assert target_product in cart_page.get_cart_item_names(), f"상세화면 > 선택한 상품이 장바구니에 없습니다. 선택한 상품: {target_product}"

def test_remove_item_in_cart_page(logged_in_driver):
    """여러 상품을 담은 후 장바구니에서 특정 상품 삭제 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)

    item1 = "Sauce Labs Backpack"
    item2 = "Sauce Labs Onesie"

    inventory_page.add_to_cart_by_name(item1)
    inventory_page.add_to_cart_by_name(item2)
    assert inventory_page.get_cart_badge_count() == 2, "여러개의 상품을 담은 경우 장바구니 뱃지에 반영되지 않습니다."

    inventory_page.go_to_cart()
    cart_page.remove_item_by_name(item1)

    remaining_items = cart_page.get_cart_item_names()
    assert item1 not in remaining_items, "장바구니에서 삭제한 상품이 장바구니에 노출됩니다."
    assert item2 in remaining_items, "장바구니에에서 삭제하지 않은 상품이 장바구니에서 미노출됩니다."
    assert inventory_page.get_cart_badge_count() == 1, "장바구니에서 삭제 후 장바구니 뱃지 확인 시, 상품 개수와 일치하지 않습니다."

def test_go_to_inventory_by_cart(logged_in_driver):
    """장바구니에서 메인화면 이동 확인"""
    cart_page = CartPage(logged_in_driver)
    inventory_page = InventoryDetailPage(logged_in_driver)
    inventory_page.go_to_cart()

    cart_page.go_to_inventory()
    assert "inventory.html" in logged_in_driver.current_url, "장바구니에서 메인 화면 이동에 실패했습니다."

def test_navigate_to_detail_from_cart(logged_in_driver):
    """장바구니에서 상품 클릭 시 상품 상세 이동"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    detail_page = InventoryDetailPage(logged_in_driver)

    target_product = "Sauce Labs Fleece Jacket"

    # 상품을 장바구니에 담고 장바구니 페이지로 이동
    inventory_page.add_to_cart_by_name(target_product)
    inventory_page.go_to_cart()

    # 장바구니에 담긴 상품 제목 클릭
    cart_page.click_product_by_name(target_product)

    # 상세 페이지 진입 및 상품 정보, 담김 상태 검증
    assert "inventory-item.html" in logged_in_driver.current_url, "장바구니 > 상품 상세 화면 진입에 실패했습니다."
    assert detail_page.get_product_name() == target_product, "장바구니 > 선택한 상품의 이름과 상세 화면의 상품명이 일치하지 않습니다."
    assert detail_page.get_product_price() == "$49.99", "장바구니 > 선택한 상품의 가격과 상세 화면의 가격이 일치하지 않습니다."
    assert detail_page.is_remove_button_displayed() is True, "장바구니 > 선택한 상품의 장바구니 remove버튼이 미노출됩니다."
