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

    # Load configurations from the external file
    config_path = os.path.join(os.path.dirname(__file__), '../configs/config.json')
    with open(config_path, "r") as file:
        config = json.load(file)
    EMAIL = config["email"]
    PASSWORD = config["jobteaser_password"]
    KEYWORD = questionary.text("Enter the job keyword:").ask()
    encoded_keyword = urllib.parse.quote_plus(KEYWORD)

    # Constants
    LOGIN_URL = "https://connect.jobteaser.com/?client_id=e500827d-07fc-4766-97b4-4f960a2835e7&nonce=dcbdb1d4b01e9159c31d738e4eb687bc&organization_domain=public&redirect_uri=https%3A%2F%2Fwww.jobteaser.com%2Fusers%2Fauth%2Fconnect%2Fcallback&response_type=code&scope=openid+email+profile+groups+urn%3Aconnect%3Ajobteaser%3Acom%3Aorganization+urn%3Aconnect%3Ajobteaser%3Acom%3Aextra_attributes&state=25f41a664373a5086e61494fc4bf31d2&ui_locales=fr"
    BASE_SEARCH_URL = f"https://www.jobteaser.com/fr/job-offers?candidacy_type=INTERNAL&q={encoded_keyword}&sort=recency&page="

    # Initialize WebDriver
    options = uc.ChromeOptions()
    #options.add_argument('--headless=new')  # headless mode
    #options.add_argument('--disable-gpu') 
    driver = uc.Chrome(version_main=140, options=options)
    wait = WebDriverWait(driver, 10)
    driver.maximize_window()

    # Track job applications
    applied_count = 0
    start_time = time.time()  # Record the start time
    TIME_OUT = 60 * 120 # Timeout in seconds

    try:
        try:
        # Login
            driver.get(LOGIN_URL)
            
            accept_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
            accept_button.click()
            
            email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_input.clear()
            email_input.send_keys(EMAIL)

            password_input = wait.until(EC.presence_of_element_located((By.ID, "passwordInput")))
            password_input.clear()
            password_input.send_keys(PASSWORD)

            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Connexion')]")))
            login_button.click()

            connect_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'JobTeaser Connect')]")))
            connect_button.click()

            time.sleep(2)
            logging.info("JobTeaser Session started.")
            print("JobTeaser Session started.")

        except Exception:
            logging.error("JobTeaser login failed.")
            print("JobTeaser login failed.")
            driver.close()  # Close the browser tab
            driver.quit()   # Quit the WebDriver instance

        page = 1
        while True:
            if time.time() - start_time > TIME_OUT:
                break
            try:
                driver.get(f"{BASE_SEARCH_URL}{page}")
                job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='PageContent_results__zSSNO']/li")))
            except Exception:
                break

            # Process each job on the page
            for i in range(len(job_list)):
                if time.time() - start_time > TIME_OUT:
                    break
                try:
                    # Refresh the job list to avoid stale elements
                    job_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='PageContent_results__zSSNO']/li")))
                    job = job_list[i]

                    # Scroll to the job element
                    driver.execute_script("arguments[0].scrollIntoView();", job)

                    # Click on the job
                    job_link = job.find_element(By.XPATH, ".//a[@class='JobAdCard_link__n5lkb']")
                    driver.execute_script("arguments[0].click();", job_link)
                    time.sleep(2)

                    # Click the "Postuler" button
                    apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='jobad-DetailView__CandidateActions__Buttons_apply_internal_candidacy']")))
                    apply_button.click()
                    time.sleep(1)
                    apply_button2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='jobad-DetailView__ApplicationFlow__Buttons__apply_button']")))
                    apply_button2.click()

                    # Wait for the response
                    time.sleep(3)
                    applied_count += 1  # Increment count

                    # Return to the job list
                    driver.get(f"{BASE_SEARCH_URL}{page}")
                    time.sleep(1)

                except Exception as e:
                    # Return to the job list
                    driver.get(f"{BASE_SEARCH_URL}{page}")
                    time.sleep(1)
                    continue

            # Pagination logic
            page += 1
            time.sleep(3)

    except Exception as e:
        logging.error("JobTeaser error occurred.")
        print("JobTeaser error occurred.")


    finally:
        try:
            logging.info(f"JobTeaser Session ended. Total jobs applied to: {applied_count}")
            print(f"JobTeaser Session ended. Total jobs applied to: {applied_count}")
            driver.close()  # Close the browser tab
            driver.quit()   # Quit the WebDriver instance
        except Exception as e:
            pass