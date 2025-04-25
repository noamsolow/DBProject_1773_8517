from datetime import datetime
import csv

# Path to the uploaded CSV file
csv_file_path = 'equipment_suppliers.csv'  # Update this path based on where your file is located

# Path to save the SQL output
sql_output_path = 'insert_equipment_suppliers.sql'  # Path where you want to save the SQL file

# Open the CSV file and read it
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    # Open the SQL output file to write the INSERT statements
    with open(sql_output_path, mode='w', encoding='utf-8') as sql_file:
        for row in reader:
            # Clean the row keys by stripping spaces (if any)
            row = {key.strip(): value for key, value in row.items()}

            # Extract the values from the row
            equipment_id = row['equipment_id']
            supplier_id = row['supplier_id']
            quantity = row['quantity']
            supply_date = row['supply_date']

            # Convert supply_date to 'YYYY-MM-DD' format if necessary
            try:
                # If the date is in DD/MM/YYYY format, convert it to YYYY-MM-DD
                supply_date_obj = datetime.strptime(supply_date, '%d/%m/%Y')
                supply_date = supply_date_obj.strftime('%Y-%m-%d')
            except ValueError:
                pass  # If the date format is already correct, do nothing

            # Ensure that the supply_date is in correct format and handle None values for other fields
            sql_statement = f"""
                INSERT INTO Equipment_Supplier (equipment_id, supplier_id, quantity, supply_date)
                VALUES ({equipment_id}, {supplier_id}, {quantity}, '{supply_date}');
            """

            # Write the SQL statement to the file
            sql_file.write(sql_statement)

sql_output_path
