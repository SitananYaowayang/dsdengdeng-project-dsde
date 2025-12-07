import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random
from urllib.parse import unquote
import os

BANGKOK_DISTRICTS = [
    "พระนคร", "ดุสิต", "หนองจอก", "บางรัก", "บางเขน", "บางกะปิ", "ปทุมวัน", "ป้อมปราบศัตรูพ่าย", 
    "พระโขนง", "มีนบุรี", "ลาดกระบัง", "ยานนาวา", "สัมพันธวงศ์", "พญาไท", "ธนบุรี", "บางกอกใหญ่", 
    "ห้วยขวาง", "คลองสาน", "ตลิ่งชัน", "บางกอกน้อย", "บางขุนเทียน", "ภาษีเจริญ", "หนองแขม", "ราษฎร์บูรณะ", 
    "บางพลัด", "ดินแดง", "บึงกุ่ม", "สาทร", "บางซื่อ", "จตุจักร", "บางคอแหลม", "ประเวศ", "คลองเตย", 
    "สวนหลวง", "จอมทอง", "ดอนเมือง", "ราชเทวี", "ลาดพร้าว", "วัฒนา", "บางแค", "หลักสี่", "สายไหม", 
    "คันนายาว", "สะพานสูง", "วังทองหลาง", "คลองสามวา", "บางนา", "ทวีวัฒนา", "ทุ่งครุ", "บางบอน"
]

if __name__ == '__main__':

    options = uc.ChromeOptions()
    
    print("กำลังเปิด Browser...")
    driver = uc.Chrome(options=options)
    
    output_filename = 'ddproperty_bangkok_all_districts.csv'
    
    visited_urls = set()

    try:
        for i, district in enumerate(BANGKOK_DISTRICTS, start=1):
            
            district_code = f"TH{1000 + i}"
            
            print(f"\n{'='*50}")
            print(f"กำลังประมวลผลเขตลำดับที่ {i}: {district} (Code: {district_code})")
            print(f"{'='*50}")
            
            district_data = []

            for page_num in range(1, 11):
                print(f"\n--- เขต {district} ({district_code}) | หน้าที่ {page_num} ---")
                
                target_url = f"https://www.ddproperty.com/รวมประกาศขาย?listingType=sale&districtCode={district_code}&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&_freetextDisplay={district}&page={page_num}"
                
                print(f"URL: {target_url}")
                driver.get(target_url)
                
                time.sleep(8)
                
                current_url = unquote(driver.current_url)
                if page_num > 1 and "page=1" in current_url and f"page={page_num}" not in current_url:
                     print(f"!!! ถูก Redirect กลับหน้า 1 (คาดว่าหมดหน้าข้อมูล) -> ข้ามไปเขตถัดไป")
                     break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                listings = soup.find_all('a', attrs={'class': 'card-footer'}) 

                if len(listings) == 0:
                    print(f"ไม่พบประกาศขายในหน้านี้ -> จบเขต {district}")
                    break

                new_item_count = 0
                page_items = [] 

                for item in listings:
                    row = {}
                    
                    url_raw = item.get('href')
                    if url_raw and not url_raw.startswith('http'):
                         url_raw = "https://www.ddproperty.com" + url_raw
                    
                    row['url'] = url_raw

                    if row['url'] not in visited_urls:
                        new_item_count += 1
                        visited_urls.add(row['url'])
                        
                        def get_text_by_da_id(da_id):
                            el = item.find(attrs={'da-id': da_id}) 
                            return el.get_text(strip=True) if el else "N/A"

                        title_el = item.find(class_='title-badge-wrapper')
                        row['title'] = title_el.get_text(strip=True) if title_el else "N/A"
                        row['publish_date'] = get_text_by_da_id('listing-card-v2-recency')
                        row['price'] = get_text_by_da_id('listing-card-v2-price')
                        row['price_per_sqm'] = get_text_by_da_id('listing-card-v2-psf')
                        row['usable_area'] = get_text_by_da_id('listing-card-v2-area')
                        row['floor'] = "-"
                        row['bedroom'] = get_text_by_da_id('listing-card-v2-bedrooms')
                        row['restroom'] = get_text_by_da_id('listing-card-v2-bathrooms')
                        address_el = item.find(class_='listing-address')
                        row['full_address'] = address_el.get_text(strip=True) if address_el else "N/A"
                        row['coords'] = "-"
                        row['district_search_term'] = district
                        row['district_code'] = district_code 

                        page_items.append(row)

                print(f"เจอทั้งหมด {len(listings)} | ใหม่ {new_item_count}")
                
                if new_item_count == 0:
                    print("!!! ข้อมูลซ้ำทั้งหน้า (Duplicate Page) -> จบเขตนี้")
                    break
                
                district_data.extend(page_items)
                
                sleep_time = random.uniform(3, 5)
                time.sleep(sleep_time)
            
            if district_data:
                df = pd.DataFrame(district_data)
                cols = ['district_code', 'district_search_term', 'url', 'title', 'publish_date', 'price', 
                        'price_per_sqm', 'usable_area', 'floor', 'bedroom', 'restroom', 'coords', 'full_address']
                
                existing_cols = [c for c in cols if c in df.columns]
                df = df[existing_cols]

                use_header = not os.path.exists(output_filename)
                df.to_csv(output_filename, mode='a', index=False, encoding='utf-8-sig', header=use_header)
                print(f"--> บันทึกข้อมูลเขต {district} เรียบร้อย ({len(df)} รายการ)")
            else:
                print(f"--> เขต {district} ไม่มีข้อมูลใหม่")
            
            print(f"พัก 5 วินาทีก่อนเริ่มเขตต่อไป...")
            time.sleep(5)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดร้ายแรง: {e}")

    finally:
        print("ปิด Browser...")
        driver.quit()
        print(f"เสร็จสิ้น! ข้อมูลทั้งหมดถูกบันทึกที่: {output_filename}")