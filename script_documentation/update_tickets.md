Documentation for update_tickets.py

Overview
This script updates Zendesk tickets by adding comments based on data from a CSV file. It handles:

Retrieving ticket status and comments.
Constructing comment bodies from CSV data.
Updating tickets and moving them to a specified queue.
Ensuring that comments are not duplicated.

Imports

import requests
import csv
import os
from hashlib import sha256
from credentials import (
    zendesk_subdomain,
    zendesk_email,
    zendesk_api_token,
    WAITING_QUEUE_ID
)
Constants
ZENDESK_BASE_URL: Base URL for Zendesk API endpoints.
zendesk_auth: Authentication tuple for Zendesk API.
Functions
get_ticket_status(ticket_id)
Retrieves the status of a ticket.

Parameters: ticket_id (int) - The ID of the ticket.
Returns: Status of the ticket (str).


def get_ticket_status(ticket_id):
    url = f'{ZENDESK_BASE_URL}/tickets/{ticket_id}.json'
    response = requests.get(url, auth=zendesk_auth)
    response.raise_for_status()
    ticket = response.json()['ticket']
    return ticket['status']
get_ticket_comments(ticket_id)
Fetches comments for a specific ticket.

Parameters: ticket_id (int) - The ID of the ticket.
Returns: List of comments.


def get_ticket_comments(ticket_id):
    url = f'{ZENDESK_BASE_URL}/tickets/{ticket_id}/comments.json'
    response = requests.get(url, auth=zendesk_auth)
    response.raise_for_status()
    comments = response.json()['comments']
    return comments
update_ticket(ticket_id, comment_body)
Updates a ticket with a new comment and moves it to the waiting queue.

Parameters:
ticket_id (int) - The ID of the ticket.
comment_body (str) - The comment text to add.
Returns: None


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
normalize_text(text)
Normalizes text by removing newlines and extra spaces.

Parameters: text (str) - The text to normalize.
Returns: Normalized text (str).


def normalize_text(text):
    return text.strip().replace('\n', ' ').replace('\r', '')
hash_comment(comment_body)
Creates a hash for the comment body to ensure uniqueness.

Parameters: comment_body (str) - The comment body.
Returns: SHA-256 hash of the normalized comment body (str).


def hash_comment(comment_body):
    """Create a hash for the comment body to ensure uniqueness"""
    return sha256(normalize_text(comment_body).encode('utf-8')).hexdigest()
comment_already_exists(comments, comment_body)
Checks if a comment with the same body already exists in the ticket's comments.

Parameters:
comments (list) - List of existing comments.
comment_body (str) - The comment body to check.
Returns: True if the comment already exists, False otherwise.


def comment_already_exists(comments, comment_body):
    """Check if a comment with the same body already exists"""
    normalized_body = normalize_text(comment_body)
    body_hash = hash_comment(normalized_body)
    return any(hash_comment(normalize_text(comment['body'])) == body_hash for comment in comments)
construct_comment_body(rows)
Constructs the comment body from a list of rows.

Parameters: rows (list) - List of dictionaries containing ticket data.
Returns: Constructed comment body (str).


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
Main Function
main()
Executes the main workflow:

Reads the CSV file and groups data by ticket ID.
Processes each ticket:
Retrieves ticket status.
Constructs the comment body.
Checks for existing comments.
Updates the ticket if necessary.
Parameters: None
Returns: None


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
This script ensures efficient handling of Zendesk tickets, providing robust mechanisms for managing ticket updates and avoiding duplicate comments.