from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class InventoryDetailPage(BasePage):
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_details_name")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_details_price")
    ADD_TO_CART_BUTTON = (By.ID, "add-to-cart")
    REMOVE_BUTTON = (By.ID, "remove")
    BACK_TO_PRODUCTS_BUTTON = (By.ID, "back-to-products")
    CART_ICON = (By.CLASS_NAME, "shopping_cart_link")

    def get_product_name(self):
        """return 상품명"""
        return self.get_text(self.PRODUCT_NAME)

    def get_product_price(self):
        """return 상품 가격"""
        return self.get_text(self.PRODUCT_PRICE)

    def add_to_cart(self):
        """장바구니 추가 선택"""
        self.click(self.ADD_TO_CART_BUTTON)

    def is_remove_button_displayed(self):
        """장바구니 담기가 remove로 변경되었는지 확인"""
        return self.is_displayed(self.REMOVE_BUTTON)

    def go_to_cart(self):
        """장바구니 아이콘에 숫자 아이콘 추가(수정)된 것 확인"""
        self.click(self.CART_ICON)

    def back_to_products(self):
        "상세화면에서 뒤로가기"
        self.click(self.BACK_TO_PRODUCTS_BUTTON)
    