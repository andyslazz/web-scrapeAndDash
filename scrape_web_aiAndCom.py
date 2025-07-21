from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd

# คำค้นหาที่ต้องการดึงข้อมูล
search_keywords = ["วิศวกรรมปัญญาประดิษฐ์", "วิศวกรรมคอมพิวเตอร์"]

# เริ่ม WebDriver
driver = webdriver.Safari()
driver.get("https://course.mytcas.com")
time.sleep(3)

all_data = []

for keyword in search_keywords:
    # กลับหน้าแรกก่อนค้นหาใหม่
    driver.get("https://course.mytcas.com")
    time.sleep(3)

    # พิมพ์คำค้นหา
    search_box = driver.find_element(By.ID, "search")
    search_box.clear()
    search_box.send_keys(keyword)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(4)

    # ดึงลิงก์ของโปรแกรมทั้งหมด
    program_links = []
    program_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/programs/']")
    for elem in program_elements:
        href = elem.get_attribute("href")
        if href not in program_links:
            program_links.append(href)

    print(f"'{keyword}' พบโปรแกรมทั้งหมด: {len(program_links)} รายการ")

    # วนลูปเก็บข้อมูลจากแต่ละลิงก์
    for link in program_links:
        driver.get(link)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ดึงชื่อมหาวิทยาลัย
        university_tag = soup.find("a", href=lambda x: x and x.startswith("/universities/"))
        university_name = university_tag.get_text(strip=True) if university_tag else "ไม่พบชื่อมหาวิทยาลัย"

        # ดึงข้อมูลจาก <dl>
        dl_block = soup.find("dl")
        program_data = {
            "คำค้นหา": keyword,
            "มหาวิทยาลัย": university_name,
            "ลิงก์": link
        }

        if dl_block:
            for dt, dd in zip(dl_block.find_all("dt"), dl_block.find_all("dd")):
                label = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                program_data[label] = value

        all_data.append(program_data)

driver.quit()

# แปลงข้อมูลเป็น Excel
df = pd.DataFrame(all_data)
df.to_excel("programs_ai_computer.xlsx", index=False)

print("บันทึกข้อมูลทั้ง 'วิศวกรรมปัญญาประดิษฐ์' และ 'วิศวกรรมคอมพิวเตอร์' (programs_ai_computer.xlsx)")
