import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# os.environ["PATH"] += r""
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# driver.get("https://google.com")
# driver.get("https://tuoitre.vn")
driver.get("https://tuoitre.vn/thoi-su.htm")

categories = driver.find_elements(By.CLASS_NAME, "nav-link")
# print(categories)
for category in categories:
    category_name = category.text
    category_link = category.get_attribute("href")
    print(f"Category: {category_name} - Link: {category_link}")

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CLASS_NAME, "box-category-item"))
)

elements = driver.find_elements(By.CLASS_NAME, "box-category-item")
print(elements)

time.sleep(5)

driver.quit()
