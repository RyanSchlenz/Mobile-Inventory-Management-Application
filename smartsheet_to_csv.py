import csv
import requests
from datetime import datetime
import os
from credentials import (
    smartsheet_sheet_id, smartsheet_token, smartsheet_api_base_url,
    desired_fieldnames, smartsheet_csv_file, zendesk_csv_file
)

# Function to format dates
def format_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return 'N/A'

# Fetch column definitions and picklist options dynamically
def fetch_column_definitions():
    url = f'{smartsheet_api_base_url}/sheets/{smartsheet_sheet_id}/columns'
    headers = {'Authorization': f'Bearer {smartsheet_token}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    columns = response.json().get('data', [])
    column_definitions = {}
    picklist_options = {}

    for column in columns:
        column_name = column.get('title')
        options = column.get('options', [])

        if isinstance(options, list):
            # Normalize options by stripping extra spaces and converting to lowercase
            picklist_options[column_name] = [option.strip().lower() for option in options]
        else:
            picklist_options[column_name] = []

        column_definitions[column_name] = column.get('id')

    return column_definitions, picklist_options

# Function to validate picklist values
def validate_picklist(value, field_name, picklist_options):
    options = [option.strip().lower() for option in picklist_options.get(field_name, [])]
    formatted_value = value.strip().lower()
    if formatted_value in options or not options:
        return value.strip()
    else:
        print(f"Invalid value '{value}' for field '{field_name}'.")  # Debug print
        return 'N/A'

# Get the full path of a file
def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

# Read data from a CSV file
def read_csv(file_name):
    file_path = get_file_path(file_name)
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

# Fetch data from Smartsheet and save it to CSV
def fetch_smartsheet_data():
    url = f'{smartsheet_api_base_url}/sheets/{smartsheet_sheet_id}'
    headers = {'Authorization': f'Bearer {smartsheet_token}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    write_smartsheet_to_csv(data)

# Write fetched data to smartsheet_data.csv
def write_smartsheet_to_csv(data):
    file_path = get_file_path(smartsheet_csv_file)
    
    column_definitions, _ = fetch_column_definitions()
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=desired_fieldnames)
        writer.writeheader()
        
        for row in data.get('rows', []):
            formatted_row = {field: 'N/A' for field in desired_fieldnames}
            for cell in row.get('cells', []):
                column_id = cell.get('columnId')
                value = cell.get('value', 'N/A')
                
                column_title = next((k for k, v in column_definitions.items() if v == column_id), None)
                
                if column_title in formatted_row:
                    formatted_row[column_title] = value.strip() if isinstance(value, str) else value
            
            writer.writerow(formatted_row)

# Sync CSV data with Smartsheet
def sync_csv_with_smartsheet():
    smartsheet_csv_file_path = get_file_path(smartsheet_csv_file)
    zendesk_csv_file_path = get_file_path(zendesk_csv_file)

    column_definitions, picklist_options = fetch_column_definitions()

    fetch_smartsheet_data()

    smartsheet_data = read_csv(smartsheet_csv_file_path)
    zendesk_data = read_csv(zendesk_csv_file_path)

    smartsheet_imei_set = {row['IMEI #'].strip() for row in smartsheet_data}

    updates = []

    for row in zendesk_data:
        imei = row.get('IMEI #', '').strip()
        if imei in smartsheet_imei_set:
            matching_row = next((item for item in smartsheet_data if item['IMEI #'].strip() == imei), None)
            if matching_row:
                matching_row.update({
                    'Serial # Apple only': row.get('Serial # Apple only', '').strip() or 'N/A',
                    'Brand': validate_picklist(row.get('Brand', ''), 'Brand', picklist_options),
                    'Model': validate_picklist(row.get('Model', ''), 'Model', picklist_options),
                    'Status': validate_picklist(row.get('Status', ''), 'Status', picklist_options),
                    'Deploy Date': format_date(row.get('Deploy Date', '')),
                    'Fulfilled By': validate_picklist(row.get('Fulfilled By', ''), 'Fulfilled By', picklist_options),
                    'Ticket #': row.get('Ticket #', '').strip() or 'N/A',
                    'GL Code - Facility Name': validate_picklist(row.get('GL Code - Facility Name', ''), 'GL Code - Facility Name', picklist_options),
                    'Recipient': validate_picklist(row.get('Recipient', ''), 'Recipient', picklist_options),
                    'Notes': validate_picklist(row.get('Notes', ''), 'Notes', picklist_options)
                })
            updates.append(matching_row)
        else:
            new_row = {
                'IMEI #': imei,
                'Serial # Apple only': row.get('Serial # Apple only', '').strip() or 'N/A',
                'Brand': validate_picklist(row.get('Brand', ''), 'Brand', picklist_options),
                'Model': validate_picklist(row.get('Model', ''), 'Model', picklist_options),
                'Status': validate_picklist(row.get('Status', ''), 'Status', picklist_options),
                'Deploy Date': format_date(row.get('Deploy Date', '')),
                'Fulfilled By': validate_picklist(row.get('Fulfilled By', ''), 'Fulfilled By', picklist_options),
                'Ticket #': row.get('Ticket #', '').strip() or 'N/A',
                'GL Code - Facility Name': validate_picklist(row.get('GL Code - Facility Name', ''), 'GL Code - Facility Name', picklist_options),
                'Recipient': validate_picklist(row.get('Recipient', ''), 'Recipient', picklist_options),
                'Notes': validate_picklist(row.get('Notes', ''), 'Notes', picklist_options)
            }
            updates.append(new_row)

    with open(smartsheet_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=desired_fieldnames)
        writer.writeheader()
        writer.writerows(updates)

    print(f"Updated {len(updates)} records in {smartsheet_csv_file_path}")

if __name__ == '__main__':
    sync_csv_with_smartsheet()
