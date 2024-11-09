import google.generativeai as genai
from PIL import Image
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os


load_dotenv()
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

API_KEY = os.getenv('GEMINI_API_KEY')
MODEL='gemini-1.5-flash'
PROMPT='Extract all the available text from the image.'

def imageToText(image_path):
    genai.configure(api_key=API_KEY)
    model=genai.GenerativeModel(MODEL)
    image=Image.open(image_path)
    
    response=model.generate_content([PROMPT,image], stream=True)
    response.resolve()

    htmlContent=response.text
    textContent=BeautifulSoup(htmlContent,'html.parser')
    textContent=textContent.get_text(separator='\n').strip()
    
    return textContent



