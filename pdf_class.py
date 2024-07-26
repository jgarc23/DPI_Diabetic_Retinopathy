import cv2
import os
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

    # Creates the introduction page - includes original eye image and other information if needed
    def intro_page(self,uploaded_image):
        # Font
        self.set_font("Courier", size=10)
        # Calculate pdf width
        doc_w = self.w
        # Image caption 
        cap = "Original Eye Image"
        # Calculate caption width and position
        cap_w = self.get_string_width(cap)
        self.set_x((doc_w - cap_w) / 2)
        # Add caption
        self.cell(cap_w, 10, txt=cap, ln=1,align="C")
        # Convert image to RGB be displayed 
        uploaded_image = Image.fromarray(cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2RGB)).convert("RGB")
        temp_filename = f"original_image.jpg"
        uploaded_image.save(temp_filename)
        # Calculate image width and position
        img_w = 100 # Adjustable
        doc_w = self.w
        img_x = (doc_w - img_w) / 2
        img_y = self.get_y()
        # Display image
        self.image(temp_filename, x=img_x, y=img_y, w=img_w)
        os.remove(temp_filename)
        # Calculate description position
        desc_y = self.get_y() + img_w
        self.set_xy(20,desc_y)
        self.set_font("Times", size=10)
        # Add description
        self.multi_cell(0, 10, txt = "Place holder text Place holder text Place holder text", align='L')

    # Segmentation Content - Add a page for each eye image
    def eye_seg(self,idx,img, cap, description):
        # Add page
        self.add_page()
        # Font sizes for caption and description of images
        cap_s = 10 # Adjustable
        desc_s = 10
        # Calculate pdf width
        doc_w = self.w
        # Font
        self.set_font("Times", "I", size=cap_s)
        # Calculate width of caption and position
        cap_w = self.get_string_width(cap)
        self.set_x((doc_w - cap_w) / 2)
        # Add caption
        self.cell(cap_w, 10, txt=cap, ln=1, align='C')
        # Convert PIL image to RGB and save it temporarily with a unique filename
        img = img.convert("RGB")
        temp_filename = f"temp_image_{idx}.jpg"
        img.save(temp_filename)
        # Calculate image width and position
        img_w = 100
        doc_w = self.w
        img_x = (doc_w - img_w) / 2
        img_y = self.get_y()
        # Add image
        self.image(temp_filename, x=img_x, y=img_y, w=img_w)
        # Calculate position of description
        desc_y = self.get_y() + img_w
        self.set_xy(20,desc_y)
        self.set_font("Times", size=desc_s)
        # Add description
        self.multi_cell(0, 10, txt = description, align='L')

        os.remove(temp_filename)  # Remove the temporary file after adding it to the PDF
    

# Function to generate PDF
def generate_pdf(images,uploaded_image):

    # Create and set pdf object
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    # get total page numbers and add a page to start
    pdf.alias_nb_pages()
    pdf.add_page()
    # Create the intro page (includes original eye image)
    pdf.intro_page(uploaded_image)

    # Run through all images and display them along with their caption and description
    # Takes in 3 parameters from session state images list (image, caption, and description)
    for idx, (img, cap, description) in enumerate(images): 
        pdf.eye_seg(idx, img, cap, description)
    # Return file 
    pdf_file = "diabetic_retinopathy_results.pdf"
    pdf.output(pdf_file)
    return pdf_file