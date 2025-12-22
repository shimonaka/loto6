import requests
from bs4 import BeautifulSoup
import re
import json
import datetime
import time
import os

BASE_URL = "https://www.ohtashp.com/topics/takarakuji/loto6/"
# Allow some retries
MAX_RETRIES = 3

def get_url_for_year(year):
    current_year = datetime.datetime.now().year
    if year == current_year:
        return BASE_URL
    else:
        return f"{BASE_URL}index_{year}.html"

def fetch_and_parse(year):
    url = get_url_for_year(year)
    print(f"Fetching data for {year} from {url}...")
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=15)
            response.encoding = response.apparent_encoding
            
            if response.status_code == 404:
                print(f"  404 Not Found for {year}. Skipping.")
                return []
            if response.status_code != 200:
                print(f"  Status {response.status_code} for {year}. Retrying...")
                time.sleep(2)
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            return parse_soup(soup, year)
            
        except Exception as e:
            print(f"  Error fetching {year} (Attempt {attempt+1}): {e}")
            time.sleep(2)
            
    return []

def parse_soup(soup, year):
    results = []
    tables = soup.find_all('table')
    
    current_year_results = []
    
    for table in tables:
        rows = table.find_all('tr')
        # Iterate all rows, don't assume header is 1st row
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 8:
                continue
                
            data = [col.get_text(strip=True) for col in cols]
            
            # Check pattern: Col 0 starts with "第" and ends with "回" (or similar)
            # Example: "第1855回"
            if not re.search(r'第\d+回', data[0]):
                continue
                
            # Date check: e.g. "2023/12/21"
            # Some years might be formatted differently, but usually YYYY/MM/DD
            if not re.search(r'\d+', data[1]):
                continue
                
            try:
                # Parse Round
                round_match = re.search(r'(\d+)', data[0])
                if not round_match:
                    continue
                round_num = int(round_match.group(1))
                
                # Parse Date
                date_str = data[1]
                # Normalize date if needed (e.g. remove spaces, handle japanese chars)
                # Assuming format is mostly consistent or we keep it as string
                
                # Parse Numbers (Cols 2, 3, 4, 5, 6, 7)
                # Note: Sometimes there might be images or extra formatting. Clean text.
                numbers = []
                # Check bounds
                if len(data) < 9: # We need up to col 8 (Bonus)
                     # Sometimes bonus is col 8 (index 8)
                     pass
                     
                valid_row = True
                for i in range(2, 8):
                   text_val = re.sub(r'\D', '', data[i])
                   if not text_val:
                       valid_row = False
                       break
                   numbers.append(int(text_val))
                
                if not valid_row:
                    continue
                    
                # Bonus (Col 8)
                bonus_text = re.sub(r'\D', '', data[8])
                if bonus_text:
                    bonus = int(bonus_text)
                else:
                    bonus = 0
                
                item = {
                    "round": round_num,
                    "date": date_str,
                    "numbers": numbers,
                    "bonus": bonus
                }
                
                # Avoid duplicates within the same soup scan
                if not any(r['round'] == round_num for r in current_year_results):
                    current_year_results.append(item)
                    
            except Exception as e:
                # print(f"  Parse error row: {data} -> {e}")
                continue

    print(f"  Parsed {len(current_year_results)} records for {year}.")
    return current_year_results

def load_existing_data():
    if not os.path.exists('loto6_data.js'):
        return []
    try:
        with open('loto6_data.js', 'r', encoding='utf-8') as f:
            content = f.read()
            # Strip "const LOTO6_DATA = " and ";"
            json_str = content.replace('const LOTO6_DATA = ', '').strip().rstrip(';')
            return json.loads(json_str)
    except Exception as e:
        print(f"Error loading existing data: {e}")
        return []

def main():
    import os # Ensure os is imported
    
    existing_data = load_existing_data()
    print(f"Loaded {len(existing_data)} existing records.")
    
    today = datetime.datetime.now()
    current_year = today.year
    
    start_year = 2000
    
    # Determine start year based on existing data
    if existing_data:
        # Assumes data corresponds to 'date' field YYYY/MM/DD
        latest_date_str = existing_data[0]['date'] # Sorted desc
        try:
             latest_year = int(latest_date_str.split('/')[0])
             start_year = latest_year
             print(f"Incremental update: Starting from {start_year}")
        except:
             pass
    
    all_data = []
    
    # If partial update, keep existing data that is OLDER than start_year
    # Actually, simpler to just fetch start_year to current_year, and merge with existing.
    # We will overwrite overlaps with fresh data.
    
    print(f"Starting scrape from {start_year} to {current_year}...")
    
    fetched_data = []
    for y in range(start_year, current_year + 1):
        year_data = fetch_and_parse(y)
        fetched_data.extend(year_data)
        time.sleep(1)
        
    # Merge: fetched_data + existing_data
    # Use dictionary by round to deduplicate. Fetched data takes precedence (updates).
    unique_map = {item['round']: item for item in existing_data}
    
    for item in fetched_data:
        unique_map[item['round']] = item
        
    unique_data = list(unique_map.values())
    
    # Sort by Round Descending
    unique_data.sort(key=lambda x: x['round'], reverse=True)
    
    print(f"Total unique records: {len(unique_data)}")
    
    if len(unique_data) > 0:
        print(f"Latest: Round {unique_data[0]['round']} ({unique_data[0]['date']})")
    
    # Save to JS file
    js_content = f"const LOTO6_DATA = {json.dumps(unique_data, ensure_ascii=False, indent=2)};"
    
    with open('loto6_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("Successfully saved to loto6_data.js")

if __name__ == "__main__":
    main()
