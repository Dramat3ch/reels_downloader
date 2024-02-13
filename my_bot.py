import os
import time
import glob
import shutil
import random
import string
import datetime
from queue import Queue
from threading import Thread

import telebot
from instaloader import Instaloader, Post
from telebot import types
from config import TOKEN

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Создаем экземпляр Instaloader
loader = Instaloader(download_pictures=False, save_metadata=False, post_metadata_txt_pattern='')

# Очередь для обработки запросов
queue = Queue()


# Функция для генерации случайного имени файла
def generate_random_filename():
    random_filename = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{random_filename}_UTC.mp4"


# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    # Проверяем, является ли сообщение текстом ссылкой на Instagram Reel
    if 'instagram.com/reel/' in message.text:
        # Сохраняем оригинальное сообщение пользователя
        original_message = message
        # Отправляем сообщение о постановке в очередь
        processing_message = bot.reply_to(message, "<b><i>Please wait...</i></b>", parse_mode='HTML')
        # Помещаем оригинальное сообщение и сообщение об обработке в очередь
        queue.put((original_message, processing_message))
    elif message.chat.type == 'private':
        bot.reply_to(message, "Please send me the Instagram Reel URL.")


# Функция для обработки очереди
def process_queue():
    while True:
        original_message, processing_message = queue.get()
        try:
            # Проверяем, является ли сообщение ссылкой на Instagram Reel
            if 'instagram.com/reel/' in original_message.text:
                # Получаем короткий код из ссылки
                shortcode = original_message.text.split('/')[-2]
                print("Shortcode:", shortcode)
                # Загружаем рил по короткому коду
                file_name = download_instagram_reel(shortcode)

                # Отправляем файл формата mp4 из временной папки 'temp'
                send_mp4(original_message.chat.id, original_message.message_id, file_name)

                # Удаляем сообщение об обработке
                bot.delete_message(processing_message.chat.id, processing_message.message_id)
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            # Уведомляем, что обработка завершена
            queue.task_done()
        time.sleep(1)


# Запускаем фоновый поток для обработки очереди
queue_thread = Thread(target=process_queue)
queue_thread.daemon = True
queue_thread.start()


# Скачивание видео с Instagram Reel
def download_instagram_reel(shortcode):
    try:
        # Создаем временную папку для видео
        video_folder = os.path.join('temp')
        os.makedirs(video_folder, exist_ok=True)

        # Загружаем рил по короткому коду
        post = Post.from_shortcode(loader.context, shortcode)
        file_name = generate_random_filename()
        loader.download_post(post, target=video_folder)

        # Получаем список загруженных файлов
        files = glob.glob(os.path.join(video_folder, '*'))
        for file_path in files:
            # Изменяем имя файла на случайное
            new_file_path = os.path.join(video_folder, file_name)
            os.rename(file_path, new_file_path)
            break  # Выходим после первой итерации, так как здесь должен быть только один файл
        return file_name
    except Exception as e:
        print(f"Error: {e}")


# Отправка файла формата mp4 из временной папки 'temp'
def send_mp4(chat_id, original_message_id, file_name):
    try:
        file_path = os.path.join('temp', file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as video_file:
                bot.send_video(chat_id, video_file, reply_to_message_id=original_message_id)
            # Удаляем файл после отправки
            os.remove(file_path)
    except Exception as e:
        print(f"Error: {e}")


# Запускаем бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
