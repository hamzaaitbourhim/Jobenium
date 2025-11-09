import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import urllib.parse
import logging
import os
import questionary
from questionary import Choice

def run():
    # Setup logging
    log_path = os.path.join(os.path.dirname(__file__), '../logs/history.log')
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M'
    )

    # Load configurations and get input
    config_path = os.path.join(os.path.dirname(__file__), '../configs/config.json')
    with open(config_path, "r") as file:
        config = json.load(file)
    EMAIL = config["email"]
    PASSWORD = config["hellowork_password"]
    KEYWORD = questionary.text("Enter the job keyword:").ask()
    encoded_keyword = urllib.parse.quote_plus(KEYWORD)

    contract_choices = {
        "CDI": "CDI",
        "CDD": "CDD",
        "Alternance": "Alternance",
        "Stage": "Stage",
        "Freelance": "Freelance",
        "Intérim": "Travail_temp"
    }
    selected_contracts = questionary.checkbox(
        "Select contract types:",
        choices=list(contract_choices.keys())
    ).ask()
    CONTRACT_TYPE_PARAMS = "&" + "&".join(f"c={contract_choices[c]}" for c in selected_contracts) if selected_contracts else ""

    sorting_choices = {
        "Date": "date",
        "Score": "relevance"
    }
    SORT_BY = questionary.select(
        "Sort jobs by:",
        choices=[
            Choice(title=label, value=code) for label, code in sorting_choices.items()
        ]
    ).ask()

    timeout_input = questionary.text("Enter max runtime in minutes :").ask()
    try:
        timeout_minutes = float(timeout_input)
        TIME_OUT = int(timeout_minutes * 60)
    except:
        print("Invalid input. Defaulting to 5 hours.")
        TIME_OUT = 5 * 60 * 60

    # URLs
    LOGIN_URL = "https://www.hellowork.com/fr-fr/candidat/connexion-inscription.html#connexion"
    BASE_SEARCH_URL = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={encoded_keyword}&k_autocomplete=&l=France&l_autocomplete=http%3A%2F%2Fwww.rj.com%2Fcommun%2Flocalite%2Fpays%2FFR&st={SORT_BY}{CONTRACT_TYPE_PARAMS}&ray=all&d=all&p="

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
        try:
        # Login
            driver.get(LOGIN_URL)
            
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
            logging.info("HelloWork Session started.")

        except Exception:
            logging.error("HelloWork login failed.")
            print("HelloWork login failed.")
            driver.close()  # Close the browser tab
            driver.quit()   # Quit the WebDriver instance

        page = 1
        while True:
            if time.time() - start_time > TIME_OUT:
                break
            try:
                driver.get(f"{BASE_SEARCH_URL}{page}")
                job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@aria-label='liste des offres']/li")))
            except Exception:
                break

            # Process each job on the page
            for i in range(len(job_list)):
                if time.time() - start_time > TIME_OUT:
                    break
                try:

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
                        applied_count += 1  # Increment count
                    except:
                        success_message = None

                    # Return to the job list
                    processed_count += 1
                    print(f"\rJobs processed: {processed_count}, Jobs applied to: {applied_count}", end='', flush=True)
                    driver.get(f"{BASE_SEARCH_URL}{page}")
                    time.sleep(1)

                except Exception as e:
                    processed_count += 1
                    # Return to the job list
                    print(f"\rJobs processed: {processed_count}, Jobs applied to: {applied_count}", end='', flush=True)
                    driver.get(f"{BASE_SEARCH_URL}{page}")
                    time.sleep(1)
                    continue
            
            # Pagination logic
            page += 1
            time.sleep(3)

    except Exception as e:
        logging.error("HelloWork error occurred.")
        print("HelloWork error occurred")

    finally:
        try:
            logging.info(f"HelloWork Session ended. Total jobs applied to: {applied_count}")
            driver.close()  # Close the browser tab
            driver.quit()   # Quit the WebDriver instance
        except Exception as e:
            pass
