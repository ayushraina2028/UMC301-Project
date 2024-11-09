import os
from paddleocr import PaddleOCR
from PIL import Image

def extract_text_from_images(images_dir):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize OCR model with angle classification
    combined_text = ""

    # Loop over all image files in the provided directory
    for image_filename in os.listdir(images_dir):
        image_path = os.path.join(images_dir, image_filename)

        # Check if the file exists and is a valid image
        if not os.path.exists(image_path) or not image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Skipping invalid image file: {image_filename}")
            continue
        
        # Use PIL to check if the image can be opened
        try:
            img = Image.open(image_path)
            img.verify()  # Verify the image integrity
        except Exception as e:
            print(f"Error opening image {image_filename}: {e}")
            continue

        # Run OCR on the image
        result = ocr.ocr(image_path, cls=True)
        print(f"len of result is:",len(result))
        for index in range(len(result)):
            res = result[index]
            
            if res is None:
                continue
            for line in res:
                line = line[1]
            
                combined_text += line[0] + " "
    return combined_text
