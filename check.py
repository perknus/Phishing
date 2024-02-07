import csv
import requests
import socket
from bs4 import BeautifulSoup
import sys
import time
import re  # Import the re module to use regular expressions

def process_csv_file(file_name):
    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        updated_rows = []

        for row in csv_reader:
            if len(row) > 1 and row[1] == 'Registered':
                first_url = f'https://{row[0]}'
                second_url = f'https://booking.{row[0]}/sign-in'
                third_url = f'https://booking.{row[0]}/sign-in/password'

                first_title = get_browser_title(first_url)
                if first_title == 'Succes':
                    second_title = get_browser_title(second_url)
                else:
                    second_title = ''

                third_title = get_browser_title(third_url)

                ip_address = get_ip_address(row[0])

                updated_row = [row[0], ip_address, first_title, second_title, third_title]
                updated_rows.append(updated_row)

    return updated_rows

def get_browser_title(url):
    try:
        response = requests.get(url)
        time.sleep(1)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else '-'
        else:
            title = '-'
    except Exception as e:
        print(f'Error fetching title for {url}: {e}')
        title = '-'

    return title

def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
    except Exception as e:
        print(f'Error fetching IP address for {domain}: {e}')
        ip_address = '-'

    return ip_address

def append_to_csv(file_name, rows):
    with open(file_name, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in rows:
            csv_writer.writerow(row)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py input_csv_file.csv")
        sys.exit(1)

    input_file_name = sys.argv[1]
    
    # Extract 数値1 and 数値2 from the input file name
    match = re.search(r'(\d+)_+(\d+)_domain_info\.csv', input_file_name)
    if match:
        num1, num2 = match.groups()
        output_file_name = f'{num1}_{num2}_check.csv'
    else:
        print("Invalid input file name format. Expected format: 【数値1】_【数値2】_domain_info.csv")
        sys.exit(1)

    updated_rows = process_csv_file(input_file_name)
    append_to_csv(output_file_name, updated_rows)
