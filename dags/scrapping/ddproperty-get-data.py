import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random
from urllib.parse import unquote
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ddproperty"
RAW_DIR.mkdir(parents=True, exist_ok=True)

CONFIG = {
    'chrome_version': 142,      
    'output_file': RAW_DIR/'ddproperty_last_7days.csv',
    'max_pages': 10,
    'sleep_range': (6, 9),     
    'base_url': "https://www.ddproperty.com/รวมประกาศขาย?listingType=sale&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&lastPosted=7"
}

class DDPropertyPipeline:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.visited_urls = set()
        
    def _init_driver(self):
        """Step 1: เริ่มต้น Browser"""
        print("[Pipeline] Initializing Browser...")
        options = uc.ChromeOptions()
        
        try:
            self.driver = uc.Chrome(
                options=options, 
                version_main=self.config['chrome_version'],
                use_subprocess=True
            )
        except Exception as e:
            print(f"[Error] Driver Init Failed: {e}")
            sys.exit(1)

    def _human_verification_checkpoint(self):
        """Step 2: จุดพักให้คนกดยืนยันตัวตน (Cloudflare)"""
        print("\n" + "="*50)
        print("!!! HUMAN VERIFICATION CHECKPOINT !!!")
        print("ระบบจะเปิดหน้าแรก... กรุณาแก้ Cloudflare (ติ๊กถูก) ให้เรียบร้อย")
        print("="*50)

        self.driver.get("https://www.ddproperty.com")
        
        input(">>> เมื่อเข้าหน้าเว็บได้ปกติแล้ว ให้กด Enter ที่นี่เพื่อเริ่มดูดข้อมูล... ")
        print("[Pipeline] Starting extraction process...\n")

    def _scroll_page(self):
        """Helper: เลื่อนหน้าจอเพื่อให้รูปและข้อมูลโหลด (Lazy Load)"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
        time.sleep(2)

    def _extract_data_from_html(self, soup):
        """Step 4: แปลง HTML Soup เป็น List of Dictionaries"""
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
        """Step 5: บันทึกข้อมูลลง CSV (Append mode)"""
        if not data:
            return

        df = pd.DataFrame(data)
        cols = ['url', 'title', 'publish_date', 'price', 'price_per_sqm', 
                'usable_area', 'bedroom', 'restroom', 'coords', 'full_address']
        
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]

        filename = self.config['output_file']
        use_header = not os.path.exists(filename)
        
        try:
            df.to_csv(filename, mode='a', index=False, encoding='utf-8-sig', header=use_header)
            print(f"   [Save] Saved {len(df)} new records.")
        except Exception as e:
            print(f"   [Error] Save failed: {e}")

    def run(self):
        """Main Execution Flow"""
        self._init_driver()
        
        try:
            self._human_verification_checkpoint()

            for page in range(1, self.config['max_pages'] + 1):
                print(f"--- Processing Page {page} / {self.config['max_pages']} ---")
                
                target_url = f"{self.config['base_url']}&page={page}"
                self.driver.get(target_url)
                
                sleep_time = random.uniform(*self.config['sleep_range'])
                time.sleep(sleep_time)

                if page > 1 and "page=1" in unquote(self.driver.current_url) and f"page={page}" not in unquote(self.driver.current_url):
                    print("   [Info] Redirected to page 1. Assuming end of listings.")
                    break
                
                self._scroll_page()
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                data, total_found, new_found = self._extract_data_from_html(soup)
                print(f"   [Stats] Found: {total_found} | New: {new_found}")

                if total_found == 0:
                    print("   [Info] No listings found on this page. Stopping.")
                    break

                self._save_batch(data)
                
        except KeyboardInterrupt:
            print("\n[Pipeline] Stopped by user.")
        except Exception as e:
            print(f"\n[Pipeline] Critical Error: {e}")
        finally:
            print("[Pipeline] Closing Browser...")
            if self.driver:
                self.driver.quit()
            print(f"[Pipeline] Finished. Data saved to: {self.config['output_file']}")

if __name__ == '__main__':
    pipeline = DDPropertyPipeline(CONFIG)
    pipeline.run()