import requests
from bs4 import BeautifulSoup
import csv
import tkinter as tk
from tkinter import simpledialog
import os
import re  # Import regular expressions module
import string  # Import string module for character validation

def get_company_info(soup):
    companies = []

    for listing in soup.find_all('div', class_='result'):
        try:
            company_name = listing.find('a', class_='business-name').text.strip()
        except AttributeError:
            company_name = None

        try:
            website = listing.find('a', class_='track-visit-website')['href']
        except (TypeError, KeyError):
            website = None

        try:
            phone_number = listing.find('div', class_='phones phone primary').text.strip()
        except AttributeError:
            phone_number = None

        try:
            email = listing.find('a', class_='email-business')['href'].replace('mailto:', '').strip()
        except (TypeError, KeyError):
            email = None

        # Add Instagram Link and First/Last Name if available (not typically found in Yellow Pages)
        instagram_link = None  # Placeholder, actual scraping logic needs to be added based on the website's HTML structure
        first_name = None  # Placeholder
        last_name = None  # Placeholder

        companies.append([company_name, website, instagram_link, phone_number, email, first_name, last_name])

    return companies

def get_valid_file_name(file_name):
    # Remove any invalid characters for file name on Windows
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    file_name = ''.join(c for c in file_name if c in valid_chars)
    return file_name

def get_unique_file_name(file_name):
    base_name, extension = os.path.splitext(file_name)
    counter = 1
    new_file_name = file_name

    while os.path.exists(new_file_name):
        counter += 1
        new_file_name = f"{base_name}_{counter}{extension}"

    return new_file_name

def save_to_csv(data, file_name):
    file_name = get_valid_file_name(file_name)
    file_name = get_unique_file_name(file_name)
    print(f"Saving data to file: {file_name}")  # Debug statement
    try:
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Count', 'First Name', 'Last Name', 'Company Website', 'Instagram Link', 'Phone Number', 'Email'])
            for count, row in enumerate(data, start=1):
                writer.writerow([count] + row)
    except OSError as e:
        print(f"Error opening or writing to file: {e}")

def get_total_pages(soup):
    try:
        pagination = soup.find('div', class_='pagination')
        pages = pagination.find_all('a', class_='page')
        total_pages = int(pages[-1].text.strip())
    except (AttributeError, IndexError, ValueError):
        total_pages = 1
    return total_pages

def main():
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask for URL and file name:
    url = simpledialog.askstring("Input", "Please enter the Yellow Pages URL:")
    file_name = simpledialog.askstring("Input", "Please enter the CSV file name (with .csv extension):")
    
    if not url or not file_name:
        print("URL or file name not provided. Exiting.")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        total_pages = get_total_pages(soup)

        base_url = url.split('&page=')[0] + '&page='

        all_companies = []
        for page in range(1, total_pages + 1):
            page_url = base_url + str(page)
            response = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            companies = get_company_info(soup)
            all_companies.extend(companies)
            print(f"Scraped page {page} of {total_pages}")

        save_to_csv(all_companies, file_name)

    except requests.exceptions.MissingSchema as e:
        print(f"Invalid URL provided: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
