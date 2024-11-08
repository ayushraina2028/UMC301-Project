import google.generativeai as genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

# Get the Gemini API key from the environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL='gemini-1.5-flash'
PROMPT="""Give me a very short summary of this email text. If some promo code is available, please include it, and its expiry date. If not available, then give 1-2 line containing the main words.
In case of travel related offers, include the destinations also (if available).

Then classify the email as one of the following categories:
1. Offers (Food, Shopping, Travel, and related categories only)
2. Events
3. Reminder/Alerts
4. Everything Else

Include offers related to subscriptions,fantasy sports in last category.
First 3 categories are important to us, so please make sure to classify them correctly. If you are not sure about the category, then you can leave it as 'Everything Else'.
If there are multiple promocodes, include all of them in summary and any one of them in promo code field.

output should be in json format with following keys:
1. Email Title
2. Category (from above)
3. Summary
4. Promo Code (if Yes mention it, otherwise No)
5. Expiry Date (if Yes mention it, otherwise No)
"""



def summarizeText(text):
    genai.configure(api_key=GEMINI_API_KEY)
    model=genai.GenerativeModel(MODEL)
    
    response=model.generate_content([PROMPT,text], stream=True)
    response.resolve()
    
    htmlContent=response.text
    textContent=BeautifulSoup(htmlContent,'html.parser')
    textContent=textContent.get_text(separator='\n').strip()
    
    return textContent

