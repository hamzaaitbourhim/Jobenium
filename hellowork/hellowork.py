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
driver = uc.Chrome(version_main=134)
wait = WebDriverWait(driver, 10)
driver.maximize_window()

try:
    try:
    # Login
        driver.get(LOGIN_URL)
        print("Logging in...")
        
        accept_button = wait.until(EC.element_to_be_clickable((By.ID, "hw-cc-notice-accept-btn")))
        accept_button.click()
        
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email2")))
        email_input.clear()
        email_input.send_keys(EMAIL)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password2")))
        password_input.clear()
        password_input.send_keys(PASSWORD)

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Je me connecte')]")))
        login_button.click()

        time.sleep(30)
        print("Login successful!\n")

    except Exception:
        print("Problem Login.")
        driver.close()  # Close the browser tab
        driver.quit()   # Quit the WebDriver instance

    page = 1
    while True:
        try:
            driver.get(f"{BASE_SEARCH_URL}{page}")
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

                # Get the current URL and append "#postuler"
                current_url = driver.current_url
                new_url = current_url + "#postuler"
                driver.get(new_url)
                time.sleep(3)

                # Click the "Postuler" button
                apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-cy='submitButton']")))
                apply_button.click()

                # Wait for the response
                time.sleep(3)

                try:
                    # Check for the first paragraph
                    success_message = driver.find_element(By.XPATH, "//p[contains(text(), 'Félicitations ! Votre candidature')]")
                    print(f"Successfully applied.\n")
                except:
                    success_message = None

                try:
                    # Check for the second paragraph
                    already_applied_message = driver.find_element(By.XPATH, "//p[contains(text(), 'Vous avez déjà postulé')]")
                    print(f"already applied.\n")
                except:
                    already_applied_message = None

                # Return to the job list
                driver.get(f"{BASE_SEARCH_URL}{page}")
                time.sleep(1)

            except Exception as e:
                print(f"Can't apply on hellowork.\n")
                # Return to the job list
                driver.get(f"{BASE_SEARCH_URL}{page}")
                time.sleep(1)
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
