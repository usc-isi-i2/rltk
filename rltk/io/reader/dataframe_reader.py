import pandas as pd

from rltk.io.reader import Reader


class DataFrameReader(Reader):
    """
    Pandas DataFrame Reader.
    
    Args:
        df (pandas.DataFrame): DataFrame.
        keep_dataframe_default_index (bool): add a key "dataframe_default_index" holding the original index in df

    """

    def __init__(self, df: pd.DataFrame, keep_dataframe_default_index: bool=False):
        self._df = df
        self._keep_dataframe_default_index = keep_dataframe_default_index

    def __next__(self):
        if self._keep_dataframe_default_index:
            for i, item in self._df.iterrows():
                yield dict(item.to_dict(), dataframe_default_index=i)
        else:
            for _, item in self._df.iterrows():
                yield item.to_dict()