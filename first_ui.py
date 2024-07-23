import streamlit as st
from PIL import Image
from microaneurysms import *
from microaneurysmdetection import *
from bvsegment import *
from text import *

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
def handle_button_click(button_id,img,cap,img_count):
    if uploaded_file is not None and st.session_state.buttons[button_id] != uploaded_file:
        st.session_state.images.append((img, cap))
        st.session_state.buttons[button_id] = uploaded_file
        img_count += 1

if __name__ == '__main__':
    # Title
    st.header("Diabetic Retinopathy Segmentation Assistant",divider='gray')
    # Short description on diabetic retinopathy. Find in text.py file
    st.markdown(dr_desc)

    # Image uploader 
    uploaded_file = st.file_uploader("Upload Image Here:",type=["jpg","jpeg","png"],help="Select an image to upload for analysis")
    uploaded_image = None
    img_count = 0

    # Initialize session state for keeping track of images and button states 
    # (to prevent images from dissapearing or being displayed twice)
    if 'images' not in st.session_state:
        st.session_state.images = []
    if 'buttons' not in st.session_state:
        st.session_state.buttons = {1: None, 2: None, 3: None, 4: None}

    # Check if an image was uploaded
    if uploaded_file is not None:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        uploaded_image = cv2.imdecode(file_bytes, 1)
    # If empty reset the session states for images and buttons.
    else:
        st.session_state.buttons = {1: None, 2: None, 3: None, 4: None}
        st.session_state.images = []
        
    # # Display original image 
    # bl1,img_org,bl2 = st.columns([2,1,2.5])
    

    # Create variables for output analyzed images 
    microaneurysmsdet = None
    microaneurysms = None
    bvsegment = None
    soft_exudates = None
    hard_exudates = None
     
    # Microaneurysms and Soft Exudate Buttons
    col1,img_org,col2= st.columns([1,1,1],vertical_alignment="bottom") 
    with img_org:
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Original Eye Image", use_column_width=True)

    if col1.button("Microaneurysms",use_container_width=True,help="Uploads image for microaneurysm detection") and uploaded_file is not None:
        microaneurysms = extract_microaneurysms(uploaded_image)
        microaneurysms = Image.fromarray(microaneurysms)
        caption = "Displaying microaneurysms in eye"
        handle_button_click(1, microaneurysms, caption,img_count)

    if col2.button("Soft Exudates",use_container_width=True,help="Uploads image for soft exudate detection") and uploaded_file is not None:
        soft_exudates = extract_microaneurysmsdet(uploaded_image)
        soft_exudates = Image.fromarray(soft_exudates)
        caption = "Displaying soft exudates in eye"
        handle_button_click(2, soft_exudates, caption,img_count)

    # Bvsegment and Hard Exudate Buttons 
    col3, bl1,col4 = st.columns([1,1,1],vertical_alignment="center")
    
    if col3.button("bvsegment",use_container_width=True,help="Uploads image for blood vessel segmentation") and uploaded_file is not None:
        bvsegment = extract_bv(uploaded_image)
        bvsegment = Image.fromarray(bvsegment)
        caption = "Displaying blood vessels in eye"
        handle_button_click(3, bvsegment, caption,img_count)

    if col4.button("Hard Exudates",use_container_width=True,help="Uploads image for hard exudates detection") and uploaded_file is not None:
        hard_exudates = extract_microaneurysmsdet(uploaded_image)
        hard_exudates = Image.fromarray(hard_exudates)
        caption = "Displaying hard exudates in eye"
        handle_button_click(4, hard_exudates, caption,img_count)
    
    st.subheader("Segmentation Results")
    anl_img1, bl1, anl_img2 = st.columns([0.4,0.1,0.4],vertical_alignment="center",gap="large")

    # Display all images in two columns
    if uploaded_file is not None and st.session_state.images:
        for idx, (img, cap) in enumerate(st.session_state.images):
            if idx % 2 == 0:
                with anl_img1:
                    st.image(img, caption=cap,use_column_width=True)
            else:
                with anl_img2:
                    st.image(img, caption=cap, use_column_width=True)
    
    # Short individual descriptions on microaneurysms, blood vessels, hard exudates, and soft exudates. Find in text.py file
    st.markdown(ind_desc)

