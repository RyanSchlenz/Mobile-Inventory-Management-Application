Documentation for smartsheet_to_csv.py

Overview
The smartsheet_to_csv.py script performs the following tasks:

Fetches column definitions and picklist options from a Smartsheet.
Retrieves data from Smartsheet and writes it to a CSV file.
Syncs data from a Zendesk CSV file with the Smartsheet CSV file, validating and updating records as needed.

Imports


import os
import csv
import requests
from datetime import datetime
Constants
smartsheet_api_base_url: Base URL for the Smartsheet API.
smartsheet_sheet_id: ID of the Smartsheet sheet to be accessed.
smartsheet_token: Bearer token for authentication with the Smartsheet API.
smartsheet_csv_file: Name of the CSV file to save Smartsheet data.
zendesk_csv_file: Name of the CSV file containing Zendesk data.
desired_fieldnames: List of field names expected in the CSV files.
Functions
format_date(date_str)
Formats a date string into '%Y-%m-%d'. Returns 'N/A' if the date format is incorrect.

Parameters:
date_str (str): The date string to format.
Returns:
str: Formatted date string or 'N/A'.
fetch_column_definitions()
Fetches column definitions and picklist options from Smartsheet.

Returns:
column_definitions (dict): Dictionary mapping column names to column IDs.
picklist_options (dict): Dictionary mapping column names to their picklist options.
validate_picklist(value, field_name, picklist_options)
Validates a value against picklist options for a given field.

Parameters:
value (str): The value to validate.
field_name (str): The name of the field.
picklist_options (dict): Dictionary of picklist options.
Returns:
str: Validated value or 'N/A' if invalid.
get_file_path(filename)
Constructs the full path for a file located in the same directory as the script.

Parameters:
filename (str): The name of the file.
Returns:
str: Full file path.
read_csv(file_name)
Reads data from a CSV file.

Parameters:
file_name (str): The name of the CSV file.
Returns:
list of dict: List of rows read from the CSV file.
fetch_smartsheet_data()
Fetches data from Smartsheet and writes it to a CSV file.

Returns: None
write_smartsheet_to_csv(data)
Writes fetched Smartsheet data to a CSV file.

Parameters:
data (dict): Data retrieved from Smartsheet.
Returns: None
sync_csv_with_smartsheet()
Syncs data between Smartsheet and Zendesk CSV files, updating records as needed.

Returns: None
Execution
The script executes the sync_csv_with_smartsheet() function when run as a main program.


if __name__ == '__main__':
    sync_csv_with_smartsheet()
Error Handling
Fetch Column Definitions: Logs errors if fetching column definitions fails.
Fetch Smartsheet Data: Logs errors if fetching Smartsheet data fails.
Read/Write CSV: Catches and handles IO errors when reading from or writing to CSV files.
Logging
The script uses print statements for debugging purposes, especially when handling invalid picklist values.