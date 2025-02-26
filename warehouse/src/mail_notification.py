import csv
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from warehouse.src.classes.stack import StackOfBoxes

path_to_email_client_config = 'configs/email_client_config.json'
path_to_email_message_config = 'configs/email_message_config.json'
path_to_csv_file = 'data/stacks.csv'
email_client_config = {}
email_message_config = {}

# Function to send email notifications
def send_email_notification(stack : StackOfBoxes):
    subject = email_message_config.get("subject")
    from_email = email_client_config.get("user")
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
        server.login(login, password)
        server.send_message(msg)
    print("Email notification sent.")


# Function that processes a StackOfBoxes object
def process_stack(stack, threshold, csv_file_path):
    # Check if the stack height exceeds the threshold
    if stack.stack_height > threshold:
        stack.is_safe = False
        # Send email notification about the unsafebox stack
        #send_email_notification(stack)
        # Append new row to CSV file with camera_id, stack_height, and safety flag
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([stack.camera_id, stack.stack_height, stack.is_safe])
    print("New row appended to CSV.")


if __name__ == "__main__":
    # Load email configuration from JSON file (email_config.json)
    with open(path_to_email_message_config, 'r') as f:
        email_message_config = json.load(f)
    with open(path_to_email_client_config, 'r') as f:
        email_client_config = json.load(f)

    # Set the threshold for the stack height (adjust as needed)
    threshold = 10.0  # Example threshold value

    # Example: Create a StackOfBoxes object with a camera ID and a stack height
    stack = StackOfBoxes(camera_id=123, stack_height=12)

    # Process the stack: check height, update safety status, append to CSV, and send email if needed
    process_stack(stack, threshold, path_to_csv_file)
