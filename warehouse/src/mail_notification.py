import time
import csv
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class StackOfBoxes:
    def __init__(self, camera_id: int, stack_height: int, timestamp: str):
        self.camera_id = camera_id
        self.stack_height = stack_height
        self.is_safe = True  # Initially safe
        self.timestamp = timestamp

path_to_email_client_config = 'configs/email_client_config.json'
path_to_email_message_config = 'configs/email_message_config.json'
DATA_FOLDER = 'data'
CSV_OUTPUT = 'data/stacks.csv'
email_client_config = {}
email_message_config = {}
THRESHOLD = 5
# Function to send email notifications
def send_email_notification(stack : StackOfBoxes, mail_server):
    subject = email_message_config.get("subject")
    from_email = email_message_config.get("from_email")
    to_email = email_message_config.get("to_email")  # Recipient email is part of the email_config

    template = email_message_config.get("template")

    # Build the email body using the template
    body = template.format(camera_id=stack.camera_id, stack_height=stack.stack_height)

    # Create MIME email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    mail_server.send_message(msg)
    print("Email notification sent.")


# Function that processes a StackOfBoxes object
def process_stack(stack, threshold, csv_file_path, mail_server):
    # Check if the stack height exceeds the threshold
    if stack.stack_height > threshold:
        stack.is_safe = False
        # Send email notification about the unsafebox stack
        send_email_notification(stack, mail_server)
        # Append new row to CSV file with camera_id, stack_height, and safety flag
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([stack.camera_id,  stack.timestamp, stack.stack_height, stack.is_safe])
    print("New row appended to CSV.")


def get_new_files(last_check_time):
    """ Returns a list of files that were created or modified since the last check. """
    new_files = []
    try:
        for root, dirs, files in os.walk(DATA_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) > last_check_time:
                    new_files.append(file_path)
    except Exception as e:
        print(f"Error scanning directory: {e}")

    return new_files


def process_new_files(last_check_time, mail_server):
    """ Detects new files, processes them, and updates the CSV. """
    new_files = get_new_files(last_check_time)
    if not new_files:
        return last_check_time  # No new files detected

    print(f"New files detected: {new_files}")

    # Process each new file and append data to the main CSV
    for filename in new_files:
        file_path = filename
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
                process_stack(stack, THRESHOLD, CSV_OUTPUT, mail_server)

        except Exception as e:
            print(f"Error reading {filename}: {e}")
    return time.time()  # Update last check time

def init_mail_server():
    smtp_server = email_client_config.get("smtp_server")
    smtp_port = int(email_client_config.get("smtp_port"))
    login = email_client_config.get("user")
    password = email_client_config.get("password")
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure connection
    server.ehlo()
    print("Connected")
    server.login(login, password)
    print("Logged in Succesfully")
    return server

def main():
    """ Monitors the data folder for new files using modification times. """
    print("Monitoring data folder for new files...")
    last_check_time = time.time()  # Start with the current time
    with init_mail_server() as mail_server:
        while True:
            last_check_time = process_new_files(last_check_time, mail_server)
            time.sleep(4)  # Check for new files every 10 seconds


if __name__ == "__main__":
    # Load email configuration from JSON file (email_config.json)
    with open(path_to_email_message_config, 'r') as f:
        email_message_config = json.load(f)
    with open(path_to_email_client_config, 'r') as f:
        email_client_config = json.load(f)
    main()