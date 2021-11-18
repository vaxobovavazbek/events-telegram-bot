import i18n

from bot import settings


def translate(text: str) -> str:
    return i18n.t(key=text, locale=settings.CURRENT_LOCALE)
