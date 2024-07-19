import cv2
import numpy as np
import os

def extract_microaneurysms(eye):
    b, g, r = cv2.split(eye)
    g = cv2.multiply(g, 2.5)
    eye_gray = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    eye_gray = cv2.cvtColor(eye_gray, cv2.COLOR_BGR2GRAY)
    eye_gray = cv2.GaussianBlur(eye_gray, (5, 5), 0)
    eye_edges = cv2.Canny(eye_gray, 70, 35)
    eye_final = eye_edges
    kernel = np.ones((5, 5), np.uint8)
    eye_final = cv2.morphologyEx(eye_final, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(eye_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    masked_image = np.zeros_like(eye)
    for cnt in contours:
        if cv2.contourArea(cnt) > 700:
            cv2.drawContours(masked_image, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)
    eye_final = cv2.subtract(eye_final, cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY))
    contours, _ = cv2.findContours(eye_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    masked_small_image = np.zeros_like(eye)
    for cnt in contours:
        if cv2.contourArea(cnt) < 10:
            cv2.drawContours(masked_small_image, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)
    eye_final = cv2.subtract(eye_final, cv2.cvtColor(masked_small_image, cv2.COLOR_BGR2GRAY))
    contours, _ = cv2.findContours(eye_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    masked_circle_image = np.zeros_like(eye)
    for cnt in contours:
        blob_height = cv2.boundingRect(cnt)[3]
        blob_width = cv2.boundingRect(cnt)[2]
        width_height_diff = abs(blob_height - blob_width)
        if (width_height_diff > 0.2 * blob_height) or (width_height_diff > 0.2 * blob_width):
            cv2.drawContours(masked_circle_image, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)
        if cv2.contourArea(cnt) < 0.05 * blob_height * blob_width:
            cv2.drawContours(masked_circle_image, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)
        if cv2.contourArea(cnt) > 90000:
            cv2.drawContours(masked_circle_image, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)
    eye_final = cv2.subtract(eye_final, cv2.cvtColor(masked_circle_image, cv2.COLOR_BGR2GRAY))
    return eye_final

if __name__ == "__main__":
    
    input_folder = r"/Users/aarshpatel/Downloads/sparks-internship-diabetic-retinopathy/images"
    output_folder = r"/Users/aarshpatel/Downloads/sparks-internship-diabetic-retinopathy/images_MA"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path)
            microaneurysms = extract_microaneurysms(image)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, microaneurysms)
