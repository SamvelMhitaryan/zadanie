from fastapi import APIRouter, Request, status
from exceptions import (
    NoContentTypeError,
    HTTPException,
    EmptyBodyError,
    ConvertError
)
from constants import supported_content_types, supported_content_types_str
from handlers import handle_body
from schemas import ValidatedResponse


router = APIRouter()


@router.post("/convert-body/", response_model=ValidatedResponse)
async def convert(request: Request):
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
    payload = await request.body()
    if not payload:
        raise EmptyBodyError
    try:
        converted_body = handle_body(payload, content_type)
    except ConvertError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    return converted_body
