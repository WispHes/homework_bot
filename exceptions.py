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


class NegativStatusCode(Exception):
    """Ошибка при ответе на запрос."""


class NegativRequestException(Exception):
    """Ошибка возникшая при запросе к серверу."""
