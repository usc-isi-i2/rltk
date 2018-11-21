import pandas as pd

from rltk.io.reader import Reader


class DataFrameReader(Reader):
    """
    Pandas DataFrame Reader.
    
    Args:
        df (pandas.DataFrame): DataFrame.
    """

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def __next__(self):
        for _, item in self._df.iterrows():
            yield item.to_dict()
