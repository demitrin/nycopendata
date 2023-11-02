import argparse
import pandas
import numpy as np

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
    leading_digits = range(1,13)
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

def main():
    args = parser.parse_args()

    # objects of {categories: [], measures: [], value: number, method: str}
    results = []

    # get numbers of interest
    clock_numbers = numbers_of_interest()

    # create pandas dataframe from dataset
    table_df = pandas.read_csv(args.input_file)
    # case insensitive by going to lowercase
    table_df.columns = [col.replace(' ', '_') for col in table_df.columns.str.lower()]

    # first, look at raw datapoints for every numerical column looking for numbers of interest
    measure_columns = args.measure_columns.lower().replace(' ', '_').split(',')
    boolean_columns = []
    for measure in measure_columns:
        table_df[f'{measure}_leading_3'] = table_df[measure].astype(str).str[:3]
        table_df[f'{measure}_leading_3_good'] = table_df[f'{measure}_leading_3'].isin(clock_numbers)
        boolean_columns.append(f'{measure}_leading_3_good')
        table_df[f'{measure}_leading_4'] = table_df[measure].astype(str).str[:4]
        table_df[f'{measure}_leading_4_good'] = table_df[f'{measure}_leading_4'].isin(clock_numbers)
        boolean_columns.append(f'{measure}_leading_4_good')

    print(table_df)
    print(table_df[table_df.eval(' or '.join(boolean_columns))].to_string())
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
# NOTE: could decide not to do pairwise until later
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
