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
        for i, item in self._df.iterrows():
            yield dict(item.to_dict(), dataframe_default_index=i)
