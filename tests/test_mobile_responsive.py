import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from config.config import Config

@pytest.mark.mobile_only
def test_mobile_no_horizontal_overflow_across_pages(driver):
    """로그인 및 상품 목록 화면에서 가로 스크롤이 발생하지 않는지 검증"""
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    # 로그인 화면 가로 스크롤 검증
    login_page.load()
    assert not inventory_page.has_horizontal_overflow(), (
        "모바일 로그인 화면에서 가로 스크롤(scrollWidth > clientWidth)이 발생했습니다."
    )

    # 로그인 후 상품 목록 화면 가로 스크롤 검증
    login_page.login(Config.STANDARD_USER, Config.PASSWORD)
    inventory_page.find(inventory_page.INVENTORY_ITEMS, description="상품 목록 컨테이너")

    assert not inventory_page.has_horizontal_overflow(), (
        "모바일 상품 목록(Inventory) 화면에서 가로 스크롤이 발생했습니다."
    )


@pytest.mark.mobile_only
def test_mobile_header_elements_do_not_overlap(driver):
    """좁은 모바일 헤더에서 햄버거 메뉴 버튼과 장바구니 아이콘 영역이 겹치지 않는지 검증"""
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    login_page.load()
    login_page.login(Config.STANDARD_USER, Config.PASSWORD)

    burger_rect = inventory_page.find(inventory_page.BURGER_MENU_BTN, description="햄버거 버튼").rect
    cart_rect = inventory_page.find(inventory_page.CART_LINK, description="장바구니 아이콘").rect

    # 햄버거 버튼의 우측 끝이 장바구니 아이콘의 좌측 시작점보다 왼쪽에 있어야 함
    burger_right_edge = burger_rect["x"] + burger_rect["width"]
    assert burger_right_edge < cart_rect["x"], (
        f"모바일 헤더 UI 요소 겹침 발생: 햄버거 우측 끝({burger_right_edge}px) >= 장바구니 시작점({cart_rect['x']}px)"
    )


@pytest.mark.mobile_only
def test_mobile_hamburger_menu_open_close_and_logout(driver):
    """햄버거 사이드바 메뉴 열기/닫기 애니메이션 및 로그아웃 기능 정상 동작 검증"""
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)

    login_page.load()
    login_page.login(Config.STANDARD_USER, Config.PASSWORD)

    # 사이드바 열기 검증
    assert inventory_page.open_sidebar_menu(), "모바일 햄버거 메뉴 클릭 후 사이드바가 열리지 않았습니다."

    # 사이드바 닫기(X) 검증
    assert inventory_page.close_sidebar_menu(), "모바일 사이드바 닫기 버튼 클릭 후 메뉴가 닫히지 않았습니다."

    # 다시 열어 로그아웃 실행 후 로그인 페이지 복귀 확인
    inventory_page.logout_via_sidebar()
    assert "saucedemo.com" in driver.current_url
    assert login_page.find(login_page.LOGIN_BUTTON, description="로그인 버튼").is_displayed()

    