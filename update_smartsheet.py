import csv
import smartsheet
import re
from datetime import datetime
import os
from credentials import (
    smartsheet_sheet_id,
    smartsheet_token,
    date_format,
    picklist_fields,
    csv_file_names
)

# Initialize Smartsheet client
smartsheet_client = smartsheet.Smartsheet(smartsheet_token)

# Function to format dates
def format_date(date_str):
    try:
        formatted_date = datetime.strptime(date_str, date_format).strftime(date_format)
        print(f"Formatted date: Original: '{date_str}' Formatted: '{formatted_date}'")
        return formatted_date
    except ValueError:
        print(f"Date formatting error: '{date_str}'")
        return ''  # Handle error or provide default value

# Normalize text for comparison
def normalize_text(text, capitalize=False):
    if text:
        original_text = text
        text = re.sub(r'[^\w\s-]', '', text)  # Remove special characters except dash
        text = ' '.join(text.split())  # Remove extra spaces
        text = text.strip().upper()  # Remove leading/trailing spaces and convert to uppercase
        if text.startswith("'"):
            text = text[1:]  # Remove leading apostrophe
        if capitalize:
            text = text.title()  # Capitalize the first letter of each word
        print(f"Normalized text: Original: '{original_text}' Normalized: '{text}'")
        return text
    return ''

# Function to clean facility names
def clean_facility_name(name):
    cleaned_name = name.strip('"').strip("'")
    print(f"Cleaned facility name: Original: '{name}' Cleaned: '{cleaned_name}'")
    return cleaned_name

# Function to get column IDs and picklists dynamically from Smartsheet
def get_column_ids_and_picklists(sheet_id):
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    column_id_mapping = {}
    picklist_options_mapping = {}

    for column in sheet.columns:
        column_id_mapping[column.title] = column.id
        if column.type == "PICKLIST":
            picklist_options_mapping[column.title] = column.options

    return column_id_mapping, picklist_options_mapping

# Function to validate and normalize picklist values
def validate_picklist(value, field_name, picklist_options_mapping):
    options = picklist_options_mapping.get(field_name, [])
    normalized_value = normalize_text(value)
    options_normalized = [normalize_text(opt) for opt in options]  # Normalize options for comparison

    if normalized_value in options_normalized:
        print(f"Value '{value}' normalized to '{normalized_value}' matches picklist options.")
        return next((opt for opt in options if normalize_text(opt) == normalized_value), value).strip()  # Return matched value from options
    else:
        print(f"Value '{value}' normalized to '{normalized_value}' does not match any picklist options.")
        return value.strip()  # Return unformatted value if not in options

# Function to prepare cells for Smartsheet
def prepare_cells(row, column_id_mapping, picklist_options_mapping):
    cells = []
    for field, column_id in column_id_mapping.items():
        value = row.get(field, '')

        # Special handling for Deploy Date
        if field == 'Deploy Date':
            value = format_date(value)
        
        # Special handling for GL Code - Facility Name
        if field == 'GL Code - Facility Name':
            value = clean_facility_name(value)  # Clean facility name
        
        # Normalize the text for other fields
        capitalize = field == 'Recipient'
        if field not in ['Deploy Date', 'GL Code - Facility Name']:
            value = normalize_text(value, capitalize=capitalize)
        
        # Remove 'N/A' or 'NA' values
        if value in ['N/A', 'NA']:
            value = ''
        
        # Validate and normalize picklist values
        if field in picklist_fields:
            value = validate_picklist(value, field, picklist_options_mapping)  # Validate relevant fields
        
        # Ensure the value is treated as text in Smartsheet
        value = str(value).strip()
        if field == 'IMEI #':
            # Ensure no leading apostrophe in IMEI value
            value = value.lstrip("'")
        print(f"Prepared cell: Field: '{field}' Value: '{value}' Column ID: {column_id}")
        cells.append({'columnId': int(column_id), 'value': value})
    return cells

# Function to get the full path of a file in the same directory as the script
def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

# Function to get all rows from Smartsheet using Smartsheet SDK
def get_smartsheet_rows(sheet_id, column_id_mapping):
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    smartsheet_rows = {}
    
    for row in sheet.rows:
        row_data = {'row_id': row.id}  # Capture the row ID
        for cell in row.cells:
            for field, column_id in column_id_mapping.items():
                if cell.column_id == column_id:
                    value = str(cell.value) if not isinstance(cell.value, str) else cell.value
                    row_data[field] = normalize_text(value)
        imei_value = row_data.get('IMEI #')
        if imei_value:
            smartsheet_rows[imei_value] = row_data
    return smartsheet_rows

# Function to update an existing row in Smartsheet
def update_smartsheet_row(sheet_id, row_id, cells):
    new_row = smartsheet.models.Row()
    new_row.id = row_id
    for cell in cells:
        new_cell = smartsheet.models.Cell()
        new_cell.column_id = cell['columnId']
        new_cell.value = cell['value']
        new_cell.type = 'TEXT'  # Ensure cell type is set to text
        new_row.cells.append(new_cell)
    updated_row = smartsheet_client.Sheets.update_rows(sheet_id, [new_row])
    print(f"Updated row {row_id} in Smartsheet")
    return updated_row

# Function to add a new row to Smartsheet
def add_smartsheet_row(sheet_id, cells):
    new_row = smartsheet.models.Row()
    for cell in cells:
        new_cell = smartsheet.models.Cell()
        new_cell.column_id = cell['columnId']
        new_cell.value = cell['value']
        new_cell.type = 'TEXT'  # Ensure cell type is set to text
        new_row.cells.append(new_cell)
    new_row.to_bottom = True
    added_row = smartsheet_client.Sheets.add_rows(sheet_id, [new_row])
    print("Added new row to Smartsheet")
    return added_row

# Function to read CSV and process rows
def read_csv_and_process(file_path, column_id_mapping, picklist_options_mapping, smartsheet_data):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            imei = normalize_text(row.get('IMEI #'))
            # Ensure no leading apostrophe in IMEI value
            imei = imei.lstrip("'")
            cells = prepare_cells(row, column_id_mapping, picklist_options_mapping)
            
            print(f"Processing IMEI: {imei} with Cells: {cells}")
            
            if imei in smartsheet_data:
                update_smartsheet_row(smartsheet_sheet_id, smartsheet_data[imei]['row_id'], cells)
            else:
                add_smartsheet_row(smartsheet_sheet_id, cells)

# Main function to process the data
def process_data():
    # Dynamically retrieve column IDs and picklist options
    column_id_mapping, picklist_options_mapping = get_column_ids_and_picklists(smartsheet_sheet_id)
    
    # Print picklist options mapping
    print("Picklist Options Mapping:", picklist_options_mapping)
    
    # Get all Smartsheet rows
    smartsheet_data = get_smartsheet_rows(smartsheet_sheet_id, column_id_mapping)
    
    smartsheet_csv_file = get_file_path(csv_file_names['smartsheet_data'])
    
    # Read CSV and process data
    read_csv_and_process(smartsheet_csv_file, column_id_mapping, picklist_options_mapping, smartsheet_data)

if __name__ == "__main__":
    process_data()
