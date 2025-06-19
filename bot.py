
import os
import json
import logging
import telegram
from google.oauth2 import service_account
from googleapiclient.discovery import build
import schedule
import time

# Configurações de logging
logging.basicConfig(level=logging.INFO)

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
CANAL_ID = os.getenv("CANAL_ID")
YUAN_PARA_REAL = float(os.getenv("YUAN_PARA_REAL"))
YUAN_PARA_EURO = float(os.getenv("YUAN_PARA_EURO"))
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))

# Inicializar bot do Telegram
bot = telegram.Bot(token=TOKEN)

# Autenticação Google Drive
creds = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/drive"]
)
service = build("drive", "v3", credentials=creds)

def listar_pastas():
    resultados = service.files().list(
        q=f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)"
    ).execute()
    return resultados.get("files", [])

def listar_arquivos(pasta_id):
    resultados = service.files().list(
        q=f"'{pasta_id}' in parents and mimeType contains 'image/' and trashed = false",
        fields="files(id, name, webContentLink)"
    ).execute()
    return resultados.get("files", [])

def enviar_postagem():
    pastas = listar_pastas()
    if not pastas:
        logging.info("Nenhuma pasta encontrada.")
        return
    
    pasta = pastas[0]
    nome = pasta['name']

    try:
        produto, preco_yuan = nome.rsplit('¥', 1)
    except ValueError:
        produto, preco_yuan = nome, "0"

    preco_yuan = float(preco_yuan.strip())
    preco_real = round(preco_yuan * YUAN_PARA_REAL, 2)
    preco_euro = round(preco_yuan * YUAN_PARA_EURO, 2)

    legenda = f"🛍️ {produto.strip()}
🇨🇳 ¥{preco_yuan}
🇧🇷 R${preco_real}
🇪🇺 €{preco_euro}"

    arquivos = listar_arquivos(pasta['id'])
    midias = [telegram.InputMediaPhoto(arquivo['webContentLink']) for arquivo in arquivos]

    if midias:
        bot.send_media_group(chat_id=CANAL_ID, media=midias)
        bot.send_message(chat_id=CANAL_ID, text=legenda)

        service.files().update(fileId=pasta['id'], addParents="POSTADO", removeParents=DRIVE_FOLDER_ID).execute()
    else:
        logging.info("Nenhuma imagem na pasta.")

# Agendamento
schedule.every(30).minutes.do(enviar_postagem)

while True:
    schedule.run_pending()
    time.sleep(1)
