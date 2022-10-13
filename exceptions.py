class NegativeSendMessageError(Exception):
    """Ошибка при отправке сообщения."""


class NegativStatusCodeError(Exception):
    """Ошибка при ответе на запрос."""


class NotFoundDateError(KeyError):
    """Ошибка при получении даты из запроса."""
