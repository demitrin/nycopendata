import argparse
import pandas
import numpy as np
import re
import os
import uuid
from typing import TypedDict, Optional, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import ClockTimeOptions

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatasetToCrawl(TypedDict):
    input_file: str
    filename: str
    measure_columns: list
    category_columns: list
    only_aggregates: bool
    prompt_template: str
    year_column: Optional[str]
    prompt_templates: List[Dict[str, any]]

datasets_to_crawl: list[DatasetToCrawl] = [
    {
        'input_file': '~/Downloads/Water_Consumption_in_the_City_of_New_York_20231101.csv',
        'filename': 'Water_Consumption_in_the_City_of_New_York_20231101.csv',
        'measure_columns': ['new york city population', 'nyc_consumption(million_gallons_per_day)'],
        'category_columns': ['year'],
        'only_aggregates': False,
        'prompt_templates': [
            {
                'measure': 'new york city population',
                'prompt_template': '{units} total residents of NYC ({year})'
            },
            {
                'measure': 'nyc_consumption(million_gallons_per_day)',
                'prompt_template': 'millions of gallons of water consumed by NYC residents every day ({year})'
            },
        ]
    },
    {
        'input_file': '~/Downloads/Citywide_Payroll_Data__Fiscal_Year__20231101.csv',
        'filename': 'Citywide_Payroll_Data__Fiscal_Year__20231101.csv',
        'measure_columns': ['base_salary'],
        'category_columns': ['agency_name', 'work_location_borough', 'title_description', 'pay_basis'],
        'year_column': 'fiscal_year',
        'only_aggregates': True,
        'prompt_templates': [
            {
                'measure': 'base_salary',
                'category_columns': ['fiscal_year', 'agency_name', 'pay_basis'],
                'aggregate_function': 'max',
                'prompt_template': '{units} {pay_basis} is the highest base salary of NYC {agency_name} employees ({fiscal_year})'
            },
            {
                'measure': 'base_salary',
                'category_columns': ['fiscal_year', 'agency_name', 'work_location_borough', 'pay_basis'],
                'aggregate_function': 'max',
                'prompt_template': '{units} {pay_basis} is the highest base salary of NYC {agency_name} employees in {work_location_borough} ({fiscal_year})'
            },
            {
                'measure': 'base_salary',
                'category_columns': ['fiscal_year', 'work_location_borough', 'title_description', 'pay_basis'],
                'aggregate_function': 'max',
                'prompt_template': '{units} {pay_basis} is the highest base salary of NYC {title_description} employees in {work_location_borough} ({fiscal_year})'
            },
            {
                'measure': 'base_salary',
                'category_columns': ['fiscal_year', 'title_description', 'pay_basis'],
                'aggregate_function': 'max',
                'prompt_template': '{units} {pay_basis} is the highest base salary of NYC {title_description} employees ({fiscal_year})'
            },
        ]
    }
]

def numbers_of_interest():
    numbers = set()
    leading_digits = range(1,13)
    trailing_digits = range(0,60)

    for leading_digit in leading_digits:
        for trailing_digit in trailing_digits:
            numbers.add(str(leading_digit * 100 + trailing_digit))
    return numbers

clock_numbers = numbers_of_interest()

def sanitize_column_name(col_name):
     return re.sub(r'[^a-zA-Z0-9]', '_', col_name).lower()

def extract_clock_rows(table_df, measure, input_file, category_columns, prompt_templates):
    extracted_clock_time_options = []
    # try and find the prompt template
    prompt_template = None
    for template_config in prompt_templates:
        if template_config['measure'] != measure:
            continue
        prompt_template= template_config['prompt_template']

    if not prompt_template:
        print(category_columns, measure, prompt_templates)
        print('no template')
        return extracted_clock_time_options

    for index, row in table_df.iterrows():
        measure_value = row[measure]
        valid_clock_time = is_valid_clock_time(measure_value)
        prompt = prompt_template
        for category_column in category_columns:
            prompt = prompt.replace(f'{{{category_column}}}', str(row[category_column]))

        units = valid_clock_time['units']
        if valid_clock_time == 'raw':
            units = ''
        prompt = prompt.replace('{units}', str(units))

        if valid_clock_time['is_valid']:
            extracted_clock_time_options.append({
                'id': str(uuid.uuid4()),
                'clock_time': valid_clock_time['clock_time'],
                'raw_measure_column_value': measure_value,
                'measure_column_value_for_clock': valid_clock_time['clock_value'],
                'measure_columns': [measure],
                'category_columns': [category_columns],
                'dataset': input_file,
                'prompt': prompt,
            })

    return extracted_clock_time_options

