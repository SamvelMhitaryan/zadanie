from fastapi import Body, FastAPI, HTTPException, Request, Response, status
from typing import Any, Literal, get_args, List
import xml.etree.ElementTree as ET
import json
import re

from other import first, second, months


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


app = FastAPI()
SupportedContentType = Literal['application/json', 'application/xml']
supported_content_types: set[SupportedContentType] = set(
    get_args(SupportedContentType))
supported_content_types_str = ', '.join(supported_content_types)


NoContentTypeError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=(
        f'No Accept header was found in headers. Pass one of the supported: '
        f'{supported_content_types_str}'
    ),
)
EmptyBodyError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Body must not be empty.',
)


class ConvertError(Exception):
    pass


def convert_json_to_dict(body: bytes) -> str | None:
    try:
        json_data = json.loads(body)
        return json_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def convert_xml_to_dict(body: bytes) -> str | None:
    try:
        root = ET.Element("data")
        xml_to_dict(body, root)
        xml_data = ET.tostring(root, encoding="unicode")
        return xml_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def xml_to_dict(data, parent) -> dict[str, str]:
    data_dict = json.loads(data)
    for key, value in data.items():
        if isinstance(value, dict):
            child = ET.Element(key)
            parent.append(child)
            xml_to_dict(value, child)
        else:
            child = ET.Element(key)
            child.text = str(value)
            parent.append(child)


def handle_body(body: bytes, content_type: SupportedContentType) -> dict[str, str] | None:
    if content_type == 'application/xml':
        data = convert_xml_to_dict(body)
        return data
    else:
        data = convert_json_to_dict(body)
        return data


@app.post("/convert-body/")
async def convert(request: Request, payload: Any = Body(...)):
    content_type = request.headers.get('Accept')
    if not content_type:
        raise NoContentTypeError
    if content_type not in supported_content_types:
        msg = (
            f'Accept header {content_type} not supported. '
            f'Use one of the following: {supported_content_types_str}'
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )
    if not payload:
        raise EmptyBodyError
    try:
        converted_body = handle_body(payload, content_type)
    except ConvertError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    if converted_body is None:
        raise ConvertError('An error occurred while parsing data')

    nd = normalize_date(converted_body)
    nt = normalize_term(nd)
    dc = dict_check(nt, pattern_date, pattern_term)

    return Response(
        content=dc,
        media_type='application/json',
        headers={'Content-Type': 'application/json'},
    )


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


pattern_date = r'''\b\d{1,2}\s(января|февраля|марта|апреля|мая|июня
|июля|августа|сентября|октября|ноября|декабря)\s\d{4}\sгода\b'''
pattern_term = r'.*?\d+\s*(года|год|месяцев|месяц|недель|неделя|дней|день).*?'

first = dict_check(first, pattern_date, pattern_term)
second = dict_check(second, pattern_date, pattern_term)

dictik = merge_dict(first, second)
print(dictik)
