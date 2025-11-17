# This file manages sending email notifications for the UTodo application.
# Created 11/14/2025 and written by Landon Tidwell for CS-2351.

import os
import smtplib
import json
import logging
from datetime import date, timedelta, datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load credentials from environment variables
BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"

# Read the .env file and extract the environment variables
if ENV_FILE.exists():
	with open(ENV_FILE) as f:
		for line in f:
			# Skip empty lines or comments
			if line.strip() == "" or line.strip().startswith("#"):
				continue
			# Split on the first '='
			key, value = line.strip().split("=", 1)
			os.environ[key] = value  # store in environment variables

# Store environment variables now that accessible by cron
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PW")


# set up log config

logging.basicConfig(filename='utodo.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get the email address from the settings json file
def get_email_address():

	with open(f"{BASE_DIR}/data/settings.json", "r") as settings_file:
		settings_data = json.load(settings_file)

	return settings_data["Email"]

# Get the current date in MM/DD format
def get_date():

	today = date.today()
	return today

# Gets tomorrow's date in MM/DD format
def get_next_date():

	tomorrow = date.today() + timedelta(days=1)
	return tomorrow

# Get to-do lists and form body of string
def write_body():

	today = get_date().strftime("%m/%d")
	body_intro = ["Here is today's to-do list summary!\n\n",
		f"\t[ Tasks Due Today   {today} ]\n"]

	directory = Path(f"{BASE_DIR}/data")

	# Loop through to check for tasks due today
	tdlists = []
	tasks = []
	for file in directory.iterdir():

		# checks to make sure file is a text file (a to-do list)
		if file.is_file() and file.suffix == ".txt":
			none_due = True
			combined_tasks = ""
			tdlists.append(f"\n\t<> {file.stem.replace('_', ' ')}:\n") # add to to-do list array

			with open(f"{directory}/{file.stem}.txt", "r") as file: # open to-do list file

				for line in file.read().splitlines():

					task = line.split('|') # split by the | characters in data file
					task_date = datetime.strptime(task[1], "%Y-%m-%d").date()

					# check if task date is the same as today
					if task_date == get_date():
						none_due = False
						combined_tasks += f"\t- {task[0]} - {task[2]}\n"
			if none_due:
				tasks.append("\t\tNo tasks due today! All caught up!\n")
			else:
				tasks.append(combined_tasks)

	body_today = []
	i = 0
	for list in tdlists:
		body_today.append(list)
		body_today.append(tasks[i])
		i += 1

	# Same exact thing but for tasks due tomorrow
	tdlists = []
	tasks = []
	for file in directory.iterdir():

		# checks to make sure file is a text file (a to-do list)
		if file.is_file() and file.suffix == ".txt":
			none_due = True
			combined_tasks = ""
			tdlists.append(f"\n\t<> {file.stem.replace('_', ' ')}:\n") # add to to-do list array

			with open(f"{directory}/{file.stem}.txt", "r") as file: # open to-do list file

				for line in file.read().splitlines():

					task = line.split('|') # split by the | characters in data file
					task_date = datetime.strptime(task[1], "%Y-%m-%d").date()

					# check if task date is the same as today
					if task_date == get_next_date():
						none_due = False
						combined_tasks += f"\t- {task[0]} - {task[2]}\n"
			if none_due:
				tasks.append("\t\tNo tasks due today! All caught up!\n")
			else:
				tasks.append(combined_tasks)

	body_tomorrow = []
	i = 0
	tomorrow = get_next_date().strftime("%m/%d")
	body_tomorrow.append(f"\n\n\n\t[ Tasks Due Tomorrow   {tomorrow} ]\n")
	for list in tdlists:
		body_tomorrow.append(list)
		body_tomorrow.append(tasks[i])
		i += 1

	# Body conclusion
	body_conclusion = ["\n\nLet's have a productive day today!\n",
		"Be sure to log in and complete your tasks as necessary.\n"]

	# Combine body
	body = body_intro + body_today + body_tomorrow + body_conclusion
	combined_string = "".join(body)
	return combined_string

def send_email(to_email, subject, body):
	msg = MIMEMultipart()
	msg["From"] = EMAIL_ADDRESS
	msg["To"] = to_email
	msg["Subject"] = subject
	msg.attach(MIMEText(body, "plain"))

    	# Gmail SMTP server
	with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
		server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
		server.send_message(msg)

	logging.info("Email sent successfully using Gmail App Password!")

# Main program

# invokes send_email to connect to the gmail servers and send an email through the unixtodolist@gmail.com account
today = get_date().strftime("%m/%d")

send_email(
	to_email=get_email_address(),
	subject=f"Unix To-Do: Summary for {today}",
	body=write_body()
)
