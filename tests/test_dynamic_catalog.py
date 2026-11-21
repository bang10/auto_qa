from pages.inventory_page import InventoryPage
from pages.dynamic_catalog_page import DynamicCatalogPage
from config.config import Config

def test_dynamic_catalog_lazy_load(logged_in_driver):
    """Lazy Load 검증: 화면 하단 스크롤 시 추가 아이템이 지연 로딩되는지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_lazy()

    initial_count = dynamic_page.get_loaded_item_count()
    dynamic_page.scroll_to_bottom()
    dynamic_page.wait_for_more_items(initial_count)

    after_scroll_count = dynamic_page.get_loaded_item_count()
    assert after_scroll_count > initial_count, f"상품이 로딩되지 않습니다. 스크롤 상품 개수: {after_scroll_count} / 초기 상품 개수 : {initial_count}"

def test_dynamic_catalog_spinner(logged_in_driver):
    """Spinner 검증: 로딩 스피너가 나타났다가 사라진 뒤 데이터가 노출되는지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_spinner()
    dynamic_page.trigger_and_wait_spinner()

    assert dynamic_page.is_spinner_content_displayed() is True, "로딩 스피너가 사라지지 않습니다."

def test_dynamic_catalog_slider_dot_click(logged_in_driver):
    """Slider 수동 제어 검증: dot 클릭 시 해당 순서의 슬라이드 활성화"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_slide()
    
    dots = dynamic_page.get_slider_dots()
    assert len(dots) >= 2, "캐러샐 상품이 1개만 존재합니다."

    # 인덱스 2 클릭 후 aria-current 활성화 상태 확인
    assert dynamic_page.click_slider_dot(2) is True, "인덱스 2번 닷 선택 시, 인덱스 2번 상품이 노출되지 않습니다."

    # 인덱스 0 클릭 후 복귀 확인
    assert dynamic_page.click_slider_dot(0) is True, "인덱스 0번 닷 선택 시, 인덱스 0번 상품이 노출되지 않습니다."

def test_dynamic_catalog_slider_auto_play(logged_in_driver):
    """Slider 자동 전환 검증: 약 2초 간격으로 다음 슬라이드로 자동 변경되는지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_slide()

    timeout_time = Config.DEFAULT_TIMEOUT
    # 인덱스 0으로 맞춘 뒤 자동 전환 대기
    dynamic_page.click_slider_dot(0)
    dynamic_page.wait_for_auto_slide_change(initial_index=0, timeout=timeout_time)

    assert dynamic_page.get_active_dot_index() == 1, f"Slider 상품이 자동 전환되지 않습니다. 대기 시간 : {timeout_time}초"

