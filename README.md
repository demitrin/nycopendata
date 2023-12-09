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
   cd nycopendata/backend
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv nycopendata-venv
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
$ cd backend
$ source nycopendata-venv/bin/activate
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
$ python3 main.py
```

Dump the data

```bash
$ python3 dump_data.py
```

Merge real data with fake data

```bash
$ cd frontend/scripts
$ npx ts-node mergeFakeWithRealData.ts
```
