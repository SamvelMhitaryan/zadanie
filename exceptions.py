from fastapi import status, HTTPException
from constants import supported_content_types_str


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


class ConvertError(BaseException):
    """Convertation error has been arise."""