class ValidClockTime(TypedDict):
    units: str
    clock_time: int
    clock_value: float
    is_valid: bool

def _number_is_good_for_clock(number):
    # any number between 1 and 13 is of the form:
    # X.YZ -- this is a valid clock number
    if number < 13 and number > 1:
        return True

    # any number between 100 and 1300 is of the form:
    # XYZ or ABCD -- these are valid clock numbers
    if number > 100 and number < 1300:
        return True

    # numbers below 10000 are of the shape
    # X.YZ in clock time, requiring a unit clarification like "1.23 thousand"
    # we thought this wasn't easy to understand, so we nixed it
    # 10.23 thousand makes more sense
    if number > 10000:
        return True

    return False

def units_and_clock_value(number):
    one_trillion = 1000000000000
    if number > one_trillion:
        return {
            'unit': 'trillion',
            'clock_value': number / one_trillion,
        }

    one_billion = one_trillion / 1000
    if number > one_billion:
        return {
            'unit': 'billion',
            'clock_value': number / one_billion,
        }

    one_million = one_billion / 1000
    if number > one_million:
        return {
            'unit': 'million',
            'clock_value': number / one_million,
        }

    if number > 10000:
        return {
            'unit': 'thousand',
            'clock_value': number / one_million,
        }

    if number < 1260 and number > 100:
        return {
            'unit': 'raw',
            'clock_value': int(number),
        }
    return {
        'unit': 'raw',
        'clock_value': number
    }

def is_valid_clock_time(number) -> ValidClockTime:
    number_metadata = units_and_clock_value(number)
    clock_value = number_metadata['clock_value']
    units = number_metadata['unit']
    # 12.1 is clock time 1210. therefore, any numbers under 100 must move decimal places
    clock_time = int(clock_value * 100) if clock_value < 100 and units != 'raw' else int(clock_value)
    return {
        'units': units,
        'clock_time': clock_time,
        'clock_value': clock_value,
        'is_valid': str(clock_time) in clock_numbers,
    }

def extract_clock_rows_from_aggregate(agg_table_df, measure, category_columns, aggregate_function_names, input_file, prompt_templates):
    extracted_clock_time_options = []

    prompt_templates = list(filter(lambda template_config: template_config['measure'] == measure and frozenset(template_config['category_columns']) == frozenset(category_columns), prompt_templates))

    if len(prompt_templates) == 0:
        return extracted_clock_time_options

    # row.Index is either a tuple or string. if it's a Tuple, then it is sorted values
    # of category_columns for the grouped value. if it's a string, then it's the single category column value
    for row in agg_table_df.itertuples():
        category_columns_values = row.Index if isinstance(row.Index, tuple) else [row.Index]
        for aggregate_func in aggregate_function_names:
            raw_measure_value = getattr(row, aggregate_func)
            valid_clock_time = is_valid_clock_time(raw_measure_value)
            prompt_template = None
            for template_config in prompt_templates:
                if template_config['aggregate_function'] == aggregate_func:
                    prompt_template = template_config['prompt_template']
                    break

            if not prompt_template:
                continue

            prompt = prompt_template
            for i, category_column in enumerate(category_columns):
                prompt = prompt.replace(f'{{{category_column}}}', str(category_columns_values[i]))

            units = valid_clock_time['units']
            if units == 'raw':
                units = ''
            prompt = prompt.replace('{units}', units)
            if valid_clock_time['is_valid']:
                extracted_clock_time_options.append({
                    'id': str(uuid.uuid4()),
                    'clock_time': valid_clock_time['clock_time'],
                    'measure_column_value_for_clock': valid_clock_time['clock_value'],
                    'raw_measure_column_value': raw_measure_value,
                    'measure_columns': [measure],
                    'category_columns': category_columns,
                    'category_columns_values': category_columns_values,
                    'aggregate_function': aggregate_func,
                    'dataset': input_file,
                    'prompt': prompt
                })

    return extracted_clock_time_options

