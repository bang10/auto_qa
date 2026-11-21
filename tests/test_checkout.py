import pytest
import os
from conftest import DOWNLOAD_DIR
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
    assert step_one_page.get_title() == "Checkout: Your Information", "배송 정보 입력 페이지에 진입하지 못했습니다."
    step_one_page.enter_shipping_info("Gildong", "Hong", "13529")
    step_one_page.click_continue()

    # 3) Step 2: 상품 합계 + 세금 = 최종 결제 금액 일치 여부 검증
    assert step_two_page.get_title() == "Checkout: Overview", "최종 결제 화면에 진입하지 못했습니다."
    item_total = step_two_page.get_item_total()
    tax = step_two_page.get_tax()
    total = step_two_page.get_total()

    assert item_total == 39.98, f"기대 총 상품 가격이 다릅니다. 실제 총 상품 가격: {item_total}, 기대 상품 총 가격: 39.38"
    assert round(item_total + tax, 2) == total, f"세금 포함 총 가격 정보가 일치하지 않습니다. 실제 세금 포함 가격: {round(item_total + tax, 2)}, 토탈 가격: {total}"
    step_two_page.click_finish()

    # 4) Complete: 주문 완료 화면 및 장바구니 뱃지 초기화 확인
    assert complete_page.get_title() == "Checkout: Complete!", "주문 완료 화면에 진입하지 못했습니다."
    assert complete_page.get_complete_message() == "Thank you for your order!", "주문 완료 화면에 진입하지 못했습니다."
    assert inventory_page.get_cart_badge_count() == 0, "주문 완료 후 장바구니 뱃지에 반영되지 않습니다."

@pytest.mark.parametrize("first_name, last_name, postal_code, expected_error", [
    ("", "sec", "12345", "Error: First Name is required"),
    ("fir", "", "12345", "Error: Last Name is required"),
    ("fir", "sec", "", "Error: Postal Code is required"),
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

    assert step_one_page.get_error_message() == expected_error, f"배송 정보 필수 입력 값 누락 시, 노출되는 문구가 다릅니다. : 기대 : {expected_error}, 실제 : {step_one_page.get_error_message()}"


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

    step_one_page.enter_shipping_info("seong", "seong", "12345")
    step_one_page.click_continue()
    assert step_two_page.get_title() == "Checkout: Overview", "최종 결제 화면에 진입하지 못했습니다."

    # 주문 요약 화면에서 상품 제목 클릭
    step_two_page.click_product_by_name(target_product)

    # 상세 페이지 진입 및 상품 정보, 담김 상태 검증
    assert "inventory-item.html" in logged_in_driver.current_url, "상품 상세 페이지에 진입하지 못했습니다."
    assert detail_page.get_product_name() == target_product, "상품 상세 페이지의 상품명과 선택한 상품명이 서로 다릅니다."
    assert detail_page.get_product_price() == "$7.99", "상품 상세 페이지의 상품 가격과 선택한 상품 가격이 서로 다릅니다."
    assert detail_page.is_remove_button_displayed() is True, "장바구니 삭제 버튼이 미노출됩니다."

def test_back_to_products_from_checkout_complete(logged_in_driver):
    """결제 완료 화면에서 Back Home 버튼 클릭 시 inventory.html 페이지로 이동 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    step_one_page = CheckoutStepOnePage(logged_in_driver)
    step_two_page = CheckoutStepTwoPage(logged_in_driver)
    complete_page = CheckoutCompletePage(logged_in_driver)

    # 결제 완료 단계까지 진행
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    cart_page.proceed_to_checkout()
    step_one_page.enter_shipping_info("seong", "seong", "1234")
    step_one_page.click_continue()
    step_two_page.click_finish()
    assert complete_page.get_title() == "Checkout: Complete!", "결제 완료 화면에 진입하지 못했습니다."

    # Back Home 버튼 클릭 및 메인 상품 목록 이동 검증
    complete_page.click_back_home()
    assert "inventory.html" in logged_in_driver.current_url, "결제 완료 화면 > [홈으로 이동] 선택 시, 홈으로 이동하지 않습니다."
    assert inventory_page.get_title() == "Products", "결제 화면 완료 > [홈으로 이동] 선택 시, 홈으로 이동되지 않습니다."

def test_generate_pdf_order_download(logged_in_driver):
    """결제 완료 화면에서 영수증 PDF 다운로드 버튼 클릭 시 실제 PDF 파일 생성 및 용량 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    step_one_page = CheckoutStepOnePage(logged_in_driver)
    step_two_page = CheckoutStepTwoPage(logged_in_driver)
    complete_page = CheckoutCompletePage(logged_in_driver)

    # 결제 완료 단계까지 진행
    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    cart_page.proceed_to_checkout()
    step_one_page.enter_shipping_info("seong", "seong", "1234")
    step_one_page.click_continue()
    step_two_page.click_finish()
    assert complete_page.get_title() == "Checkout: Complete!", "결제 완료 화면에 진입하지 못했습니다."

    # 다운로드 전 폴더 파일 목록 스냅샷 기록 후 PDF 버튼 클릭
    before_files = set(os.listdir(DOWNLOAD_DIR))
    complete_page.click_generate_pdf_order()

    # 새 PDF 파일 다운로드 완료 대기 및 실제 파일 크기(> 0 bytes) 검증
    downloaded_filename = complete_page.wait_for_pdf_download(DOWNLOAD_DIR, before_files)
    downloaded_filepath = os.path.join(DOWNLOAD_DIR, downloaded_filename)

    assert downloaded_filename.lower().endswith(".pdf"), "영수증 PDF 다운로드에 실패했습니다."
    assert os.path.getsize(downloaded_filepath) > 0, "영수증 PDF 파일 크기가 0 이하입니다."

    # 검증 완료 후 테스트 폴더 정리를 위해 다운로드된 임시 파일 삭제
    os.remove(downloaded_filepath)

def test_checkout_shipping_inputs_preserve_values_baseline(logged_in_driver):
    """정상 기준선 대비 결제 정보(First Name, Last Name, Postal Code) 개별 입력값 유지 여부 검증"""
    inventory_page = InventoryPage(logged_in_driver)
    cart_page = CartPage(logged_in_driver)
    step_one_page = CheckoutStepOnePage(logged_in_driver)

    expected_info = {
        "first_name": "fir",
        "last_name": "sec",
        "postal_code": "12345",
    }

    inventory_page.add_to_cart_by_name("Sauce Labs Backpack")
    inventory_page.go_to_cart()
    cart_page.proceed_to_checkout()

    # 배송 정보 3개 필드 순차 입력
    step_one_page.enter_shipping_info(
        expected_info["first_name"],
        expected_info["last_name"],
        expected_info["postal_code"]
    )

    # 입력 직후 각 필드의 실제 value가 일치하는지
    actual_info = step_one_page.get_entered_shipping_info()

    assert actual_info == expected_info, (
        f"- 기대값(Expected): {expected_info}\n"
        f"- 실제값(Actual)  : {actual_info}"
    )