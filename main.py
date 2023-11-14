import argparse
import pandas
import numpy as np
import re
import os
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import ClockTimeOptions

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# we want:
# 1. path to the dataset (assume csv)
# 2. all numerical columns of interest (measures)
# 3. all categorical columns of interest (categories)
parser = argparse.ArgumentParser(description='Process some data from nyc open data and find potential aggregates')
parser.add_argument('--input_file', type=str, help='path to the file that has the dataset', required=True)
parser.add_argument('--category_columns', type=str, help='comma-separated list of categorical column names (case insensitive) for aggregation', required=True)
parser.add_argument('--measure_columns', type=str, help='comma-separated list of measurement column names (case insensitive) for aggregation', required=True)
parser.add_argument('--only_aggs', action=argparse.BooleanOptionalAction, help='if set, will parse the data only in aggregate mode. use on datasets that are not pre-aggregated')


def numbers_of_interest():
    numbers = set()
    leading_digits = range(1,25)
    trailing_digits = range(0,61)

    for leading_digit in leading_digits:
        for trailing_digit in trailing_digits:
            numbers.add(str(leading_digit * 100 + trailing_digit))
    return numbers

clock_numbers = numbers_of_interest()

def sanitize_column_name(col_name):
     return re.sub(r'[^a-zA-Z0-9]', '_', col_name).lower()

def extract_clock_rows(table_df, measure, input_file, category_columns):
    boolean_columns = []

    table_df[f'{measure}_leading_3'] = table_df[measure].astype(str).str[:3]
    table_df[f'{measure}_leading_3_good'] = table_df[f'{measure}_leading_3'].isin(clock_numbers)
    boolean_columns.append(f'{measure}_leading_3_good')

    table_df[f'{measure}_leading_4'] = table_df[measure].astype(str).str[:4]
    table_df[f'{measure}_leading_4_good'] = table_df[f'{measure}_leading_4'].isin(clock_numbers)
    boolean_columns.append(f'{measure}_leading_4_good')

    table_df = table_df[table_df.eval(' or '.join(boolean_columns))]
    extracted_clock_time_options = []
    for index, row in table_df.iterrows():
        if row[f'{measure}_leading_4_good']:
            extracted_clock_time_options.append({
                'id': str(uuid.uuid4()),
                'clock_time': row[f'{measure}_leading_4'],
                'measure_column_value': row[measure],
                'measure_columns': [measure],
                'category_columns': [category_columns],
                'dataset': input_file,
            })
        elif row[f'{measure}_leading_3_good']:
            extracted_clock_time_options.append({
                'id': str(uuid.uuid4()),
                'clock_time': row[f'{measure}_leading_3'],
                'measure_column_value': row[measure],
                'measure_columns': [measure],
                'category_columns': [category_columns],
                'dataset': input_file,
            })

    return extracted_clock_time_options

def extract_clock_rows_from_aggregate(agg_table_df, measure, category_columns, aggregate_function_names, input_file):
    extracted_clock_time_options = []
    # row.Index is either a tuple or string. if it's a Tuple, then it is sorted values
    # of category_columns for the grouped value. if it's a string, then it's the single category column value
    for row in agg_table_df.itertuples():
        category_columns_values = row.Index if isinstance(row.Index, tuple) else [row.Index]
        for aggregate_func in aggregate_function_names:
            str_agg_value = str(getattr(row, aggregate_func))
            leading_3 = str_agg_value[:3]
            leading_4 = str_agg_value[:4]
            for potential_clock_value in [leading_3, leading_4]:
                if potential_clock_value in clock_numbers:
                    extracted_clock_time_options.append({
                        'id': str(uuid.uuid4()),
                        'clock_time': potential_clock_value,
                        'measure_column_value': getattr(row, aggregate_func),
                        'measure_columns': [measure],
                        'category_columns': category_columns,
                        'category_columns_values': category_columns_values,
                        'aggregate_function': aggregate_func,
                        'dataset': input_file,
                    })
    return extracted_clock_time_options

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

    engine = create_engine(os.getenv("DB_URI"))
    # find rows with valid clock times w/leading 3 or leading 4 digits
    if not args.only_aggs:
        print('scanning raw data for matches. use --only_aggs if you want aggregates instead')
        rows_to_insert = []
        for measure in measure_columns:
            rows_to_insert.extend(extract_clock_rows(table_df=table_df, measure=measure, input_file=args.input_file, category_columns=category_columns))

        Session = sessionmaker(bind=engine)
        session = Session()
        print(f'inserting {len(rows_to_insert)} rows')
        session.bulk_insert_mappings(ClockTimeOptions, rows_to_insert)
        session.commit()
        print(f'finished insert {len(rows_to_insert)} rows')
        session.close()
    else:
        print('skipping raw data scan for matches. do not set --only_aggs if you want to scan raw data')

    # then, create a groupBy table for every combination of categories of interest
    if args.only_aggs:
        aggregate_funcs = [('sum'), 'mean', 'min', 'max', 'median']
        print(f'working on aggregates, functions to use: {aggregate_funcs}')

        print(f'categories columns to group by: {category_columns}')

        # TODO: consider doing a proper powerset calculation for all combinations
        # for now, do pairwise
        # Array[Array[string]] for all pairs of categories
        power_set_categories = []
        for i in range(len(category_columns)):
            power_set_categories.append([category_columns[i]])
            for j in range(i+1, len(category_columns)):
                power_set_categories.append([category_columns[i], category_columns[j]])

        aggregate_rows_to_insert = []
        for categories in power_set_categories:
            for measure in measure_columns:
                print(f"working on pivot table.\ncategories: {categories}\nmeasure:{measure}")
                grouped_table = table_df.groupby(categories).aggregate(**{agg_name: (measure, agg_name) for agg_name in aggregate_funcs})
                aggregate_rows_to_insert.extend(extract_clock_rows_from_aggregate(
                    agg_table_df=grouped_table,
                    category_columns=categories,
                    measure=measure,
                    aggregate_function_names=aggregate_funcs,
                    input_file=args.input_file))
        print(f'inserting {len(aggregate_rows_to_insert)} aggregate rows')
        Session = sessionmaker(bind=engine)
        session = Session()
        session.bulk_insert_mappings(ClockTimeOptions, aggregate_rows_to_insert)
        session.commit()
        print(f'finished insert {len(aggregate_rows_to_insert)} aggregate rows')
        session.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
