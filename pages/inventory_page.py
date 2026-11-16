from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage

class InventoryPage(BasePage):
    PAGE_TITLE = (By.CLASS_NAME, "title")
    CART_ICON = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICES = (By.CLASS_NAME, "inventory_item_price")

    def get_title(self):
        return self.get_text(self.PAGE_TITLE)

    def click_product_by_name(self, product_name):
        """상품 상세 페이지로 이동"""
        locator = (By.XPATH, f"//div[@class='inventory_item_name ' and normalize-space()='{product_name}']")
        self.click(locator)

    def add_to_cart_by_name(self, product_name):
        """메인 화면에서 장바구니 담기"""
        """소문자에 "-"를 붙혀서 id를 만들고 있음"""
        formatted_name = product_name.lower().replace(" ", "-")
        locator = (By.ID, f"add-to-cart-{formatted_name}")
        self.click(locator)

    def remove_to_cart_by_name(self, product_name):
        """메인화면에서 장바구니 삭제"""
        """소문자에 "-"를 붙혀서 id를 만들고 있음"""
        formatted_name = product_name.lower().replace(" ", "-")
        locator = (By.ID, f"remove-{formatted_name}")
        self.click(locator)

    def is_remove_button_displayed(self, product_name):
        """장바구니 아이콘에 숫자 아이콘 사라진 것 확인"""
        remove_button = product_name.lower().replace(" ", "-")
        locator = (By.ID, f"remove-{remove_button}")
        return self.is_displayed(locator)

    def get_cart_badge_count(self):
        """우측 상단 장바구니 뱃지 수량"""
        if self.is_displayed(self.CART_BADGE):
            return int(self.get_text(self.CART_BADGE))
        return 0

    def go_to_cart(self):
        """장바구니 페이지로 이동"""
        self.click(self.CART_ICON)

    def select_sort_option(self, option_value):
        """정렬 옵션 (az, za, lohi, hilo)"""
        dropdown_element = self.find(self.SORT_DROPDOWN)
        select = Select(dropdown_element)
        select.select_by_value(option_value)

    def get_all_product_names(self):
        """현재 화면에 노출된 상품명 리스트 반환"""
        elements = self.driver.find_elements(*self.ITEM_NAMES)
        return [el.text for el in elements]

    def get_all_product_prices(self):
        """현재 화면에 노출된 상품 가격(float) 리스트 반환"""
        elements = self.driver.find_elements(*self.ITEM_PRICES)
        return [float(el.text.replace("$", "")) for el in elements]


    