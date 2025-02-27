import time
import csv
import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from warehouse.src.classes.stack import StackOfBoxes

path_to_email_client_config = 'configs/email_client_config.json'
path_to_email_message_config = 'configs/email_message_config.json'
DATA_FOLDER = 'data'
CSV_OUTPUT = 'data/stacks.csv'
email_client_config = {}
email_message_config = {}
THRESHOLD = 5
# Function to send email notifications
def send_email_notification(stack : StackOfBoxes):
    subject = email_message_config.get("subject")
    from_email = "to@example.com"
    to_email = email_message_config.get("to_email")  # Recipient email is part of the email_config
    smtp_server = email_client_config.get("smtp_server")
    smtp_port = int(email_client_config.get("smtp_port"))
    login = email_client_config.get("user")
    password = email_client_config.get("password")
    template = email_message_config.get("template")

    # Build the email body using the template
    body = template.format(camera_id=stack.camera_id, stack_height=stack.stack_height)

    # Create MIME email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure connection
        print("Connected")
        server.login(login, password)
        print("Logged in Succesfully")
        server.send_message(msg)
    print("Email notification sent.")


# Function that processes a StackOfBoxes object
def process_stack(stack, threshold, csv_file_path):
    # Check if the stack height exceeds the threshold
    if stack.stack_height > threshold:
        stack.is_safe = False
        # Send email notification about the unsafebox stack
        send_email_notification(stack)
        # Append new row to CSV file with camera_id, stack_height, and safety flag
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([stack.camera_id,  stack.timestamp, stack.stack_height, stack.is_safe])
    print("New row appended to CSV.")


def get_new_files(last_check_time):
    """ Returns a list of files that were created or modified since the last check. """
    new_files = []
    try:
        for entry in os.scandir(DATA_FOLDER):
            if entry.is_file() and entry.stat().st_mtime > last_check_time:
                new_files.append(entry.name)
    except Exception as e:
        print(f"Error scanning directory: {e}")

    return new_files


def process_new_files(last_check_time):
    """ Detects new files, processes them, and updates the CSV. """
    new_files = get_new_files(last_check_time)
    if not new_files:
        return last_check_time  # No new files detected

    print(f"New files detected: {new_files}")

    # Process each new file and append data to the main CSV
    for filename in new_files:
        file_path = os.path.join(DATA_FOLDER, filename)
        #Skip file if not a .txt
        if not file_path.endswith('.txt'):
            continue
        #Rea txt and split it into camera id, timestamp, and max_boxes
        try:
            with open(file_path, 'r') as f:
                data = f.read().strip().split(',')
                camera_id = int(data[0])
                timestamp = data[1]
                max_boxes = int(data[2])
                stack = StackOfBoxes(camera_id, max_boxes, timestamp)
                process_stack(stack, THRESHOLD, CSV_OUTPUT)

        except Exception as e:
            print(f"Error reading {filename}: {e}")
    return time.time()  # Update last check time


def main():
    """ Monitors the data folder for new files using modification times. """
    print("Monitoring data folder for new files...")
    last_check_time = time.time()  # Start with the current time

    while True:
        last_check_time = process_new_files(last_check_time)
        time.sleep(4)  # Check for new files every 10 seconds


if __name__ == "__main__":
    # Load email configuration from JSON file (email_config.json)
    with open(path_to_email_message_config, 'r') as f:
        email_message_config = json.load(f)
    with open(path_to_email_client_config, 'r') as f:
        email_client_config = json.load(f)
    main()