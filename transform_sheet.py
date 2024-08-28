import smartsheet
from credentials import smartsheet_sheet_id, smartsheet_token

# Initialize Smartsheet client
smartsheet_client = smartsheet.Smartsheet(smartsheet_token)

# Specify your sheet ID
sheet_id = smartsheet_sheet_id

try:
    # Load the sheet
    sheet = smartsheet_client.Sheets.get_sheet(sheet_id)
except smartsheet.exceptions.ApiError as e:
    print(f"Error loading sheet: {e}")
    exit(1)  # Exit the script if the sheet could not be loaded

# Check if the sheet object has rows
if hasattr(sheet, 'rows'):
    # Prepare to update rows
    updated_rows = []

    # Iterate through each row in the sheet
    for row in sheet.rows:
        # Get the first cell in the row (assuming it's the first column)
        first_cell = row.cells[0]
        original_value = str(first_cell.value) if first_cell.value is not None else ""

        # Debug print the original value
        print(f"Original value: '{original_value}'")

        # Add leading single quote if not present
        if not original_value.startswith("'"):
            updated_value = f"'{original_value}"
        else:
            updated_value = original_value
        
        # Remove leading single quote if present
        if updated_value.startswith("'"):
            updated_value = updated_value.lstrip("'")
        
        # Remove '.0' suffix if present
        if updated_value.endswith(".0"):
            updated_value = updated_value.rstrip(".0")

        # Debug print the updated value
        print(f"Updated value: '{updated_value}'")

        # Update only if any changes were made
        if updated_value != original_value:
            # Create the updated cell
            updated_cell = smartsheet.models.Cell()
            updated_cell.column_id = first_cell.column_id
            updated_cell.value = updated_value
            
            # Create the updated row
            updated_row = smartsheet.models.Row()
            updated_row.id = row.id
            updated_row.cells.append(updated_cell)
            
            # Add the row to the list of rows to update
            updated_rows.append(updated_row)

    # Check if there are rows to update
    if updated_rows:
        smartsheet_client.Sheets.update_rows(sheet_id, updated_rows)
        print(f"Updated {len(updated_rows)} rows in the first column of the sheet.")
    else:
        print("No rows needed updating.")
else:
    print("Failed to retrieve rows from the sheet.")
