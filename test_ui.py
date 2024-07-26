import streamlit as st
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

# Title
# Variables for caption and description font size for later use

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

    # Creates the introduction page included original eye image and other information if needed
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
        img_w = 100
        doc_w = self.w
        img_x = (doc_w - img_w) / 2
        img_y = self.get_y()
        # Display image
        self.image(temp_filename, x=img_x, y=img_y, w=img_w)
        os.remove(temp_filename)

    # Segmentation Content
    def eye_seg(self,idx,img, cap, description):
        # Add page
        self.add_page()
        # Font sizes for caption and description of images
        cap_s = 10
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

        # Add description
        desc_y = self.get_y() + img_w
        self.set_xy(20,desc_y)
        self.set_font("Times", size=desc_s)
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

    # Check if an image was uploaded
    if uploaded_file is not None:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        uploaded_image = cv2.imdecode(file_bytes, 1)
    # If empty reset the session states for images and buttons.
    else:
        st.session_state.buttons = {1: None, 2: None, 3: None, 4: None, 5: None}
        st.session_state.images = []
        
    # # Display original image 
    # bl1,img_org,bl2 = st.columns([2,1,2.5])
    

    # Create variables for output analyzed images 
    microaneurysmsdet = None
    microaneurysms = None
    bvsegment = None
    optical_disk = None
    soft_exudates = None
    hard_exudates = None
     
    # Microaneurysms and Soft Exudate Buttons
    col1,img_org,col2= st.columns([1,1,1],vertical_alignment="bottom") 
    with img_org:
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Original Eye Image", use_column_width=True)
    # Creates first button, if pressed add images plus caption and description to session state image list
    if col1.button("Microaneurysms",use_container_width=True,help="Uploads image for microaneurysm detection") and uploaded_file is not None:
        microaneurysms = extract_microaneurysms(uploaded_image)
        microaneurysms = Image.fromarray(microaneurysms)
        caption = "Displaying microaneurysms in eye"
        description = image_desc[0] # Find text for description in text.py file
        handle_button_click(1, microaneurysms, caption, description) # Function call to add images to list

    # Creates second button, if pressed add images plus caption and description to session state image list
    if col2.button("Soft Exudates",use_container_width=True,help="Uploads image for soft exudate detection") and uploaded_file is not None:
        soft_exudates = extract_microaneurysmsdet(uploaded_image)
        soft_exudates = Image.fromarray(soft_exudates)
        caption = "Displaying soft exudates in eye"
        description = image_desc[1] # Find text for description in text.py file
        handle_button_click(2, soft_exudates, caption, description)

    # Bvsegment and Hard Exudate Buttons 
    col3, col4,col5 = st.columns([1,1,1],vertical_alignment="center")
    
    # Creates third button, if pressed add images plus caption and description to session state image list
    if col3.button("bvsegment",use_container_width=True,help="Uploads image for blood vessel segmentation") and uploaded_file is not None:
        bvsegment = extract_bv(uploaded_image)
        bvsegment = Image.fromarray(bvsegment)
        caption = "Displaying blood vessels in eye"
        description = image_desc[2] # Find text for description in text.py file
        handle_button_click(3, bvsegment, caption, description)

    # Creates fourth button, if pressed add images plus caption and description to session state image list
    if col4.button("Optical Disk",use_container_width=True,help="Uploads image for optical disk segmentation") and uploaded_file is not None:
        optical_disk_result = extract_opticdisk(uploaded_image)
        if isinstance(optical_disk_result, tuple):
            optical_disk = optical_disk_result[0]  # Adjust this index based on your function's return value
        else:
            optical_disk = optical_disk_result
        optical_disk = Image.fromarray(optical_disk)
        caption = "Displaying optical disk in eye"
        description = image_desc[3] # Find text for description in text.py file
        handle_button_click(4, optical_disk, caption, description)
   
    # Creates fifth button, if pressed add images plus caption and description to session state image list
    if col5.button("Hard Exudates",use_container_width=True,help="Uploads image for hard exudates detection") and uploaded_file is not None:
        hard_exudates = extract_microaneurysmsdet(uploaded_image)
        hard_exudates = Image.fromarray(hard_exudates)
        caption = "Displaying hard exudates in eye"
        description = image_desc[4] # Find text for description in text.py file
        handle_button_click(5, hard_exudates, caption, description)
    
    st.subheader("Segmentation Results:")
    anl_img1, bl1, anl_img2 = st.columns([0.4,0.1,0.4],vertical_alignment="center",gap="large")

    # Display all images in two columns
    if uploaded_file is not None and st.session_state.images:
        for idx, (img, cap, description) in enumerate(st.session_state.images):
            if idx % 2 == 0:
                with anl_img1:
                    st.image(img, caption=cap,use_column_width=True)
            else:
                with anl_img2:
                    st.image(img, caption=cap, use_column_width=True)
    
    # Short individual descriptions on microaneurysms, blood vessels, hard exudates, and soft exudates. Find in text.py file
    st.markdown(ind_desc)

    # Button to generate and download PDF
    if st.button("Generate PDF"):
        if st.session_state.images:
            pdf_file = generate_pdf(st.session_state.images,uploaded_image)
            with open(pdf_file, "rb") as f:
                if st.download_button("Download PDF", f, file_name="diabetic_retinopathy_results.pdf"):
                    pdf_file = None