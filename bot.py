import os
import json
import logging
import time
import schedule
from google.oauth2 import service_account
from googleapiclient.discovery import build
from telegram import Bot

# Configurações
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")
CANAL_ID = os.getenv("CANAL_ID")
YUAN_PARA_REAL = float(os.getenv("YUAN_PARA_REAL", 0.76))
YUAN_PARA_EURO = float(os.getenv("YUAN_PARA_EURO", 0.12))
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))

# Inicializar bot do Telegram
bot = Bot(token=TOKEN)

# Função para postar no Telegram
def postar_no_telegram():
    bot.send_message(chat_id=CANAL_ID, text="Postagem automática funcionando!")

# Agendamento
schedule.every(30).minutes.do(postar_no_telegram)

# Loop principal
while True:
    schedule.run_pending()
    time.sleep(1)
