from paddleocr import PaddleOCR
import os

def extract_text_from_images(images_dir):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize OCR model with angle classification
    combined_text = ""

    # Loop over all image files in the provided directory
    for image_filename in os.listdir(images_dir):
        image_path = os.path.join(images_dir, image_filename)
        
        # Run OCR on the image
        result = ocr.ocr(image_path, cls=True)
        
        # Extract text from OCR result
        for line in result[0]:
            text = line[1]  # The text is at index 1 in the tuple (line[0] is the position info)
            print(text)
    
    return combined_text

# Example usage
combined_text = extract_text_from_images("extracted_content")
print(combined_text)
