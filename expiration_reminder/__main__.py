import os
import gspread
import requests
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
import locale
from .utils import is_float, convert_sheet_to_date

# Load variables from .env file
load_dotenv()

# --- ENVIRONMENT VARIABLES CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CREDS_PATH = os.getenv("GOOGLE_SHEETS_CREDS_PATH")
SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

LOCALE = os.getenv("FORCE_LOCALE", locale.getlocale())

SOON_TIMESPAN = int(os.getenv("SOON_TIMESPAN", "2"))

MSG_EXPIRATION_TODAY = os.getenv("MSG_EXPIRATION_TODAY", "🚨 Servicios que vencen hoy")
MSG_EXPIRATION_SOON = os.getenv("MSG_EXPIRATION_SOON", "🔔 Servicios que vencen pronto")


# Locale setting
try:
    locale.setlocale(locale.LC_ALL, LOCALE)
except Exception:
    print(f"Could not set Locale: {LOCALE}, using default: {locale.getlocale()}")
    pass
print(f"Using Locale: {locale.getlocale()}")


def send_msg_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

def process_services_reminder():
    if not all([TOKEN, CHAT_ID, CREDS_PATH, SHEETS_ID]):
        print("Error: Environment variables missing.")
        return

    try:
        # Auth from JSON file path
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
        client = gspread.authorize(creds)
        
        hoy = datetime.now()
        actual_year = datetime.now().strftime("%Y")
        actual_month = datetime.now().strftime("%B")
        
        sheet = client.open_by_key(SHEETS_ID).worksheet(actual_year)
        data = sheet.get_all_values(major_dimension="COLUMNS",value_render_option="UNFORMATTED_VALUE", return_type=gspread.utils.GridRangeType.ValueRange)

        services = []
        services_expire_today = []
        services_expires_soon = []

        encontrado = False

        for index,column in enumerate(data):
            if str.lower(column[1]) != str.lower(actual_month):
                continue
            else:
                print(f"Analyzing month: {actual_month}")
                break
        
        row_count = len(data[0])

        service_col = data[0]
        amount_col = data[index]
        expiration_col = data[index+1]
        already_paid_col = data[index+2]

        for row in range(2,row_count):
            print(f"Analyzing service: {service_col[row]} | {convert_sheet_to_date(expiration_col[row]).strftime('%d/%m/%Y')} | {amount_col[row]} | {already_paid_col[row]}")

            if service_col[row] == "" \
                or expiration_col[row] == "" \
                or amount_col[row] == "" \
                or is_float(amount_col[row]) is False \
                or already_paid_col[row] != False:
                continue

            service = {
                "name": service_col[row],
                "amount": amount_col[row],
                # Fix for Sheets date, days
                "expiration": convert_sheet_to_date(expiration_col[row]).strftime('%d/%m/%Y')
            }

            services.append(service)

            if service.get("expiration") == hoy.strftime("%d/%m/%Y"):
                services_expire_today.append(service)

            elif service.get("expiration") <= (hoy + timedelta(days=SOON_TIMESPAN)).strftime("%d/%m/%Y") \
                and service.get("expiration") > hoy.strftime("%d/%m/%Y") :
                services_expires_soon.append(service)

        if len(services_expire_today) > 0:
            message = f"{MSG_EXPIRATION_TODAY}:\n"
            for service in services_expire_today:
                message+=f"* {service.get("name")} - ${service.get("amount")}\n"
        
            print(message)
            send_msg_telegram(message)

        if len(services_expires_soon) > 0:
            message = f"{MSG_EXPIRATION_SOON}:\n"
            for service in services_expires_soon:
                message+=f"* {service.get("name")} - ${service.get("amount")} - ${service.get("expiration")}\n"
            
            print(message)
            send_msg_telegram(message)

        print(f"Services: {services}")


    except Exception as e:
        print(f"An error ocurred: {e}")

if __name__ == "__main__":
    process_services_reminder()
