from fastapi import Body, FastAPI, HTTPException, Request, Response, status
from typing import Any, Literal, get_args, List
import xml.etree.ElementTree as ET
import re

app = FastAPI()

months = {
    "января": "01", "февраля": "02", "марта": "03",
    "апреля": "04", "мая": "05", "июня": "06",
    "июля": "07", "августа": "08", "сентября": "09",
    "октября": "10", "ноября": "11", "декабря": "12"
}

pattern_date = r'''\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня
|июля|августа|сентября|октября|ноября|декабря)\s\d{4}\sгода\b'''
pattern_term = r'.*?\d+\s*(года|год|месяцев|месяц|недель|неделя|дней|день).*?'


def normalize_date(date_str):  # исправляет дату, выдает дд.мм.гггг
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


def normalize_term(term):  # исправляет срок оплаты, выдает г_м_н_д
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


@app.post("/convert-body/")
def dict_check(d, pattern_date, pattern_term=None):
    # проверяет данные согласно паттернам (дата, срок оплаты, создает список продавцов)
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


def merge_dict(dict1, dict2):  # объединяет валидированные словари в один
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


# first = dict_check(request, pattern_date, pattern_term)
# second = dict_check(request, pattern_date, pattern_term)

# dictik = merge_dict(first, second)
# print(dictik)
