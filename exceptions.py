class NoForSendingInTelegramError(Exception):
    """Общий баззоый класс не для отправки в телеграм."""


class NegativeSendMessageError(NoForSendingInTelegramError):
    """Ошибка при отправке сообщения."""


class NegativStatusCodeError(Exception):
    """Ошибка при ответе на запрос."""


class NotFoundDateError(NoForSendingInTelegramError):
    """Ошибка при получении даты из запроса."""
