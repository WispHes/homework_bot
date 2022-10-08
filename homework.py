import logging
import os
import time
import sys

import telegram
import requests

from dotenv import load_dotenv
from http import HTTPStatus


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class NegativeResponseStatus(Exception):
    """Ошибка в статусе домашней работы."""


class NegativeResponseStatusCode(Exception):
    """Ошибка в статусе кода."""


class NegativeResponseAPI(Exception):
    """Ошибка в API запросе."""


class NegativeResponseDict(Exception):
    """Ошибка в словаре полученного из запроса."""


class NegativeParsStatus(Exception):
    """Ошибка в полученном статусе."""


class NegativeSendMessage(Exception):
    """Ошибка при отправке сообщения."""


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError:
        raise NegativeSendMessage


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if homework_statuses.status_code != HTTPStatus.OK:
        raise KeyError('Ошибка статус кода')
    else:
        logger.info('Запрос к эндпоинту API-сервиса прошел успешно')
        return homework_statuses.json()


def check_tokens():
    """Проверяет доступность переменных окружения."""
    error_message = 'Отсутствует переменная окружения'
    token = True
    if PRACTICUM_TOKEN is None:
        token = False
        logger.error(f'{error_message} PRACTICUM_TOKEN')
    if TELEGRAM_TOKEN is None:
        token = False
        logger.error(f'{error_message} TELEGRAM_TOKEN')
    if TELEGRAM_CHAT_ID is None:
        token = False
        logger.error(f'{error_message} TELEGRAM_CHAT_ID')
    return token


def check_response(response):
    """Проверяет ответ API на корректность."""
    if response is None:
        logger.error('В ответе API произошла ошибка')
        raise NegativeResponseDict(
            logger.error('Произошла ошибка в полученном словаре из запроса')
        )
    elif response == []:
        return {}
    else:
        logger.info('Корректный API ответ')
        return response['homeworks'][0]


def parse_status(homework):
    """Проверка статуса."""
    if isinstance(homework, dict):
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
        if homework_status not in HOMEWORK_VERDICT:
            raise NegativeResponseStatus(
                logger.error(f'Несуществующий статус: {homework_status}')
            )
        else:
            logger.info('Найден корректный статус домашней работы')
        if homework_name is None:
            raise NegativeParsStatus(
                'Ошибка в значении homework_name: ', homework_name
            )
        verdict = HOMEWORK_VERDICT[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        raise KeyError('ошибка')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Работа рограммы приостановленна')
        sys.exit()
    logger.info('Все токены доступны')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.info('Запущен телеграмм бот')
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks.get('status') != 'approved':
                message = parse_status(homeworks)
                send_message(bot, message)
                logger.info(f'Отправлено сообщение: {message}')
            else:
                message = HOMEWORK_VERDICT[homeworks.get('status')]
                send_message(bot, message)
                logger.info(f'Отправлено сообщение: {message}')
        except NegativeSendMessage:
            logger.error('Сообщение не было отправелно')
        except Exception as error:
            message = (
                f'Сбой в работе, требуется перезапустить программу: {error}'
            )
            if error:
                send_message(bot, message)
                logging.error(f'Ошибка при отправке сообщения: {error}')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
