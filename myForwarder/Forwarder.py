import asyncio
import random
import os
from telethon import TelegramClient, events
from telethon.errors import AuthKeyUnregisteredError
from auth import api_id, api_hash, phone_number
from config import source_chat_ids, target_chat_ids, delay_range

try:
    import socks  # from PySocks
except ImportError:
    print("❌ Модуль 'socks' не установлен. Установите через: pip install pysocks")
    exit(1)

SESSION_NAME = "session"


def load_random_proxy():
    proxies = []
    if not os.path.exists("proxy.txt"):
        return None

    with open("proxy.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            host = parts[0].strip()
            try:
                port = int(parts[1].strip())
                proxies.append((socks.SOCKS5, host, port))
            except ValueError:
                continue

    if proxies:
        selected = random.choice(proxies)
        print(f"🔀 Выбран случайный прокси: {selected[1]}:{selected[2]}")
        return selected
    else:
        print("⚠️ Прокси не найдены или файл пуст. Использую подключение без прокси.")
        return None


async def list_chats(client):
    await client.start(phone_number)
    dialogs = await client.get_dialogs()
    output_lines = []

    for dialog in dialogs:
        entity = dialog.entity
        name = getattr(entity, 'title', None) or getattr(entity, 'first_name', 'Unknown')
        chat_id = entity.id

        if hasattr(entity, 'megagroup') and entity.megagroup:
            chat_type = 'С_
