import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('DROPBOX_TOKEN'))

DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
print("DROPBOX_TOKEN =", DROPBOX_TOKEN)

if not DROPBOX_TOKEN:
    raise RuntimeError("DROPBOX_TOKEN не задан! Проверьте переменные окружения.")
else:
    print("Токен найден")

