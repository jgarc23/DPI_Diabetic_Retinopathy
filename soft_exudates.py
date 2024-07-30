import cv2
import numpy as np
import os

def extract_soft_exudates(image):

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    contrast_enhanced_image = clahe.apply(gray_image)
    
    blurred_image = cv2.GaussianBlur(contrast_enhanced_image, (5, 5), 0)
    
    _, binary_image = cv2.threshold(blurred_image, 180, 255, cv2.THRESH_BINARY)
    binary_image = cv2.bitwise_not(binary_image)
    

    contours, _ = cv2.findContours(binary_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    mask = np.zeros(binary_image.shape[:2], dtype="uint8")


    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 100 < area < 5000:
            cv2.drawContours(mask, [cnt], -1, 255, -1)
    final_image = cv2.bitwise_and(gray_image, gray_image, mask=mask)
    
    return final_image

if __name__ == "__main__":
    input_folder = r"C:\Users\Yoona\Downloads\opencv\Image Segmentation\input_folder"
    output_folder = r"C:\Users\Yoona\Downloads\opencv\Image Segmentation\output_folder"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path)
            soft_exudates = extract_soft_exudates(image)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, soft_exudates)
