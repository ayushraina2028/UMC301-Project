import fitz  
import io
from PIL import Image
import os
import hashlib
import summarize
import paddleocr1
import json

def compute_image_hash(image):
    """Compute a hash for an image."""
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    return hashlib.md5(image_bytes.getvalue()).hexdigest()

def extract_text_and_images_from_pdf(pdf_path, save_dir='extracted_content'):
    text = ""
    images = []
    minWidth = 300
    minHeight = 300
    seen_hashes = set()

    # Create directory to save images if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # Clear the previously saved images from extracted_content directory
    for file in os.listdir(save_dir):
        os.remove(os.path.join(save_dir, file))

    pdf_document = fitz.open(pdf_path)
    if(len(pdf_document) > 4):
        text = "The PDF document is too large to process."
        return text, images
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")

        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))

            # Save only images that meet the size threshold
            width, height = image.size
            if width >= minWidth and height >= minHeight:
                image_hash = compute_image_hash(image)
                if image_hash not in seen_hashes:
                    seen_hashes.add(image_hash)
                    images.append(image)

                    # Save image in PNG format with a sequential name
                    image_filename = os.path.join(save_dir, f"image{len(images)}.png")
                    image.save(image_filename, format="PNG")

    return text, images

def parseSummary(summary):
    # Parse the summary and extract the required information
    # For example, extract the email title, category, promo code, expiry date, etc.
    
    # Delete first and last lines of the summary
    summary = summary.split('\n')[1:-1]
    
    # Extract the email title
    print(summary)
    
    # Join the list of strings into a single string
    summary_str = ''.join(summary)

    try:
        # Parse the string as JSON
        summary_data = json.loads(summary_str)
        print(summary_data)
        print(type(summary_data))
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    
    return summary_data

def getContent(pdfPath):
    pdfText, pdfImages = extract_text_and_images_from_pdf(pdfPath)
    if pdfText == "The PDF document is too large to process.":
        
        # Create a summary JSON object with a message
        summaryJSON = {
            "email_title": "N/A",
            "Category": "N/A",
            "Summary": "The PDF document is too large to process.",
            "Promo Code": "N/A",
            "Expiry Date": "N/A"
        }
        
        
        return json.dumps(summaryJSON, indent=2)
    
    # Extract text from images
    image_text = paddleocr1.extract_text_from_images("extracted_content") # From PaddleOCR

    pdfText += "\n\n"
    pdfText += "Text extracted from image:\n\n"
    pdfText += image_text  
    save_dir='extracted_content'
    text_filename = os.path.join(save_dir, "extracted_text.txt")

    with open(text_filename, "w") as text_file:
        text_file.write("Text extracted from PDF:\n\n")
        text_file.write(pdfText)
        
    # summarize the text
    summary = summarize.summarizeText(pdfText)
    summaryJSON = parseSummary(summary)
    
    print(summaryJSON)
    
    return json.dumps(summaryJSON, indent=2)
    




