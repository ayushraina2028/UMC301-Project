import google.generativeai as genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

# Get the Gemini API key from the environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL='gemini-1.5-flash'
PROMPT='Give me a very short summary of this email text. If some promo code is available, please include it, and its expiry date. If not available, then give 1-2 line containing the main words.'

"""
Scan through the document, look at all the offers, check their expiry dates, order them by expiry date, and provide a single line summary of the offers.
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

