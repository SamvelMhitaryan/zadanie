from typing import Literal, get_args


months = {
    "января": "01", "февраля": "02", "марта": "03",
    "апреля": "04", "мая": "05", "июня": "06",
    "июля": "07", "августа": "08", "сентября": "09",
    "октября": "10", "ноября": "11", "декабря": "12"
}

SupportedContentType = Literal['application/json', 'application/xml']
supported_content_types: set[SupportedContentType] = set(
    get_args(SupportedContentType))
supported_content_types_str = ', '.join(supported_content_types)


pattern_date = r'''\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня
|июля|августа|сентября|октября|ноября|декабря)\s\d{4}\sгода\b'''
pattern_term = r'.*?\d+\s*(года|год|месяцев|месяц|недель|неделя|дней|день).*?'
