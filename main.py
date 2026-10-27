from dotenv import load_dotenv
from classes.class_database import database
from classes.work import work
from threading import Thread
import os
import datetime
import logging
import time
import asyncio

# Функция удаления баз данных
def deletedates():
    # Удаление баз данных для тестирования
    try:
        os.remove(os.getenv('FIRSTMAINFOLDER') + "/DataBase.db")
        os.remove(os.getenv('SECONDMAINFOLDER') + "/DataBase.db")
    except Exception:
        return Exception

async def main():

    # Загрузка данных окружения
    load_dotenv()

    # Импорт данных из файла env
    firstmainfolder = os.getenv('FIRSTMAINFOLDER')
    secondmainfolder = os.getenv('SECONDMAINFOLDER')
    mass = [firstmainfolder, secondmainfolder]

    # Проверка на наличие базы данных
    for elem in mass:
        dbase = database(elem)
        today = datetime.datetime.today().strftime("%H:%M:%S")
        if dbase.checkdatabase() == False:
            logging.info(f"{today} Надо создать новую базу данных.")
            dbase.initialdatabase(elem)
            # Заполняем базы данных
            dbase.importdates()
        else:
            logging.info(f"{today} База данных есть.")

    # Создаём экземпляр класса work для постинга контента первого канала
    firstchennel = work(os.getenv('FIRSTBOTKEY'),
                        os.getenv('FIRSTNAMECHANNEL'),
                        os.getenv('FIRSTIDCHANNEL'),
                        os.getenv('FIRSTMAINFOLDER'))

    # Создаём экземпляр класса work для постинга контента второго канала
    secondchennel = work(os.getenv('SECONDBOTKEY'),
                        os.getenv('SECONDNAMECHANNEL'),
                        os.getenv('SECONDIDCHANNEL'),
                        os.getenv('SECONDMAINFOLDER'))

    # Запускаем оба воркера МНОГОЗАДАЧНО (одновременно)
    # asyncio.gather объединяет их в один event loop, и они не блокируют друг друга
    await asyncio.gather(
        firstchennel.eternalcycle(),
        secondchennel.eternalcycle(),
    )



if __name__ == '__main__':
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO,
                        filename="../dates/telegramchennels.log",
                        filemode="w",
                        encoding='utf-8',
                        format="%(asctime)s %(levelname)s %(message)s")

    # Запуск главной функции приложения (ассинхронно)
    asyncio.run(main())