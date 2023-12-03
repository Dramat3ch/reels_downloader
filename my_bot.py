import telebot
from instaloader import Instaloader, Post
import os
import glob
import shutil
from queue import Queue
from threading import Thread
from telebot import types
from config import TOKEN

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Создаем экземпляр Instaloader
loader = Instaloader()

# Очередь для обработки запросов
queue = Queue()

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    # Проверяем, является ли сообщение текстом ссылкой на Instagram Reel
    if 'instagram.com/reel/' in message.text:
        # Сохраняем оригинальное сообщение пользователя
        original_message = message
        # Отправляем сообщение о постановке в очередь
        processing_message = bot.reply_to(message, "Please wait...\n\nПожалуйста, подождите...")
        # Помещаем оригинальное сообщение и сообщение об обработке в очередь
        queue.put((original_message, processing_message))
    elif message.chat.type == 'private':
        bot.reply_to(message, "Please send me the Instagram Reel link.\n\nПожалуйста, отправьте мне ссылку на Instagram Reel.")

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
                # Загружаем реел по короткому коду
                download_instagram_reel(shortcode)

                # Отправляем файл формата mp4 из временной папки 'temp'
                send_mp4(original_message.chat.id, original_message.message_id)

                # Удаляем сообщение об обработке
                bot.delete_message(processing_message.chat.id, processing_message.message_id)
        except Exception as e:
            print(f"Error processing message: {e}")
        finally:
            # Уведомляем, что обработка завершена
            queue.task_done()

# Запускаем фоновый поток для обработки очереди
queue_thread = Thread(target=process_queue)
queue_thread.daemon = True
queue_thread.start()

# Скачивание видео с Instagram Reel
def download_instagram_reel(shortcode):
    try:
        # Создаем уникальную временную папку для каждого видео
        video_folder = os.path.join('temp')
        os.makedirs(video_folder, exist_ok=True)

        # Загружаем реел по короткому коду
        post = Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=video_folder)
    except Exception as e:
        print(f"Error: {e}")

# Отправка любого файла формата mp4 из временной папки 'temp'
def send_mp4(chat_id, original_message_id):
    try:
        # Получаем список файлов в папке 'temp' с расширением mp4
        mp4_files = glob.glob(os.path.join('temp', '*.mp4'))

        if mp4_files:
            # Отправляем любой файл mp4
            with open(mp4_files[0], 'rb') as video_file:
                bot.send_video(chat_id, video_file, reply_to_message_id=original_message_id)
            shutil.rmtree('temp')
        else:
            bot.send_message(chat_id, "Временная папка 'temp' пуста.")
    except Exception as e:
        print(f"Error: {e}")

# Запускаем бота
if __name__ == "__main__":
    bot.polling(none_stop=True)