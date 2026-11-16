from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text

    def is_displayed(self, locator, timeout=5):
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

