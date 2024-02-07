import csv
import sys
import re

def sort_domains_by_status(input_file_name):
    # Prepare lists to hold rows sorted by status
    registered_rows = []
    server_hold_rows = []

    # Extract 【数値1】 and 【数値2】 from the input file name
    match = re.search(r'(\d+)_+(\d+)_domain_info\.csv', input_file_name)
    if not match:
        print("Invalid input file name format. Expected format: 【数値1】_【数値2】_domain_info.csv")
        sys.exit(1)
    
    num1, num2 = match.groups()

    # Read the input CSV file
    with open(input_file_name, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        for row in csv_reader:
            # Check if the row contains domain information
            if len(row) > 1:
                if row[1] == 'Registered':
                    registered_rows.append(row)
                elif row[1] == 'Server Hold':
                    server_hold_rows.append(row)

    # Write the sorted rows into separate output files
    output_file_registered = f'{num1}_{num2}_Registered.csv'
    output_file_server_hold = f'{num1}_{num2}_ServerHold.csv'

    with open(output_file_registered, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(registered_rows)
    
    with open(output_file_server_hold, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(server_hold_rows)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py input_csv_file.csv")
        sys.exit(1)

    input_file_name = sys.argv[1]
    sort_domains_by_status(input_file_name)
