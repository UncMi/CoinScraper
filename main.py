import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import json

# Function to save image
def save_image(image_url, file_name):
    with open(f"{file_name}.jpg", 'wb') as f:
        f.write(requests.get(image_url).content)

# Function to zoom out
def zoom_out():
    pyautogui.hotkey('ctrl', '-')
    time.sleep(0.1)

website = 'https://en.ucoin.net/table/?country=turkey&period=55'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)

def openWebsite():
    driver.get(website)
    time.sleep(1)

openWebsite()

# Initialize list to store cell data
cell_data = []

# Load existing data from JSON file if it exists
try:
    with open('coin_info.json', 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    existing_data = []

# Append new data to the existing data
cell_data.extend(existing_data)

# Specify the starting indexes for table and cell traversal
table_start = 1
cell_start = 1

try:
    # Wait for all elements whose href attribute matches the pattern
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "/table/?country=turkey&period=")]'))
    )

    # Create an array to store the href attributes and indexes
    TurkishCoinYears = []

    for index, element in enumerate(elements, start=1):
        # Extract the href attribute of each element
        href = element.get_attribute("href")
        # Check if the href starts with "https://en"
        if href.startswith("https://en"):
            TurkishCoinYears.append((href, index))

    # Traverse the array and click on each link starting from table_start index
    for href, table_index in TurkishCoinYears[table_start - 1:]:
        # Click on the link
        driver.get(href)
        time.sleep(2)  # Adjust this delay as needed

        # Find all elements with class "cell marked-0"
        marked_elements = driver.find_elements(By.CSS_SELECTOR, 'a.cell.marked-0')

        # Click on each marked element starting from cell_start index
        for cell_index, marked_element in enumerate(marked_elements[cell_start - 1:], start=cell_start):
            marked_element.click()
            print(f"Table Index: {table_index}, Cell Index: {cell_index}")

            try:
                # Download and save the images
                coin_img1 = driver.find_element(By.ID, 'coin-img1').get_attribute('src')
                coin_img2 = driver.find_element(By.ID, 'coin-img2').get_attribute('src')

                save_image(coin_img1, f"{table_index}_{cell_index}_1")
                save_image(coin_img2, f"{table_index}_{cell_index}_2")

                # Get the table element
                table_element = driver.find_element(By.CLASS_NAME, 'tbl.coin-info')

                # Extract data from table
                rows = table_element.find_elements(By.TAG_NAME, 'tr')
                cell_dict = {}
                for row in rows:
                    th = row.find_element(By.TAG_NAME, 'th').text
                    td = row.find_element(By.TAG_NAME, 'td').text
                    cell_dict[th] = td

                # Add the data to the list in JSON format
                cell_data.append({
                    f"{table_index}:{cell_index}": cell_dict
                })

                print("Data inside the table:")
                print(cell_dict)

                # Write the data to a JSON file after each cell is processed
                with open('coin_info.json', 'w') as json_file:
                    json.dump(cell_data, json_file, indent=4)

            except NoSuchElementException:
                print("One or both images not found")

            time.sleep(1)  # Adjust this delay as needed

            # Go back to the main page
            driver.back()
            # Wait for the page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/table/?country=turkey&period=")]')))
            time.sleep(2)  # Adjust this delay as needed

        # After clicking on all marked elements, move to the next link
        openWebsite()

except TimeoutException:
    print("Timeout occurred. Page elements not found or failed to load.")
except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Close the browser
    driver.quit()
