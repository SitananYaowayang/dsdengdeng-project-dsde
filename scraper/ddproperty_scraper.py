from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random
from urllib.parse import unquote
import os
import sys

# --- CONFIGURATION ---
# Path ที่ต้องการเซฟไฟล์ (ควรเป็น Path ที่ Airflow Worker เข้าถึงได้ หรือ Mounted Volume)
OUTPUT_PATH = "/opt/airflow/dags/data/ddproperty_data.csv" 

CONFIG = {
    'chrome_version': 131,       # Update ให้ตรงกับ Chrome ใน Docker/Server ของ Airflow
    'output_file': OUTPUT_PATH,
    'max_pages': 100,
    'sleep_range': (10, 15),     # เพิ่มเวลาพักให้นานขึ้น เพื่อลดโอกาสโดนจับเมื่อรัน Headless
    'base_url': "https://www.ddproperty.com/รวมประกาศขาย?listingType=sale&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&lastPosted=7"
}

# --- CLASS DEFINITION (Embedded inside DAG file for simplicity) ---
class DDPropertyPipeline:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.visited_urls = set()
        
    def _init_driver(self):
        print("[Pipeline] Initializing Browser (Headless Mode)...")
        options = uc.ChromeOptions()
        
        # --- AIRFLOW SPECIFIC SETTINGS ---
        # จำเป็นต้องเปิด Headless เมื่อรันบน Server
        options.add_argument('--headless=new') 
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            # หมายเหตุ: version_main อาจต้องปรับตาม Chrome ที่ติดตั้งใน Airflow Docker Image
            self.driver = uc.Chrome(
                options=options, 
                version_main=self.config['chrome_version'],
                use_subprocess=True
            )
        except Exception as e:
            print(f"[Error] Driver Init Failed: {e}")
            raise e

    def _scroll_page(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
        time.sleep(2)

    def _extract_data_from_html(self, soup):
        listings = soup.find_all('a', attrs={'class': 'card-footer'})
        extracted_rows = []
        new_count = 0

        for item in listings:
            row = {}
            url_raw = item.get('href')
            if url_raw and not url_raw.startswith('http'):
                url_raw = "https://www.ddproperty.com" + url_raw
            row['url'] = url_raw

            if row['url'] in self.visited_urls:
                continue

            self.visited_urls.add(row['url'])
            new_count += 1

            def get_text(da_id):
                el = item.find(attrs={'da-id': da_id})
                return el.get_text(strip=True) if el else "N/A"

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
            
            row['floor'] = "-"
            row['coords'] = "-"

            extracted_rows.append(row)
        
        return extracted_rows, len(listings), new_count

    def _save_batch(self, data):
        if not data:
            return

        df = pd.DataFrame(data)
        cols = ['url', 'title', 'publish_date', 'price', 'price_per_sqm', 
                'usable_area', 'bedroom', 'restroom', 'coords', 'full_address']
        
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config['output_file']), exist_ok=True)
        
        filename = self.config['output_file']
        use_header = not os.path.exists(filename)
        
        try:
            df.to_csv(filename, mode='a', index=False, encoding='utf-8-sig', header=use_header)
            print(f"   [Save] Saved {len(df)} new records to {filename}")
        except Exception as e:
            print(f"   [Error] Save failed: {e}")

    def run(self):
        self._init_driver()
        try:
            # ตัด Human Checkpoint ออก เพราะ Airflow ไม่มีคนกด
            print("WARNING: Running in Automated Mode (No Human Verification). Cloudflare might block this.")
            
            for page in range(1, self.config['max_pages'] + 1):
                print(f"--- Processing Page {page} / {self.config['max_pages']} ---")
                
                target_url = f"{self.config['base_url']}&page={page}"
                self.driver.get(target_url)
                
                # Sleep นานขึ้นในโหมด Headless
                sleep_time = random.uniform(*self.config['sleep_range'])
                time.sleep(sleep_time)

                # Check Title for Cloudflare Block
                if "Just a moment" in self.driver.title or "Security" in self.driver.title:
                    print("!!! BLOCKED BY CLOUDFLARE !!!")
                    raise Exception("Cloudflare blocking detected. Aborting task.")

                # Check Redirect
                if page > 1 and "page=1" in unquote(self.driver.current_url) and f"page={page}" not in unquote(self.driver.current_url):
                    print("   [Info] Redirected to page 1. Assuming end of listings.")
                    break
                
                self._scroll_page()
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                data, total_found, new_found = self._extract_data_from_html(soup)
                print(f"   [Stats] Found: {total_found} | New: {new_found}")

                if total_found == 0:
                    print("   [Info] No listings found. Stopping.")
                    break

                self._save_batch(data)
                
        except Exception as e:
            print(f"\n[Pipeline] Critical Error: {e}")
            raise e # Raise error to mark Task as Failed in Airflow
        finally:
            print("[Pipeline] Closing Browser...")
            if self.driver:
                self.driver.quit()

# --- AIRFLOW DAG DEFINITION ---

def run_ddproperty_scraper():
    pipeline = DDPropertyPipeline(CONFIG)
    pipeline.run()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ddproperty_scraper_pipeline',
    default_args=default_args,
    description='Scrape Condo Data from DDProperty',
    schedule_interval='@daily', # รันทุกวัน
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['scraping', 'selenium'],
) as dag:

    scrape_task = PythonOperator(
        task_id='scrape_ddproperty_task',
        python_callable=run_ddproperty_scraper,
    )

    scrape_task