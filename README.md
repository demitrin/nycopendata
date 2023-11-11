# nycopendata

Scripts to parse datasets for potential clock entries, and save them into a db.

### Prerequisites

- Python 3.x
- Setup Postgres

```
brew services start postgresql@14
psql postgres
```

Example connection string: `postgresql://avimoondra:password@localhost:5432/postgres`


### Setting Up the Virtual Environment

1. Clone the repository:

    ```bash
    git clone https://github.com/demitrin/nycopendata.git
    ```

2. Navigate to the project directory:

    ```bash
    cd nycopendata
    ```

3. Create a virtual environment:

    ```bash
    python -m venv nycopendata-venv
    ```

4. Activate the virtual environment:

    ```bash
    source nycopendata-venv/bin/activate
    ```

5. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Script

Activate the virtual environment if it's not already activated:
```bash
$ source venv/bin/activate
```

Store `DB_URI` in your `.env` file, e.g.:
```
DB_URI=postgresql://avimoondra:password@localhost:5432/postgres
```

Run migrations
```bash
alembic upgrade head
```

Run script
```bash
$ python3 main.py --input_file Water_Consumption_in_the_City_of_New_York_20231110.csv --measure_columns='NYC Consumption(Million gallons per day),Per Capita(Gallons per person per day),New York City Population' --category_columns='Year'
```
