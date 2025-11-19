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

# --- Helper Function: หาค่าจาก list รายละเอียด (เช่น ชั้น, พื้นที่) ---
def get_property_value(soup, keyword):
    """
    ค้นหา div ที่มี class 'detail-list-property' 
    แล้วค้นหา div ย่อย 'detail-col-property-list' ที่มี keyword อยู่ข้างใน
    """
    property_groups = soup.find_all("div", class_="detail-list-property")
    
    for group in property_groups:
        # ค้นหาเฉพาะรายการย่อยที่ระบุ: detail-col-property-list
        property_items = group.find_all("div", class_="detail-col-property-list")
        
        for item in property_items:
            # ค้นหา span ที่เป็น title ภายในรายการย่อยนั้น
            title_span = item.find("span", class_="detail-property-list-title")
            
            # ตรวจสอบว่า keyword ที่ต้องการอยู่ในชื่อข้อมูลหรือไม่
            if title_span and keyword in title_span.get_text(strip=True):
                # ดึงค่าข้อมูล (span ที่เป็น text)
                value_span = item.find("span", class_="detail-property-list-text")
                if value_span:
                    return value_span.get_text(strip=True)
                    
    return None

# --- Helper Function: แยก Latitude และ Longitude จาก Google Maps URL ---
def extract_coords_from_google_maps_url(url):
    """
    ดึงค่า Lat, Lng จาก URL ของ Google Maps โดยค้นหาหลังสัญลักษณ์ @
    รูปแบบ: /@lat,lng,zoom
    """
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        latitude = match.group(1)
        longitude = match.group(2)
        # ส่งค่ากลับในรูปแบบ 'latitude,longitude'
        return f"{latitude},{longitude}"
    return None

# --- Helper Function: Reverse Geocoding ---
def reverse_geocode_coords(coords):
    """
    แปลงพิกัด (Lat, Lng) เป็นข้อมูลที่อยู่ (แขวง, เขต, จังหวัด, รหัสไปรษณีย์) โดยใช้ Nominatim
    """
    if not coords:
        return None, None, None, None, None # แก้ไขให้ return ค่าครบตามจำนวนตัวรับ

    try:
        latitude, longitude = map(str.strip, coords.split(','))
    except ValueError:
        return None, None, None, None, None

    # ตั้งค่า Geocoder
    geolocator = Nominatim(user_agent="living_insider_scraper_v1", timeout=10)
    
    try:
        # ใช้ภาษาไทยในการค้นหา
        location = geolocator.reverse((latitude, longitude), exactly_one=True, language='th')
        
        if location and location.raw and 'address' in location.raw:
            full_address = location.address
            address_parts = location.raw['address']
            
            # การดึงข้อมูลที่ละเอียดขึ้นอยู่กับโครงสร้างที่ Nominatim คืนมา 
            sub_district = address_parts.get('quarter')
            district = address_parts.get('suburb')
            province = address_parts.get('city')
            postcode = address_parts.get('postcode')
            
            return sub_district, district, province, postcode , full_address
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"    ⚠️ Reverse Geocoding Error: {e}. Waiting 2 seconds...")
        time.sleep(2)
    except Exception as e:
        print(f"    ⚠️ Unexpected Reverse Geocoding Error: {e}")
        
    return None, None, None, None, None

