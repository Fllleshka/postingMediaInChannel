import datetime
import os.path
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter, TelegramAPIError
import aiosqlite
import asyncio
from moviepy import VideoFileClip


class work():

    def __init__(self, botkey, namechannel, idchannel, pathfolder):

        self.botkey = botkey
        self.namechennel = namechannel
        self.idchannel = idchannel
        self.pathfolder = pathfolder
        self.pathtodatabase = pathfolder + "/DataBase.db"
        self.listdatesonday = None
        self.bot = Bot(token = botkey)

        # Время функции печати
        self.printPhoto = (datetime.datetime.today() +
                      datetime.timedelta(seconds=25)).strftime("%H:%M:%S")

        # Время выяснения данных для постинга
        # insertDatesOnDay = datetime.time(0, 0, 1).strftime("%H:%M:%S")
        self.insertDatesOnDay = (datetime.datetime.today() +
                            datetime.timedelta(seconds=20)).strftime("%H:%M:%S")

    def printdates(self):
        print(f"=============")
        print(f"BotKey: \t\t\t{self.botkey}")
        print(f"Название канала: \t{self.namechennel}")
        print(f"Id канала: \t\t\t{self.idchannel}")
        print(f"Путь к базе данных: {self.pathtodatabase}")
        print(f"Путь к папке: \t\t{self.pathfolder}")
        print(f"Список постинга на сегодня: {self.listdatesonday}")
        print(f"Время функции получения данных из базы данных: {self.insertDatesOnDay}")
        print(f"Время функции постинга данных: {self.printPhoto}")
        print(f"=============")

    # Функция выбора действия каждую секунду
    async def eternalcycle(self):
        while True:
            # Время сейчас
            today = datetime.datetime.today()
            todaytime = today.strftime("%H:%M:%S")
            await self.switcher(todaytime)
            await asyncio.sleep(1)

    # Функция для выбора действия
    async def switcher(self, argument):
        match argument:
            case self.insertDatesOnDay:
                print("Данные на сегодня:")
                self.listdatesonday = await self.detesfromtable()
                for element in self.listdatesonday:
                    print(f"\t{self.namechennel}: \t{element}")
                # Формирование времени постинга первой картинки
                self.printPhoto = str(self.listdatesonday[0][2])[11:]
                print("Первое время для постинга: ", self.printPhoto)
                # Приведение времени импорта в соответствие
                self.insertDatesOnDay = datetime.time(0, 0, 1).strftime(
                    "%H:%M:%S")
                print("Получение данных на день: ", self.insertDatesOnDay)
                #await self.postmediainchannel()
            case self.printPhoto:
                print("Запуск функции постинга медиа.")
                await self.postmediainchannel()
            case _:
                print(f"{self.namechennel}: {argument}")

    # Функция получения данных из базы данных на сегодняшний день
    async def detesfromtable(self):

        today = datetime.datetime.today()
        todayday = today.strftime("%Y-%m-%d")

        if self.insertDatesOnDay != datetime.time(0, 0, 1).strftime("%H:%M:%S"):
            starttime = today.strftime("%Y-%m-%d %H:%M:%S")
        else:
            starttime = todayday + " 00:00:01"

        endtime = todayday + " 23:59:59"
        # Запрос к базе данных на формирование данных по всем запланированным постам на сегодня
        query = (("SELECT * FROM IMAGES WHERE time_to_post >= '") +
                 starttime + "' and time_to_post <= '" + endtime +
                 "' UNION SELECT * FROM VIDEOS WHERE time_to_post >= '" +
                 starttime + "' and time_to_post <= '" + endtime + "' ORDER BY time_to_post ASC")

        # Асинхронное подключение к базе данных
        async with aiosqlite.connect(self.pathtodatabase) as db:
            async with db.execute(query) as cursor:
                results = await cursor.fetchall()
                return results

    # Функция постинга картинок в канал
    async def postmediainchannel(self):
        # Имя медиа
        date = self.listdatesonday[0][1]
        # Путь до файла
        pathtodate = self.createpathtofile(date)
        print(f"Фотография {date}\n \tНаходится по пути: {pathtodate}\n \tВ канал:{self.namechennel}")
        result = os.path.exists(pathtodate)
        print(f"Проверка файла на доступность: {result}")
        media = FSInputFile(pathtodate)
        try:
            if date.endswith(".mp4"):
                if await self.chevideofile(pathtodate) > 10:
                    await self.bot.send_video(chat_id=self.idchannel,
                                          video = media,
                                          caption=self.namechennel)
                else:
                    await self.bot.send_animation(chat_id=self.idchannel,
                                          animation = media,
                                          caption=self.namechennel)
            else:
                await self.bot.send_photo(chat_id = self.idchannel,
                                          photo = media,
                                          caption=self.namechennel)
        except TelegramRetryAfter as e:
            # Ошибка Flood Control (слишком много запросов). Telegram сам говорит, сколько ждать.
            print(f"Превышен лимит запросов.")
            await asyncio.sleep(e.retry_after)

        except TelegramNetworkError as e:
            # Ошибка сети (таймауты, потеря соединения, проблемы с прокси/VPN)
            print(f"Сетевая ошибка: {e}.")

        except TelegramAPIError as e:
            # Критические ошибки API (например, бота заблокировали или неверный chat_id). Повторять нет смысла.
            print(f"Критическая ошибка Telegram API: {e}")

        print("Размер массива с данными: ", len(self.listdatesonday))
        # Проверка на наличие оставшихся элементов
        if len(self.listdatesonday) == 1:
            # Удаление первой строки
            self.listdatesonday.pop(0)
            self.insertDatesOnDay = datetime.time(0, 0, 1).strftime("%H:%M:%S")
            print("На сегодня контент кончился.")
        else:
            # Удаление первой строки
            self.listdatesonday.pop(0)
            # Формирование нового времени постинга
            self.printPhoto = str(self.listdatesonday[0][2])[11:]
            print("=========> Новое время постинга: ", self.printPhoto)

    # Функция составления полного пути до файла
    def createpathtofile(self, namefile):
        if namefile.endswith(".mp4"):
            namefolder = "/video_files/"
        else:
            namefolder = "/photos/"
        result = self.pathfolder + namefolder + namefile
        return result

    # Функция вычисления времени видео
    async def chevideofile(self, pathtovideofile):
        try:
            clip = VideoFileClip(pathtovideofile)
            duration = clip.duration
            clip.close()
            print(f"Продолжительность файла: {pathtovideofile}\n{duration}")
            # Важно закрыть клип после использования
            return duration
        except Exception as e:
            print(f"Ошибка при работе с moviepy: {e}")
            return 0