import os
import gspread
import requests
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, date
import locale
from .utils import is_float

# Cargar variables desde el archivo .env
load_dotenv()

# --- CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CREDS_PATH = os.getenv("GOOGLE_SHEETS_CREDS_PATH")
SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

print(f"Locale Before: {locale.getlocale()}")
# Alternatively, set a specific locale (e.g., Argentina (Linux/macOS))
try:
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
except Exception:
    pass
print(f"Locale After: {locale.getlocale()}")


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def procesar_recordatorios():
    if not all([TOKEN, CHAT_ID, CREDS_PATH, SHEETS_ID]):
        print("Error: Faltan variables de entorno.")
        return

    try:
        # Autenticación usando la ruta del JSON de la variable de entorno
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
        client = gspread.authorize(creds)
        
        hoy = datetime.now()
        actualYear = datetime.now().strftime("%Y")
        actualMonth = datetime.now().strftime("%B")
        
        sheet = client.open_by_key(SHEETS_ID).worksheet(actualYear)
        data = sheet.get_all_values(major_dimension="COLUMNS",return_type=gspread.utils.GridRangeType.ValueRange)
        #data = sheet.get_all_values(return_type=)
        #monthCell = sheet.find(actualMonth,in_row=2,case_sensitive=False)
        #data = sheet.batch_get(monthCell.numeric_value)

        servicios = []
        servicios_vencen_hoy = []
        servicios_vencen_pronto = []

        encontrado = False

        index = 0

        for index,columna in enumerate(data):
            if str.lower(columna[1]) != str.lower(actualMonth):
                continue
            else:
                print(f"Analizando mes {actualMonth}")

                break
        
        cantidad_filas = len(data[0])

        columna_servicio = data[0]
        columna_monto = data[index]
        columna_vencimiento = data[index+1]
        columna_pagado = data[index+2]

        for step in range(2,cantidad_filas):
            print(f"Analizando servicio: {columna_servicio[step]} | {columna_vencimiento[step]} | {columna_monto[step]} | {columna_pagado[step]}")

            if columna_servicio[step] == "" \
                or columna_vencimiento[step] == "" \
                or columna_monto[step] == "" \
                or is_float(str.replace(str.replace(str.replace(columna_monto[step],".",""),"$",""),",",".")) is False \
                or columna_pagado[step] != "FALSE":
                continue

            servicio = {
                "name": columna_servicio[step],
                "monto": columna_monto[step],
                "vencimiento": columna_vencimiento[step] if len(columna_vencimiento[step]) == 8 else f"0{columna_vencimiento[step]}"
            }

            servicios.append(servicio)

            if servicio.get("vencimiento") == hoy.strftime("%d/%m/%Y") \
                or servicio.get("vencimiento") == hoy.strftime("%d/%m/%y"):
                servicios_vencen_hoy.append(servicio)

            elif servicio.get("vencimiento") <= (hoy + timedelta(days=2)).strftime("%d/%m/%Y") \
                and servicio.get("vencimiento") > hoy.strftime("%d/%m/%Y") \
                or servicio.get("vencimiento") <= (hoy + timedelta(days=2)).strftime("%d/%m/%y") \
                and servicio.get("vencimiento") > hoy.strftime("%d/%m/%y") :
                servicios_vencen_pronto.append(servicio)

        if len(servicios_vencen_hoy) > 0:
            mensaje = f"🚨 Servicios que vencen hoy:\n"
            for servicio in servicios_vencen_hoy:
                mensaje+=f"* {servicio.get("name")} - ${servicio.get("monto")}\n"
        
            print(mensaje)
            enviar_telegram(mensaje)

        if len(servicios_vencen_hoy) > 0:
            mensaje = f"🔔 Servicios que vencen pronto:\n"
            for servicio in servicios_vencen_pronto:
                mensaje+=f"* {servicio.get("name")} - ${servicio.get("monto")}\n"
            
            print(mensaje)
            enviar_telegram(mensaje)

        print(f"Servicios: {servicios}")


    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    procesar_recordatorios()
