from pathlib import Path
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


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


def export_dataframe_to_csv(dataframe, filename):
    dataframe_to_csv_file(dataframe, filename + '.csv')
    data_written = file_has_content(filename + '.csv')
    if data_written:
        return True
    else:
        return False


def export_dataframe_to_html(dataframe, filename):
    dataframe_to_html_file(dataframe, filename + '.html')
    prettify_html(filename + '.html')
    data_written = file_has_content(filename + '.html')
    if data_written:
        return True
    else:
        return False


def export_dataframe_to_files(dataframe, filename):
    """Writes a dataframe to CSV and prettified HTML"""
    export_dataframe_to_csv(dataframe, filename)
    export_dataframe_to_html(dataframe, filename)


def file_has_content(path):
    return Path(path).stat().st_size > 0


def prettify_html(filename):
    content = Path("./" + filename).read_text()
    soup = BeautifulSoup(content, features='lxml')
    css = soup.new_tag('link')
    css['rel'] = 'stylesheet'
    css['href'] = './mvp.css'
    head = soup.new_tag('head')
    head.insert(1, css)
    html = soup.find('html')
    html.insert(1, head)
    with open(Path("./" + filename), 'w') as f:
        f.write(soup.prettify(formatter='html'))
