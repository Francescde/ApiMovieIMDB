import gzip
from io import BytesIO

import pandas as pd
import requests


class DataSource:
    def __init__(self, source, downloadable):
        self.source = source
        self.downloadable = downloadable

    def download_and_extract(self):
        response = requests.get(self.source)
        with gzip.GzipFile(fileobj=BytesIO(response.content), mode='rb') as file:
            content = file.read()
        return content

    def download_df(self):
        content = self.download_and_extract()
        return pd.read_csv(BytesIO(content), sep='\t')

    def read(self):
        if self.downloadable:
            return self.download_df()
        return pd.read_csv(self.source, sep='\t')
