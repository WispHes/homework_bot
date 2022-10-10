class NegativeResponseStatusError(Exception):
    """Ошибка в статусе домашней работы."""


class NegativeSendMessageError(Exception):
    """Ошибка при отправке сообщения."""


class NegativStatusCodeError(Exception):
    """Ошибка при ответе на запрос."""
