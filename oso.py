from google.cloud import bigquery
import os
import pandas as pd


# replace with your project name
GCP_PROJECT = 'opensource-observer' 

# replace with your path to credentials
PATH_TO_CREDENTIALS = 'oso_gcp_credentials.json'


def fetch_data(query, data_path, connect_to_oso=False):
    
    filetype = 'parquet' if data_path.endswith('.parquet') else 'csv'
    
    if connect_to_oso:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH_TO_CREDENTIALS
        client = bigquery.Client(project=GCP_PROJECT)
        results = client.query(query)
        dataframe = results.to_dataframe()
        
        save_functions = {
            'parquet': lambda df, path: df.to_parquet(path),
            'csv': lambda df, path: df.to_csv(path, index=True)
        }
        save_functions[filetype](dataframe, data_path)
    else:
        read_functions = {
            'parquet': pd.read_parquet,
            'csv': lambda path: pd.read_csv(path, index_col=0)
        }
        dataframe = read_functions[filetype](data_path)
    
    return dataframe