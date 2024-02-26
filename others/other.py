import re


xml_first = """
<?xml version="1.0" encoding="UTF-8" ?>
<root><ДатаДокумента>15 сентября 2022 года

</ДатаДокумента><Продавец>Иванов Лев Давидович</Продавец><Продавец>Петрова Мария Васильевна</Продавец><Оплата><Сумма>10000,00 рублейundefined
</Сумма><Покупатель>ООО Управляющая компания «Арасака»undefined
</Покупатель>undefined
</Оплата><ПредметДоговора><ВидОбъектаНедвижимости>ЗемельныйУчастокundefined
</ВидОбъектаНедвижимости><ВидРазрешенногоИспользования>для сельскохозяйственного производстваundefined
</ВидРазрешенногоИспользования><КадастровыйНомер>1237:09234123532:4521undefined
</КадастровыйНомер><Площадь>5 гаundefined
</Площадь>undefined
</ПредметДоговора>undefined
</root>
"""

first = {
    "ДатаДокумента": "15 сентября 2022 года",
    "Продавец[0]": "Иванов Лев Давидович",
    "Продавец[1]": "Петрова Мария Васильевна",
    "Оплата": {
        "Сумма": "10000,00 рублей",
        "Покупатель": "ООО Управляющая компания «Арасака»"},
    "ПредметДоговора": {
        "ВидОбъектаНедвижимости": "ЗемельныйУчасток",
        "ВидРазрешенногоИспользования": "для сельскохозяйственного производства",
        "КадастровыйНомер": "1237:09234123532:4521",
        "Площадь": "5 га"
    }
}

second = {
    'Оплата': {
        'СрокОплаты': 'в течении 30 дней со дня подписания договора'},
    'ПредметДоговора': {
        'Адрес': 'Московская область, 5 км от ориентира Ракушки',
        'ОбъектыНаЗемельномУчастке': 'здание',
        'ОбъектыНаЗемельномУчастке': 'склад',
        'ОбременениеОбъектаНедвижимости': 'ипотека',
        'ОбъектПереданПокупателюДоДоговора': 'НЕТ'
    }
}


months = {
    "января": "01", "февраля": "02", "марта": "03",
    "апреля": "04", "мая": "05", "июня": "06",
    "июля": "07", "августа": "08", "сентября": "09",
    "октября": "10", "ноября": "11", "декабря": "12"
}


def normalize_date(date_str):
    for month in months:
        date_str = re.sub(r'\b{}\b'.format(month),
                          months[month], date_str, flags=re.IGNORECASE)
    match = re.search(r'(\d{1,2})[^\d]*(\d{1,2})[^\d]*(\d{4})', date_str)
    if match:
        day = match.group(1).zfill(2)
        month = match.group(2).zfill(2)
        year = match.group(3)
        return f"{day}.{month}.{year}"
    return None


def normalize_term(term):
    years = re.findall(r'\d+\s{0,1}год|\d+\s{0,1}лет', term)
    months = re.findall(r'\d+\s{0,1}месяц', term)
    weeks = re.findall(r'\d+\s{0,1}недел', term)
    days = re.findall(r'\d+\s{0,1}ден|\d+\s{0,1}дне', term)

    total_years = sum(int(re.search(r'\d+', year).group()) for year in years)
    total_months = sum(int(re.search(r'\d+', month).group())
                       for month in months)
    total_weeks = sum(int(re.search(r'\d+', week).group()) for week in weeks)
    total_days = sum(int(re.search(r'\d+', day).group()) for day in days)

    return f"{total_years}_{total_months}_{total_weeks}_{total_days}"


def dict_check(d, pattern_date, pattern_term=None):
    final = {}
    sellers = []
    for k, v in d.items():
        if isinstance(v, dict):
            v = dict_check(v, pattern_date, pattern_term)
        if isinstance(v, str):
            if re.match(pattern_date, v):
                v = normalize_date(v)
            elif re.match(pattern_term, v):
                v = normalize_term(v)
        if re.match(r'Продавец\[\d+\]', k):
            sellers.append(v)
        else:
            final[k] = v
    if sellers:
        final['Продавец'] = sellers
    if d[k] != 'ДатаДокумента' and 'Продавец' and 'Сумма' and 'Оплата':
        del d[k]
    return final


def merge_dict(dict1, dict2):
    for key, val in dict1.items():
        if type(val) == dict:
            if key in dict2 and type(dict2[key] == dict):
                merge_dict(dict1[key], dict2[key])
        else:
            if key in dict2:
                dict1[key] = dict2[key]

    for key, val in dict2.items():
        if not key in dict1:
            dict1[key] = val
    return dict1


pattern_date = r'''\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня
|июля|августа|сентября|октября|ноября|декабря)\s\d{4}\sгода\b'''
pattern_term = r'.*?\d+\s*(года|год|месяцев|месяц|недель|неделя|дней|день).*?'

first = dict_check(first, pattern_date, pattern_term)
second = dict_check(second, pattern_date, pattern_term)

dictik = merge_dict(first, second)
print(dictik)
