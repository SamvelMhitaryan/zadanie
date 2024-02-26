from fastapi import Body, FastAPI, HTTPException, Request, Response, status
from typing import Any, Literal, get_args, List
from datetime import datetime
import re


class ConvertError(Exception):
    pass


app = FastAPI()
SupportedContentType = Literal['application/json', 'application/xml']
supported_content_types: set[SupportedContentType] = set(get_args(SupportedContentType))
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


def normalize_date(date_str: str) -> str:
    for fmt in ("%d %B %Y", "%d.%m.%Y", "%d %b %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return date_str

def normalize_term(term_str: str) -> str:
    years, months, weeks, days = 0, 0, 0, 0
    patterns = {
        "год": (r"\b(\d+)\s*(?:года?|лет)\b", lambda x: (int(x), 0, 0, 0)),
        "месяц": (r"\b(\d+)\s*месяц[а-я]*\b", lambda x: (0, int(x), 0, 0)),
        "неделя": (r"\b(\d+)\s*недел[иь]\b", lambda x: (0, 0, int(x), 0)),
        "день": (r"\b(\d+)\s*дн[яей]\b", lambda x: (0, 0, 0, int(x))),
    }
    
    for unit, (pattern, converter) in patterns.items():
        match = re.search(pattern, term_str)
        if match:
            y, m, w, d = converter(match.group(1))
            years += y
            months += m
            weeks += w
            days += d
    
    return f"{years}_{months}_{weeks}_{days}"

import json
import xmltodict

def handle_json_body(body: bytes) -> str:
    data = json.loads(body.decode("utf-8"))
    normalized_data = normalize_date(data)
    return json.dumps(normalized_data, ensure_ascii=False)

def handle_xml_body(body: bytes) -> str:
    data = xmltodict.parse(body.decode("utf-8"))
    normalized_data = normalize_date(data)
    xml_string = xmltodict.unparse(normalized_data, pretty=True)
    return xml_string


def handle_body(body: bytes, content_type: SupportedContentType):
    if content_type == 'application/xml':
        return handle_xml_body(body)
    return handle_json_body(body)


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
    body = await request.body()
    if not body:
        raise EmptyBodyError
    try:
        converted_body = handle_body(body, content_type)
    except ConvertError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    return Response(
        content=converted_body,
        media_type=content_type,
        headers={'Content-Type': content_type},
    )