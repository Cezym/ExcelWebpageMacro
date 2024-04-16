import time

from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from Interpreter import Interpreter


class WebpageMacro(Interpreter):
    __WEBDRIVER_PATH__ = 'edgedriver_win64/msedgedriver.exe'
    str_to_By = {by.lower(): by for by in dir(By) if not by.startswith("__")}
    str_to_Key: dict[str, Keys] = {key.lower(): getattr(Keys, key) for key in dir(Keys) if
                                   not key.startswith("__")}
    str_to_jsFind = {
        "css": "querySelector",
        "id": "getElementById"
    }
    str_to_get_type = {
        "text": lambda element: element.text,
        "value": lambda element: element.get_attribute("value"),
        "attribute": lambda element, value: element.get_attribute(value)
    }
    str_to_By["css"] = By.CSS_SELECTOR
    str_to_select_type = {
        "value": lambda select, option: select.select_by_value(option.get_attribute("value")),
        "text": lambda select, option: select.select_by_visible_text(option.text),
        "index": lambda select, index: select.select_by_index(index)
    }

    def __init__(self, click_exception_sleep_time_sec: int = 1, stale_exception_sleep_time_sec: int = 1):
        super().__init__()
        self.click_exception_sleep_time_sec = click_exception_sleep_time_sec
        self.stale_exception_sleep_time_sec = stale_exception_sleep_time_sec
        self.driver: webdriver.Edge = None

        self.interpretations["type"] = self.typeTo
        self.interpretations["click"] = self.click
        self.interpretations["press"] = self.press
        self.interpretations["delete"] = self.delete
        self.interpretations["get"] = self.get
        self.interpretations["int"] = lambda *x: int(self.exec_line(x))
        self.interpretations["select"] = self.select
        self.interpretations["open_url"] = self.open_url
        self.interpretations["select"] = self.select
        self.interpretations["close"] = self.close

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver.quit()
            self.driver = None

    def __del__(self):
        try:
            self.driver.close()
            self.driver.quit()
        except Exception:
            pass

    def open_url(self, url: str):
        if not self.driver:
            self.driver = webdriver.Edge()
        self.driver.get(url)

    def typeTo(self, by: str, find_by: str, value: str):
        element: WebElement = self.find_element(by, find_by)
        if Interpreter.is_num(value, float):
            while float(element.get_attribute("value").strip()) != float(value):
                element = self.find_element(by, value)
                element.send_keys(value)
        else:
            while element.get_attribute("value") != value:
                element = self.find_element(by, find_by)
                element.send_keys(value)

    def click(self, by: str, find_by: str):
        element = self.find_element(by, find_by)
        try:
            element.click()
        except selenium.common.exceptions.ElementClickInterceptedException:
            time.sleep(self.click_exception_sleep_time_sec)
            self.click(by, find_by)

    def press(self, by: str, find_by: str, key: str):
        element = self.find_element(by, find_by)
        element.send_keys(self.str_to_Key[key.lower()])

    def delete(self, by: str, find_by: str):
        js = "var aa = document." + self.str_to_jsFind[
            by.lower()] + "(\"" + find_by + "\");aa.parentNode.removeChild(aa);"
        self.driver.execute_script(js)

    def find_element(self, by, find_by):
        try:
            return self.driver.find_element(self.str_to_By[by.lower()], find_by)
        except selenium.common.exceptions.StaleElementReferenceException:
            time.sleep(self.stale_exception_sleep_time_sec)
            return self.find_element(by, find_by)
        except selenium.common.exceptions.InvalidSelectorException:
            time.sleep(self.stale_exception_sleep_time_sec)
            return self.find_element(by, find_by)


    def get(self, by, find_by, type_get):
        element = self.find_element(by, find_by)
        return self.str_to_get_type[type_get](element)

    def select(self, by, find_by, select_by: str, selection: str):
        element = self.find_element(by, find_by)
        select: Select = Select(element)
        options = select.options

        for option in options:
            if selection == option.text or selection == option.get_attribute("value"):
                while select.first_selected_option != option:
                    WebpageMacro.str_to_select_type[select_by.lower()](select, option)
                return
        for option in options:
            if selection.lower() == option.text.lower() or selection.lower() == option.get_attribute("value").lower():
                while select.first_selected_option != option:
                    WebpageMacro.str_to_select_type[select_by.lower()](select, option)
                return
        for option in options:
            if Interpreter.levenstein(selection.lower(), option.text.lower()) < 4 or \
                    Interpreter.levenstein(selection.lower(), option.get_attribute("value").lower()) < 4:
                while select.first_selected_option != option:
                    WebpageMacro.str_to_select_type[select_by.lower()](select, option)
                return

if __name__ == "__main__":
    w = WebpageMacro()
    # print(w.str_to_By)
    # print(Interpreter.try_converting("123 5", int, float))
    # w.open_url("https://pl.wikipedia.org/wiki/Fundacja_SCP")
    # time.sleep(1)
    # print(w.exec_line("get css \"span[class='mw-page-title-main']\" text"))
    # print(w.exec_line(
    #     "if get css \"span[class='mw-page-title-main']\" text = Fundacja SCP -> delete css \"img[alt='Ilustracja']\"")
    # https://demo.guru99.com/test/newtours/register.php
    inp: str = ""
    while inp != "STOP":
        try:
            inp = input()
            print(w.exec_line(inp))
        except Exception as e:
            print(e)

    #print(Interpreter.levenstein("abc", "ab"))
