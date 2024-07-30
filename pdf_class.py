import cv2
import os
import numpy as np
from PIL import Image
from fpdf import FPDF
from text import *
import tempfile

class PDF(FPDF):
    
    # Header
    def header(self):
        # Title of header
        title = "Diabetic Retinopathy Segmentation Results"
        header_h = 30
        # Calculate of pdf
        doc_w = self.w
        # Font 
        self.set_font("Courier", "B",size=15) 
        # Create background
        self.set_fill_color(173, 216, 230) # background = light blue
        self.set_xy(0,0)
        self.cell(doc_w, header_h, "", border=False, ln=0, align="C", fill = 1)

        # Calculate title position
        title_w = self.get_string_width(title) + 6
        self.set_xy((doc_w - title_w) / 2, 0)
        # Colors of frame and text
        self.set_draw_color(0, 80, 180) # border = blue
        self.set_text_color(0, 0, 0) # text = black
        # Thickness of frame (border)
        self.set_line_width(1)
        # Add Title 
        self.cell(title_w, 30/1.5, title, border=False, ln=0, align="C", fill = 0) # border and background false
        
        # Image width and add image
        img_w = 25
        self.image('eye_icon1.png', x=180, y=0, w=img_w)
        # Line break
        self.ln(header_h)

    # Footer
    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        # Set font
        self.set_font("Arial", "I", 8)
        # Set font color grey
        self.set_text_color(169,169,169)
        # Page number
        self.cell(0,10, f'Page {self.page_no()}/{{nb}}', align='C')

    # Segmentation Content - Add images in a grid
    def eye_seg(self, idx, img, cap, description):
        img_w, img_h = 50, 50  # Adjust image width and height
        margin = 10  # Margin between images
        images_per_row = 3
        x_start = 21  # Starting X position
        y_start = self.get_y()  # Starting Y position
        
        # Calculate the row and column for the current image
        row = idx // images_per_row
        col = idx % images_per_row
        
        x_position = x_start + col * (img_w + margin)
        if idx < 3:
            y_position = 30
        else:
            y_position = 140
        self.set_xy(x_position, y_position)

        self.set_font("Times", "I", size=8)
        cap_w = self.get_string_width(cap)
        self.cell(cap_w, 10, txt=cap, ln=1, align='C')
        
        if idx != 0:
            img = img.convert("RGB")
            temp_filename = f"temp_image_{idx}.jpg"
            img.save(temp_filename)
        else:
            file_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert("RGB")
            temp_filename = f"original_image.jpg"
            img.save(temp_filename)

        self.image(temp_filename, x=x_position, y=self.get_y(), w=img_w, h=img_h)
        os.remove(temp_filename)
        
        self.set_xy(x_position, self.get_y() + img_h + margin)
        self.set_font("Times", size=8)
        self.multi_cell(img_w, 4, txt=description, align='L')
        self.set_y(y_position)

# Function to generate PDF
def generate_pdf(images, uploaded_image):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()

    for idx, (img, cap, description) in enumerate(images): 
        if idx != -1:
            pdf.eye_seg(idx, img, cap, description)
    
    pdf_file = "diabetic_retinopathy_results.pdf"
    pdf.output(pdf_file)
    return pdf_file