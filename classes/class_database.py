import logging
import os
import sqlite3
import time
import tqdm
import random
import datetime

from pathlib import Path

class database:
    def __init__(self, pathmainfolder):
        # Путь к главной папке
        self.pathmainfolder = pathmainfolder
        # Путь до Базы Данных
        self.pathdatabase = self.pathmainfolder + '/DataBase.db'
        # Путь до папки с картинками
        self.imagesfolder = self.pathmainfolder + "/photos/"
        # Путь до папки с видео
        self.videosfolder = self.pathmainfolder + "/video_files/"

    # Метод вывода всех переменных
    def printdates(self):
        print(f"Путь к главной папке: {self.pathmainfolder}")
        print(f"Папки в папке [{self.pathmainfolder}]: {os.listdir(self.pathmainfolder)}")
        print(f"Путь к базе данных: {self.pathdatabase}")
        print(f"Путь к папке картинок: {self.imagesfolder}")
        print(f"Путь к папке видео: {self.videosfolder}")

    # Проверка и создание базы данных
    def checkdatabase(self):
        result = os.path.exists(self.pathdatabase)
        if result is True:
            return True
        else:
            return False

    # Инициализация базы данных
    def initialdatabase(self, namefolder):
        logging.info(f"Название папки {namefolder}.База данных [{self.pathdatabase}] не найден. Надо создать.")
        # Открываем соединение с базой данных
        con = sqlite3.connect(self.pathdatabase)
        # Создаём таблицу постинга картинок
        with con:
            con.execute(
                """
                    CREATE TABLE IMAGES (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name_pic TEXT,
                        time_to_post datetime
                    );
                """
            )
        # Создаём таблицу постинга видео
        with con:
            con.execute(
                """
                    CREATE TABLE VIDEOS (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name_video TEXT,
                        time_to_post datetime
                    );
                """
            )
        # Создаём таблицу постинга рекламы
        with con:
            con.execute(
                """
                    CREATE TABLE PROMOTION (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name_media TEXT,
                        text_media TEXT,
                        time_to_post datetime
                    );
                """
            )
        # Закрываем соединение с базой данных
        con.close()

    # Проверка папок на повторы
    def checkfolderforduplicate(self, path):
        logging.info(f"Проверяем папку {path} а повторы и удаляем не нужное")
        listdir = os.listdir(path)
        logging.info(f"Количество файлов в папке [{path}]: {len(listdir)}")
        time.sleep(5)
        index = 0
        for element in tqdm.tqdm(listdir):
            if "thumb" in element or "(1)" in element:
                index += 1
                pathtofile = path + element
                print(f"{element} необходимо удалить. Путь [{pathtofile}] доступность [{os.path.exists(self.pathdatabase)}]")
                os.remove(pathtofile)
        logging.info(f"Количество файлов удалённых в папке [{path}]: {index}")

    # Вставка данных в таблицу
    def insertdatesintable(self, listdates):

        videodates = []
        imagedates = []

        # Получаем время сейчас
        timetopost = datetime.datetime.today()
        index = 0
        # Формирование списков с данными
        for element in tqdm.tqdm(listdates):
            timetopost2 = datetime.timedelta(
                minutes=random.randint(10, 20),
                seconds=random.randint(1, 60))
            timetopost += timetopost2
            index += 1
            newelem = (index, element[1], timetopost.strftime("%Y-%m-%d %H:%M:%S"))
            if element[0] == 'IMAGE':
                imagedates.append(newelem)
            else:
                videodates.append(newelem)


        # Добавляем данные в базу
        self.insertonestrintable("IMAGES", imagedates)
        self.insertonestrintable("VIDEOS", videodates)

    # Вставка строки в базу данных
    def insertonestrintable(self, table, dates):
        match(table):
            case "IMAGES":
                sql = 'INSERT INTO IMAGES (id, name_pic, time_to_post) VALUES (?, ?, ?)'
            case "VIDEOS":
                sql = 'INSERT INTO VIDEOS (id, name_video, time_to_post) VALUES (?, ?, ?)'
            case _:
                sql = ''

        # Открываем соединение с базой данных
        con = sqlite3.connect(self.pathdatabase)
        # Заполняем таблицу
        with con:
            con.executemany(sql, dates)

    # Функция распределения медиа (алгоритм Брезенхэма)
    def merge_proportionally(self, arr1, arr2):
        arrayfirst = os.listdir(arr1)
        arraysecond = os.listdir(arr2)

        shuffledfirst = random.sample(arrayfirst, len(arrayfirst))
        shuffledsecond = random.sample(arraysecond, len(arraysecond))

        res = []
        len1, len2 = len(shuffledfirst), len(shuffledsecond)
        total_elements = len1 + len2

        # Указатели на текущие элементы в массивах
        i, j = 0, 0
        # Накопители для отслеживания пропорций
        count1, count2 = 0, 0

        while i < len1 or j < len2:
            if i < len1 and j < len2:
                # Считаем "идеальный шаг" на основе оставшихся элементов
                # и выбираем тот массив, чей элемент сейчас нужнее для баланса
                if (count1 + 1) * len2 <= (count2 + 1) * len1:
                    res = self.appendelemimsilt(res, arrayfirst[i])
                    i += 1
                    count1 += 1
                else:
                    res = self.appendelemimsilt(res, arraysecond[j])
                    j += 1
                    count2 += 1

            elif i < len1:
                # Если второй массив закончился, забираем остатки первого
                res = self.appendelemimsilt(res, arrayfirst[i])
                i += 1
            else:
                # Если первый массив закончился, забираем остатки второго
                res = self.appendelemimsilt(res, arraysecond[j])
                j += 1

        return res

    # Функция правильного добавления данных в результирующий массив
    def appendelemimsilt(self, result, element):
        if element.endswith(".mp4"):
            result.append(["VIDEO", element])
        else:
            result.append(["IMAGE", element])
        return result

    # Функция проверки и исправления типа файлов
    def verificationandcorrection(self, path, endoffile):
        folder_path = Path(path)
        count = 0

        for file_path in folder_path.iterdir():
            if file_path.is_file():
                if str(file_path).endswith(endoffile):
                    pass
                else:
                    # Меняем расширение
                    new_path = file_path.with_suffix(endoffile)
                    file_path.rename(new_path)
                    count += 1

        print(f"Файлы в папке: {path} | обработаны {count} ")

    # Заполнение данных в базах данных
    def importdates(self):
        # Проверка картинок на повторы
        self.checkfolderforduplicate(self.imagesfolder)
        # Проверка видео на повторы
        self.checkfolderforduplicate(self.videosfolder)
        # Проверка и исправление на правильность типа файлов для видео
        self.verificationandcorrection(self.videosfolder, ".mp4")
        # Проверка и исправление на правильность типа файлов для картинок
        self.verificationandcorrection(self.imagesfolder, ".jpg")
        # Формирование правильно списка
        all_dates = self.merge_proportionally(self.imagesfolder, self.videosfolder)
        # Вставка данных в таблицу
        self.insertdatesintable(all_dates)