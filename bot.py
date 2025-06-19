import os
import io
import time
import schedule
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from telegram import Bot, InputMediaPhoto

TOKEN = os.getenv("TOKEN")
CANAL_ID = os.getenv("CANAL_ID")
YUAN_PARA_REAL = float(os.getenv("YUAN_PARA_REAL", "0.76"))
YUAN_PARA_EURO = float(os.getenv("YUAN_PARA_EURO", "0.12"))
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

SCOPES = ['https://www.googleapis.com/auth/drive']
creds_dict = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)
bot = Bot(token=TOKEN)

def listar_pastas():
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def listar_arquivos(pasta_id):
    query = f"'{pasta_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get('files', [])

def baixar_arquivo(file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def postar_produto():
    pastas = listar_pastas()
    if not pastas:
        print('Nenhuma pasta disponível para postagem.')
        return

    pasta = pastas[0]
    pasta_id = pasta['id']
    pasta_nome = pasta['name']

    try:
        nome_produto, preco = pasta_nome.split('¥')
        preco_yuan = float(preco.strip())
    except:
        print(f"Erro no nome da pasta: {pasta_nome}")
        return

    preco_real = round(preco_yuan * YUAN_PARA_REAL, 2)
    preco_euro = round(preco_yuan * YUAN_PARA_EURO, 2)

    legenda = f"""🧥 {nome_produto.strip()}
🇨🇳 ¥{preco_yuan}
🇧🇷 R${preco_real}
🇪🇺 €{preco_euro}

Disponível para alunos 📄
Clique e conheça a Connect 🔥💙
connectacademy.com.br"""

    arquivos = listar_arquivos(pasta_id)
    imagens = [a for a in arquivos if a['mimeType'].startswith('image/')]

    if not imagens:
        print(f"Sem imagens na pasta {pasta_nome}")
        return

    midias = []
    for idx, img in enumerate(imagens):
        file_stream = baixar_arquivo(img['id'])
        if idx == 0:
            midias.append(InputMediaPhoto(file_stream, caption=legenda))
        else:
            midias.append(InputMediaPhoto(file_stream))

    bot.send_media_group(chat_id=CANAL_ID, media=midias)
    mover_para_postado(pasta_id)
    print(f"Postagem concluída: {pasta_nome}")

def mover_para_postado(pasta_id):
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = 'POSTADO'"
    response = service.files().list(q=query, fields="files(id, name)").execute()
    pastas_postado = response.get('files', [])

    if pastas_postado:
        postado_id = pastas_postado[0]['id']
    else:
        file_metadata = {
            'name': 'POSTADO',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [DRIVE_FOLDER_ID]
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        postado_id = file.get('id')

    service.files().update(fileId=pasta_id, addParents=postado_id, removeParents=DRIVE_FOLDER_ID).execute()

schedule.every(30).minutes.do(postar_produto)

print('Bot rodando...')
while True:
    schedule.run_pending()
    time.sleep(5)