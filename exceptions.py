class NegativeResponseStatus(Exception):
    """Ошибка в статусе домашней работы."""


class NegativeParsStatus(Exception):
    """Ошибка в полученном статусе."""


class NegativeSendMessage(Exception):
    """Ошибка при отправке сообщения."""


class NegativStatusCode(Exception):
    """Ошибка при ответе на запрос."""


class NegativRequestException(Exception):
    """Ошибка возникшая при запросе к серверу."""


class NegativTypeDict(KeyError):
    """Ошибка в передаваемом типе функции."""


class NegitivJSONDecode(Exception):
    """Cбой декодирования JSON."""
