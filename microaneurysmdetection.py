import cv2
import numpy as np
import os

def extract_microaneurysmsdet(image):
    b, green_fundus, r = cv2.split(image)

    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_enhanced_green_fundus = clahe.apply(green_fundus)

  
    r1 = cv2.morphologyEx(contrast_enhanced_green_fundus, cv2.MORPH_OPEN, 
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
    R1 = cv2.morphologyEx(r1, cv2.MORPH_CLOSE, 
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
    r2 = cv2.morphologyEx(R1, cv2.MORPH_OPEN, 
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)), iterations=1)
    R2 = cv2.morphologyEx(r2, cv2.MORPH_CLOSE, 
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)), iterations=1)
    r3 = cv2.morphologyEx(R2, cv2.MORPH_OPEN, 
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)), iterations=1)
    R3 = cv2.morphologyEx(r3, cv2.MORPH_CLOSE, 
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)), iterations=1)

   
    f4 = cv2.subtract(R3, contrast_enhanced_green_fundus)
    f5 = clahe.apply(f4)

   
    ret, f6 = cv2.threshold(f5, 15, 255, cv2.THRESH_BINARY)

    
    edges = cv2.Canny(f6, 50, 150)

   
    edges = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
    edges = cv2.erode(edges, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)

    
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.ones(f6.shape[:2], dtype="uint8") * 255

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 15 or area > 150:
            cv2.drawContours(mask, [cnt], -1, 0, -1)

    
    final_image = cv2.bitwise_and(f6, f6, mask=mask)
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

            
            microaneurysms = extract_microaneurysmsdet(image)

           
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_microaneurysms.png")
            cv2.imwrite(output_path, microaneurysms)
