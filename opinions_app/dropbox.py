# # what_to_watch/opinions_app/dropbox.py

# import json

# import requests

# from . import app

# from dotenv import load_dotenv

# load_dotenv()

# # Заголовок для авторизации. Так заголовок к API будет выполняться
# # как от авторизованного пользователя. 
# AUTH_HEADER = f'Bearer {app.config["DROPBOX_TOKEN"]}'
# # Эндпоинт для загрузки изображений. Его можно найти в документации
# # метода [upload()](https://www.dropbox.com/developers/documentation/http/documentation#files-upload).
# UPLOAD_LINK = 'https://content.dropboxapi.com/2/files/upload'
# # Эндпоинт для создания ссылки на изображение. Его можно найти 
# # в документации метода [create_shared_link_with_settings()](https://www.dropbox.com/developers/documentation/http/documentation#sharing-create_shared_link_with_settings).
# SHARING_LINK = ('https://api.dropboxapi.com/2/'
#                 'sharing/create_shared_link_with_settings')

# def upload_files_to_dropbox(images):
#     urls = []  # Список для сбора готовых ссылок.
#     if images is not None:  # Если были переданы изображения...
#         for image in images:  # ...для каждого изображения...
#             # ...подготовить словарь и указать в нём, 
#             # что надо загружать файлы по указанному пути path.
#             # В случае если такой файл существует, переименовывать его.
#             dropbox_args = json.dumps({
#                 'autorename': True,
#                 'path': f'/{image.filename}',
#             })
#             # Отправить post-запрос для загрузки файла.   
#             response = requests.post(
#                 UPLOAD_LINK,
#                 headers={
#                     # Передать токен.
#                     'Authorization': AUTH_HEADER,
#                     # Указать, что передача будет в формате бинарных данных.
#                     'Content-Type': 'application/octet-stream',
#                     # Передать подготовленные ранее аргументы.
#                     'Dropbox-API-Arg': dropbox_args
#                 },
#                 # Передать файл в виде бинарных данных.
#                 data=image.read()
#             )
#             # Получить путь до файла из ответа от API.
#             path = response.json()['path_lower']
#             # Отправить второй запрос на формирование ссылки.
#             response = requests.post(
#                 SHARING_LINK,
#                 headers={
#                     'Authorization': AUTH_HEADER,
#                     # Здесь данные уже в формате обычного json.
#                     'Content-Type': 'application/json',
#                 },
#                 json={'path': path}
#             )
#             data = response.json()
#             # Проверить, есть ли ключ url на верхнем уровне ответа.
#             if 'url' not in data:
#                 # Обходной манёвр на случай, 
#                 # если пользователь попытается отправить
#                 # один и тот же файл дважды. Ему вернётся
#                 # ссылка на уже существующий файл.
#                 data = data['error']['shared_link_already_exists']['metadata']
#             # Получить ссылку по ключу.
#             url = data['url']
#             # Заменить режим работы ссылки, 
#             # чтобы получить ссылку на скачивание.
#             url = url.replace('&dl=0', '&raw=1')
#             # Добавить ссылку в общий список ссылок.
#             urls.append(url)
#     return urls

import json
import requests
from . import app
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

DROPBOX_TOKEN = app.config.get("DROPBOX_TOKEN")
if not DROPBOX_TOKEN:
    raise RuntimeError("DROPBOX_TOKEN не задан! Проверьте файл .env")

AUTH_HEADER = f'Bearer {DROPBOX_TOKEN}'

UPLOAD_LINK = 'https://content.dropboxapi.com/2/files/upload'
SHARING_LINK = 'https://api.dropboxapi.com/2/sharing/create_shared_link_with_settings'


def upload_files_to_dropbox(images):
    urls = []
    if images is None:
        return urls

    for image in images:
        # Формируем путь и аргументы для Dropbox
        dropbox_args = json.dumps({
            'autorename': True,
            'path': f'/{image.filename}',
        })

        # Загружаем файл
        response = requests.post(
            UPLOAD_LINK,
            headers={
                'Authorization': AUTH_HEADER,
                'Content-Type': 'application/octet-stream',
                'Dropbox-API-Arg': dropbox_args
            },
            data=image.read()
        )

        # Проверяем статус
        if response.status_code != 200:
            print(f"Ошибка загрузки {image.filename}: {response.status_code} {response.text}")
            continue

        try:
            path = response.json()['path_lower']
        except (ValueError, KeyError):
            print(f"Невозможно прочитать ответ от Dropbox для {image.filename}: {response.text}")
            continue

        # Создаём ссылку для общего доступа
        response = requests.post(
            SHARING_LINK,
            headers={
                'Authorization': AUTH_HEADER,
                'Content-Type': 'application/json',
            },
            json={'path': path}
        )

        try:
            data = response.json()
        except ValueError:
            print(f"Ошибка создания ссылки для {image.filename}: {response.text}")
            continue

        # Если ссылка уже существует
        if 'url' not in data:
            data = data.get('error', {}).get('shared_link_already_exists', {}).get('metadata', {})

        url = data.get('url')
        if url:
            url = url.replace('&dl=0', '&raw=1')
            urls.append(url)

    return urls
