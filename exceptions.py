class AllBaseError(Exception):
    """Общий баззоый класс для кастомных ошибок."""


class NegativeSendMessageError(AllBaseError):
    """Ошибка при отправке сообщения."""


class NegativStatusCodeError(Exception):
    """Ошибка при ответе на запрос."""


class NotFoundDateError(AllBaseError):
    """Ошибка при получении даты из запроса."""
