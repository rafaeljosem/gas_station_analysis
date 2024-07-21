import json
import os
import traceback
from io import BufferedReader
from pathlib import Path
from typing import Generator

import pandas as pd
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
from tqdm import tqdm

from lib.analyzer.data_extractor import DataExtractor


class DocumentAnalyzer:
    """
    Esta clase se encarga de leer cada uno de los archivos
    en el directorio especificado y enviarlos al servicio de
    Azure
    """

    document_analysis_client: DocumentAnalysisClient | None = None
    processed_files: list[str] = []
    errors: list[dict[str, str | BaseException]] = []

    def __init__(self) -> None:

        load_dotenv(override=True)
        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        self.document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

    def __file_reader(self, dirname: str) \
            -> Generator[BufferedReader, None, None]:

        for name in tqdm(
                os.listdir(dirname), unit='file', desc='Files processed: '):
            with open(os.path.join(dirname, name), "rb") as f:
                yield f

    def __get_analysis(self, file: BufferedReader) -> dict[str, str]:

        poller = self.document_analysis_client.begin_analyze_document(
            "prebuilt-document", document=file
        )
        return poller.result().to_dict()

    def __write_results(self, filename: str,
                        results: dict[str, str],
                        output_dir: str, log_dir='./var') -> None:

        with open(
                os.path.join(output_dir, filename + '.json'),
                'w', encoding='utf8') as json_file, \
                open(
                    os.path.join(log_dir, 'checkpoint.txt'),
                    'w', encoding='utf8') as log_file:

            json_file.write(json.dumps(results))
            log_file.write(json.dumps(self.processed_files))

    def analyze_and_extract_tables(
            self, input_dir: str,
            output_dir: str, log_dir='./var') -> pd.DataFrame:
        '''
        Analyzes the documents and extract the tables in them.
        '''

        df = pd.DataFrame()
        results = self.analyze(input_dir, output_dir, log_dir)

        for result in results:
            extractor = DataExtractor(result['result'])
            extracted_df = extractor.extract_tables() \
                .assign(ARCHIVO=result['file_name'])

            df = pd.concat([df, extracted_df], ignore_index=True)

        return df

    def analyze(self, input_dir: str, output_dir: str, log_dir='./var') \
            -> list[dict]:
        '''
        This method analyzes the document and writes to the output dir the
        obtained json response
        '''

        # df = pd.DataFrame()
        self.processed_files = []
        self.errors = []
        # i = 1

        for file in self.__file_reader(input_dir):

            filename = Path(output_dir, file.name).stem

            try:
                result = self.__get_analysis(file)

                # extractor = DataExtractor(result)
                # extracted_df = extractor.extract_tables() \
                #     .assign(ARCHIVO=filename + '.pdf')

                # df = pd.concat([df, extracted_df], ignore_index=True)

                self.processed_files.append(
                    {'file_name': filename + '.pdf', 'result': result})

            except (HttpResponseError, Exception) as e:
                error = {
                    'file': file.name,
                    'error': str(e),
                    'traceback': traceback.extract_tb(e.__traceback__).format()
                }

                if e is HttpResponseError:
                    error['comment'] = 'Archivo no procesado'
                    result = None

                self.errors.append(error)

            finally:
                if result is not None:
                    self.__write_results(filename, result, output_dir, log_dir)

            # if i % 5 == 0:
            #     break
            # i += 1

        return self.processed_files
