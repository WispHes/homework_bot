import logging
import os
import requests
import time
import telegram

from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    level=logging.DEBUG,
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


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    # Нужно отнять от времени для получения последней работы - 2229743
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if homework_statuses.status_code != 200:
        raise KeyError('Ошибка статус кода')
    else:
        logger.info('Запрос к эндпоинту API-сервиса прошел успешно')
        print(homework_statuses.json())
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
        if homework_status not in HOMEWORK_STATUSES:
            raise NegativeResponseStatus(
                logger.error(f'Несуществующий статус: {homework_status}')
            )
        else:
            logger.info('Найден корректный статус домашней работы')
        if homework_status is None:
            raise NegativeParsStatus(
                'Ошибка в значении homework_status: ', homework_status
            )
        if homework_name is None:
            raise NegativeParsStatus(
                'Ошибка в значении homework_name: ', homework_name
            )
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        raise KeyError('ошибка')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Работа рограммы приостановленна')
        raise SystemExit
    logger.info('Все токены доступны')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.info('Запущен телеграмм бот')
    current_timestamp = int(time.time())
    try_status = 'approved'
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks.get('status') != try_status:
                message = parse_status(homeworks)
                send_message(bot, message)
                logger.info('Работа еще не проверена')
            else:
                send_message(bot, HOMEWORK_STATUSES[try_status])
        except Exception as error:
            message = (
                f'Сбой в работе, требуется перезапустить программу: {error}'
            )
            if error:
                send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
