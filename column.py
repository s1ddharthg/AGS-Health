import cv2
import numpy as np
import os

def detect_columns(image_path, save_debug_images=False, return_lines=False):
    if not os.path.isfile(image_path):
        print(f"Error: The file '{image_path}' does not exist.")
        return None, None, None, None

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read the image file '{image_path}'.")
        return None, None, None, None

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

    # Apply morphological operations to merge text within columns
    kernel = np.ones((5, 5), np.uint8)
    processed_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract bounding boxes from contours
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours]

    # Sort bounding boxes by x coordinate
    bounding_boxes = sorted(bounding_boxes, key=lambda x: x[0])

    # Calculate vertical gaps between bounding boxes
    gaps = [bounding_boxes[i+1][0] - (bounding_boxes[i][0] + bounding_boxes[i][2])
            for i in range(len(bounding_boxes) - 1)]

    # Define a threshold to determine significant gaps (indicative of column separation)
    gap_threshold = max(gaps) / 2  # Adjust this based on document structure
    significant_gaps = [gap for gap in gaps if gap > gap_threshold]

    # Number of columns is the number of significant gaps + 1
    number_of_columns = len(significant_gaps) + 1

    # Draw bounding boxes and gaps on the original image for visualization
    if save_debug_images:
        debug_image = image.copy()
        for bbox in bounding_boxes:
            x, y, w, h = bbox
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        line_coordinates = []
        for i, gap in enumerate(gaps):
            if gap in significant_gaps:
                x1 = bounding_boxes[i][0] + bounding_boxes[i][2]
                x2 = bounding_boxes[i+1][0]
                line_coordinates.append(((x1, 0), (x1, image.shape[0])))
                line_coordinates.append(((x2, 0), (x2, image.shape[0])))
                cv2.line(debug_image, (x1, 0), (x1, image.shape[0]), (255, 0, 0), 2)
                cv2.line(debug_image, (x2, 0), (x2, image.shape[0]), (255, 0, 0), 2)
        
        debug_image_path = os.path.join(os.path.dirname(image_path), 'columns_debug.png')
        cv2.imwrite(debug_image_path, debug_image)
    
        if return_lines:
            return number_of_columns, debug_image_path, line_coordinates, image
        else:
            return number_of_columns, debug_image_path, image
    
    else:
        if return_lines:
            return number_of_columns, None, None, image
        else:
            return number_of_columns, None, image

def split_image(image, line_coordinates):
    if image is None:
        print("Error: No image provided.")
        return None, None

    # Sort line coordinates to get the second line (index 1)
    line_coordinates.sort(key=lambda x: x[0][0])  # Sort by x-coordinate of the first point
    second_line = line_coordinates[1]

    # Extract x-coordinate of the second line
    x_split = second_line[0][0]

    # Split the image into left and right portions
    left_image = image[:, :x_split, :]
    right_image = image[:, x_split:, :]

    return left_image, right_image

# Example usage
image_path = './img/page_1.png'  # Replace with your image path

# Detect columns and get line coordinates
columns, result_image, line_coordinates, original_image = detect_columns(image_path, save_debug_images=True, return_lines=True)

if columns is not None:
    print(f'Number of columns detected: {columns}')
    print(f'Debug image saved to: {result_image}')
    if line_coordinates:
        print(f'Coordinates of lines between columns:')
        for line in line_coordinates:
            print(line)

    # Split the image based on the detected lines
    left_image, right_image = split_image(original_image, line_coordinates)

    # Save the split images as L1_double.png and R1_double.png
    if left_image is not None and right_image is not None:
        cv2.imwrite('./img/L1_double.png', left_image)
        cv2.imwrite('./img/R1_double.png', right_image)

        print('Left and right images saved as L1_double.png and R1_double.png.')
