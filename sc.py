import requests
import base64
import time
import random
from bs4 import BeautifulSoup
import csv

def decrypt_xor(encoded_str, key):
    decoded_bytes = base64.b64decode(encoded_str)
    decrypted_chars = [chr(byte ^ ord(key[i % len(key)])) for i, byte in enumerate(decoded_bytes)]
    return ''.join(decrypted_chars)

def send_request(url):
    for attempt in range(3):  # 最大3回まで再試行
        response = requests.get(url)
        if response.status_code == 429:  # Too Many Requests
            print("Rate limit exceeded. Waiting for 30 seconds...")
            time.sleep(30)  # 30秒待機
        else:
            return response  # 成功したレスポンスを返すまたは他のステータスコード
    return None  # 3回試行しても成功しなかった場合

def log_failed_domain(domain):
    with open("failed.log", "a") as log_file:
        log_file.write(f"{domain}\n")

def query_eurid(domain, csv_writer):
    url = f"https://whois.eurid.eu/en/search/?domain={domain}"
    response = send_request(url)

    if response and response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        general_section = soup.find("section", id="section-general")
        registrant_section = soup.find("dl", id="registrant")
        status = registered_date = registrar = email = address = ""

        if general_section:
            status_elements = general_section.find_all("dd")
            status_text = status_elements[1].text.strip() if len(status_elements) > 1 else ""
            status = status_text.split('\n')[0].strip() if status_text else ""
            registered_date = status_elements[2].text.strip() if len(status_elements) > 2 else ""
            registrar = status_elements[3].text.strip() if len(status_elements) > 3 else ""

        if registrant_section:
            email_element = registrant_section.find("a", {"data-xor-email": True})
            if email_element:
                email_encoded = email_element["data-xor-email"]
                email_key = email_element["data-xor-key"]
                email = decrypt_xor(email_encoded, email_key)
            
            address_elements = registrant_section.find_all("span", {"data-xor-text": True})
            if address_elements:
                address = ", ".join([decrypt_xor(element["data-xor-text"], element["data-xor-key"]) for element in address_elements])

        csv_writer.writerow([domain, status, registered_date, registrar, email, address])

    elif response:
        print(f"Error with domain {domain}: {response.status_code}")
        log_failed_domain(domain)
    else:
        print(f"Failed to retrieve data for domain {domain} after multiple attempts.")
        log_failed_domain(domain)

if __name__ == "__main__":
    lower_bound = int(input("Enter the lower bound: "))
    upper_bound = int(input("Enter the upper bound: "))
    output_file_name = f"{lower_bound}_{upper_bound}_domain_info.csv"

    with open(output_file_name, "a", newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        for i in range(lower_bound, upper_bound + 1):
            domain = f"id-{i}.eu"
            query_eurid(domain, csv_writer)
            wait_time = random.randint(5, 20)  # 5から20秒の間でランダムに待機時間を決定
            print(f"Waiting for {wait_time} seconds...")
            time.sleep(wait_time)