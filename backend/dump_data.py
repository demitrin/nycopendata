from sqlalchemy import create_engine, text
import os
import json
from dotenv import load_dotenv
from operator import itemgetter
from collections import defaultdict
from itertools import groupby
from decimal import Decimal

# Load environment variables from .env file
load_dotenv()

engine = create_engine(os.getenv("DB_URI"))

datasource_mapping: dict = {
    "~/Downloads/Individual_Census_by_Borough__Community_District__and_Facility_Type_20231206.csv": {
        "department": "Department of Homeless Services (DHS)",
        "datasource": "Individual Census by Borough, Community District, and Facility Type"
    },
    "~/Downloads/Civilian_Complaint_Review_Board__Allegations_Against_Police_Officers_20231206.csv": {
        "department": "Civilian Complaint Review Board (CCRB)",
        "datasource": "Allegations Against Police Officers"
    },
    "~/Downloads/GreenThumb_Site_Visits_20231206.csv": {
        "department": "Department of Parks and Recreation (DPR)",
        "datasource": "GreenThumb Site Visits"
    },
    "~/Downloads/Water_Consumption_in_the_City_of_New_York_20231206.csv": {
        "department": "Department of Environmental Protection (DEP)",
        "datasource": "Water Consumption in the City of New York"
    },
    "~/Downloads/Citywide_Payroll_Data__Fiscal_Year__20231114.csv": {
        "department": "Department of Citywide Administrative Services (DCAS)",
        "datasource": "Citywide Payroll Data (Fiscal Year)"
    }
}

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def main():
    with engine.connect() as conn:
        stmt = text("""
            SELECT
                clock_time,
                prompt,
                dataset
            FROM clock_time_options
            WHERE (clock_time / 100) BETWEEN 0 AND 13
            ORDER BY clock_time ASC
        """)
        results = conn.execute(stmt).fetchall()
        print('# of records available', len(results))

        grouped_results = {key: list(group) for key, group in groupby(results, key=itemgetter(0))}

        counts_per_dataset = defaultdict(int)
        for _, group in grouped_results.items():
            unique_datasets = set(record[2] for record in group)
            for dataset in unique_datasets:
                counts_per_dataset[dataset] += 1

        ordered_datasets = sorted(counts_per_dataset.keys(), key=lambda x: counts_per_dataset[x])
        dataset_distribution = {dataset: counts_per_dataset[dataset] for dataset in ordered_datasets}
        print('Distribution of datasets of raw data:', dataset_distribution)

        selected_records = []
        for _clock_time, group in grouped_results.items():
            record_selected = False
            for dataset in ordered_datasets:
                for record in group:
                    if record[2] == dataset:
                        # print(record[2])
                        # print(datasource_mapping[record[2]])
                        camel_case_record = { 
                            'clockTime': record[0], 
                            'prompt': record[1], 
                            'datasource': datasource_mapping[record[2]]['datasource'],
                            'department': datasource_mapping[record[2]]['department'] 
                        }
                        selected_records.append(camel_case_record)
                        record_selected = True
                        break 
                if record_selected:
                    break

        print('Selected records', len(selected_records))

        selected_records_distribution = defaultdict(int)
        for record in selected_records:
            selected_records_distribution[record['datasource']] += 1
        print('Distribution of datasets within selected records:', dict(selected_records_distribution))

        with open('../frontend/scripts/realData.json', 'w') as json_file:
            json.dump(selected_records, json_file, indent=2, cls=DecimalEncoder)
        print('Results dumped in frontend/scripts/realData.json')

if __name__ == "__main__":
    main()