import pandas as pd
from transformer import geo_transformer


if __name__ == '__main__':
    address_list = pd.read_csv('example_address.csv')['Address'].values
    geo_transformer(address_list)