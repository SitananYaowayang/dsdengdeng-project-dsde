import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random
from urllib.parse import unquote
import os
import sys
from datetime import datetime

# --- CONFIGURATION ---
TRIGGER_FILE = "trigger_ddproperty.txt"  # ชื่อไฟล์ Trigger ต้องตรงกับใน Airflow DAG
OUTPUT_FILE = "ddproperty_condo_nofloor_triggered.csv"

CONFIG = {
    'chrome_version': 142,       # [สำคัญ] เปลี่ยนให้ตรงกับ Chrome ในเครื่อง Windows ของคุณ
    'max_pages': 100,
    'sleep_range': (6, 9),
    'base_url': "https://www.ddproperty.com/รวมประกาศขาย?listingType=sale&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&lastPosted=7"
}

class DDPropertyLocalPipeline:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.visited_urls = set()
        
    def _init_driver(self):
        """เริ่ม Browser แบบเห็นหน้าจอ (Visible) เพื่อให้แก้ Cloudflare ได้"""
        print("[Pipeline] กำลังเปิด Chrome Browser...")
        options = uc.ChromeOptions()
        
        # ไม่ใช้ Headless เพื่อให้เราเห็นหน้าจอ
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = uc.Chrome(
                options=options, 
                version_main=self.config['chrome_version'],
                use_subprocess=True
            )
        except Exception as e:
            print(f"[Error] เปิด Chrome ไม่สำเร็จ: {e}")
            print("คำแนะนำ: ตรวจสอบ 'chrome_version' ใน CONFIG ว่าตรงกับในเครื่องหรือไม่")
            return False
        return True

    def _scroll_page(self):
        """เลื่อนหน้าจอเพื่อให้ข้อมูลโหลด"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
        time.sleep(2)

    def _extract_data_from_html(self, soup):
        """แปลง HTML เป็น Data (ตัด Floor ออกแล้ว)"""
        listings = soup.find_all('a', attrs={'class': 'card-footer'})
        extracted_rows = []
        new_count = 0

        for item in listings:
            row = {}
            
            # URL
            url_raw = item.get('href')
            if url_raw and not url_raw.startswith('http'):
                url_raw = "https://www.ddproperty.com" + url_raw
            row['url'] = url_raw

            # Check Duplicates
            if row['url'] in self.visited_urls:
                continue

            self.visited_urls.add(row['url'])
            new_count += 1

            # Helper function
            def get_text(da_id):
                el = item.find(attrs={'da-id': da_id})
                return el.get_text(strip=True) if el else "N/A"

            # Parse Fields
            title_el = item.find(class_='title-badge-wrapper')
            row['title'] = title_el.get_text(strip=True) if title_el else "N/A"
            row['publish_date'] = get_text('listing-card-v2-recency')
            row['price'] = get_text('listing-card-v2-price')
            row['price_per_sqm'] = get_text('listing-card-v2-psf')
            row['usable_area'] = get_text('listing-card-v2-area')
            row['bedroom'] = get_text('listing-card-v2-bedrooms')
            row['restroom'] = get_text('listing-card-v2-bathrooms')
            
            address_el = item.find(class_='listing-address')
            row['full_address'] = address_el.get_text(strip=True) if address_el else "N/A"
            
            # --- ส่วนที่เอา Floor ออกแล้ว ---
            row['coords'] = "-"

            extracted_rows.append(row)
        
        return extracted_rows, len(listings), new_count

    def _save_batch(self, data):
        """บันทึกข้อมูลลง CSV (ไม่มีคอลัมน์ Floor)"""
        if not data: return

        df = pd.DataFrame(data)
        
        # กำหนด Column ที่ต้องการ (เอา floor ออก)
        cols = ['url', 'title', 'publish_date', 'price', 'price_per_sqm', 
                'usable_area', 'bedroom', 'restroom', 'coords', 'full_address']
        
        # Filter existing columns
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]

        use_header = not os.path.exists(OUTPUT_FILE)
        
        try:
            df.to_csv(OUTPUT_FILE, mode='a', index=False, encoding='utf-8-sig', header=use_header)
            print(f"   [Save] Saved {len(df)} new records.")
        except Exception as e:
            print(f"   [Error] Save failed: {e}")

    def run_scrape(self):
        """เริ่มทำงาน Scrape (หลังจากถูก Trigger)"""
        if not self._init_driver(): return
        
        try:
            print(f"\n--- เริ่มต้นดึงข้อมูล (Max Pages: {self.config['max_pages']}) ---")
            print("!!! ถ้าติดหน้า Cloudflare ให้รีบกดแก้ด้วยมือได้เลย !!!")

            for page in range(1, self.config['max_pages'] + 1):
                print(f"\nProcessing Page {page} / {self.config['max_pages']}...")
                
                target_url = f"{self.config['base_url']}&page={page}"
                self.driver.get(target_url)
                
                # Check Cloudflare Checkpoint
                if "just a moment" in self.driver.title.lower():
                    print('\a') # ส่งเสียงเตือน
                    print(">>> [ALERT] ติด Cloudflare! กรุณากดแก้ที่หน้าจอ Chrome...")
                    time.sleep(10) # ให้เวลาแก้

                # Sleep & Check Redirect
                time.sleep(random.uniform(*self.config['sleep_range']))
                
                if page > 1 and "page=1" in unquote(self.driver.current_url) and f"page={page}" not in unquote(self.driver.current_url):
                    print("   [Info] Redirected to page 1. Assuming end of listings.")
                    break
                
                # Extract
                self._scroll_page()
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                data, total, new_items = self._extract_data_from_html(soup)
                
                print(f"   [Stats] Found: {total} | New: {new_items}")
                if total == 0:
                    print("   [Info] No listings found. Stopping.")
                    break

                self._save_batch(data)
                
        except Exception as e:
            print(f"\n[Error] เกิดข้อผิดพลาดระหว่างทำงาน: {e}")
        finally:
            print(">>> ปิด Browser")
            if self.driver:
                self.driver.quit()

# --- MAIN LISTENER LOOP ---
def start_listener():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] --- เริ่มระบบรอรับคำสั่ง (Monitoring {TRIGGER_FILE}) ---")
    print(f"การทำงาน: เมื่อ Airflow สร้างไฟล์ {TRIGGER_FILE} -> โปรแกรมนี้จะเปิด Chrome มาดูดข้อมูลทันที")
    print(f"ไฟล์ผลลัพธ์: {OUTPUT_FILE}")
    print("-" * 60)
    
    while True:
        # เช็คว่ามีไฟล์ Trigger ไหม
        if os.path.exists(TRIGGER_FILE):
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ตรวจพบคำสั่งจาก Airflow! เริ่มทำงาน...")
            
            # 1. ลบไฟล์ทิ้งเพื่อกันรันซ้ำ
            try:
                os.remove(TRIGGER_FILE)
            except:
                pass
            
            # 2. เริ่ม Pipeline
            pipeline = DDPropertyLocalPipeline(CONFIG)
            pipeline.run_scrape()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] งานเสร็จสิ้น! กลับสู่โหมดรอคำสั่ง...\n")
        
        # พัก 5 วินาทีก่อนเช็คใหม่
        time.sleep(5)

if __name__ == '__main__':
    start_listener()