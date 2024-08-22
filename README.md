# Mobile-Inventory-Management-Application

# Overview
The Mobile Inventory Management Application is a comprehensive solution designed to integrate and synchronize mobile inventory data between Zendesk and Smartsheet. This application consists of a series of scripts that dynamically pull, compare, update, and synchronize data to ensure accuracy and consistency across platforms. It handles large datasets efficiently and automates the process of inventory management.

# Project Structure
The application is comprised of the following scripts:

zendesk_data.py: Pulls data from Zendesk and saves it to a CSV file.
smartsheet_to_csv.py: Pulls data from Smartsheet and saves it to a CSV file if an IMEI on the Smartsheet matches an IMEI on the Zendesk CSV. 
transform_sheet.py: Normalizes all the IMEI data on the Smartsheet before uploading CSV data.
update_smartsheet.py: Uploads data from the Smartsheet CSV to Smartsheet, updating existing rows or adding new ones based on IMEI matches.
update_tickets.py: Updates Zendesk tickets with new comments if they don’t already exist in the ticket history.
main.py: Runs all scripts in one file, and deletes the CSV files after successful completion of the script.

# Workflow

Fetch Data: Use zendesk_data.py to gather data from Zendesk and save to CSV files.
Compare and Update: Run smartsheet_to_csv.py to align the Smartsheet data with Zendesk data and save to a CSV.
Normalize Smartsheet Data: Run transform_sheet.py to correctly match existing IMEIs on the Smartsheet to the CSV data being uploaded. 
Upload Updated Data: Execute update_smartsheet.py to upload the updated Smartsheet data.
Synchronize Zendesk: Finally, run update_tickets.py to ensure Zendesk tickets are updated with the latest information.
Error Handling
Ensure API credentials are valid and have the necessary permissions.
Check for connectivity issues with Zendesk or Smartsheet.
Review log files for detailed error information if any script fails.
