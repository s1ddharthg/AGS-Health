# Import the necessary libraries
from pdf2image import convert_from_path
import os

# Function to convert PDF to images
def pdf_to_images(pdf_path, output_folder, image_format='png'):
    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Save each page as an image
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{i + 1}.{image_format}')
        image.save(image_path, image_format.upper())
        print(f'Saved: {image_path}')

# Example usage
pdf_path = 'double.pdf'  # Replace with the path to your PDF file
output_folder = 'img'  # Replace with the path to your output folder
image_format = 'png'  # You can change this to 'jpeg' if you prefer JPEG images

pdf_to_images(pdf_path, output_folder, image_format)
