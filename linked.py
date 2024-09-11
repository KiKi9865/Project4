from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
import re
import yaml

import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Load credentials from credentials.yaml
with open("credentials.yaml", 'r') as stream:
    credentials = yaml.safe_load(stream)

google_email = credentials['google']['email']
google_password = credentials['google']['password']

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open LinkedIn login page
driver.get("https://www.linkedin.com/login")

time.sleep(5)
# Click on 'Sign in with Google' button
google_sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(),'Sign in with Google')]")
google_sign_in_button.click()

# Switch to Google login window
driver.switch_to.window(driver.window_handles[1])

# Enter Google email
email_input = driver.find_element(By.ID, "identifierId")
email_input.send_keys(google_email)
email_input.send_keys(Keys.RETURN)

# Wait for the password field to be present and enter the password
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys(google_password)
password_input.send_keys(Keys.RETURN)

# Switch back to LinkedIn window
driver.switch_to.window(driver.window_handles[0])

# Wait for user confirmation before continuing
input("Log in via Google, then press Enter here to continue...")

def fetch_profile_data_selenium(driver, url):
    driver.get(url)
    time.sleep(5)  # Wait for page to load

    profile_data = {}

    try:
        name_element = driver.find_element(By.CSS_SELECTOR, 'li.inline.t-24.t-black.t-normal.break-words')
        profile_data['name'] = name_element.text.strip()
    except:
        profile_data['name'] = 'N/A'
    
    try:
        headline_element = driver.find_element(By.CSS_SELECTOR, 'h2.mt1.t-18.t-black.t-normal')
        profile_data['headline'] = headline_element.text.strip()
    except:
        profile_data['headline'] = 'N/A'

    print(f"Profile data from {url}: {profile_data}")
    return profile_data

def google_linkedin_search(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    search_url = f"https://www.google.com/search?q=site:linkedin.com+{query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    linkedin_urls = set()  # Use a set to avoid duplicate profiles
    linkedin_pattern = re.compile(r'https://www\.linkedin\.com/in/[^&"]+')
    
    for result in soup.find_all('a', href=True):
        link = result['href']
        matches = linkedin_pattern.findall(link)
        for match in matches:
            linkedin_urls.add(match)  # Add to set (automatically handles duplicates)
    
    return linkedin_urls

def filter_links_by_name(linkedin_urls, name):
    filtered_urls = []
    name_lower = name.lower()
    
    for url in linkedin_urls:
        if name_lower in url.lower():  # Check if name appears in the URL
            filtered_urls.append(url)
    
    return filtered_urls

driver = webdriver.Chrome()

# Load credentials from credentials.yaml
with open("credentials.yaml", 'r') as stream:
    credentials = yaml.safe_load(stream)

linkedin_username = credentials['linkedin']['username']
linkedin_password = credentials['linkedin']['password']

# Initialize the WebDriver (e.g., Chrome)

# Open LinkedIn login page
driver.get("https://www.linkedin.com/login")

# # Enter username
# username_input = driver.find_element(By.ID, "username")
# username_input.send_keys(linkedin_username)

# # Enter password
# password_input = driver.find_element(By.ID, "password")
# password_input.send_keys(linkedin_password)

# # Click the login button
# password_input.send_keys(Keys.RETURN)

# Wait for some time to ensure login completes
time.sleep(5)
input("Login to LinkedIn manually, then press Enter here to continue...")

names = ['Djuvane Martin', 'Chris Readus', 'Frank Pabelonio']
all_profiles = set()

try:
    for name in names:
        profile_links = google_linkedin_search(name)
        filtered_links = filter_links_by_name(profile_links, name)
        all_profiles.update(filtered_links)
    
    for profile_url in all_profiles:
        fetch_profile_data_selenium(driver, profile_url)
        time.sleep(5)  # Avoid making requests too quickly

finally:
    driver.quit()
