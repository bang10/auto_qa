import pytest
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_step_one_page import CheckoutStepOnePage
from pages.checkout_step_two_page import CheckoutStepTwoPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.inventory_detail_page import InventoryDetailPage

def test_complete_checkout_flow(logged_in_driver):
    """장바구니 추가부터 주문 완료까지"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    step_one_page = CheckoutStepOnePage(logged_in_driver)
    step_two_page = CheckoutStepTwoPage(logged_in_driver)
    complete_page = CheckoutCompletePage(logged_in_driver)

    # 1) 상품 2개 담고 장바구니 이동 후 Checkout 클릭
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")     # $29.99
    inventory_page.add_to_cart_by_name("Sauce Labs Bike Light")   # $9.99
    inventory_page.go_to_cart()
    cart_page.proceed_to_checkout()

    # 2) Step 1: 배송 정보 입력
    assert step_one_page.get_title() == "Checkout: Your Information"
    step_one_page.enter_shipping_info("Gildong", "Hong", "13529")
    step_one_page.click_continue()

    # 3) Step 2: 상품 합계 + 세금 = 최종 결제 금액 일치 여부 검증
    assert step_two_page.get_title() == "Checkout: Overview"
    item_total = step_two_page.get_item_total()
    tax = step_two_page.get_tax()
    total = step_two_page.get_total()

    assert item_total == 39.98
    assert round(item_total + tax, 2) == total
    step_two_page.click_finish()

    # 4) Complete: 주문 완료 화면 및 장바구니 뱃지 초기화 확인
    assert complete_page.get_title() == "Checkout: Complete!"
    assert complete_page.get_complete_message() == "Thank you for your order!"
    assert inventory_page.get_cart_badge_count() == 0

@pytest.mark.parametrize("first_name, last_name, postal_code, expected_error", [
    ("", "Hong", "13529", "Error: First Name is required"),
    ("Gildong", "", "13529", "Error: Last Name is required"),
    ("Gildong", "Hong", "", "Error: Postal Code is required"),
])
def test_checkout_step_one_validation(logged_in_driver, first_name, last_name, postal_code, expected_error):
    """ 배송 정보 필수 입력값 누락 검증 """
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    step_one_page = CheckoutStepOnePage(logged_in_driver)

    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    cart_page.proceed_to_checkout()

    step_one_page.enter_shipping_info(first_name, last_name, postal_code)
    step_one_page.click_continue()

    assert step_one_page.get_error_message() == expected_error


def test_navigate_to_detail_from_checkout_step_two(logged_in_driver):
    """Step2 상품 제목 선택 시 상품 상세로 이동"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    step_one_page = CheckoutStepOnePage(logged_in_driver)
    step_two_page = CheckoutStepTwoPage(logged_in_driver)
    detail_page = InventoryDetailPage(logged_in_driver)

    target_product = "Sauce Labs Onesie"

    # 상품 담기 > 장바구니 > Checkout Step 1 > Step2까지 이동
    inventory_page.add_to_cart_by_name(target_product)
    inventory_page.go_to_cart()
    cart_page.proceed_to_checkout()

    step_one_page.enter_shipping_info("Gildong", "Hong", "13529")
    step_one_page.click_continue()
    assert step_two_page.get_title() == "Checkout: Overview"

    # 주문 요약 화면에서 상품 제목 클릭
    step_two_page.click_product_by_name(target_product)

    # 상세 페이지 진입 및 상품 정보, 담김 상태 검증
    assert "inventory-item.html" in logged_in_driver.current_url
    assert detail_page.get_product_name() == target_product
    assert detail_page.get_product_price() == "$7.99"
    assert detail_page.is_remove_button_displayed() is True

# TODO step 3 영수증 다운로드


