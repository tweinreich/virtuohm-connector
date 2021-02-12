from pathlib import Path
import pandas as pd
import numpy as np


def dataframe_to_gui_table(dataframe):
    """Transforms a pandas dataframe into an array that can be used by Dear PyGUI"""
    index = dataframe.index
    rows = len(index)
    cols = len(dataframe.columns)
    tabledata = []
    for i in range(0, rows):
        row = []
        for j in range(0, cols):
            row.append(dataframe.iat[i, j])
        tabledata.append(row)
    return tabledata


def dataframe_to_html_file(dataframe, filename):
    dataframe.to_html(Path("./" + filename))


def table_to_dataframe(table):
    return pd.read_html(str(table))[0]


def remove_nan(dataframe):
    return dataframe.replace(to_replace=np.NaN, value='', regex=True)


def dataframe_to_csv_file(dataframe, filename):
    path = Path("./" + filename)
    print('File saved to path: ')
    print(path.absolute())
    dataframe.to_csv(path, index=True)
