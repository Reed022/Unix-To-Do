import sys
import os
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# set up log config

logging.basicConfig(filename='utodo.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# return the number of to-do lists stored
def get_num_lists():

	num_lists = 0

	directory = Path("data")

	# iterate through files in data subdirectory and count them
	for file in directory.iterdir():
		if file.is_file() and file.suffix == ".txt":
			num_lists += 1

	return num_lists

# return the number of tasks in to-do list passed as arg list_num
def get_num_tasks(list_name):

	line_count = 0
	with open(f"data/{list_name.replace(' ', '_')}.txt", "r") as file: # open file with name given
		line_count = sum(1 for line in file) # sum the lines
	return line_count

# return a list of to-do lists
def get_lists():
	directory = Path("data")

	# iterates through the files in the subdirectory /data and stores in list tdlists
	i = 1
	tdlists = []
	for file in directory.iterdir():
		if file.is_file() and file.suffix == ".txt":
			tdlists.append(file.stem.replace('_', ' '))
			i += 1
	return tdlists

# return a dictionary of tasks in a to-do list
def get_tasks(list_name):
	tasks = {}
	i = 1
	with open(f"data/{list_name.replace(' ', '_')}.txt", "r") as file: # reads every line in the to-do list's file
		for line in file.read().splitlines():
			tasks[f"{i}"] = line # set each entry in dict
			i += 1
	return tasks

# displays navigation footer 
# Args: True=display main menu navigation msg, False=no main menu navigation msg
def display_nav_footer(main_menu):
	if main_menu:
		print("Type 'M' to return to main menu")
	print("Type 'Q' to exit")

# displays main menu selection screen
def display_main_menu():
	print("\n-------- UNIX TO DO LIST --------\n")
	print("[1] View to-do lists")
	print("[2] Create new to-do list")
	print("[3] Notification settings")
	print("\n---------------------------------")
	display_nav_footer(False)

# displays to-do lists
def display_lists():

	if get_num_lists() == 0:
		print("\n----------- TO-DO LISTS -----------\n")
		print("\tNo active to-do lists.")
		print("\n-----------------------------------\n")
	else:

		print("\n----------- TO-DO LISTS -----------\n")

		directory = Path("data")

		# iterates through the files in the subdirectory /data and prints their names

		tdlists = get_lists()
		i = 1
		for list in tdlists:
			print(f"[{i}] {list}")

			i += 1

		print("\n-----------------------------------\n")

	display_nav_footer(True)

# displays tasks for to-do list passed in as arg list_num
def display_tasks(list_name):

	if get_num_tasks(list_name) == 0:
		print(f"\n----------- {list_name} -----------\n")
		print("\tNo active tasks in this to-do list.")
		print("\n------------------------------------\n")
	else:

		print(f"\n----------- {list_name} -----------\n")

		# iterates through tasks and prints them
		tasks = get_tasks(list_name)
		i = 1
		for task in tasks.values():
			task_name = task.split('|')[0] # gets everything in the string before the first '|' char... the task name
			print(f"[{i}] {task_name}")
			i += 1

		print("\n------------------------------------\n")

	print("Type 'C' to create a new task")
	print("Type 'D' to delete the entire to-do list (Irreversible!)")
	display_nav_footer(True)

# displays a specific task's details within a to-do list
def display_task(list_name, task_num):
	# get the tasks for that list, get task data and split into strings
	tasks = get_tasks(list_name)
	task_details = tasks.get(str(task_num)).split('|')
	task_details[2].strip()

	# print task information
	print(f"------------ {task_details[0]} ------------")
	print(f"Description: {task_details[2]}")
	print(f"Due date: {task_details[1]}")
	print("----------------------------------------\n")

# parses input for a date in MM/DD/YYYY format
def get_valid_date():
	while True:
		user_input = input()
		try:
			# Try to parse this input according to the format specified...
			date = datetime.strptime(user_input, "%m/%d/%Y").date()
			print("Valid date entered.")
			return date
		except ValueError:
			print("Invalid format! Please enter a date in format MM/DD/YYYY")

# parses input for a time in HH:MM format
def get_valid_time():
	while True:
		user_input = input()
		try:
			# Try to parse this input according to the format specified...
			time = datetime.strptime(user_input, "%H:%M").time()
			print("Valid time entered.")
			return time
		except ValueError:
			print("Invalid format! Please enter a time in format HH:MM")

# writes the file for a new to-do list
def create_new_list(list_name):

	# make the file path
	file_name = list_name.replace(' ', '_')
	file_path = f"data/{file_name}.txt"

	# create the file with given file path
	open(file_path, "w").close()
	return file_path

# deletes the file for a to-do list
def delete_list(list_name):

	# make the file path
	file_name = list_name.replace(' ', '_')
	file_path = Path(f"data/{file_name}.txt")

	# PERMANENTLY delete the file with given file path
	if file_path.exists():
		file_path.unlink(missing_ok=True) # if somehow an error is thrown, nothing happens and silent
		print("File deleted successfully!")
		return True
	else:
		print("File does not exist.")
		return False

# prompts information for a new task and stores in the appropriate to-do list file
def create_new_task(list_name):


	print("What would you like to name your task? (Keep it short - under 50 characters recommended)")
	name = input()
	print("When would you like this task to be due?")
	print("|  Date format:   MM/DD/YYYY")
	print("|  Example:   11/02/2025   ---   \"November 2, 2025\"")
	print("If you would like to skip this step, type 'S'")
	date = get_valid_date() # take input for a date and validate it
	print(f"Due date set to {date}")
	print("Give your new task a short description:")
	description = input()

	tasks = get_tasks(list_name)
	task = f"{name}|{date}|{description}\n" # task as should appear in file

	# Check to see if exact task already exists in the to-do list -- returns True if it finds a match
	task_exists = any(task.strip() == t.strip() for t in tasks.values())

	if task_exists:
		print("This exact task already exists! Try again.")
		print("Task creation unsuccessful.")
	else:
		# display summary of task ...
		print("You have successfully created a task! View your new task below:\n")
		print(f"{name} | Due: {date} | {description}\n")

		# implement storing this data
		print("Saving new task . . .")

		# make the file path
		file_name = list_name.replace(' ', '_')
		file_path = f"data/{file_name}.txt"

		# open the file and append new task to it
		with open(file_path, "a") as list:
			list.write(task)

		print("Task saved! Returning to list menu.")

# overwrites appropriate to-do list file without the specified task
def delete_task(list_name, task_num):

	tasks = get_tasks(list_name)
	task = tasks.get(str(task_num))

	# make file path
	file_name = list_name.replace(' ', '_')
	file_path = f"data/{file_name}.txt"

	# open file and write its contents to an array
	with open(file_path, "r") as list:
		current_tasks = list.readlines()

	# overwrite the file without the task to be deleted
	with open(file_path, "w") as new_list:
		for line in current_tasks:
			if task not in line:
				new_list.write(line)

	print("Task removed!")

# overwrites the file with new information for a given task
def edit_task(list_name, task_num):

	# store current task data... will be written over in editing
	tasks = get_tasks(list_name)
	task_details = tasks.get(str(task_num)).split('|')
	task_details[2].strip() # strips newline character from description

	# these are still old values, but will be overwritten in editing
	new_name = task_details[0]
	new_date = task_details[1]
	new_description = task_details[2]

	display_task(list_name, task_num)

	editing = True
	while editing:

		print("[1] Name")
		print("[2] Due Date")
		print("[3] Description")
		print("\nSelect an option. Type \"done\" when finished editing:")
		option = input()

		# allow user to select edit option
		match option.lower():
			case "1":
				new_name = input("Enter a new name for this task: ")
				print(f"New task name set to: {new_name}.")
			case "2":
				print("Enter a new due date and time for this task.")
				print("|  Date format:   MM/DD/YYYY")
				print("|  Example:   11/02/2025   ---   \"November 2, 2025\"")
				new_date = get_valid_date()
				print(f"New task due date set to {new_date}")
			case "3":
				new_description = input("Enter a new description for this task:\n")
				print(f"New task description set to: {new_description}")
			case "done":
				editing = False
				print("Editing complete!")
			case _:
				print("That is not a valid edit option.")
		if editing:
			# print NEW task information
			print(f"------------ {new_name} ------------")
			print(f"Description: {new_description}")
			print(f"Due date: {new_date}")
			print("----------------------------------------\n")


	# display summary of task ...
	print("View the edited task below:\n")
	print(f"{new_name} | Due: {new_date} | {new_description}\n")
	print("\nSaving task . . .\n")

	# parse details and store in tasks
	new_task = f"{new_name}|{new_date}|{new_description}" # task as should appear in file
	tasks[str(task_num)] = new_task

	# make file path
	file_name = list_name.replace(' ', '_')
	file_path = f"data/{file_name}.txt"

	# overwrite list file to store new edited data
	with open(file_path, "w") as list:
		list.writelines(f"{task}\n" for task in tasks.values())

	print("Task saved! Returning to list menu.")

# display a task and prompt user to complete task, edit task, or return
def view_task(list_name, task_num):

	# eventually input data for task... for now placeholder data
	display_task(list_name, task_num)
	print("Type 'C' to complete/delete this task")
	print("Type 'E' to edit the details of this task")
	print("Type 'L' to return to list menu")
	display_nav_footer(True)

	# tasks = get_tasks(list_name)

	while True:
		option = input("\nSelect a menu option: ")

		# check option
		match option.lower():
			case 'c':
				delete_task(list_name, task_num)
				return
			case 'e':
				print("Editing task")
				edit_task(list_name, task_num)
				return
			case 'l':
				return 'l'
			case 'm':
				return 'm'
			case 'q':
				return 'q'
			case _:
				print("Invalid option.")

def call_cron_edit():
	try:
    		result = subprocess.run(['/bin/bash', 'utodo_cron_edit'], capture_output=True, text=True, check=True)
    		if result.stderr:
        		logging.error("Script errors:")
        		logging.error(result.stderr)
	except subprocess.CalledProcessError as e:
    		logging.error(f"Error executing script: {e}")
    		logging.error(f"Stderr: {e.stderr}")

# main program:
running = True
current_menu = "main" # by default, main menu

if not os.path.exists("data"):
	# means program has never been run... make necessary files
	print("Program startup:")

	os.makedirs("data") # make data directory
	print("- Data directory initialized.")

	# eventually have it initialize the settings json file as well
	print("\nConfigure your notification settings before beginning.")
	print("Please enter an email to use for task notifications:")
	email = input()

	print("Please enter a time you would like to receive notifications.")
	print("Time will be on the day the task is set due.")
	print("- Time format: HH:MM   24-hour format")
	print("- Example times:   Midnight: 00:00     10:30am: 10:30     5:00pm: 17:00")
	time = get_valid_time().strftime("%H:%M")

	settings_data = {
		"Email": email,
		"Time": time
	}

	with open("data/settings.json", "w") as settings_file:
		json.dump(settings_data, settings_file, indent=4)

	# Runs cron edit script to ensure cronjob is updated with new time information
	call_cron_edit()

	print("\n- Notification settings initialized.\n")
	print("Startup tasks complete!\n\n")


# main menu loop
while running:

	if current_menu == "main":
		display_main_menu()
		option = input("Please select a menu option: ")
		match option:
			case "1":
				current_menu = "lists"
			case "2":
				current_menu = "new"
			case "3":
				current_menu = "settings"
				# call notification settings menu
				print("Changing notification settings")
			case "q" | "Q":
				# quit program
				print("Now closing program...")
				running = False
				sys.exit(0)
			case _:
				print("Invalid option. Please select menu option again.")

	else:		# loop into inner menus
		match current_menu:
			case "lists":

				# get the lists, display them, accept input
				tdlists = get_lists()
				display_lists()
				list_choice = input("Select a list number or menu option to continue: ")

				if list_choice.isdigit():
					list_choice = int(list_choice)
					if list_choice <= get_num_lists():	# user selected valid list - enter task menu

						list_name = tdlists[list_choice - 1]

						display_tasks(list_name) # display the tasks in the list
						task_choice = input("Select a task number or menu option to continue: ")

						if task_choice.isdigit(): # user selected a task to view
							task_choice = int(task_choice)
							if task_choice <= get_num_tasks(list_name):	# user selected valid task - enter edit menu
								edit_result = view_task(list_name, task_choice)
								if edit_result == 'l': # check for menu selection that was NOT editing/completing
									print("Returning to list menu.")
									continue
								elif edit_result == 'm':
									print("Returning to main menu.")
									current_menu = "main"
									continue
								elif edit_result == 'q':
									# quit program
									print("Now closing program...")
									running = False
									sys.exit(0)

							else:
								print(f"There are only {get_num_tasks(list_choice)} lists available to choose from.")
								print("Please select a menu option.")

						elif task_choice.lower() == 'c':	# user selected to create a task - enter create menu
							create_new_task(list_name)

						elif task_choice.lower() == 'd':	# user selected delete list
							# confirm deletion
							confirmation = input("Are you sure you want to delete this to-do list? This is an irreversible decision. (Y/N) ")
							if confirmation.lower() == 'y':
								if delete_list(list_name): # runs deletion function and returns True if successful
									print("To-do list has successfully been deleted.")
								else:
									print("To-do list unable to be removed. Please try again.")
								current_menu = "main"
								continue

							elif confirmation.lower() == 'n':
								# should make it to where it can loop back to show tasks again.. for now just to lists
								print("Returning to list menu.")
								continue

							else:
								# should make it to where it can loop back to show tasks again... for now just to lists
								print("That is not a valid option. Returning to list menu.")
								current_menu = "lists"
								continue

						elif task_choice.lower() == 'm':	# user selected return to main menu
							current_menu = "main"
							continue

						elif task_choice.lower() == 'q':	# user selected to QUIT program
							# quit program
							print("Now closing program...")
							running = False
							sys.exit(0)

						else:	# invalid option
							print("Invalid option. Please select a task number or menu option.")

					else:	# user selected a list number that doesn't exist...
						print(f"There are only {get_num_lists()} lists available to choose from.")
						print("Please select a menu option.")

				elif list_choice.lower() == 'm':	# user selected return to main menu
					current_menu = "main"
					continue

				elif list_choice.lower() == 'q':	# user selected to QUIT program
					# quit program
					print ("Now closing program...")
					running = False
					sys.exit(0)

				else:	# user selected an invalid option
					print("Invalid option. Please select a menu option.")

			case "new":

				print("Give your new to-do list a short name (Recommended: less than 50 characters)")
				list_name = input()

				# check to see if to-do list with that name already exists
				tdlists = get_lists()
				while list_name in tdlists:
					print(f"A to-do list with the name {list_name} already exists!")
					print("Give your new to-do list another short name (Recommended: less than 50 characters)")
					list_name = input()

				# create the new list and store in data dir
				list_file_path = create_new_list(list_name)
				print(f"Created new to-do list named: {list_name}")
				print(f"To-do list saved to {list_file_path}")

				current_menu = "main"

			case "settings":

				# get settings values
				with open("data/settings.json", "r") as settings_file:
					settings_data = json.load(settings_file)

				current_email = settings_data["Email"]
				current_time = settings_data["Time"]

				print("\n---------- SETTINGS ----------\n")
				print("Current settings:")
				print(f"Email address: {current_email}")
				print(f"Notification time: {current_time}")
				print("\n------------------------------\n")

				print("[1] Change email address")
				print("[2] Change notification time")
				print("\n------------------------------\n")
				display_nav_footer(True)
				setting_choice = input("Choose a settings option: ")
				match setting_choice.lower():
					case "1":

						current_menu = "main"
						new_email = input("Set a new email address to use:\n")

						# open settings file and get its data
						with open("data/settings.json", "r") as settings_file:
							settings_data = json.load(settings_file)

						# edit the email data
						settings_data["Email"] = new_email

						# rewrite settings file
						with open("data/settings.json", "w") as settings_file:
							json.dump(settings_data, settings_file, indent=4)

						print(f"New email set to: {new_email}")

					case "2":

						current_menu = "main"
						print("Please enter a new time in the format HH:MM")
						print("  | Example format: 17:30   ---   5:30pm")
						new_time = get_valid_time().strftime("%H:%M")

						# open settings file and get its data
						with open("data/settings.json", "r") as settings_file:
							settings_data = json.load(settings_file)

						# edit the email data
						settings_data["Time"] = new_time

						# rewrite settings file
						with open("data/settings.json", "w") as settings_file:
							json.dump(settings_data, settings_file, indent=4)

						# Runs cron edit script to ensure cronjob is updated with new time
						call_cron_edit()

						print(f"New notification time set to {new_time}")

					case "m":	# user selected return to main menu
						current_menu = "main"
						continue

					case "q":	# user selected to QUIT program
						# quit program
						print("Now closing program...")
						running = False
						sys.exit(0)

					case _:	# user selected an invalid option
						print("Invalid option. Please select a menu option.")
