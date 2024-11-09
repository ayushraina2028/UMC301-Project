import os
import pickle
import base64
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from weasyprint import HTML
from google_auth_oauthlib.flow import InstalledAppFlow
import apicall
import json
import pandas as pd 
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB setup
mongodb = os.getenv('MONGO_URI')
client = MongoClient(mongodb)  # Replace with your MongoDB URI
db = client["email_database"]  # Database name
emails_collection = db["users"]  # Collection name

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    """Get Gmail API service."""
    creds = None
    if os.path.exists('../token.pickle'):
        with open('../token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('../token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def get_email_content(service, message_id):
    """Fetch email content given a message ID."""
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    email_body = None
    sender = None
    subject = None
    snippet = None
    
    # Extract the email details
    if 'payload' in msg:
        headers = msg['payload']['headers']
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        snippet = msg.get('snippet', '')
        
        # Extract email body (HTML)
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/html':
                    email_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            if 'data' in msg['payload']['body']:
                email_body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
    return email_body, sender, subject, snippet

def save_email_as_pdf(email_body, email_index, folder_path = '../ExtractedEmails'):
    """Convert the email body (HTML) to a PDF file using WeasyPrint with backgrounds enabled."""
    
     # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Define the PDF filename and full path
    pdf_filename = f"Email{email_index}.pdf"
    pdf_path = os.path.join(folder_path, pdf_filename)
    
    # Ensure any relative URLs are replaced with full URLs (you may need to adjust this based on your email)
    email_body = email_body.replace('src="/', 'src="https://mail.google.com/')
    
    # Create PDF with backgrounds enabled
    html = HTML(string=email_body)
    html.write_pdf(pdf_path, stylesheets=None, presentational_hints=True)
    print(f"Saved: {pdf_path}")
    return pdf_path

def get_labels(service):
    """Fetch all labels for the authenticated user."""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return {label['name']: label['id'] for label in labels}


def save_metadata_to_csv(data, folder_path="../ExtractedEmails"):
    """Save email metadata to CSV in a specified folder."""
    
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Define the path for the CSV file within the specified folder
    csv_file = os.path.join(folder_path, 'emails_metadata.csv')
    
    # Check if the file already exists to add headers if it's new
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write headers if file is new
        # if not file_exists:
        #     writer.writerow(['pdf_filename', 'email_title', 'category', 'summary_text', 'promo_code', 'expiry_date'])
        
        # check if file is empty or not instead of checking if file exists
        if os.stat(csv_file).st_size == 0:
            writer.writerow(['pdf_filename', 'email_title', 'category', 'summary_text', 'promo_code', 'expiry_date'])
        
        # Write the email metadata (pdf filename, title, sender, category)
        writer.writerow(data)
        
def main():
    """Main function to fetch emails from a specific category, convert them to PDF, and save metadata to CSV."""
    service = get_service()
    
    # Fetch all labels and print them
    labels = get_labels(service)
    print("Available labels:", labels)
    
    # Specify the desired category (label name)
    
    category_name = 'CATEGORY_PROMOTIONS'  # Change this to 'Primary', 'Social', 'Updates', or 'Forums' as needed
    category_id = labels.get(category_name)  # Get the label ID
    if category_id:
        results = service.users().messages().list(userId='me', labelIds=[category_id]).execute()
        emailID = service.users().getProfile(userId='me').execute()
        userEmail = emailID['emailAddress']
        
        print(f"Email ID: {userEmail}")
        
        
        
        messages = results.get('messages', [])
        if messages:
            for i, message in enumerate(messages[:4]):  # Process the first 3 messages
                msg_id = message['id']
                email_body, sender, subject, snippet = get_email_content(service, msg_id)
                if email_body:
                    # Save email as PDF
                    pdf_filename = save_email_as_pdf(email_body, i + 1)
                    
                    # Get summary of the PDF
                    summaryJSON = apicall.getContent(pdf_filename)
                    summaryJSON = json.loads(summaryJSON)
                    
                    # Extract relevant fields from the JSON response
                    email_title = subject
                    category = summaryJSON.get("Category", "N/A")
                    summary_text = summaryJSON.get("Summary", "N/A")
                    promo_code = summaryJSON.get("Promo Code", "N/A")
                    expiry_date = summaryJSON.get("Expiry Date", "N/A")
                    
                    # check if it is already in the csv
                    # If the CSV file exists, read it to check for duplicates
                    flag = True
                    csv_file = "../ExtractedEmails/emails_metadata.csv"
                    if os.path.exists(csv_file):
                        if os.stat(csv_file).st_size == 0:
                            flag = False
                            
                        if(flag):
                            # Read the first column (PDF Filename) of the CSV
                            existing_df = pd.read_csv(csv_file)
                            existing_titles = existing_df['email_title'].tolist()  # Get the list of titles (subjects)

                            # Check if the email_title is already in the list
                            if email_title in existing_titles:
                                print(f"Email with subject '{email_title}' already exists in the CSV. Skipping...")
                                break  # Skip saving this metadata if it's already present
                    else:
                        print("CSV file not found. Proceeding with saving new data.")

                        
                    # Save metadata to CSV
                    save_metadata_to_csv([pdf_filename, email_title, category, summary_text, promo_code, expiry_date])
                    # save_metadata_to_csv([pdf_filename, subject, sender, category_name])
                    
                    # remove the PDF file after saving metadata
                    os.remove(pdf_filename)
                else:
                    print(f"No HTML content found for message ID: {msg_id}")
    else:
        print(f"Label '{category_name}' not found.")
        
    try:
        # Path to your CSV file
        csv_file_path = '../ExtractedEmails/emails_metadata.csv'

        # List to hold the offers as dictionaries
        offers = []

        # Read the CSV file and populate the offers list
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                # Create a dictionary with the required fields
                offer = {
                    "email_title": row["email_title"],
                    "category": row["category"],
                    "summary_text": row["summary_text"],
                    "promo_code": row["promo_code"],
                    "expiry_date": row["expiry_date"]
                }
                # Append each offer dictionary to the offers list
                offers.append(offer)

        # Print the result to verify
        print(offers)
        
        existing_entry = emails_collection.find_one({"userEmail": userEmail})
        
        if existing_entry:
            # Update the existing document with the new offers
            emails_collection.update_one(
                {"userEmail": userEmail},
                {"$set": {"offers": offers}}
            )
            print("Email metadata updated in MongoDB successfully.")
        else:
            # Insert a new document if the user's email is not present
            emails_collection.insert_one({"userEmail": userEmail, "offers": offers})
            print("Email metadata saved to MongoDB successfully.")
    except Exception as e:
        print(f"Error saving email metadata to MongoDB: {e}")
    

if __name__ == '__main__':
    main()