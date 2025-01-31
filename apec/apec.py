import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import urllib.parse

# Load configurations from the external file
with open("apec-config.json", "r") as file:
    config = json.load(file)

EMAIL = config["email"]
PASSWORD = config["password"]
KEYWORD = config["keyword"]

# Encode the keyword for URL
encoded_keyword = urllib.parse.quote_plus(KEYWORD)

# Constants
LOGIN_URL = "https://www.apec.fr/"

BASE_SEARCH_URL = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?typesConvention=143684&typesConvention=143685&typesConvention=143686&typesConvention=143687&typesConvention=143706&motsCles={encoded_keyword}&typesContrat=101888&niveauxExperience=101881&sortsType=SCORE&page=" # sortsType=SCORE/DATE

# Initialize WebDriver
driver = uc.Chrome()
wait = WebDriverWait(driver, 10)
driver.maximize_window()

try:
    # Login to the website
    try:
        driver.get(LOGIN_URL)
        print("Logging in...")
        
        cookies_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Autoriser tous les cookies')]")))
        cookies_button.click()

        login_popup_button = driver.find_element(By.XPATH, "//a[@onclick='showloginPopin()']")
        login_popup_button.click()

        email_input = wait.until(EC.presence_of_element_located((By.NAME, "emailid")))
        email_input.clear()
        email_input.send_keys(EMAIL)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.clear()
        password_input.send_keys(PASSWORD)

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Se connecter')]")))
        login_button.click()

        time.sleep(5)
        print("Login successful!\n")
        
    except Exception:
        print("Problem Login.")
        driver.close()  # Close the browser tab
        driver.quit()   # Quit the WebDriver instance


    page = 0
    while True:
        try:
            driver.get(f"{BASE_SEARCH_URL}{page}")
            job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='container-result']/div")))
        except Exception:
            print("No more pages.")
            break

        # Process each job on the page
        for i in range(len(job_list)):
            try:
                print(f"Processing job {i + 1} on page {page + 1}...")

                # Refresh the job list to avoid stale elements
                job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='container-result']/div")))
                job = job_list[i]

                # Scroll to the job element
                driver.execute_script("arguments[0].scrollIntoView();", job)

                # Click on the job
                job_link = job.find_element(By.XPATH, ".//a[@queryparamshandling='merge']")
                driver.execute_script("arguments[0].click();", job_link)

                # Wait for the application form to load
                #time.sleep(2)

                # Click the "Postuler" button
                apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn-primary mr-12 mb-20']")))

                if apply_button.text == "Postuler":
                    apply_button.click()
                    time.sleep(1)
                    # Click the "Postuler" button on the second page
                    apply_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Postuler']")))
                    apply_button2.click()
                    time.sleep(1)
                    # Click the "Envoyer ma candidature" button on the third page
                    apply_button3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Envoyer ma candidature']")))
                    apply_button3.click()

                # Wait for the response
                time.sleep(1)

                # Check for success or "Already applied" message
                try:
                    success_message = driver.find_element(By.XPATH, "//p[text()='Votre candidature a été transmise au recruteur.']")
                    print(f"Successfully applied.\n")
                except:
                    print(f"Can't apply on apec.\n")

                # Return to the job list
                driver.get(f"{BASE_SEARCH_URL}{page}")
                time.sleep(1)

            except Exception as e:
                print(f"already applied.\n")
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
