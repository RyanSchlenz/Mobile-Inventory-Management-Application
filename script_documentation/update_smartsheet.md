Documentation for Smartsheet Update Script

Overview
This script updates a Smartsheet with data from a CSV file. It handles:

Formatting and normalizing data.
Updating existing rows or adding new ones based on IMEI numbers.
Dynamically retrieving column IDs and picklist options from Smartsheet.

Imports

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
Constants
smartsheet_sheet_id: ID of the Smartsheet sheet to be updated.
smartsheet_token: API token for authenticating with Smartsheet.
date_format: Format for parsing and formatting dates.
picklist_fields: List of fields that require picklist validation.
csv_file_names: Dictionary containing file names for CSV files.
Initialization


# Initialize Smartsheet client
smartsheet_client = smartsheet.Smartsheet(smartsheet_token)
Functions
format_date(date_str)
Formats a date string according to date_format.

Parameters: date_str (str) - The date string to format.
Returns: Formatted date string or an empty string if formatting fails.


def format_date(date_str):
    try:
        formatted_date = datetime.strptime(date_str, date_format).strftime(date_format)
        print(f"Formatted date: Original: '{date_str}' Formatted: '{formatted_date}'")
        return formatted_date
    except ValueError:
        print(f"Date formatting error: '{date_str}'")
        return ''
normalize_text(text, capitalize=False)
Normalizes text for comparison, optionally capitalizing it.

Parameters:
text (str) - The text to normalize.
capitalize (bool) - Whether to capitalize the text.
Returns: Normalized text.


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
clean_facility_name(name)
Cleans up facility names by stripping unwanted characters.

Parameters: name (str) - The facility name to clean.
Returns: Cleaned facility name.


def clean_facility_name(name):
    cleaned_name = name.strip('"').strip("'")
    print(f"Cleaned facility name: Original: '{name}' Cleaned: '{cleaned_name}'")
    return cleaned_name
get_column_ids_and_picklists(sheet_id)
Retrieves column IDs and picklist options from Smartsheet.

Parameters: sheet_id (int) - The Smartsheet sheet ID.
Returns: Tuple containing:
column_id_mapping (dict) - Mapping of column titles to IDs.
picklist_options_mapping (dict) - Mapping of picklist columns to options.


def get_column_ids_and_picklists(sheet_id):
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
    column_id_mapping = {}
    picklist_options_mapping = {}

    for column in sheet.columns:
        column_id_mapping[column.title] = column.id
        if column.type == "PICKLIST":
            picklist_options_mapping[column.title] = column.options

    return column_id_mapping, picklist_options_mapping
validate_picklist(value, field_name, picklist_options_mapping)
Validates and normalizes picklist values.

Parameters:
value (str) - The value to validate.
field_name (str) - The field name for picklist validation.
picklist_options_mapping (dict) - Mapping of picklist options.
Returns: Validated and normalized value.


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
prepare_cells(row, column_id_mapping, picklist_options_mapping)
Prepares cell data for Smartsheet.

Parameters:
row (dict) - Data for a single row.
column_id_mapping (dict) - Mapping of column titles to IDs.
picklist_options_mapping (dict) - Mapping of picklist columns to options.
Returns: List of cells with column IDs and values.


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
get_file_path(filename)
Gets the full path of a file in the same directory as the script.

Parameters: filename (str) - The name of the file.
Returns: Full file path.


def get_file_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)
get_smartsheet_rows(sheet_id, column_id_mapping)
Retrieves rows from Smartsheet and normalizes data.

Parameters:
sheet_id (int) - The Smartsheet sheet ID.
column_id_mapping (dict) - Mapping of column titles to IDs.
Returns: Dictionary of rows keyed by IMEI numbers.


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
update_smartsheet_row(sheet_id, row_id, cells)
Updates an existing row in Smartsheet.

Parameters:
sheet_id (int) - The Smartsheet sheet ID.
row_id (int) - The ID of the row to update.
cells (list) - List of cells to update.
Returns: Updated row data.


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
add_smartsheet_row(sheet_id, cells)
Adds a new row to Smartsheet.

Parameters:
sheet_id (int) - The Smartsheet sheet ID.
cells (list) - List of cells to add.
Returns: Added row data.


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
read_csv_and_process(file_path, column_id_mapping, picklist_options_mapping, smartsheet_data)
Reads data from a CSV file and updates or adds rows in Smartsheet.

Parameters:
file_path (str) - Path to the CSV file.
column_id_mapping (dict) - Mapping of column titles to IDs.
picklist_options_mapping (dict) - Mapping of picklist columns to options.
smartsheet_data (dict) - Existing data from Smartsheet.
Returns: None


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
Main Function
process_data()
Executes the main workflow: retrieves column IDs and picklists, gets Smartsheet data, and processes the CSV file.

Parameters: None
Returns: None


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
This script provides a robust framework for updating Smartsheet data based on CSV input, including handling various data formatting and validation tasks.