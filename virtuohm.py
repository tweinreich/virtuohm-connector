def interpret_current_grades(dataframe):
    dataframe['Note'] = dataframe['Note'].apply(lambda x: float(x) / 10.0 if '?' not in x else x)
    return dataframe['Note']
