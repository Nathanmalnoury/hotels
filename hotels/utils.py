import pandas as pd


def save_as_excel(list_of_hotels, path_to_file):
    list_of_dicts = [hotel.__dict__ for hotel in list_of_hotels]
    df = pd.DataFrame(list_of_dicts)
    df.to_excel(path_to_file)
