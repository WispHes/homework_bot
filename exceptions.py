class NegativeResponseStatusError(Exception):
    """Ошибка в статусе домашней работы."""


class NegativeParsStatusError(Exception):
    """Ошибка в полученном статусе."""


class NegativeSendMessageError(Exception):
    """Ошибка при отправке сообщения."""


class NegativStatusCodeError(Exception):
    """Ошибка при ответе на запрос."""


class NegativRequestExceptionError(Exception):
    """Ошибка возникшая при запросе к серверу."""


class NegativTypeDictError(KeyError):
    """Ошибка в передаваемом типе функции."""


class NegitivJSONDecodeError(Exception):
    """Cбой декодирования JSON."""
