import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def display_value(tuple):
    return (round(tuple[0], 2), round(tuple[1], 2))

if __name__ == '__main__':
    # Use panda to load the csv files from the data folder into a dataframe
    mirantis_df = pd.read_csv('data/IST_MIR.csv')
    mozilla_df = pd.read_csv('data/IST_MOZ.csv')
    ost_df = pd.read_csv('data/IST_OST.csv')
    wik_df = pd.read_csv('data/IST_WIK.csv')

    datasets = {
        'Mirantis': mirantis_df,
        'Mozilla': mozilla_df,
        'OpenStack': ost_df,
        'Wikimedia': wik_df
    }

    property_cols = range(2, 14)
    property_cols_names = sorted(mirantis_df.columns[property_cols])
    print(property_cols_names)

    table_6 = pd.DataFrame(columns=datasets.keys(), index=property_cols_names)
    # For each row in the dataframe, store the mean and the maximum for each column in the table_6 dataframe
    for row in table_6.index:
        for name, df in datasets.items():
            table_6.loc[row, name] = df.loc[:, row].mean(), df.loc[:, row].max()

    display_table_6 = table_6.copy()
    display_table_6 = display_table_6.applymap(lambda value: display_value(value))
    print(display_table_6)






