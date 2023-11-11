import argparse
import pandas
import numpy as np
import re
import os
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import ClockTimeOptions

# we want:
# 1. path to the dataset (assume csv)
# 2. all numerical columns of interest (measures)
# 3. all categorical columns of interest (categories)
parser = argparse.ArgumentParser(description='Process some data from nyc open data and find potential aggregates')
parser.add_argument('--input_file', type=str, help='path to the file that has the dataset', required=True)
parser.add_argument('--category_columns', type=str, help='comma-separated list of categorical column names (case insensitive) for aggregation', required=True)
parser.add_argument('--measure_columns', type=str, help='comma-separated list of measurement column names (case insensitive) for aggregation', required=True)


def numbers_of_interest():
    numbers = set()
    leading_digits = range(1,25)
    trailing_digits = range(0,61)

    for leading_digit in leading_digits:
        for trailing_digit in trailing_digits:
            numbers.add(str(leading_digit * 100 + trailing_digit))
    return numbers

clock_numbers = numbers_of_interest()

def leading_3_or_null(num):
    leading_3 = int(str(num)[:3])
    if leading_3 in clock_numbers:
        return leading_3
    return None

def leading_4_or_none(num):
    leading_4 = int(str(num)[:4])
    if leading_4 in clock_numbers:
        return leading_4
    return None

def sanitize_column_name(col_name):
     return re.sub(r'[^a-zA-Z0-9]', '_', col_name).lower()

def main():
    args = parser.parse_args()

    # objects of {categories: [], measures: [], value: number, method: str}
    results = []

    # get numbers of interest
    clock_numbers = numbers_of_interest()

    # create pandas dataframe from dataset
    table_df = pandas.read_csv(args.input_file)
    
    # clean column names
    table_df.columns = [sanitize_column_name(col) for col in table_df.columns.str.lower()]
    category_columns = [sanitize_column_name(col) for col in args.category_columns.split(",")]
    measure_columns = [sanitize_column_name(col) for col in args.measure_columns.split(",")]
    table_df = table_df.drop(columns=[col for col in table_df.columns if col not in measure_columns and col not in category_columns])

    # find rows with valid clock times w/leading 3 or leading 4 digits
    boolean_columns = []
    for measure in measure_columns:
        table_df[f'{measure}_leading_3'] = table_df[measure].astype(str).str[:3]
        table_df[f'{measure}_leading_3_good'] = table_df[f'{measure}_leading_3'].isin(clock_numbers)
        boolean_columns.append(f'{measure}_leading_3_good')
        table_df[f'{measure}_leading_4'] = table_df[measure].astype(str).str[:4]
        table_df[f'{measure}_leading_4_good'] = table_df[f'{measure}_leading_4'].isin(clock_numbers)
        boolean_columns.append(f'{measure}_leading_4_good')

    table_df = table_df[table_df.eval(' or '.join(boolean_columns))]

    # write rows to the DB
    extracted_clock_time_options = []

    for index, row in table_df.iterrows():
        for measure in measure_columns:
            if row[f'{measure}_leading_4_good']:
                extracted_clock_time_options.append({
                    'id': str(uuid.uuid4()),
                    'clock_time': row[f'{measure}_leading_4'],
                    'measure_columns': [measure],
                    'category_columns': [category_columns],
                    'dataset': args.input_file,
                })
            if row[f'{measure}_leading_3_good']:
                extracted_clock_time_options.append({
                    'id': str(uuid.uuid4()),
                    'clock_time': row[f'{measure}_leading_3'],
                    'measure_columns': [measure],
                    'category_columns': [category_columns],
                    'dataset': args.input_file,
                })

    engine = create_engine(os.getenv("DB_URI"))
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f'inserting {len(extracted_clock_time_options)} rows')
    session.bulk_insert_mappings(ClockTimeOptions, extracted_clock_time_options)
    session.commit()
    session.close()


    # then, create a pivot table for every combination of categories of interest
    # in pivot table, calculate aggregates

'''
np.sum	np.nansum	Compute sum of elements
np.prod	np.nanprod	Compute product of elements
np.mean	np.nanmean	Compute mean of elements
np.std	np.nanstd	Compute standard deviation
np.var	np.nanvar	Compute variance
np.min	np.nanmin	Find minimum value
np.max	np.nanmax	Find maximum value
np.argmin	np.nanargmin	Find index of minimum value
np.argmax	np.nanargmax	Find index of maximum value
np.median	np.nanmedian	Compute median of elements
np.percentile	np.nanpercentile	Compute rank-based statistics of elements
np.any	N/A	Evaluate whether any elements are true
np.all
'''

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
