from constants import SupportedContentType, pattern_date, pattern_term
from converters import ConverterFasade
from normalizers import NormalizeFasade


def handle_body(
        body: bytes | dict,
        content_type: SupportedContentType
        ) -> dict[str, str] | None:
    converter = ConverterFasade(
        body=body,
        content_type=content_type,
    )
    data = converter.payload_body_to_dict()
    normalizer = NormalizeFasade(
        pattern_date=pattern_date,
        pattern_term=pattern_term,
    )
    normalized_data = normalizer.normalize_data(data=data)
    return normalized_data
