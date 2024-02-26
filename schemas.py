from pydantic import BaseModel, Field


class Payment(BaseModel):
    amount: str = Field(alias='Сумма')
    buyer: str = Field(alias='Покупатель')


class DocumentSubject(BaseModel):
    type_immovables_objects: str = Field(alias='ВидОбъектаНедвижимости')
    permitted_use_type: str = Field(alias='ВидРазрешенногоИспользования')
    cadastral_number: str = Field(alias='КадастровыйНомер')
    area: str = Field(alias='Площадь')


class ValidatedResponse(BaseModel):
    document_date: str = Field(alias='ДатаДокумента')
    payment: Payment = Field(alias='Оплата')
    document_subject: DocumentSubject = Field(alias='ПредметДоговора')
    salesman: list[str] = Field(alias='Продавец')
