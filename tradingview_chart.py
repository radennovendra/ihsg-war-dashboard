from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

os.makedirs("charts", exist_ok=True)

def generate_chart(symbol):

    ticker = symbol.replace(".JK","")

    url = f"https://www.tradingview.com/chart/?symbol=IDX:{ticker}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,720")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(url)

    time.sleep(5)

    path = f"charts/{symbol}.png"

    driver.save_screenshot(path)

    driver.quit()

    return path