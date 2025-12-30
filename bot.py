import os
import requests
import gspread
import datetime as dt
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

PINTEREST_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN', '').strip()
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', '').strip()
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '').strip()
SHEET_NAME = "Pinterest" #Sheet name in Google Sheets

def get_google_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

def get_pinterest_data():
    headers = {
        "Authorization": f"Bearer {PINTEREST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    all_pins = []
    
    now = dt.datetime.now()
    start_dt = now - dt.timedelta(days=89)
    
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")
    
    print(f"Запрос статистики за период: {start_date} — {end_date}")
    
    boards_url = "https://api.pinterest.com/v5/boards"
    try:
        boards_res = requests.get(boards_url, headers=headers)
        boards = boards_res.json().get('items', [])
    except Exception as e:
        print(f"Ошибка доступа к Pinterest: {e}")
        return []

    for board in boards:
        board_id = board['id']
        print(f"Сканирую доску: {board['name']}...")
        
        pins_url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
        pins_res = requests.get(pins_url, headers=headers)
        
        if pins_res.status_code == 200:
            pins_data = pins_res.json().get('items', [])
            for p in pins_data:
                pin_id = p['id']
                
                media_type = p.get('media', {}).get('media_type', '')
                p['custom_type'] = "Видео" if media_type == "video" else "Пост"
                
                ana_url = (f"https://api.pinterest.com/v5/pins/{pin_id}/analytics"
                           f"?metric_types=IMPRESSION,PIN_CLICK"
                           f"&start_date={start_date}"
                           f"&end_date={end_date}")
                
                ana_res = requests.get(ana_url, headers=headers)
                
                views = 0
                clicks = 0
                
                if ana_res.status_code == 200:
                    data = ana_res.json()
                    
                    all_data = data.get('all', {})
                    summary = all_data.get('summary_metrics', all_data)
                    
                    views = summary.get('IMPRESSION', 0)
                    clicks = summary.get('PIN_CLICK', 0)
                    
                    if views == 0 and clicks == 0:
                        if not hasattr(get_pinterest_data, 'debug_done'):
                            print(f"DEBUG: {data}")
                            get_pinterest_data.debug_done = True
                else:
                    error_detail = ana_res.json()
                    print(f"Ошибка пина {pin_id}: {ana_res.status_code} - {error_detail.get('message')}")
                
                p['views'] = views
                p['clicks'] = clicks
                all_pins.append(p)
                time.sleep(0.25)
                
    return all_pins

def run_sync():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Запуск синхронизации...")
    
    try:
        sheet = get_google_sheet()
        pins = get_pinterest_data()
    except Exception as e:
        print(f"Ошибка: {e}")
        return

    if not pins:
        print("Пины не найдены.")
        return

    existing_ids = sheet.col_values(11)
    
    new_rows = []
    updates = [] 

    for pin in pins:
        pin_id = str(pin['id'])
        title = pin.get('title') or pin.get('description', 'Без названия')
        if len(title) > 50: title = title[:47] + "..."
        
        views = pin['views']
        clicks = pin['clicks']
        p_type = pin['custom_type']

        created_at_raw = pin.get('created_at', "")
        if created_at_raw:
            publish_date = created_at_raw[:10]
        else:
            publish_date = datetime.now().strftime("%Y-%m-%d")

        if pin_id in existing_ids:
            row_idx = existing_ids.index(pin_id) + 1
            updates.append({'range': f'C{row_idx}:E{row_idx}', 'values': [[p_type, views, clicks]]})
        else:
            new_row = [
                publish_date,  # A
                title,         # B
                p_type,        # C
                views,         # D
                clicks,        # E
                "", "", "", "", "", 
                pin_id         # K
            ]
            new_rows.append(new_row)
            print(f"    Добавлен {p_type} от {publish_date}: {title}")

    if new_rows:
        sheet.append_rows(new_rows)
        print(f" Добавлено: {len(new_rows)}")
    
    if updates:
        sheet.batch_update(updates)
        print(f" Обновлено записей: {len(updates)}")

if __name__ == "__main__":
    run_sync()
    
    schedule.every(3).hours.do(run_sync)
    
    while True:
        schedule.run_pending()
        time.sleep(60)