from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.config import Config

class BasePage:
    # 사이드 바 영역
    SIDEBAR_WRAP = (By.CLASS_NAME, "bm-menu-wrap")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    CLOSE_MENU_BUTTON = (By.ID, "react-burger-cross-btn")
    ALL_ITEMS_LINK = (By.ID, "inventory_sidebar_link")
    LAZY_BUTTON = (By.ID, "dynamic_catalog_lazy_load_link")
    SPINNER_BUTTON = (By.ID, "dynamic_catalog_spinner_link")
    SLIDE_BUTTON = (By.ID, "dynamic_catalog_slider_link")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    DYNAMIC_CATALOG_LINK = (By.XPATH, "//nav[@class='bm-item-list']//a[contains(text(), 'Dynamic Catalog')]")

    def __init__(self, driver, timeout=Config.DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)

    def find(self, locator, description=None):
        """요소가 화면에 나타날 때까지 대기 및 Timeout 예외 처리 """
        target = description if description else f"{locator[0]}='{locator[1]}'"
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            current_url = self.driver.current_url
            raise TimeoutException(
                f"[요청 시간 초과 ({self.timeout}초)] 화면에서 요소를 찾지 못했습니다.\n"
                f"대상 요소: {target}\n"
                f"현재 페이지 URL: {current_url}"
            ) from None
        except NoSuchElementException:
            raise NoSuchElementException(
                f"[요소 미발견] DOM에서 대상 요소를 찾을 수 없습니다.\n"
                f"• 대상 요소: {target}\n"
                f"• 현재 페이지 URL: {self.driver.current_url}"
            ) from None

    def click(self, locator, description=None):
        """요소가 클릭 가능할 때까지 대기 후 클릭하며, Timeout 발생 시 안내 출력"""
        target = description if description else f"{locator[0]}='{locator[1]}'"
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except TimeoutException:
            current_url = self.driver.current_url
            raise TimeoutException(
                f"[요청 시간 초과 ({self.timeout}초)] 요소를 클릭할 수 있는 상태가 되지 않았습니다.\n"
                f"• 대상 요소: {target}\n"
                f"• 현재 페이지 URL: {current_url}"
            ) from None
        except NoSuchElementException:
            raise NoSuchElementException(
                f"[요소 미발견] 클릭할 대상 요소를 DOM에서 찾을 수 없습니다.\n"
                f"• 대상 요소: {target}\n"
                f"• 현재 페이지 URL: {self.driver.current_url}"
            ) from None

    def type_text(self, locator, text, description=None):
        element = self.find(locator, description=description)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator, description=None):
        return self.find(locator, description=description).text

    def is_displayed(self, locator, timeout=Config.DEFAULT_TIMEOUT):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def open_sidebar(self):
        self.click(self.MENU_BUTTON)
        self.wait.until(
            lambda d: d.find_element(*self.SIDEBAR_WRAP).get_attribute("aria-hidden") == "false"
        )

    def close_sidebar(self):
        self.click(self.CLOSE_MENU_BUTTON)
        self.wait.until(
            lambda d: d.find_element(*self.SIDEBAR_WRAP).get_attribute("aria-hidden") == "true"
        )

    def is_sidebar_open(self):
        wrap = self.driver.find_element(*self.SIDEBAR_WRAP)
        return wrap.get_attribute("aria-hidden") == "false"

    def open_dynamic_catalog(self): 
        self.click(self.DYNAMIC_CATALOG_LINK)

    def click_all_items(self):
        self.open_sidebar()
        self.click(self.ALL_ITEMS_LINK)

    def click_lazy (self):
        self.open_sidebar()
        self.open_dynamic_catalog()
        self.click(self.LAZY_BUTTON)
    
    def click_spinner (self):
        self.open_sidebar()
        self.open_dynamic_catalog()
        self.click(self.SPINNER_BUTTON)

    def click_slide (self):
        self.open_sidebar()
        self.open_dynamic_catalog()
        self.click(self.SLIDE_BUTTON)

    def click_logout(self):
        self.open_sidebar()
        self.click(self.LOGOUT_LINK)

