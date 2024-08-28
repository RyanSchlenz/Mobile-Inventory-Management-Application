Documentation for zendesk_data 

Overview
This script is designed to interact with the Zendesk API to fetch and process ticket data. It performs the following key tasks:

Fetches ticket field definitions from Zendesk.
Retrieves dropdown options for specific fields.
Fetches tickets based on specific form and group criteria.
Processes and saves tickets to a CSV file.
Configuration
Logging Configuration: The script uses Python's built-in logging module to log information and errors. Logs include timestamps, log levels, and messages.



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
Zendesk API Base URL: Constructed using the zendesk_subdomain variable. Replace zendesk_subdomain with your actual Zendesk subdomain.



ZENDESK_BASE_URL = f'https://{zendesk_subdomain}.zendesk.com/api/v2'
Authentication: Uses email and API token for authentication. Replace zendesk_email and zendesk_api_token with your actual Zendesk credentials.



zendesk_auth = (f'{zendesk_email}/token', zendesk_api_token)
Functions

1. fetch_ticket_fields()
Fetches all ticket fields and their IDs from Zendesk.

URL: https://{zendesk_subdomain}.zendesk.com/api/v2/ticket_fields.json

Returns: A dictionary mapping field titles to field IDs.

Error Handling: Logs errors if the request fails.



def fetch_ticket_fields():
    ...
2. fetch_dropdown_options(field_id)
Fetches options for a dropdown field.

URL: https://{zendesk_subdomain}.zendesk.com/api/v2/ticket_fields/{field_id}/options.json

Returns: A dictionary with two mappings:

id_to_name: Maps option IDs to option names.
tag_to_raw_name: Maps option values to option names.
Error Handling: Logs errors if the request fails.



def fetch_dropdown_options(field_id):
    ...
3. fetch_all_dropdown_mappings(field_ids)
Fetches dropdown options for predefined fields (e.g., Brand, Model, Status).

Field Names: 'Brand', 'Model', 'Status', 'Fulfilled By', 'GL Code - Facility Name', 'Notes'

Returns: A dictionary where each key is a field name and each value is the result from fetch_dropdown_options().

Logging: Logs fetched dropdown options for each field.



def fetch_all_dropdown_mappings(field_ids):
    ...
4. fetch_zendesk_tickets(status=None)
Fetches tickets from Zendesk based on form and group IDs.

URL: https://{zendesk_subdomain}.zendesk.com/api/v2/search.json?query=type:ticket form:{FORM_ID} group:{QUEUE_ID} (and WAITING_QUEUE_ID)

Parameters:

status: Optional filter to specify ticket status.
Returns: A list of tickets.

Error Handling: Logs errors and exits the loop if an error occurs.



def fetch_zendesk_tickets(status=None):
    ...
5. save_tickets_to_csv(tickets, field_ids, dropdown_mappings)
Saves fetched tickets to a CSV file.

File Path: zendesk_tickets.csv in the script's directory.

Fields: Includes 'IMEI #', 'Serial # Apple only', 'Brand', 'Model', etc.

Duplicates: Uses a set to track and avoid writing duplicate rows.

Error Handling: Logs errors if file operations fail.



def save_tickets_to_csv(tickets, field_ids, dropdown_mappings):
    ...
Main Execution Flow
Step 1: Fetches all ticket field IDs.

Step 2: Fetches dropdown mappings for predefined fields.

Step 3: Fetches tickets from Zendesk.

Step 4: Saves tickets to a CSV file.

Error Handling: Logs any exceptions encountered during the execution of the main workflow.



def main():
    try:
        ...
    except Exception as e:
        logging.error(f"An error occurred: {e}")
Running the Script
To execute the script, ensure all configuration variables (e.g., zendesk_subdomain, zendesk_email, zendesk_api_token, FORM_ID, QUEUE_ID, WAITING_QUEUE_ID) are correctly set. Run the script in an environment where the required libraries (requests, csv, os, logging) are available.