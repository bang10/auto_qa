from pages.inventory_page import InventoryPage
from pages.dynamic_catalog_page import DynamicCatalogPage

def test_dynamic_catalog_lazy_load(logged_in_driver):
    """Lazy Load 검증: 화면 하단 스크롤 시 추가 아이템이 지연 로딩되는지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_lazy()

    initial_count = dynamic_page.get_loaded_item_count()
    dynamic_page.scroll_to_bottom()
    dynamic_page.wait_for_more_items(initial_count)

    after_scroll_count = dynamic_page.get_loaded_item_count()
    assert after_scroll_count > initial_count

def test_dynamic_catalog_spinner(logged_in_driver):
    """Spinner 검증: 로딩 스피너가 나타났다가 사라진 뒤 데이터가 노출되는지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_spinner()
    dynamic_page.trigger_and_wait_spinner()

    assert dynamic_page.is_spinner_content_displayed() is True

# FIXME 전체적인 수정 필요
def test_dynamic_catalog_slider_dot_click(logged_in_driver):
    """Slider 수동 제어 검증: dot 클릭 시 해당 순서의 슬라이드 활성화"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_slide()
    
    dots = dynamic_page.get_slider_dots()
    assert len(dots) >= 3  # 슬라이더 닷이 여러 개 존재하는지 확인

    # 인덱스 2 클릭 후 aria-current 활성화 상태 확인
    assert dynamic_page.click_slider_dot(2) is True

    # 인덱스 0 클릭 후 복귀 확인
    assert dynamic_page.click_slider_dot(0) is True

def test_dynamic_catalog_slider_auto_play(logged_in_driver):
    """Slider 자동 전환 검증: 약 2초 간격으로 다음 슬라이드로 자동 변경되는지 확인"""
    inventory_page = InventoryPage(logged_in_driver)
    dynamic_page = DynamicCatalogPage(logged_in_driver)

    inventory_page.click_slide()

    # 인덱스 0으로 맞춘 뒤 자동 전환 대기
    dynamic_page.click_slider_dot(0)
    dynamic_page.wait_for_auto_slide_change(initial_index=0, timeout=5)

    assert dynamic_page.get_active_dot_index() == 1

