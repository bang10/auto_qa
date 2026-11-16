from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CheckoutStepTwoPage(BasePage):
    PAGE_TITLE = (By.CLASS_NAME, "title")
    ITEM_TOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")


    def get_title(self):
        return self.get_text(self.PAGE_TITLE)

    def get_item_total(self):
        """숫자만 float로 변환 / $29.99" -> 29.99"""
        text = self.get_text(self.ITEM_TOTAL_LABEL)
        return float(text.split("$")[1])

    def get_tax(self):
        text = self.get_text(self.TAX_LABEL)
        return float(text.split("$")[1])

    def get_total(self):
        text = self.get_text(self.TOTAL_LABEL)
        return float(text.split("$")[1])

    def click_finish(self):
        self.click(self.FINISH_BUTTON)

    def click_product_by_name(self, product_name):
        locator = (By.XPATH, f"//div[@class='inventory_item_name' and normalize-space()='{product_name}']")
        self.click(locator)

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    
