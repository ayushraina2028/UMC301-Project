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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
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
    """Save email metadata to CSV in a specified folder using Pandas."""
    
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Define the path for the CSV file within the specified folder
    csv_file = os.path.join(folder_path, 'emails_metadata.csv')
    
    # Prepare the data as a DataFrame
    df = pd.DataFrame([data], columns=['PDF Filename', 'Title', 'Category', 'Summary', 'Promo Code', 'Expiry Date'])
    
    # Check if the CSV file exists
    if os.path.exists(csv_file):
        # If file exists, append the new data without writing the header
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        # If the file doesn't exist, write the data along with the header
        df.to_csv(csv_file, mode='w', header=True, index=False)


        
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
        messages = results.get('messages', [])
        if messages:
            for i, message in enumerate(messages[:5]):  # Process the first 3 messages
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
                    promo_code = summaryJSON.get("Promo Code", "N/A")
                    expiry_date = summaryJSON.get("Expiry Date", "N/A")
                    summary_text = summaryJSON.get("Summary", "N/A")
                    
                    # check if it is already in the csv
                    
                        
                    # Save metadata to CSV
                    save_metadata_to_csv([pdf_filename, email_title, category, summary_text, promo_code, expiry_date])
                    # save_metadata_to_csv([pdf_filename, subject, sender, category_name])
                else:
                    print(f"No HTML content found for message ID: {msg_id}")
    else:
        print(f"Label '{category_name}' not found.")

if __name__ == '__main__':
    main()