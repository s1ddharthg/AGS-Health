import fitz  # PyMuPDF
import pdfplumber
import cv2
import numpy as np
import os

def detect_columns(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    height, width = image.shape

    # Edge detection
    edges = cv2.Canny(image, 50, 150, apertureSize=3)

    # Detect lines using Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=height//2, maxLineGap=20)

    # Filter vertical lines
    vertical_lines = [line for line in lines if abs(line[0][0] - line[0][2]) < 10]

    # Sort lines by x-coordinate
    vertical_lines = sorted(vertical_lines, key=lambda x: x[0][0])

    # Calculate column boundaries based on vertical lines
    column_boundaries = []
    for line in vertical_lines:
        x = line[0][0]
        column_boundaries.append(x)

    # Add edges of the page as column boundaries
    column_boundaries = [0] + column_boundaries + [width]
    
    # Remove duplicate or very close boundaries
    column_boundaries = sorted(set(column_boundaries))
    column_boundaries = [column_boundaries[i] for i in range(len(column_boundaries)) if i == 0 or column_boundaries[i] - column_boundaries[i-1] > 10]

    return column_boundaries

def extract_text_from_columns(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Extract the page as an image
        pix = page.get_pixmap()
        img_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
        pix.save(img_path)
        
        # Detect column boundaries
        column_boundaries = detect_columns(img_path)
        
        # Open the page with pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pdf_page = pdf.pages[page_num]
            width = pdf_page.width
            height = pdf_page.height
            
            for i in range(len(column_boundaries) - 1):
                left = column_boundaries[i]
                right = column_boundaries[i + 1]
                
                bbox = (left, 0, right, height)
                column_text = pdf_page.within_bbox(bbox).extract_text()
                
                # Save the extracted text to separate files
                with open(os.path.join(output_dir, f"page_{page_num + 1}_column_{i + 1}.txt"), "w", encoding="utf-8") as file:
                    file.write(column_text or "")
    
    print(f"Processed {len(pdf_document)} pages. Outputs are saved in '{output_dir}'")

pdf_path = "C:\GH1\AdvancedLiterateMachinery\87568950_20230620.pdf"
output_dir = "C:\GH1\AdvancedLiterateMachinery"
extract_text_from_columns(pdf_path, output_dir)

