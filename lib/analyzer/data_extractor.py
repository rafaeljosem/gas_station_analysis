import re
from datetime import datetime
from typing import Callable

import pandas as pd
from dateutil.parser import ParserError, parse


class DataExtractor:
    """
    Esta clase tiene como propósito extraer los datos del
    json devuelto por el servicio de Azure.
    """

    page_num = None
    key_value_pairs: list[dict] = []
    tables: list[dict] = []
    paragraphs: list[dict] = []

    def __init__(self, data: dict) -> None:

        self.key_value_pairs = data['key_value_pairs'] \
            if 'key_value_pairs' in data.keys() else []

        self.tables = data['tables'] if 'tables' in data.keys() else []

        self.paragraphs = data['paragraphs'] \
            if 'paragraphs' in data.keys() else []

    def __filter_by_content_fn(self, page_num: int, keyword: str) -> Callable:

        return lambda item: re.search(
            keyword, item['key']['content'].lower()) is not None \
            and item['key']['bounding_regions'][0]['page_number'] == page_num

    def __filter_table(self, page_number: int) -> dict | None:
        results = list(filter(
            lambda table:
            table['bounding_regions'][0]['page_number'] == page_number,
            self.tables))

        if len(results) == 0:
            return None

        return results[0]

    def __extract_headers(self, cells: list[dict]) -> list[str]:
        filtered_cells = list(
            filter(lambda item:
                   'kind' in item and item['kind'] == 'columnHeader', cells))
        headers = []

        for header in filtered_cells:
            # No nos interesan las columnas combinadas
            if 'column_span' in header and header['column_span'] >= 2:
                continue

            headers.insert(header['column_index'], header['content'])

        return headers

    def __extract_rows(self, cells: list[dict], column_count: int) \
            -> list[str | float | int]:

        filtered_cells = list(
            filter(lambda item:
                   'kind' in item and item['kind'] == 'content', cells))
        rows = []
        row = []

        for index, cell in enumerate(filtered_cells):

            if index > 0 and (index % column_count) == 0:

                rows.append(row)
                row = []

            row.insert(cell['column_index'], cell['content'])

        return rows

    def extract_client_name(self, page_number: int) -> str:

        results = list(filter(self.__filter_by_content_fn(
            page_number, r"cliente[\s|\/\\n]+client"), self.key_value_pairs))

        if len(results) == 0:
            return ''

        return results[0]['value']['content']

    def extract_test_date(self, page_number: int) -> datetime | str:

        results = list(filter(
            self.__filter_by_content_fn(
                page_number, r"date-time"), self.key_value_pairs))

        if len(results) == 0:
            return ''

        date = re.match(
            r"(\d{1,2}/\d{1,2}/\d{4}\s\d{1,2}:\d{2}(?:\s[ap]\.m)?)",
            results[0]['value']['content'])[0]

        try:
            return parse(date)
        except ParserError:
            return parse(re.sub(r'p\.m|a\.m', '', date))

    def extract_product_name(self, page_number: int) -> str:

        results = list(filter(self.__filter_by_content_fn(
            page_number, 'producto'), self.key_value_pairs))

        if len(results) == 0:
            return ''

        return results[0]['value']['content']

    def extract_table(self, page_num: int) -> pd.DataFrame:

        table_items = self.__filter_table(page_num)
        if table_items is None:
            return pd.DataFrame

        headers = self.__extract_headers(table_items['cells'])
        values = self.__extract_rows(
            table_items['cells'], len(headers))

        df = pd.DataFrame(values, columns=headers)

        return df.assign(
            CLIENTE=self.extract_client_name(page_num),
            PRODUCTO=self.extract_product_name(page_num),
            FECHA=self.extract_test_date(page_num))

    def extract_tables(self) -> pd.DataFrame:

        df = pd.DataFrame()

        for table in self.tables:
            df1 = self.extract_table(
                table['bounding_regions'][0]['page_number'])
            df1['NUM PAGINA'] = table['bounding_regions'][0]['page_number']
            df = pd.concat([df, df1], ignore_index=True)

        return df

    def extract_address(self) -> str | None:
        pattern = r'(?:E/S\s+)(.*)'
        # pattern = r'(?:Fecha\s+de\s+Inspección:.*?\n)(?:E/S\s+)?(.*?)(?=\s*\
        #     (?:VISTA|MEDICIÓN|PROCESO|COMPARACIÓN|Precios|\*recios|\n\n|\Z))'

        for paragraph in self.paragraphs:
            match = re.search(pattern, paragraph['content'], re.DOTALL)

            if match:
                return ' '.join(match.group(1).split())

        return None
