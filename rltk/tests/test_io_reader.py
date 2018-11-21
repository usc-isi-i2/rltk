import pandas as pd
import csv
import json
import io

from rltk.io.reader import *


arr = [{'1': 'A', '2': 'B'}, {'1': 'a', '2': 'b'}]


def test_array_reader():
    for idx, obj in enumerate(ArrayReader(arr)):
        assert obj == arr[idx]


def test_dataframe_reader():
    df = pd.DataFrame(arr)
    for idx, obj in enumerate(DataFrameReader(df)):
        assert obj == arr[idx]


def test_csv_reader():
    f = io.StringIO()

    writer = csv.DictWriter(f, fieldnames=['1', '2'])
    writer.writeheader()
    for a in arr:
        writer.writerow(a)

    for idx, obj in enumerate(CSVReader(f)):
        assert obj == arr[idx]

    f.close()


def test_jsonlines_reader():
    f = io.StringIO()

    for a in arr:
        f.write(json.dumps(a) + '\n')

    for idx, obj in enumerate(JsonLinesReader(f)):
        assert obj == arr[idx]

    f.close()
