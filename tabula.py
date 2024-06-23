import fitz  # PyMuPDF
import cv2
import numpy as np
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
import io
import os

def pdf_to_images(input_pdf_path):
    doc = fitz.open(input_pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:  # if RGBA, convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        images.append(img)
    return images

def save_image_to_pdf(image, output_pdf_path):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    pdf_bytes = io.BytesIO()
    c = canvas.Canvas(pdf_bytes, pagesize=img_pil.size)
    c.drawImage(ImageReader(img_pil), 0, 0, width=img_pil.width, height=img_pil.height)
    c.save()
    with open(output_pdf_path, 'wb') as f:
        f.write(pdf_bytes.getbuffer())

def detect_columns(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    
    kernel = np.ones((50, 1), np.uint8)
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    column_bboxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 30 and h > 30:
            column_bboxes.append((x, y, w, h))
    
    column_bboxes = sorted(column_bboxes, key=lambda bbox: bbox[0])
    return column_bboxes

def extract_and_save_columns(images, output_pdf_path_base):
    for page_num, image in enumerate(images):
        print(f"Processing page {page_num + 1}")
        page_columns = detect_columns(image)
        
        for col_num, (x, y, w, h) in enumerate(page_columns):
            column_img = image[y:y+h, x:x+w]
            output_pdf_path = os.path.join(os.path.dirname(output_pdf_path_base), f"{os.path.basename(output_pdf_path_base)}_page{page_num+1}_col{col_num+1}.pdf")
            save_image_to_pdf(column_img, output_pdf_path)
            print(f"Saved column {col_num + 1} of page {page_num + 1} to {output_pdf_path}")

# Ensure output directory exists
os.makedirs('output', exist_ok=True)



# Usage
input_pdf_path = "C:\GH1\AGS-Health\8_7971155.pdf"
output_pdf_path_base = 'C:\GH1\AGS-Health'
images = pdf_to_images(input_pdf_path)
extract_and_save_columns(images, output_pdf_path_base)


