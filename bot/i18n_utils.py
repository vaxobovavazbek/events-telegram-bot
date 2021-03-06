import i18n

from bot import settings


def translate(text: str, **kwargs) -> str:
    return i18n.t(key=text, locale=settings.CURRENT_LOCALE, **kwargs)


def set_locale(locale):
    settings.CURRENT_LOCALE = locale
