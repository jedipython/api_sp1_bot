import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    """В зависимости от статуса проверки домашней рабтоы, отправляет нужное сообщение."""
    homework_name = homework.get('homework_name')
    if homework.get('status') != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, \
             можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """Получает статус проверки домашней работы через API."""
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, params=params, headers=headers)
    return homework_statuses.json()


def send_message(message):
    """Отправляет сообщение в телеграм."""
    proxy = telegram.utils.request.Request(
        proxy_url='https://103.125.253.251:8080')
    bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    """Основная функция, вызывает все функции и выполняет скрипт."""
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')
            time.sleep(600)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
