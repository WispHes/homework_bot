import logging
import os
import time
import sys
import json

import telegram
import requests

from dotenv import load_dotenv
from http import HTTPStatus
from exceptions import (
    NegativeResponseStatus,
    NegativeParsStatus,
    NegativeSendMessage,
    NegativStatusCode,
    NegativRequestException,
    NegitivJSONDecode,
    NegativTypeDict
)


load_dotenv()
logger = logging.getLogger(__name__)

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


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Отправлено сообщение: {message}')
    except telegram.error.TelegramError as error:
        raise NegativeSendMessage(
            'Произошла ошибка при отправке сообщения'
        ) from error


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise NegativStatusCode(
                'Запрос выполнен безуспешно: '
                f'статус ответа {homework_statuses.status_code}'
            )
        else:
            logger.info('Запрос к эндпоинту API-сервиса прошел успешно')
            return homework_statuses.json()
    except requests.exceptions.RequestException as error:
        raise NegativRequestException(
            f'Произошла ошибка при запросе к серверу: {error}'
        )
    except json.JSONDecodeError as error:
        raise NegitivJSONDecode(
            f'Произошел сбой декодирования JSON {error}'
        )


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True


def check_response(response):
    """Проверяет ответ API на корректность."""
    if type(response) is not dict:
        raise TypeError('Ответ не соответствует нужному формату')
    if 'homeworks' not in response:
        raise KeyError('На сервере нет домашней работы')
    homeworks = response.get('homeworks')
    if type(homeworks) is not list:
        raise TypeError('Нет домашних работ в списке')
    if homeworks == []:
        raise ValueError(
            'Получен пустой список в котором должна находиться домашняя работа'
        )
    return homeworks[0]


def parse_status(homework):
    """Проверка статуса."""
    if not isinstance(homework, dict):
        raise NegativTypeDict('Произошла ошибка в передаваемом типе функции.')
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


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(stream=sys.stdout)],
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    if not check_tokens():
        logger.critical('Работа рограммы приостановленна')
        sys.exit()
    logger.info('Все токены доступны')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.info('Запущен телеграмм бот')
    current_timestamp = int(time.time())
    while True:
        try:
            homeworks = check_response(get_api_answer(current_timestamp))
            message = parse_status(homeworks)
            send_message(bot, message)
        except NegativeSendMessage as error:
            logger.error(error)
        except Exception as error:
            message = (
                f'Сбой в работе, требуется исправить ошибку: {error}'
            )
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
