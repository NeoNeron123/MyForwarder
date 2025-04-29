import asyncio
import random
from telethon import TelegramClient, events
from auth import api_id, api_hash, phone_number
from config import source_chat_ids, target_chat_ids, delay_range

client = TelegramClient('session', api_id, api_hash)


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

    @client.on(events.NewMessage(chats=source_chat_ids))
    async def handler(event):
        message = event.message

        for chat_id in target_chat_ids:
            try:
                await asyncio.sleep(random.uniform(*delay_range))
                await client.send_message(chat_id, message)
                print(f"✅ Сообщение переслано в {chat_id}")
            except Exception as e:
                print(f"❌ Не удалось переслать в {chat_id}: {e}")

    print("📡 Скрипт запущен. Ожидаю сообщения...")
    await client.run_until_disconnected()


def main():
    print("Выберите действие:")
    print("1. Запустить пересылку сообщений")
    print("2. Сохранить список всех чатов в chat_list.txt и выйти")
    choice = input("Введите 1 или 2: ").strip()

    with client:
        if choice == '1':
            client.loop.run_until_complete(forward_messages())
        elif choice == '2':
            client.loop.run_until_complete(list_chats())
        else:
            print("❌ Неверный выбор. Завершение работы.")


if __name__ == '__main__':
    main()
