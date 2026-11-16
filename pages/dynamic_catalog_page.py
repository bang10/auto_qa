from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

class DynamicCatalogPage(BasePage):
    LAZY_TITLE = (By.CLASS_NAME, "Dynamic Catalog - Lazy Load")
    SPINNER_TITLE = (By.CLASS_NAME, "Dynamic Catalog - Spinner")
    SLIDER_TITLE = (By.CLASS_NAME, "Dynamic Catalog - Slider")

    # Lazy Load 관련 Locators
    LAZY_ITEMS = (By.CSS_SELECTOR, ".dynamic_catalog_card")

    # Spinner 관련 Locators
    SPINNER_ICON = (By.CSS_SELECTOR, ".dynamic_catalog_spinner")
    SPINNER_RESULT_ICON = (By.CSS_SELECTOR, ".dynamic_catalog_spinner_grid")

    # Slider 관련 Locators
    SLIDER_DOTS = (By.CLASS_NAME, "dynamic_catalog_slider_dot")

    def get_lazy_title(self):
        return self.get_text(self.LAZY_TITLE)

    def get_spinner_title(self):
        return self.get_text(self.SPINNER_TITLE)

    def get_silder_title(self):
        return self.get_text(self.SLIDER_TITLE)

    # Lazy Load 제어
    def get_loaded_item_count(self):
        return len(self.driver.find_elements(*self.LAZY_ITEMS))

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def wait_for_more_items(self, initial_count):
        # 스크롤 후 기존 개수보다 상품 카드 개수가 늘어날 때까지 대기
        self.wait.until(lambda d: len(d.find_elements(*self.LAZY_ITEMS)) > initial_count)

    # Spinner 제어
    def trigger_and_wait_spinner(self):
        # 스피너가 화면에 나타나는지 확인
        self.wait.until(EC.visibility_of_element_located(self.SPINNER_ICON))
        # 스피너가 완전히 사라질 때까지 대기 (핵심 검증 포인트)
        self.wait.until(EC.invisibility_of_element_located(self.SPINNER_RESULT_ICON))

    def is_spinner_content_displayed(self):
        return self.is_displayed(self.SPINNER_RESULT_ICON)

    # FIXME Slider 제어
    def get_slider_dots(self):
        # 닷 요소들이 화면에 렌더링될 때까지 대기 후 전체 리스트 반환
        self.find(self.SLIDER_DOTS)
        return self.driver.find_elements(*self.SLIDER_DOTS)

    def get_active_dot_index(self):
        # aria-current가 "true"인 닷의 index 반환
        dots = self.get_slider_dots()
        for idx, dot in enumerate(dots):
            if dot.get_attribute("aria-current") == "true":
                return idx
        return -1

    def click_slider_dot(self, index):
        # index 동그란 닷 버튼을 클릭하고 해당 닷이 활성화될 때까지 대기
        dots = self.get_slider_dots()
        dots[index].click()
        return self.wait.until(
            lambda d: d.find_elements(*self.SLIDER_DOTS)[index].get_attribute("aria-current") == "true"
        )

    def wait_for_auto_slide_change(self, initial_index, timeout=5):
        # 약 2초 간격 자동 슬라이드로 인해 활성 닷 인덱스가 바뀔 때까지 대기
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.get_active_dot_index() != initial_index
        )

