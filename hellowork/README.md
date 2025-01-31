# Hellowork Automated Job Application Script

This project automates job applications on [Hellowork](https://www.hellowork.com) using Selenium with undetected Chromedriver. It processes jobs based on specified criteria and applies to each one.

## Features
- Automatically logs in to your Hellowork account.
- Searches for jobs based on a specified keyword and contract type.
- Iterates through job pages and applies to available jobs.
- Handles already-applied scenarios gracefully.
- Uses an external configuration file for sensitive data and customizable parameters.

## Prerequisites

### 1. Install Python
Make sure you have Python 3.8 or higher installed. You can download it from [python.org](https://www.python.org/).

### 2. Install Required Libraries
Install the required Python libraries using `pip`:
```bash
pip install selenium undetected-chromedriver
```

### 3. Hellowork Account
You need a valid Hellowork account with your CV uploaded.

## Files

### 1. hellowork.py
This is the main script that:
- Reads configurations from hellowork-config.json.
- Logs into your Hellowork account.
- Searches and applies for jobs based on specified criteria.

### 2. hellowork-config.json
A configuration file that stores sensitive and customizable information (replace the placeholder values with your actual details).

## Usage

### Step 1: Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/hamzaaitbourhim/Jobenium.git
cd Jobenium/hellowork
```

### Step 2: Set Up the Configuration File
Edit the hellowork-config.json file with your personal details:

- `email`: Your Hellowork account email.
- `password`: Your Hellowork account password.
- `first_name`: Your first name.
- `last_name`: Your last name.
- `keyword`: The job keyword you want to search for (e.g., java).
- `contract_type`: The type of contract to search for (e.g., CDI, CDD, Stage, Alternance, or Travail_temp).

### Step 3: Run the Script
Run the script using Python:
```bash
python hellowork.py
```

### Step 4: Monitor the Process
Monitor the output in your terminal. The script will log:
- Which job it is processing.
- Whether the application was successful or if you already applied.

## Troubleshooting
If you encounter any issues:
- Verify your credentials in hellowork-config.json.
- Check if the required Python libraries are installed.
- Ensure that the Hellowork website layout hasn't changed significantly.
  
Feel free to report issues or contribute to the project!