def crawl_dataset(input_file, category_columns, measure_columns, only_aggregates, prompt_templates, year_column=None):
    # create pandas dataframe from dataset
    table_df = pandas.read_csv(input_file)

    # clean column names
    table_df.columns = [sanitize_column_name(col) for col in table_df.columns.str.lower()]
    measure_columns = [sanitize_column_name(col.lower()) for col in measure_columns]
    category_columns = [sanitize_column_name(col.lower()) for col in category_columns]
    table_df = table_df.drop(columns=[col for col in table_df.columns if col not in measure_columns and col not in category_columns and col != year_column])

    # sanitize prompt template
    for prompt_template in prompt_templates:
        prompt_template['measure'] = sanitize_column_name(prompt_template['measure'])
        if 'category_columns' in prompt_template:
            prompt_template['category_columns'] = [sanitize_column_name(col) for col in prompt_template['category_columns']]

    engine = create_engine(os.getenv("DB_URI"))
    if not only_aggregates:
        print('scanning raw data for matches. use --only_aggs if you want aggregates instead')
        rows_to_insert = []
        for measure in measure_columns:
            rows_to_insert.extend(extract_clock_rows(
                table_df=table_df,
                measure=measure,
                input_file=input_file,
                category_columns=category_columns,
                prompt_templates=prompt_templates))

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
    if only_aggregates:
        aggregate_funcs = ['sum', 'mean', 'min', 'max', 'median', 'count']
        print(f'working on aggregates, functions to use: {aggregate_funcs}')

        print(f'categories columns to group by: {category_columns}')

        # TODO: consider doing a proper powerset calculation for all combinations
        # for now, do pairwise
        # Array[Array[string]] for all pairs of categories
        power_set_categories = []
        for i in range(len(category_columns)):
            power_set_categories.append([year_column, category_columns[i]])
            for j in range(i+1, len(category_columns)):
                power_set_categories.append([year_column, category_columns[i], category_columns[j]])

        aggregate_rows_to_insert = []
        for categories in power_set_categories:
            # do every aggregate for all the measures
            grouped_by_table = table_df.groupby(categories)
            for measure in measure_columns:
                print(f"working on pivot table.\ncategories: {categories}\nmeasure:{measure}")
                aggregate_table = grouped_by_table.aggregate(**{agg_name: (measure, agg_name) for agg_name in aggregate_funcs})
                aggregate_rows_to_insert.extend(extract_clock_rows_from_aggregate(
                    agg_table_df=aggregate_table,
                    category_columns=categories,
                    measure=measure,
                    aggregate_function_names=aggregate_funcs,
                    input_file=input_file,
                    prompt_templates=prompt_templates))

        print(f'inserting {len(aggregate_rows_to_insert)} aggregate rows')
        Session = sessionmaker(bind=engine)
        session = Session()
        session.bulk_insert_mappings(ClockTimeOptions, aggregate_rows_to_insert)
        session.commit()
        print(f'finished insert {len(aggregate_rows_to_insert)} aggregate rows')
        session.close()
def main():
    for dataset in datasets_to_crawl:
        crawl_dataset(
            input_file=dataset['input_file'],
            category_columns=dataset['category_columns'],
            measure_columns=dataset['measure_columns'],
            only_aggregates=dataset['only_aggregates'],
            prompt_templates=dataset['prompt_templates'],
            year_column=dataset.get('year_column')
        )



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
