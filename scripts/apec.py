import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import urllib.parse
import logging
import os
import questionary

def run():
    # Setup logging
    log_path = os.path.join(os.path.dirname(__file__), '../logs/history.log')
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M'
    )

    # Load configurations from the external file
    config_path = os.path.join(os.path.dirname(__file__), '../configs/config.json')
    with open(config_path, "r") as file:
        config = json.load(file)
    EMAIL = config["email"]
    PASSWORD = config["apec_password"]
    KEYWORD = questionary.text("Enter the job keyword:").ask()
    encoded_keyword = urllib.parse.quote_plus(KEYWORD)

    contract_choices = {
        "CDI": "101888",
        "CDD": "101887",
        "Alternance": "20053",
        "Intérim": "101930"
    }
    CONTRACT_TYPE = questionary.select(
        "Select contract type:",
        choices=[
            questionary.Choice(title=label, value=code) for label, code in contract_choices.items()
        ]
    ).ask()

    sorting_choices = {
        "Date": "DATE",
        "Score": "SCORE"
    }
    SORT_BY = questionary.select(
        "Sort jobs by:",
        choices=[
            questionary.Choice(title=label, value=code) for label, code in sorting_choices.items()
        ]
    ).ask()

    timeout_input = questionary.text("Enter max runtime in minutes :").ask()
    try:
        timeout_minutes = float(timeout_input)
        TIME_OUT = int(timeout_minutes * 60)
    except:
        print("Invalid input. Defaulting to 5 hours.")
        TIME_OUT = 5 * 60 * 60

    # Constants
    LOGIN_URL = "https://www.apec.fr/"
    BASE_SEARCH_URL = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?typesConvention=143684&typesConvention=143685&typesConvention=143686&typesConvention=143687&typesConvention=143706&motsCles={encoded_keyword}&typesContrat={CONTRACT_TYPE}&niveauxExperience=101881&sortsType={SORT_BY}&page="

    # Initialize WebDriver
    options = uc.ChromeOptions()
    #options.add_argument('--headless=new')  # headless mode
    #options.add_argument('--disable-gpu') 
    driver = uc.Chrome(version_main=140, options=options)
    wait = WebDriverWait(driver, 10)
    driver.maximize_window()

    # Track job applications
    applied_count = 0
    processed_count = 0
    start_time = time.time()  # Record the start time

    try:
        # Login
        try:
            driver.get(LOGIN_URL)
            
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
            logging.info("APEC Session started.")
            
        except Exception:
            logging.error("APEC login failed.")
            print("APEC login failed.")
            driver.close()  # Close the browser tab
            driver.quit()   # Quit the WebDriver instance

        page = 0
        while True:
            if time.time() - start_time > TIME_OUT:
                break
            try:
                driver.get(f"{BASE_SEARCH_URL}{page}")
                job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='container-result']/div")))
            except Exception:
                break

            # Process each job on the page
            for i in range(len(job_list)):
                if time.time() - start_time > TIME_OUT:
                    break
                try:
                    # Refresh the job list to avoid stale elements
                    job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='container-result']/div")))
                    job = job_list[i]

                    # Scroll to the job element
                    driver.execute_script("arguments[0].scrollIntoView();", job)

                    # Click on the job
                    job_link = job.find_element(By.XPATH, ".//a[@queryparamshandling='merge']")
                    driver.execute_script("arguments[0].click();", job_link)

                    # Click the "Postuler" button
                    apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn-primary mr-12 mb-20']")))

                    if apply_button.text == "Postuler":
                        apply_button.click()
                        time.sleep(1)
                        # Click the "Postuler" button on the second page
                        apply_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Postuler']")))
                        apply_button2.click()
                        time.sleep(1)

                        try:
                            # Click the "Envoyer ma candidature" button on the third page
                            apply_button3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Envoyer ma candidature']")))
                            apply_button3.click()
                            applied_count += 1  # Increment count
                        except TimeoutException:
                            pass

                    # Return to the job list
                    processed_count += 1
                    print(f"\rJobs processed: {processed_count}, Jobs applied to: {applied_count}", end='', flush=True)
                    driver.get(f"{BASE_SEARCH_URL}{page}")
                    time.sleep(1)

                except Exception as e:
                    # Return to the job list
                    processed_count += 1
                    print(f"\rJobs processed: {processed_count}, Jobs applied to: {applied_count}", end='', flush=True)
                    driver.get(f"{BASE_SEARCH_URL}{page}")
                    time.sleep(1)
                    continue

            # Pagination logic
            page += 1
            time.sleep(3)

    except Exception as e:
        logging.error("APEC error occurred.")
        print(f"\nAn error occurred.")

    finally:
        try:
            logging.info(f"APEC Session ended. Total jobs applied to: {applied_count}")
            driver.close()  # Close the browser tab
            driver.quit()   # Quit the WebDriver instance
        except Exception as e:
            pass
