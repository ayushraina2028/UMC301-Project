from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB setup
mongodb = os.getenv('MONGO_URI')
client = MongoClient(mongodb)  # Replace with your MongoDB URI
db = client["email_database"]  # Database name
emails_collection = db["users"]  # Collection name

# get data of specific email from emails_collection 

def get_email_data(email_id):
    """Get email data from MongoDB."""
    email_data = emails_collection.find_one({"userEmail": email_id})
    return email_data

# get all emails from emails_collection
email = "ayushraina767@gmail.com"
print(get_email_data(email))



