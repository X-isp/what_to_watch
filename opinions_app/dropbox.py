import asyncio

import aiohttp

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


# Асинхронная функция, которая создаёт задачи и запускает их.
async def async_upload_files_to_dropbox(images):
    if images is not None:
        # Создать пустой список для асинхронных задач.
        tasks = []
        # Инициализировать единую сессию для работы с aiohttp.
        async with aiohttp.ClientSession() as session:
            for image in images:
                # Для каждого изображения создать асинхронную задачу.
                tasks.append(
                    asyncio.ensure_future(
                        # Передать в асинхронную функцию сессию и изображение.
                        upload_file_and_get_url(session, image)
                    )
                )
            # После того, как все задачи созданы, запустить их на выполнение.
            urls = await asyncio.gather(*tasks)
        return urls
 
 # Асинхронная функция загрузки изображений и получения на них ссылок.
async def upload_file_and_get_url(session, image):
    dropbox_args = json.dumps({
        'autorename': True,
        'mode': 'add',
        'path': f'/{image.filename}',
    })   
    # Асинхронная загрузка в aiohttp выполняется 
    # с помощью асинхронного контекстного менеджера.
    async with session.post(
        UPLOAD_LINK,
        headers={
            'Authorization': AUTH_HEADER,
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': dropbox_args
        },
        data=image.read()
    ) as response:
        # Асинхронное получение ответа должно сопровождаться 
        # ключевым словом await.
        data = await response.json()
        path = data['path_lower']
    async with session.post(
        SHARING_LINK,
        headers={
            'Authorization': AUTH_HEADER,
            'Content-Type': 'application/json',
        },
        json={'path': path}
    ) as response:
        data = await response.json()
        if 'url' not in data:
            data = data['error']['shared_link_already_exists']['metadata']
        url = data['url']
        url = url.replace('&dl=0', '&raw=1')
    return url 

# def upload_files_to_dropbox(images):
#     urls = []
#     if images is None:
#         return urls

#     for image in images:
#         # Формируем путь и аргументы для Dropbox
#         dropbox_args = json.dumps({
#             'autorename': True,
#             'path': f'/{image.filename}',
#         })

#         # Загружаем файл
#         response = requests.post(
#             UPLOAD_LINK,
#             headers={
#                 'Authorization': AUTH_HEADER,
#                 'Content-Type': 'application/octet-stream',
#                 'Dropbox-API-Arg': dropbox_args
#             },
#             data=image.read()
#         )

#         # Проверяем статус
#         if response.status_code != 200:
#             print(f"Ошибка загрузки {image.filename}: {response.status_code} {response.text}")
#             continue

#         try:
#             path = response.json()['path_lower']
#         except (ValueError, KeyError):
#             print(f"Невозможно прочитать ответ от Dropbox для {image.filename}: {response.text}")
#             continue

#         # Создаём ссылку для общего доступа
#         response = requests.post(
#             SHARING_LINK,
#             headers={
#                 'Authorization': AUTH_HEADER,
#                 'Content-Type': 'application/json',
#             },
#             json={'path': path}
#         )

#         try:
#             data = response.json()
#         except ValueError:
#             print(f"Ошибка создания ссылки для {image.filename}: {response.text}")
#             continue

#         # Если ссылка уже существует
#         if 'url' not in data:
#             data = data.get('error', {}).get('shared_link_already_exists', {}).get('metadata', {})

#         url = data.get('url')
#         if url:
#             url = url.replace('&dl=0', '&raw=1')
#             urls.append(url)

#     return urls


