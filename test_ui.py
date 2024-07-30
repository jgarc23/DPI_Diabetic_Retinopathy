import streamlit as st
import cv2
import os
from PIL import Image
from microaneurysms import *
from microaneurysmdetection import *
from bvsegment import *
from optical_disk import *
from text import *
from fpdf import FPDF
import tempfile


# Background color of app
page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
    background: linear-gradient(#EAE1E1, #D2BFBF);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

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
        x_start = 10  # Starting X position
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
        self.multi_cell(img_w, 10, txt=description, align='L')
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

# Function to handle button click
# Takes in 3 parameters (image, caption and description)
def handle_button_click(button_id,img, cap, description): 
    if uploaded_file is not None and st.session_state.buttons[button_id] != uploaded_file:
        # Append parametes to session_state images and update button ID list whenever 1 of the 5 algorithm buttons are pressed
        st.session_state.images.append((img, cap, description))
        st.session_state.buttons[button_id] = uploaded_file

if __name__ == '__main__':
    # Title and icon
    title, img_icon = st.columns([0.7,0.3],vertical_alignment="bottom")
    with title:
        st.header("Diabetic Retinopathy Segmentation Assistant",divider='gray')
    with img_icon: 
        st.image("https://cdn-icons-png.flaticon.com/512/9031/9031971.png",width=150) # Eye icon

    # Short description on diabetic retinopathy. Find in text.py file
    st.markdown(dr_desc)

    # Image uploader 
    uploaded_file = st.file_uploader("Upload Image Here:",type=["jpg","jpeg","png"],help="Select an image to upload for analysis")
    uploaded_image = None

    # Initialize session state for keeping track of images and button states 
    # (to prevent images from dissapearing or being displayed twice)
    if 'images' not in st.session_state:
        st.session_state.images = []
    if 'buttons' not in st.session_state:
        st.session_state.buttons = {1: None, 2: None, 3: None, 4: None, 5: None}
    if 'original_added' not in st.session_state:
        st.session_state.original_added = False

    # Check if an image was uploaded
    if uploaded_file is not None:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        uploaded_image = cv2.imdecode(file_bytes, 1)

        # Adds original image if not added
        if not st.session_state.original_added:
            # Resets image list and button state
            st.session_state.buttons = {1: None, 2: None, 3: None, 4: None, 5: None}
            st.session_state.images = []
            img = uploaded_file
            cap = "Displaying original eye image"
            description = "This is the original eye image that was uploaded for segmentation analysis"  # Find text for description in text.py file
            st.session_state.images.append((img, cap, description))
            st.session_state.original_added = True
    # If empty reset the session states for images and buttons.
    else:
        st.session_state.original_added = False
        

    # Create variables for output analyzed images 
    microaneurysmsdet = None
    microaneurysms = None
    bvsegment = None
    optical_disk = None
    soft_exudates = None
    hard_exudates = None
     
    # Microaneurysms and Soft Exudate Buttons
    col1,img_org,col2= st.columns([1,1,1],vertical_alignment="bottom") 
    # with img_org:
    #         if uploaded_file is not None:
    #             st.image(uploaded_file, caption="Original Eye Image", use_column_width=True)

    # Creates first button, if pressed add images plus caption and description to session state image list
    if col1.button("Microaneurysms",use_container_width=True,help="Uploads image for microaneurysm detection") and uploaded_file is not None:
        # Run algorithm and get analyzed image
        microaneurysms = extract_microaneurysms(uploaded_image)
        microaneurysms = Image.fromarray(microaneurysms)
        # Add caption and description and call button function
        caption = "Displaying microaneurysms in eye"
        description = image_desc[0] # Find text for description in text.py file
        handle_button_click(1, microaneurysms, caption, description) # Function call to add images to list

    # Creates second button, if pressed add images plus caption and description to session state image list
    if col2.button("Soft Exudates",use_container_width=True,help="Uploads image for soft exudate detection") and uploaded_file is not None:
        # Run algorithm and get analyzed image
        soft_exudates = extract_microaneurysmsdet(uploaded_image)
        soft_exudates = Image.fromarray(soft_exudates)
        # Add caption and description and call button function
        caption = "Displaying soft exudates in eye"
        description = image_desc[1] # Find text for description in text.py file
        handle_button_click(2, soft_exudates, caption, description)

    # Bvsegment and Hard Exudate Buttons 
    col3, col4,col5 = st.columns([1,1,1],vertical_alignment="center")
    
    # Creates third button, if pressed add images plus caption and description to session state image list
    if col3.button("bvsegment",use_container_width=True,help="Uploads image for blood vessel segmentation") and uploaded_file is not None:
        # Run algorithm and get analyzed image
        bvsegment = extract_bv(uploaded_image)
        bvsegment = Image.fromarray(bvsegment)
        # Add caption and description and call button function
        caption = "Displaying blood vessels in eye"
        description = image_desc[2] # Find text for description in text.py file
        handle_button_click(3, bvsegment, caption, description)

    # Creates fourth button, if pressed add images plus caption and description to session state image list
    if col4.button("Optical Disk",use_container_width=True,help="Uploads image for optical disk segmentation") and uploaded_file is not None:
        # Run algorithm and get analyzed image
        optical_disk_result = extract_opticdisk(uploaded_image)
        if isinstance(optical_disk_result, tuple):
            optical_disk = optical_disk_result[0]  # Adjust this index based on your function's return value, changing it will change image output
        else:
            optical_disk = optical_disk_result
        optical_disk = Image.fromarray(optical_disk)
        # Add caption and description and call button function
        caption = "Displaying optical disk in eye"
        description = image_desc[3] # Find text for description in text.py file
        handle_button_click(4, optical_disk, caption, description)
   
    # Creates fifth button, if pressed add images plus caption and description to session state image list
    if col5.button("Hard Exudates",use_container_width=True,help="Uploads image for hard exudates detection") and uploaded_file is not None:
        # Run algorithm and get analyzed image
        hard_exudates = extract_microaneurysmsdet(uploaded_image)
        hard_exudates = Image.fromarray(hard_exudates)
        # Add caption and description and call button function
        caption = "Displaying hard exudates in eye"
        description = image_desc[4] # Find text for description in text.py file
        handle_button_click(5, hard_exudates, caption, description)
    
    st.subheader("Segmentation Results:")
    anl_img1, bl1, anl_img2, bl2, anl_img3 = st.columns([0.3,0.05,0.3,0.05,0.3],vertical_alignment="center",gap="large")

    # Display all images in two rows
    if uploaded_file is not None and st.session_state.images:
        for idx, (img, cap, description) in enumerate(st.session_state.images):
            if idx % 3 == 0 :
                with anl_img1:
                    st.image(img, caption=cap,use_column_width=True)
            elif idx % 3 == 1:
                with anl_img2:
                    st.image(img, caption=cap, use_column_width=True)
            else:
                with anl_img3:
                    st.image(img, caption=cap, use_column_width=True)
    
    # Short individual descriptions on microaneurysms, blood vessels, hard exudates, and soft exudates. Find in text.py file
    st.markdown(ind_desc)

    # Button to generate and download PDF
    if st.button("Generate PDF"):
        if st.session_state.images:
            pdf_file = generate_pdf(st.session_state.images, uploaded_image)
            with open(pdf_file, "rb") as f:
                if st.download_button("Download PDF", f, file_name="diabetic_retinopathy_results.pdf"):
                    pdf_file = None