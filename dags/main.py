import time
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re 
from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import traceback # เอาไว้ดู Error ละเอียด

# --- Helper 1: ดึง Property ---
def get_property_value(soup, keyword):
    property_groups = soup.find_all("div", class_="detail-list-property")
    for group in property_groups:
        property_items = group.find_all("div", class_="detail-col-property-list")
        for item in property_items:
            title_span = item.find("span", class_="detail-property-list-title")
            if title_span and keyword in title_span.get_text(strip=True):
                value_span = item.find("span", class_="detail-property-list-text")
                if value_span:
                    return value_span.get_text(strip=True)
    return None

# --- Helper 2: ดึงพิกัดจาก URL ---
def extract_coords_from_google_maps_url(url):
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        return f"{match.group(1)},{match.group(2)}"
    return None

# --- Helper 3: Reverse Geocoding ---
def reverse_geocode_coords(coords):
    if not coords:
        return None, None, None, None, None

    try:
        latitude, longitude = map(str.strip, coords.split(','))
    except ValueError:
        return None, None, None, None, None

    geolocator = Nominatim(user_agent="living_insider_scraper_team_a", timeout=10)
    
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True, language='th')
        if location and location.raw and 'address' in location.raw:
            full_address = location.address
            address_parts = location.raw['address']
            
            sub_district = address_parts.get('quarter')
            district = address_parts.get('suburb')
            province = address_parts.get('city')
            postcode = address_parts.get('postcode')
            
            return sub_district, district, province, postcode , full_address
            
    except (GeocoderTimedOut, GeocoderServiceError):
        time.sleep(2)
    except Exception:
        pass
        
    return None, None, None, None, None

# --- ฟังก์ชันสร้าง Driver ใหม่ (เอาไว้เรียกตอน Chrome ตาย) ---
def init_driver():
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new')  # ปิดบรรทัดนี้ถ้าอยากดูหน้าจอ (แนะนำให้เปิดจอแบบ Normal)
    options.add_argument('--window-size=1280,960')
    options.add_argument('--disable-popup-blocking')
    
    # เพิ่ม flag เพื่อความเสถียร
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options)
    return driver

