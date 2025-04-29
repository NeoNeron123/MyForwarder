import asyncio
import random
import os
from telethon import TelegramClient, events
from telethon.errors import AuthKeyUnregisteredError
from auth import api_id, api_hash, phone_number
from config import source_chat_ids, target_chat_ids, delay_range

SESSION_NAME = "session"

# Прокси список: (proxy_type, address, port, [secret])
proxy_list = [
    ('none',),  # Без прокси
    ('socks5', '127.0.0.1', 1080),
    ('socks5', 'proxy.example.com', 1080, 'user', 'pass'),  # с авторизацией
    ('mtproto', 'proxy.mtproto.com', 443, 'abcdef1234567890abcdef1234567890'),
]

# Функция выбора прокси
def choose_proxy():
    print("Выберите прокси:")
    for i, proxy in enumerate(proxy_list):
        name = proxy[0].upper() if proxy[0] != 'none' else 'Без прокси'
        print(f"{i + 1}. {name} — {proxy[1:] if len(proxy) > 1 else ''}")

    try:
        choice = int(input("Введите номер прокси: ").strip()) - 1
        selected = proxy_list[choice]

        if selected[0] == 'none':
            return None
        elif selected[0] == 'socks5':
            if len(selected) == 5:
                return ('socks5', selected[1], selected[2], True, selected[3], selected[4])
            else:
                return ('socks5', selected[1], selected[2])
        elif selected[0] == 'mtproto':
            return ('mtproxy', selected[1], selected[2], selected[3])
    except Exception as e:
        print(f"❌ Неверный выбор: {e}")
        return None


async def list_chats():
    await client.start(phone_number)
    dialogs = await client.get_dialogs()
    output_lines = []

    for dialog in dialogs:
        entity = dialog.entity
        name = getattr(entity, 'title', None) or getattr(entity, 'first_name', 'Unknown')
        chat_id = entity.id

        if hasattr(entity, 'megagroup') and entity.megagroup:
            chat_type = 'Супергруппа'
        elif hasattr(entity, 'broadcast') and entity.broadcast:
            chat_type = 'Канал'
        elif entity.id > 0:
            chat_type = 'Личное сообщение'
        else:
            chat_type = 'Группа/Другое'

        output_lines.append(f"{name} — ID: {chat_id} — Тип: {chat_type}")

    with open("chat_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print("✅ Список чатов сохранён в файл chat_list.txt")


async def forward_messages():
    await client.start(phone_number)

    target_peers = []
    for chat_id in target_chat_ids:
        try:
            peer = await client.get_entity(chat_id)
            target_peers.append(peer)
        except Exception as e:
            print(f"❌ Не удалось получить entity для {chat_id}: {e}")

    if not target_peers:
        print("⚠️ Нет доступных целевых чатов для пересылки. Завершение.")
        return

    @client.on(events.NewMessage(chats=source_chat_ids))
    async def handler(event):
        message = event.message
        for peer in target_peers:
            try:
                await asyncio.sleep(random.uniform(*delay_range))
                await client.send_message(peer, message)
                print(f"✅ Сообщение переслано в {peer.id}")
            except Exception as e:
                print(f"❌ Не удалось переслать в {peer.id}: {e}")

    print("📡 Скрипт запущен. Ожидаю сообщения...")
    await client.run_until_disconnected()


def main():
    proxy = choose_proxy()

    global client
    client = TelegramClient(SESSION_NAME, api_id, api_hash, proxy=proxy)

    print("\nВыберите действие:")
    print("1. Запустить пересылку сообщений")
    print("2. Сохранить список всех чатов в chat_list.txt и выйти")
    choice = input("Введите 1 или 2: ").strip()

    try:
        with client:
            if choice == '1':
                client.loop.run_until_complete(forward_messages())
            elif choice == '2':
                client.loop.run_until_complete(list_chats())
            else:
                print("❌ Неверный выбор. Завершение работы.")
    except AuthKeyUnregisteredError:
        print("❌ Сессия Telegram недействительна. Удаление старой сессии...")
        try:
            os.remove(f"{SESSION_NAME}.session")
            print("🔁 Повторите запуск скрипта — будет запрошен код подтверждения.")
        except Exception as e:
            print(f"❌ Не удалось удалить сессию: {e}")


if __name__ == '__main__':
    main()
