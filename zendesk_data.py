import requests
import csv
import os
import logging
from credentials import zendesk_subdomain, zendesk_email, zendesk_api_token, FORM_ID, QUEUE_ID, WAITING_QUEUE_ID

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for Zendesk API
ZENDESK_BASE_URL = f'https://{zendesk_subdomain}.zendesk.com/api/v2'

# Authentication for Zendesk API
zendesk_auth = (f'{zendesk_email}/token', zendesk_api_token)

# Fetch all ticket fields and their IDs from Zendesk
def fetch_ticket_fields():
    url = f"{ZENDESK_BASE_URL}/ticket_fields.json"
    try:
        response = requests.get(url, auth=zendesk_auth)
        response.raise_for_status()
        fields = response.json().get('ticket_fields', [])
        field_ids = {field['title']: field['id'] for field in fields}
        logging.info(f"Fetched ticket fields: {field_ids}")
        return field_ids
    except requests.RequestException as e:
        logging.error(f"Error fetching ticket fields: {e}")
        return {}

# Fetch options for a dropdown field from Zendesk
def fetch_dropdown_options(field_id):
    url = f"{ZENDESK_BASE_URL}/ticket_fields/{field_id}/options.json"
    try:
        response = requests.get(url, auth=zendesk_auth)
        response.raise_for_status()
        options = response.json().get('custom_field_options', [])
        return {
            'id_to_name': {str(option['id']): option['name'] for option in options},
            'tag_to_raw_name': {option['value']: option['name'] for option in options}
        }
    except requests.RequestException as e:
        logging.error(f"Error fetching dropdown options for field ID {field_id}: {e}")
        return {'id_to_name': {}, 'tag_to_raw_name': {}}

# Fetch all dropdown field options and return as a dictionary
def fetch_all_dropdown_mappings(field_ids):
    mappings = {}
    for field_name in ['Brand', 'Model', 'Status', 'Fulfilled By', 'GL Code - Facility Name', 'Notes']:
        field_id = field_ids.get(field_name)
        if field_id:
            mappings[field_name] = fetch_dropdown_options(field_id)
            logging.info(f"Fetched dropdown options for {field_name}: {mappings[field_name]}")
    return mappings

# Fetch tickets from Zendesk for a specific form and group
def fetch_zendesk_tickets(status=None):
    tickets = []
    for queue_id in [QUEUE_ID, WAITING_QUEUE_ID]:
        url = f"{ZENDESK_BASE_URL}/search.json?query=type:ticket form:{FORM_ID} group:{queue_id}"
        if status:
            url += f" status:{status}"
        
        logging.info(f"Fetching tickets from URL: {url}")

        while url:
            try:
                response = requests.get(url, auth=zendesk_auth)
                response.raise_for_status()
                data = response.json()
                
                # Log the raw response
                logging.info(f"Raw response data for queue {queue_id}: {data}")

                # Extract and store the tickets
                results = data.get('results', [])
                tickets.extend(results)
                logging.info(f"Fetched {len(results)} tickets from queue {queue_id}")

                # Check for pagination
                url = data.get('next_page')  # Get the URL for the next page if available

            except requests.RequestException as e:
                logging.error(f"Error fetching tickets from queue {queue_id}: {e}")
                break  # Exit the loop on error

    return tickets

# Save tickets to CSV with the specified format
def save_tickets_to_csv(tickets, field_ids, dropdown_mappings):
    script_dir = os.path.dirname(__file__)
    tickets_file = os.path.join(script_dir, 'zendesk_tickets.csv')
    seen_rows = set()  # To track and avoid duplicates

    try:
        with open(tickets_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['IMEI #', 'Serial # Apple only', 'Brand', 'Model', 'Status', 'Deploy Date',
                          'Fulfilled By', 'Ticket #', 'GL Code - Facility Name', 'Recipient', 'Notes',
                          'QUEUE_ID', 'WAITING_QUEUE_ID', 'FORM_ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for ticket in tickets:
                custom_fields = {str(field['id']): field['value'] for field in ticket.get('custom_fields', [])}

                gl_code_tag = custom_fields.get(str(field_ids.get('GL Code - Facility Name')), 'N/A')
                gl_code_name = dropdown_mappings['GL Code - Facility Name']['tag_to_raw_name'].get(gl_code_tag, 'N/A')

                imei_list = custom_fields.get(str(field_ids.get('IMEI #', 'N/A')), '')
                imei_values = [imei.strip().lstrip("'") for imei in (imei_list or '').split(',') if imei.strip()]

                recipients_list = custom_fields.get(str(field_ids.get('Recipient', 'N/A')), '')
                recipients = [recipient.strip() for recipient in (recipients_list or '').split(',') if recipient.strip()]

                # Iterate through imei_values to write each one as a separate row
                for i, imei in enumerate(imei_values):
                    row = {
                        'IMEI #': imei,
                        'Serial # Apple only': custom_fields.get(str(field_ids.get('Serial # Apple only', 'N/A')), 'N/A'),
                        'Brand': dropdown_mappings['Brand']['tag_to_raw_name'].get(custom_fields.get(str(field_ids.get('Brand', 'N/A')), 'N/A'), 'N/A'),
                        'Model': dropdown_mappings['Model']['tag_to_raw_name'].get(custom_fields.get(str(field_ids.get('Model', 'N/A')), 'N/A'), 'N/A'),
                        'Status': dropdown_mappings['Status']['tag_to_raw_name'].get(custom_fields.get(str(field_ids.get('Status', 'N/A')), 'N/A'), 'N/A'),
                        'Deploy Date': custom_fields.get(str(field_ids.get('Deploy Date', 'N/A')), 'N/A'),
                        'Fulfilled By': dropdown_mappings['Fulfilled By']['tag_to_raw_name'].get(custom_fields.get(str(field_ids.get('Fulfilled By', 'N/A')), 'N/A'), 'N/A'),
                        'Ticket #': ticket.get('id', 'N/A'),
                        'GL Code - Facility Name': gl_code_name,
                        'Recipient': recipients[i % len(recipients)] if recipients else 'N/A',
                        'Notes': dropdown_mappings['Notes']['tag_to_raw_name'].get(custom_fields.get(str(field_ids.get('Notes', 'N/A')), 'N/A'), 'N/A'),
                        'QUEUE_ID': QUEUE_ID if ticket.get('group_id') == QUEUE_ID else 'N/A',
                        'WAITING_QUEUE_ID': WAITING_QUEUE_ID if ticket.get('group_id') == WAITING_QUEUE_ID else 'N/A',
                        'FORM_ID': FORM_ID
                    }

                    # Convert the row values to strings
                    row_tuple = tuple(f"{key}:{str(value)}" for key, value in row.items())

                    # Only write unique rows
                    if row_tuple not in seen_rows:
                        writer.writerow(row)
                        seen_rows.add(row_tuple)

        logging.info(f"Tickets saved to {tickets_file}")
    except IOError as e:
        logging.error(f"Error saving tickets to CSV: {e}")


def main():
    try:
        # Fetch all ticket field IDs from Zendesk
        field_ids = fetch_ticket_fields()
        if not field_ids:
            logging.error("No ticket fields fetched. Exiting.")
            return

        # Fetch all dropdown mappings from Zendesk
        dropdown_mappings = fetch_all_dropdown_mappings(field_ids)

        # Fetch tickets from Zendesk
        tickets = fetch_zendesk_tickets()

        # Save tickets to CSV with the specified format
        save_tickets_to_csv(tickets, field_ids, dropdown_mappings)
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