# --- MAIN SCRAPER ---
def scrape_living_insider():
    # เริ่มต้น Driver ครั้งแรก
    driver = init_driver()

    base_url = "https://www.livinginsider.com/searchword/Condo/Buysell/{}/รวมประกาศ-ขาย-คอนโด.html"
    
    # 🔴 กำหนดจำนวนหน้าที่จะดึงตรงนี้ 🔴
    START_PAGE = 31
    END_PAGE = 60       
    
    # ตัวแปรเก็บข้อมูลทั้งหมด
    all_data_list = []

    print(f"🚀 เริ่มต้น Scraper (ระบบ Auto-Restart) (เป้าหมาย: หน้า {START_PAGE} ถึง {END_PAGE})")
    print(f"💾 ข้อมูลจะถูกบันทึกลงไฟล์ 'living_insider_full_data.csv' ตลอดเวลา...")

    # 2. Loop Pagination
    for page in range(START_PAGE, END_PAGE + 1):
        
        # --- 🛡️ Zone ตรวจชีพจร Driver ---
        try:
            # ลองเช็คว่า Driver ยังอยู่ไหมด้วยการเรียก current_url
            _ = driver.current_url
        except Exception:
            print("🚨 Driver ตาย! (Invalid Session) กำลังชุบชีวิตใหม่...")
            try: driver.quit()
            except: pass
            driver = init_driver() # สร้างใหม่
            print("✅ ชุบชีวิตสำเร็จ! ลุยต่อ...")
        # ------------------------------

        main_url = base_url.format(page)
        print(f"\n════════════════════════════════════════════════════════")
        print(f"📄 กำลังประมวลผล: หน้าที่ {page}/{END_PAGE}")
        print(f"════════════════════════════════════════════════════════")
        
        try:
            driver.get(main_url)
            time.sleep(1)

            # เช็คว่ามีรายการไหม
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "item-desc")))
            except:
                print(f"⚠️ ไม่พบข้อมูลในหน้าที่ {page} (อาจจะหมดแล้ว หรือเน็ตหลุด)")
                # ถ้าไม่เจอ ลอง Refresh 1 ที เผื่อเน็ตหลุด
                driver.refresh()
                time.sleep(2)
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "item-desc")))
                except:
                    print(f"❌ ยังไม่พบข้อมูล ข้ามหน้านี้")
                    continue

            soup_main = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup_main.find_all('div', class_='item-desc')
            
            # หา Link (ตัดตัวซ้ำ)
            unique_links = set()
            for item in items:
                a_tag = item.find_parent('a') 
                if a_tag and 'href' in a_tag.attrs: unique_links.add(a_tag['href'])
                a_tag_inner = item.find('a')
                if a_tag_inner and 'href' in a_tag_inner.attrs: unique_links.add(a_tag_inner['href'])
            
            all_links = list(unique_links)
            print(f"   🔎 เจอ {len(all_links)} รายการในหน้านี้")

            # 3. Loop รายการย่อย
            for i, link in enumerate(all_links): 
                full_url = link if link.startswith("http") else f"https://www.livinginsider.com{link}"
                print(f"   [{i+1}/{len(all_links)}] Scraping... ", end="")
                
                # Reset Vars
                coords = None; sub_district = None; district = None; province = None; postcode = None; full_address = None
                
                try:
                    driver.get(full_url)
                    # รอ Title
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "text_project_detail_green")))
                    
                    # --- MAP SECTION ---
                    try:
                        map_link = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "detail-view-map")))
                        google_maps_query_url = map_link.get_attribute("href")
                        
                        if google_maps_query_url:
                            driver.get(google_maps_query_url)
                            time.sleep(4) # รอ Maps โหลด
                            
                            # ดึงพิกัด
                            coords = extract_coords_from_google_maps_url(driver.current_url)
                            
                            # ดึง Address จากหน้า Map
                            soup_map = BeautifulSoup(driver.page_source, 'html.parser')
                            address_div = soup_map.find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc") or soup_map.find("div", class_="fontBodyMedium")
                            address_map = address_div.get_text(strip=True) if address_div else None

                            # Reverse Geocode
                            if coords and address_map:
                                sub_district, district, province, postcode , full_address = reverse_geocode_coords(coords)
                            
                            # กลับหน้าเดิม
                            driver.get(full_url)
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "text_project_detail_green")))
                    except:
                        # ถ้า Map Error ให้พยายามกลับหน้าหลักก่อน
                        try: driver.get(full_url)
                        except: pass
                        pass

                    # --- CONTENT SECTION ---
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    title_div = soup.find("span", class_="text_project_detail_green")
                    title = title_div.get_text(strip=True) if title_div else None
                    
                    date_span = soup.find("span", class_="lv-small-font grey font_10_date font_sarabun")
                    publish_date = date_span.get_text(strip=True).replace("สร้างเมื่อ", "").replace("ปรับปรุง", "").strip() if date_span else None

                    # กดปุ่มเพิ่มเติม
                    try:
                        more_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'font_title_more')]//span[contains(text(), 'ข้อมูลเพิ่มเติม')]")))
                        driver.execute_script("arguments[0].click();", more_btn)
                        time.sleep(0.5)
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                    except: pass 

                    price = None; price_sqm = None
                    price_div = soup.find("div", class_="box_price_mb")
                    if price_div:
                        if price_div.find("span", class_="price-detail"): price = price_div.find("span", class_="price-detail").get_text(strip=True)
                        if price_div.find("span", class_="price_cal_area_text_modal"): price_sqm = price_div.find("span", class_="price_cal_area_text_modal").get_text(strip=True)

                    row_data = {
                        "url": full_url,
                        "title": title,
                        "publish_date": publish_date, 
                        "price": price,
                        "price_per_sqm": price_sqm,
                        "usable_area": get_property_value(soup, "พื้นที่ใช้สอย"),
                        "floor": get_property_value(soup, "ชั้น"),
                        "bedroom": get_property_value(soup, "ห้องนอน"),
                        "restroom": get_property_value(soup, "ห้องน้ำ"),
                        "coords": coords,   
                        "full_address": full_address,
                        "sub_district": sub_district, 
                        "district": district,    
                        "province": province,    
                        "postcode": postcode,    
                    }
                    
                    all_data_list.append(row_data)
                    print("✅ Done")

                except Exception as e:
                    # ตรวจจับ Error ว่า Driver ตายไหม
                    if "invalid session" in str(e) or "no such execution context" in str(e):
                        print("❌ CRITICAL ERROR: Driver ตายกลางทาง!")
                        raise e # โยน Error ออกไปให้ Loop ใหญ่จัดการ (เพื่อ Restart)
                    else:
                        print("❌ Skip (Item Error)")
                        continue
        
        except Exception as e:
            print(f"⚠️ Error Page {page}: {e}")
            # ถ้า Error เป็นเพราะ Driver ตาย ให้ Loop รอบถัดไป (ซึ่งจะไปเข้าเงื่อนไข if driver ตายข้างบนสุด)
            # แต่ถ้า Driver ยังรอด ก็แค่ข้ามหน้านี้ไป
            if "invalid session" in str(e) or "no such window" in str(e):
                 # ปิดให้แน่ใจ
                 try: driver.quit()
                 except: pass
            continue
        
        # --- 🔥 SAVE UPDATE (ทับไฟล์เดิมทุกครั้งที่จบหน้า) ---
        if len(all_data_list) > 0:
            df = pd.DataFrame(all_data_list)
            df.to_csv("living_insider_full_data_p3.csv", index=False, encoding="utf-8-sig")
            print(f"💾 Updated CSV -> Total: {len(df)} records")

    driver.quit()
    print(f"\n🎉 เสร็จสิ้นภารกิจ! ได้ข้อมูลทั้งหมด {len(all_data_list)} รายการ")

if __name__ == "__main__":
    scrape_living_insider()