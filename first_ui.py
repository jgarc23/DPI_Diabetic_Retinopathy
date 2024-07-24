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

# Function to handle button click
# Takes in 3 parameters (image, caption and description)
def handle_button_click(button_id,img, cap, description): 
    if uploaded_file is not None and st.session_state.buttons[button_id] != uploaded_file:
        # Append parametes to session_state images and update button ID list whenever 1 of the 5 algorithm buttons are pressed
        st.session_state.images.append((img, cap, description))
        st.session_state.buttons[button_id] = uploaded_file

# Function to generate PDF
def generate_pdf(images, uploaded_image):
    # Variables for caption and description font size for later use
    cap_size = 10
    desc_size = 12

    # Create and set pdf 
    pdf = FPDF()
    pdf.set_margins(1,1,1)
    pdf.set_auto_page_break(auto=True, margin=15)
    # Add title to first page
    pdf.set_font("Arial", size=20)
    pdf.add_page()
    pdf.cell(200, 10, txt="Diabetic Retinopathy Segmentation Results", ln=2, align="C")
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200,10, txt="Original Eye Image", ln=2,align="C")
    uploaded_image = Image.fromarray(cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2RGB)).convert("RGB")
    temp_filename = f"original_image.jpg"
    uploaded_image.save(temp_filename)
    pdf.image(temp_filename, x=55, y=30, w=100)
    os.remove(temp_filename)
    
    # Run through all images and display them along with their caption and description
    # Takes in 3 parameters from session state images list (image, caption, and description)
    for idx, (img, cap, description) in enumerate(images): 
        # Add caption
        pdf.add_page()
        pdf.set_font("Arial", size=cap_size)
        pdf.cell(200, 10, txt=cap, ln=1, align='C')
        
        # Convert PIL image to RGB and save it temporarily with a unique filename
        img = img.convert("RGB")
        temp_filename = f"temp_image_{idx}.jpg"
        img.save(temp_filename)
        # Add image
        pdf.image(temp_filename, x=55, y=10, w=100)

        # Add description
        pdf.set_xy(20,130)
        pdf.set_font("Arial", size=desc_size)
        pdf.multi_cell(0,10, txt = description, align='L')

        os.remove(temp_filename)  # Remove the temporary file after adding it to the PDF
    
    # Return file 
    pdf_file = "diabetic_retinopathy_results.pdf"
    pdf.output(pdf_file)
    return pdf_file

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
        description = "kanf aknffka"
        handle_button_click(1, microaneurysms, caption, description) # Function call to add images to list

    # Creates second button, if pressed add images plus caption and description to session state image list
    if col2.button("Soft Exudates",use_container_width=True,help="Uploads image for soft exudate detection") and uploaded_file is not None:
        soft_exudates = extract_microaneurysmsdet(uploaded_image)
        soft_exudates = Image.fromarray(soft_exudates)
        caption = "Displaying soft exudates in eye"
        description = "bifndf"
        handle_button_click(2, soft_exudates, caption, description)

    # Bvsegment and Hard Exudate Buttons 
    col3, col4,col5 = st.columns([1,1,1],vertical_alignment="center")
    
    # Creates third button, if pressed add images plus caption and description to session state image list
    if col3.button("bvsegment",use_container_width=True,help="Uploads image for blood vessel segmentation") and uploaded_file is not None:
        bvsegment = extract_bv(uploaded_image)
        bvsegment = Image.fromarray(bvsegment)
        caption = "Displaying blood vessels in eye"
        description = "jfnsfklf"
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
        description = "hbfjnosf"
        handle_button_click(4, optical_disk, caption, description)
   
    # Creates fifth button, if pressed add images plus caption and description to session state image list
    if col5.button("Hard Exudates",use_container_width=True,help="Uploads image for hard exudates detection") and uploaded_file is not None:
        hard_exudates = extract_microaneurysmsdet(uploaded_image)
        hard_exudates = Image.fromarray(hard_exudates)
        caption = "Displaying hard exudates in eye"
        description = "uinfiofnj"
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
            pdf_file = generate_pdf(st.session_state.images, uploaded_image)
            with open(pdf_file, "rb") as f:
                if st.download_button("Download PDF", f, file_name="diabetic_retinopathy_results.pdf"):
                    pdf_file = None