def scrape_living_insider():
    # 1. ตั้งค่า Driver
    options = uc.ChromeOptions()
    # options.add_argument('--headless') 
    driver = uc.Chrome(options=options)

    # Base URL สำหรับการทำ Pagination
    base_url = "https://www.livinginsider.com/searchword/Condo/Buysell/{}/รวมประกาศ-ขาย-คอนโด.html"
    
    # 🔴 ปรับการตั้งค่าตามที่ร้องขอ 🔴
    START_PAGE = 1
    END_PAGE = 2      # <--- ดึงถึงหน้าที่ 2
    ITEMS_PER_PAGE = 3  # <--- ดึงหน้าละ 3 รายการ
    
    data_list = []

    # 2. Loop ผ่านหน้าต่างๆ (Pagination)
    for page in range(START_PAGE, END_PAGE + 1):
        main_url = base_url.format(page)
        print(f"\n=======================================================")
        print(f"🚀 กำลังเข้าสู่หน้าหลักที่: {page}/{END_PAGE} URL: {main_url}")
        print(f"=======================================================")
        
        driver.get(main_url)
        time.sleep(3) 

        # เก็บ Link ของแต่ละคอนโดในหน้านี้
        all_links = []
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item-desc"))
            )
        except Exception as e:
            print(f"Error: ไม่พบประกาศในหน้าหลักที่ {page}: {e}")
            continue

        soup_main = BeautifulSoup(driver.page_source, 'html.parser')
        
        # ดึง Link ที่ไม่ซ้ำจากหน้านี้
        items = soup_main.find_all('div', class_='item-desc')
        unique_links = set()
        for item in items:
            a_tag = item.find_parent('a') 
            if a_tag and 'href' in a_tag.attrs:
                unique_links.add(a_tag['href'])
            a_tag_inner = item.find('a')
            if a_tag_inner and 'href' in a_tag_inner.attrs:
                 unique_links.add(a_tag_inner['href'])
        
        all_links = list(unique_links)
        
        print(f"🔎 เจอประกาศทั้งหมด {len(all_links)} รายการในหน้านี้")
        
        # 3. Loop เข้าไปทีละ Link (จำกัดเพียง ITEMS_PER_PAGE รายการ)
        for i, link in enumerate(all_links[:ITEMS_PER_PAGE]): 
            full_url = link if link.startswith("http") else f"https://www.livinginsider.com{link}"
            print(f"\n--- [หน้า {page}/{END_PAGE} | รายการ {i+1}/{ITEMS_PER_PAGE}] กำลังดึงข้อมูล: {full_url} ---")
            
            # Reset ตัวแปรให้เป็น None ทุกรอบ
            coords = None
            address_map = None 
            sub_district = None
            district = None
            province = None
            postcode = None
            full_address = None
            
            try:
                driver.get(full_url)
                
                # ใช้ WebDriverWait รอให้ Title หลักแสดงผล
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "text_project_detail_green"))
                )
                
                # --- Step A: ดึง URL แผนที่จาก HREF โดยตรง และโหลดเพื่อหาพิกัดและที่อยู่ ---
                try:
                    # 1. รอให้แท็ก <a> ของแผนที่ปรากฏ
                    map_link_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "detail-view-map")) 
                    )
                    
                    # 2. ดึงค่า href โดยตรง
                    google_maps_query_url = map_link_element.get_attribute("href")
                    
                    if google_maps_query_url:
                        # 3. โหลด Query URL นี้ในหน้าต่าง Driver หลัก
                        driver.get(google_maps_query_url)
                        
                        # 4. รอให้ Google Maps โหลดและเปลี่ยน URL เป็นพิกัด
                        time.sleep(5) 
                        
                        # 5. ดึง URL สุดท้ายที่มี Lat/Lng
                        final_google_maps_url = driver.current_url
                        coords = extract_coords_from_google_maps_url(final_google_maps_url)

                        # 6. ดึง Address จากหน้า Google Maps
                        soup_map = BeautifulSoup(driver.page_source, 'html.parser')
                        address_div = soup_map.find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc")
                        if not address_div:
                            address_div = soup_map.find("div", class_="fontBodyMedium") # Fallback
                            
                        if address_div:
                            address_map = address_div.get_text(strip=True)
                        
                        print(f"   📍 Coords: {coords} | 🏠 Address (Map): {address_map}")
                        
                        # 7. Reverse Geocoding (แก้ไข: เช็คทั้ง coords และ address_map)
                        # ถ้า address_map ไม่มี (Google Maps หาไม่เจอหรือโหลดไม่ทัน) จะไม่ทำ Geocoding
                        # ทำให้ full_address เป็น None ตามที่ต้องการ
                        if coords and address_map:
                            sub_district, district, province, postcode , full_address = reverse_geocode_coords(coords)
                            print(f"   📌 Geocoded: จว.={province}, เขต={district}, รหัส={postcode}")
                        else:
                            print("   ⚠️ Address Map is empty/null. Skipping geocoding. Full address set to null.")
                        
                        # 8. สลับกลับไปหน้าประกาศเดิม (สำคัญมาก!)
                        driver.get(full_url)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "text_project_detail_green"))
                        )
                    else:
                        print("   ⚠️ ไม่พบแอตทริบิวต์ href ในปุ่มแผนที่")

                except Exception as e:
                    print(f"   ❌ Error ในการดึง Coords/Address: {e}")
                    try:
                        driver.get(full_url) # พยายามกลับหน้าหลักถ้าเกิด error
                    except:
                        pass
                    pass 

                # --- Step B: ดึงข้อมูลส่วนอื่น (ใช้ BeautifulSoup) ---
                
                # อัพเดท soup อีกครั้งหลังกลับหน้าหลัก
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 1. Title
                title_div = soup.find("span", class_="text_project_detail_green")
                title = title_div.get_text(strip=True) if title_div else None
                
                # 2. Publish Date
                date_span = soup.find("span", class_="lv-small-font grey font_10_date font_sarabun")
                publish_date = None
                if date_span:
                    date_text = date_span.get_text(strip=True)
                    publish_date = date_text.replace("สร้างเมื่อ", "").replace("ปรับปรุง", "").strip()


                # --- Step C: กดปุ่ม "ข้อมูลเพิ่มเติม..." (ถ้ามี) ---
                try:
                    more_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'font_title_more')]//span[contains(text(), 'ข้อมูลเพิ่มเติม')]"))
                    )
                    driver.execute_script("arguments[0].click();", more_btn)
                    time.sleep(1)
                    
                    # อัพเดท soup หลังจากกดปุ่ม
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                except Exception:
                    pass 

                # 3. Price
                price_div = soup.find("div", class_="box_price_mb")
                price = None
                if price_div:
                    price_b = price_div.find("span", class_="price-detail")
                    if price_b:
                        price_b_inner = price_b.find("b")
                        if price_b_inner:
                            price = price_b_inner.get_text(strip=True)

                # 4. Price per Sq.m.
                price_sqm = None
                if price_div:
                    sqm_span = price_div.find("span", class_="price_cal_area_text_modal")
                    if sqm_span:
                        price_sqm = sqm_span.get_text(strip=True)

                # 5. ใช้ Helper Function ดึงพวก list property 
                usable_area = get_property_value(soup, "พื้นที่ใช้สอย")
                floor = get_property_value(soup, "ชั้น") 
                bedroom = get_property_value(soup, "ห้องนอน")
                restroom = get_property_value(soup, "ห้องน้ำ") 
                
                # เก็บลง Dictionary
                row_data = {
                    "url": full_url,
                    "title": title,
                    "publish_date": publish_date, 
                    "price": price,
                    "price_per_sqm": price_sqm,
                    "usable_area": usable_area,
                    "floor": floor,
                    "bedroom": bedroom,
                    "restroom": restroom,
                    "coords": coords,   
                    # "address_map": address_map,
                    "address": full_address, # จะเป็น Null ถ้า address_map เป็น Null
                    "sub_district": sub_district, 
                    "district": district,    
                    "province": province,    
                    "postcode": postcode,    
                }
                
                data_list.append(row_data)
                print(f"   ✅ ได้ข้อมูล: {title[:30]}... | จว.: {province} | เขต: {district}")

            except Exception as e:
                print(f"   ❌ Error ในการดึงข้อมูล {full_url} โดยรวม: {e}")
                continue

    driver.quit()

    # 4. Save to CSV
    df = pd.DataFrame(data_list)
    df.to_csv("living_insider_data_updated.csv", index=False, encoding="utf-8-sig")
    print(f"\n🎉 เสร็จสิ้น! บันทึกไฟล์ living_insider_data_updated.csv เรียบร้อย ทั้งหมด {len(df)} รายการ จาก {END_PAGE} หน้า")

if __name__ == "__main__":
    scrape_living_insider()