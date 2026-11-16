from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CartPage(BasePage):
    PAGE_TITLE = (By.CLASS_NAME, "title")
    CART_ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    GO_INVENTORY_BUTTON = (By.ID, "continue-shopping")

    def get_title(self):
        return self.get_text(self.PAGE_TITLE)

    def get_cart_item_names(self):
        """return 장바구니에 담긴 상품명 리스트"""
        elements = self.driver.find_elements(*self.CART_ITEM_NAMES)
        return [el.text for el in elements]

    def remove_item_by_name(self, product_name):
        """장바구니 목록에서 제거"""
        formatted_name = product_name.lower().replace(" ", "-")
        locator = (By.ID, f"remove-{formatted_name}")
        self.click(locator)

    def go_to_inventory(self):
        """장바구니에서 쇼핑계속하기 버튼 선택"""
        self.click(self.GO_INVENTORY_BUTTON)

    def proceed_to_checkout(self):
        """결제 단계로 넘어가는 버튼"""
        self.click(self.CHECKOUT_BUTTON)

    def click_product_by_name(self, product_name):
        """상품명을 클릭하면 상세로 이동"""
        locator = (By.XPATH, f"//div[@class='inventory_item_name' and normalize-space()='{product_name}']")
        self.click(locator)

    
