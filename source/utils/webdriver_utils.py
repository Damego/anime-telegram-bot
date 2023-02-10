from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def build_chrome_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )