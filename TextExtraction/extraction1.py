import fitz  
import io
from PIL import Image
import os
import hashlib
import summarize
import paddleocr1


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

# Provide the path to your PDF file
pdf_path = "../ExtractedEmails/Email1.pdf"
pdf_text, pdf_images = extract_text_and_images_from_pdf(pdf_path)



# image_text = imageText.imageToText(imagepath) # From Gemini
image_text = paddleocr1.extract_text_from_images("extracted_content") # From PaddleOCR

# add this text to pdf_text
pdf_text += "\n\n"
pdf_text += "Text extracted from image:\n\n"
pdf_text += image_text  
save_dir='extracted_content'
text_filename = os.path.join(save_dir, "extracted_text.txt")

with open(text_filename, "w") as text_file:
    text_file.write("Text extracted from PDF:\n\n")
    text_file.write(pdf_text)
    
# summarize the text
summary = summarize.summarizeText(pdf_text)
print(summary)