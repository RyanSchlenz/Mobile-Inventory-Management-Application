import requests
import csv
import os
from hashlib import sha256
from credentials import zendesk_subdomain, zendesk_email, zendesk_api_token, WAITING_QUEUE_ID

# Base URL for Zendesk API
ZENDESK_BASE_URL = f'https://{zendesk_subdomain}.zendesk.com/api/v2'

# Authentication for Zendesk API
zendesk_auth = (f'{zendesk_email}/token', zendesk_api_token)

def get_ticket_status(ticket_id):
    url = f'{ZENDESK_BASE_URL}/tickets/{ticket_id}.json'
    response = requests.get(url, auth=zendesk_auth)
    response.raise_for_status()
    ticket = response.json()['ticket']
    return ticket['status']

def get_ticket_comments(ticket_id):
    url = f'{ZENDESK_BASE_URL}/tickets/{ticket_id}/comments.json'
    response = requests.get(url, auth=zendesk_auth)
    response.raise_for_status()
    comments = response.json()['comments']
    return comments

def update_ticket(ticket_id, comment_body):
    url = f'{ZENDESK_BASE_URL}/tickets/{ticket_id}.json'
    data = {
        'ticket': {
            'comment': {
                'body': comment_body,
                'public': False  # Make this comment private
            },
            'group_id': WAITING_QUEUE_ID  # Move the ticket to the waiting queue
        }
    }
    response = requests.put(url, json=data, auth=zendesk_auth)
    response.raise_for_status()
    print(f"Updated ticket {ticket_id} and moved to waiting queue {WAITING_QUEUE_ID}")

def normalize_text(text):
    return text.strip().replace('\n', ' ').replace('\r', '')

def hash_comment(comment_body):
    """Create a hash for the comment body to ensure uniqueness"""
    return sha256(normalize_text(comment_body).encode('utf-8')).hexdigest()

def comment_already_exists(comments, comment_body):
    """Check if a comment with the same body already exists"""
    normalized_body = normalize_text(comment_body)
    body_hash = hash_comment(normalized_body)
    return any(hash_comment(normalize_text(comment['body'])) == body_hash for comment in comments)

def construct_comment_body(rows):
    comment_body = "Form Data:\n"

    for row in rows:
        imei = normalize_text(row['IMEI #'])
        comment_body += (
            f"IMEI #: {imei}\n"
            f"Serial # Apple Only: {row['Serial # Apple only']}\n"
            f"Brand: {row['Brand']}\n"
            f"Model: {row['Model']}\n"
            f"Status: {row['Status']}\n"
            f"Deploy Date: {row['Deploy Date']}\n"
            f"Fulfilled By: {row['Fulfilled By']}\n"
            f"GL Code - Facility Name: {row['GL Code - Facility Name']}\n"
            f"Recipient: {row['Recipient']}\n"
            f"Notes: {row['Notes']}\n\n"
        )
    
    return comment_body.strip()

def main():
    # Path to the CSV file relative to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, 'zendesk_tickets.csv')

    # Read the CSV file
    tickets_data = {}
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticket_id = row['Ticket #']
            if ticket_id:
                if ticket_id not in tickets_data:
                    tickets_data[ticket_id] = []
                tickets_data[ticket_id].append(row)

    # Process each ticket
    for ticket_id, rows in tickets_data.items():
        # Check ticket status
        status = get_ticket_status(ticket_id)
        if status.lower() != 'closed':
            # Construct the comment body from all rows for this ticket
            comment_body = construct_comment_body(rows)

            # Get existing comments for the ticket
            comments = get_ticket_comments(ticket_id)

            # Check if the comment already exists
            if not comment_already_exists(comments, comment_body):
                # Update the ticket with the comment and move it to the waiting queue
                update_ticket(ticket_id, comment_body)
                print(f"Ticket {ticket_id} comments were updated.")
            else:
                print(f"Comment already exists for ticket {ticket_id}.")
        else:
            print(f"Ticket {ticket_id} is closed and will not be updated.")

if __name__ == '__main__':
    main()
