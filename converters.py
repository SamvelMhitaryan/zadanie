import json
from typing import Self
import xmltodict


class ConverterFasade:
    def __init__(
            self: Self,
            body: bytes | dict,
            content_type: str,
            ) -> None:
        self.body = body
        self.content_type = content_type

    def json_to_dict(
            self: Self,
            ) -> dict | None:
        try:
            json_data: dict = json.loads(self.body)
            return json_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def xml_to_dict(
            self: Self,
            ) -> dict | None:
        try:
            xml_data = xmltodict.parse(self.body)
            return xml_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def payload_body_to_dict(
            self: Self,
            ) -> dict[str, str]:
        if isinstance(self.body, dict):
            return self.body
        if self.content_type == 'application/xml':
            data = self.xml_to_dict()
            return data
        else:
            data = self.json_to_dict()
            return data
