import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import urllib.parse

# Load configurations from the external file
with open("hellowork-config.json", "r") as file:
    config = json.load(file)

EMAIL = config["email"]
PASSWORD = config["password"]
FIRST_NAME = config["first_name"]
LAST_NAME = config["last_name"]
KEYWORD = config["keyword"]
CONTRACT_TYPE = config["contract_type"]

# Encode the keyword for URL
encoded_keyword = urllib.parse.quote_plus(KEYWORD)

# Constants
LOGIN_URL = "https://www.hellowork.com/fr-fr/candidat/connexion-inscription.html#connexion"
BASE_SEARCH_URL = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={encoded_keyword}&k_autocomplete=&l=France&l_autocomplete=http%3A%2F%2Fwww.rj.com%2Fcommun%2Flocalite%2Fpays%2FFR&st=date&c={CONTRACT_TYPE}&ray=all&d=all&p="

# Initialize WebDriver
driver = uc.Chrome()
wait = WebDriverWait(driver, 10)

try:
    # Login
    driver.get(LOGIN_URL)
    driver.maximize_window()
    try:
        accept_button = wait.until(EC.element_to_be_clickable((By.ID, "hw-cc-notice-accept-btn")))
        accept_button.click()
    except Exception:
        print("No cookie modal displayed.")

    email_input = wait.until(EC.presence_of_element_located((By.NAME, "email2")))
    email_input.clear()
    email_input.send_keys(EMAIL)

    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password2")))
    password_input.clear()
    password_input.send_keys(PASSWORD)

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Je me connecte')]")))
    login_button.click()

    time.sleep(60)
    print("Login successful!")

    page = 1
    while True:
        try:
            driver.get(f"{BASE_SEARCH_URL}{page}")
            print(f"Processing page {page}...")
            job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@aria-label='liste des offres']/li")))
        except Exception:
            print("No more pages.")
            break

        # Process each job on the page
        for i in range(len(job_list)):
            try:
                print(f"Processing job {i + 1} on page {page}...")

                # Refresh the job list to avoid stale elements
                job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@aria-label='liste des offres']/li")))
                job = job_list[i]

                # Scroll to the job element
                driver.execute_script("arguments[0].scrollIntoView();", job)

                # Click on the job
                job_link = job.find_element(By.XPATH, ".//a[@data-cy='offerTitle']")
                driver.execute_script("arguments[0].click();", job_link)

                # Wait for the application form to load
                time.sleep(10)

                # Click the "Postuler" button
                apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-cy='submitButton']")))
                apply_button.click()

                # Wait for the response
                time.sleep(5)

                # Check for success or "Already applied" message
                try:
                    success_message = driver.find_element(By.CLASS_NAME, "message-rebond.ok")
                    print(f"Successfully applied for job {i + 1} on page {page}.")
                except:
                    try:
                        already_applied_message = driver.find_element(By.CLASS_NAME, "message-rebond__container")
                        if "Vous avez déjà postulé" in already_applied_message.text:
                            print(f"Already applied for job {i + 1} on page {page}.")
                    except Exception as e:
                        print(f"Error checking application result for job {i + 1} on page {page}.")

                # Return to the job list
                driver.get(f"{BASE_SEARCH_URL}{page}")
                time.sleep(5)

            except Exception as e:
                print(f"Error processing job {i + 1} on page {page}.")
                # Return to the job list
                driver.get(f"{BASE_SEARCH_URL}{page}")
                time.sleep(5)
                continue

        # Pagination logic
        page += 1
        time.sleep(3)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    try:
        driver.close()  # Close the browser tab
        driver.quit()   # Quit the WebDriver instance
    except Exception as e:
        print(f"Error during cleanup: {e}")
