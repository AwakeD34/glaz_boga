import psycopg2
from config import host, user, password, db_name1, db_name2, db_name3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio
import logging
import re


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# инициализация бота и диспетчера
my_bot = Bot(token='TOKEN')
dp = Dispatcher(my_bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('🔎 сервисы по которым будет осуществляться поиск информации:\n\n'
                        '🔴 1. Mamba.ru\n'
                        '🟠 2. Sberbank.ru\n'
                        '🟡 3. Telegram.org\n'
                        '\n⬇️ Возможные команды:\n'
                        ' ├ 📱 - 904777777 \\ 79378886666 \n'
                        ' └ 🆔 - id Telegramm (без @)\n'
                        '\n ℹ️ Инструкция:\n'
                        'https://telegra.ph/kratkoe-opisanie-po-deanonu-v-telegram-03-01', disable_web_page_preview=True)
    
    
@dp.message_handler()
async def search_phone(message: types.Message):
    phone_number = message.text
    # logger.info будет показывать какой (ID) пользователя телеграмм, который искал инфу по номеру.
    logger.info(f"Пользователь ID: {message.from_user.id} | Выполнил запрос по: {message.text}")

    try:
        # подключение к первой базе данных на сервере
        connection = psycopg2.connect(
            host=host,
            port=5432,
            user=user,
            password=password,
            database=db_name1
        )
        # подключение ко второй базе данных на том же сервере
        connection2 = psycopg2.connect(
            host=host,
            port=5432,
            user=user,
            password=password,
            database=db_name2
        )
        # подключение к третей базе данных на том же сервере
        connection3 = psycopg2.connect(
            host=host,
            port=5432,
            user=user,
            password=password,
            database=db_name3
        )


        user_phone_number = message.text
        cleared_phone_number = re.sub(r'^(\+7|8)', '', user_phone_number)
        # отправляем пользователю сообщение о начале поиска
        reply_message = await message.reply('⏳ Выполняется поиск, это займет время...')
        await asyncio.sleep(3)
        await my_bot.delete_message(message.chat.id, reply_message.message_id)


        with connection.cursor() as cursor, connection2.cursor() as cursor2, connection3.cursor() as cursor3:
            sql_query = f"SELECT * FROM base_1 WHERE phone LIKE '%{phone_number}%'"
            cursor.execute(sql_query)

            phone_number = phone_number.replace('.0', '')
            sql_query2 = f"SELECT * FROM base_2 WHERE phone LIKE '%{phone_number}%'"
            cursor2.execute(sql_query2)

            sql_query3 = f"SELECT * FROM base_3 WHERE phone LIKE '%{phone_number}%' OR uid = '{phone_number}' OR uid LIKE '%{phone_number}%'"
            cursor3.execute(sql_query3)

            # получение результатов запросов
            results1 = cursor.fetchall()
            results2 = cursor2.fetchall()
            results3 = cursor3.fetchall()

        reply = ""

        if results1:
            for row in results1:
                reply += f"Mamba\n├ 📲 Номер: {row[0]}\n├ 📧 Почта: {row[1]}\n└ ⏺ PW:\n{row[2]}\n"

        if results2:
            for row in results2:
                reply += f"\nSberbank\n├ 🤵‍ Имя: {row[0]} {row[1]} {row[2]}\n├ 🗓 Дата рождения: {row[3]}\n└ 📧 Почта: {row[5]}\n"

        if results3:
            for row in results3:
                reply += f"\nTelegram\n├ 🤵‍ Nickname: {row[0]} {row[1]}\n├ 📲 Номер: {row[2]}\n└ 🆔: {row[3]}\n"
        
        await message.reply(reply)

        connection.close()
        connection2.close()
        connection3.close()

    except Exception as ex: 
        await message.reply("🚫 Информация не найдена.\n\n‼️ Правильный поиск:\n9022223334 или 79022223334\n\nID Телеграмм: 27348723")
        print(ex)


if __name__ == '__main__':
    executor.start_polling(dp)