import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

# Function to fetch data from LinkedIn profile
def fetch_linkedin_data(driver):
    try:
        # Wait for the profile elements to load
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.inline.t-24.t-black.t-normal.break-words'))
        ).text
        job_title = driver.find_element(By.CSS_SELECTOR, 'h2.mt1.t-18.t-black.t-normal').text

        return {'Name': name, 'Job Title': job_title}
    except Exception as e:
        print(f"Error while fetching LinkedIn data: {e}")
        return {}

# Save the fetched data to the CSV
def save_to_csv(data, csv_file_path='bootcamp_student_data.csv'):
    # Create the CSV file if it does not exist
    if not os.path.isfile(csv_file_path):
        df = pd.DataFrame(columns=['Name', 'Job_Title'])
        df.to_csv(csv_file_path, index=False)

    # Load the existing CSV file
    df = pd.read_csv(csv_file_path)

    # Find the row that matches the student's name and update it
    for i, row in df.iterrows():
        if row['Name'] == data['Name']:
            df.at[i, 'Job_Title'] = data['Job Title']
            break
    else:
        # If the name is not found, append a new row
        df = df.append(data, ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, index=False)

def search_and_fetch(driver, name):
    search_url = "https://www.linkedin.com/search/results/people/"
    driver.get(search_url)

    try:
        # Enter the name in the search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-global-typeahead__input'))
        )
        search_box.clear()
        search_box.send_keys(name)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.search-results__list'))
        )

        # Locate and click the profile link with the exact name
        profile_elements = driver.find_elements(By.CSS_SELECTOR, 'li.search-result')
        for profile_element in profile_elements:
            try:
                profile_name = profile_element.find_element(By.CSS_SELECTOR, 'span.actor-name').text
                if profile_name == name:
                    profile_link = profile_element.find_element(By.CSS_SELECTOR, 'a.search-result__result-link')
                    profile_url = profile_link.get_attribute('href')
                    driver.get(profile_url)

                    # Fetch data from the profile
                    data = fetch_linkedin_data(driver)
                    return data
            except Exception as e:
                print(f"Error finding or clicking profile for {name}: {e}")

    except Exception as e:
        print(f"Error during search and fetch for {name}: {e}")
        return {}

def main():
    names = [
        "Ogechukwu, Tasie",
        "Ragland, Joy",
        "McCallum, Tymeeka",
        "Treski, Karin",
        "Byrd, Reah",
        "Keeter, Jessica",
        "Onyebinachi, Kingsley",
        "Mendez, Alex",
        "Martin, Djuvane",
        "McClellan, Alexis",
        "Davison, Arthur",
        "McCall, Cheri",
        "Martin, Justin",
        "Rich, Kiana",
        "Thiera, Taylor",
        "Cummings, Latoya",
        "Robinson, Nadia",
        "Green, Yvette",
        "Willie, T’uana",
        "Izzard, Atavia",
        "Houston, Bria"
    ]

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()

    # Navigate to LinkedIn login page
    url = "https://www.linkedin.com/"
    driver.get(url)

    # Prompt to complete manual login
    input("Please log in manually and press Enter to continue...")

    # Loop through each name and fetch data
    for name in names:
        print(f"Searching for: {name}")
        data = search_and_fetch(driver, name)

        if data:
            # Save the scraped data to the CSV file
            save_to_csv(data)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
