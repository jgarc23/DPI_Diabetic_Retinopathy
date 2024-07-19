import streamlit as st
from PIL import Image
from microaneurysms import *
from microaneurysmdetection import *
import os
import cv2
import numpy as np


if __name__ == '__main__':
    # Title
    st.header("Diabetic Retinopathy Clinical Support Assisant",divider='gray')

    # Image uploader 
    uploaded_image = st.file_uploader("Upload Image Here:",type=["jpg","jpeg","png"],help="help")
    if uploaded_image is not None:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        uploaded_image = cv2.imdecode(file_bytes, 1)
    
    microaneurysmsdet = None
    microaneurysms = None

    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    def click_button():
        st.session_state.clicked = True

    # Upload Image to server for analysis
    bl1, upl, bl2 = st.columns([3,1,3])
    with upl:
        st.button("Upload",use_container_width=True, on_click=click_button)
        if st.session_state.clicked: 

            # Process the images to extract microaneurysms
            if uploaded_image is not None:
                microaneurysms = extract_microaneurysms(uploaded_image)
                microaneurysmsdet = extract_microaneurysmsdet(uploaded_image)
                
                # Convert processed images to a format that can be displayed by Streamlit
                microaneurysms = Image.fromarray(microaneurysms)
                microaneurysmsdet = Image.fromarray(microaneurysmsdet)
            else:
                st.write("Please upload image")

    # Display buttons for diagnostic categories
    col1, bl3, col2 = st.columns([2,3,2])
    
    # Buttons Microaneurysm and Soft Exudates functionality 
    with col1:
        # Displays image analyzed with microaneursysms algorithm 
        if st.button("Microaneurysms",use_container_width=True):
           
            if microaneurysms is not None:
                st.image(microaneurysms, caption="Microaneurysms found in eye", use_column_width=True)

        # Displays image analyzed with soft exudates algorithm
        if st.button("Soft Exudates",use_container_width=True):

            if microaneurysmsdet is not None:
                st.image(microaneurysmsdet, caption="Soft Exudates found in eye", use_column_width=True)

    # Buttons Hard Exudates and optical disk functionality
    with col2:
        # Displays image analyzed with hard exudates algorithm
        if st.button("Hard Exudates",use_container_width=True):

            if microaneurysmsdet is not None:
                st.image(microaneurysmsdet, caption="Hard Exudates found in eye", use_column_width=True)
        
        # Displays image analyzed with optical disk algorithm
        if st.button("Optical Disk",use_container_width=True):
            
            if microaneurysmsdet is not None:
                st.image(microaneurysmsdet, caption="Optical Disk found in eye", use_column_width=True)

