import re
from constants import months
from typing import Self


class NormalizeFasade:
    def __init__(
            self: Self,
            pattern_term,
            pattern_date
            ) -> None:
        self.pattern_term = pattern_term
        self.pattern_date = pattern_date

    def normalize_date(self, date_str):
        """Исправляет дату, выдает дд.мм.гггг."""
        for month in months:
            date_str = re.sub(
                r'\b{}\b'.format(month),
                months[month],
                date_str,
                flags=re.IGNORECASE
            )
        match = re.search(r'(\d{1,2})[^\d]*(\d{1,2})[^\d]*(\d{4})', date_str)
        if match:
            day = match.group(1).zfill(2)
            month = match.group(2).zfill(2)
            year = match.group(3)
            return f"{day}.{month}.{year}"
        return None

    def normalize_term(self, term_str):
        # исправляет срок оплаты, выдает г_м_н_д
        years = re.findall(r'\d+\s{0,1}год|\d+\s{0,1}лет', term_str)
        months = re.findall(r'\d+\s{0,1}месяц', term_str)
        weeks = re.findall(r'\d+\s{0,1}недел', term_str)
        days = re.findall(r'\d+\s{0,1}ден|\d+\s{0,1}дне', term_str)

        total_years = sum(
            int(
                re.search(r'\d+', year).group()
                ) for year in years
            )
        total_months = sum(
            int(
                re.search(r'\d+', month).group()
                ) for month in months
            )
        total_weeks = sum(
            int(
                re.search(r'\d+', week).group()
                ) for week in weeks
            )
        total_days = sum(
            int(
                re.search(r'\d+', day).group()
                ) for day in days
            )

        return f"{total_years}_{total_months}_{total_weeks}_{total_days}"

    def normalize_data(self: Self, data: dict) -> dict:
        # проверяет данные согласно паттернам (дата, срок оплаты, создает список продавцов)
        final = {}
        sellers = []
        for key, value in data.items():
            if isinstance(value, dict):
                value = self.normalize_data(data=value)
            if isinstance(value, str):
                if re.match(self.pattern_date, value):
                    value = self.normalize_date(date_str=value)
                elif re.match(self.pattern_term, value):
                    value = self.normalize_term(term_str=value)
            if re.match(r'Продавец\[\d+\]', key):
                sellers.append(value)
            else:
                final[key] = value
        if sellers:
            final['Продавец'] = sellers
        if data[key] != 'ДатаДокумента' and 'Продавец' and 'Сумма' and 'Оплата':
            del data[key]
        return final
