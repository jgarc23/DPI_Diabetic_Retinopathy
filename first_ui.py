import streamlit as st
from PIL import Image
from microaneurysms import *
from microaneurysmdetection import *
from bvsegment import *
import os
import cv2
import numpy as np

def click_button():        
    st.session_state.clicked = True

if __name__ == '__main__':
    # Title
    st.header("Diabetic Retinopathy Segmentation Assistant",divider='gray')

    # Image uploader 
    uploaded_file = st.file_uploader("Upload Image Here:",type=["jpg","jpeg","png"],help="Select an image to upload for analysis")
    uploaded_image = None

    if uploaded_file is not None:
        # Convert the uploaded file to an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        uploaded_image = cv2.imdecode(file_bytes, 1)
    
    microaneurysmsdet = None
    microaneurysms = None
    bvsegment = None

    # Button state control
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False


    # Upload Image to server for analysis
    bl1, upl, bl2 = st.columns([1,3,1])
    with upl:
        st.button("Upload",use_container_width=True, on_click=click_button)
        if st.session_state.clicked: 

            # Process the images to extract microaneurysms
            if uploaded_image is not None:
                microaneurysms = extract_microaneurysms(uploaded_image)
                microaneurysmsdet = extract_microaneurysmsdet(uploaded_image)
                bvsegment = extract_bv(uploaded_image)
                
                # Convert processed images to a format that can be displayed by Streamlit
                microaneurysms = Image.fromarray(microaneurysms)
                microaneurysmsdet = Image.fromarray(microaneurysmsdet)
                bvsegment = Image.fromarray(bvsegment)
                st.session_state.clicked = False
            # else:
            #   st.write("Please upload image")
    
    # Display original eye image
    bl1,img_org,bl2 = st.columns([2,1,2.5])
    with img_org:
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Original Eye Image", width=200)

    # Display analyzed eye images
    img_mic,bl1,img_bvseg,bl2 = st.columns([1,1,1,0.5])
    with img_mic:
        if microaneurysms is not None:
            st.image(microaneurysms, caption="Microaneurysms found in eye",width=300)
    with img_bvseg:
        if microaneurysmsdet is not None:
            st.image(bvsegment, caption="BV Segmentation of eye", width=300)
           

    # DELETE EXTRA BUTTONS
    # Display buttons for diagnostic categories
    col1, b1, col2 = st.columns([2,3,2])
    
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
        if st.button("BV Segmentation",use_container_width=True):
 
            if bvsegment is not None:
                st.image(bvsegment, caption="BV Segmentation of eye", use_column_width=True)
        
        # Displays image analyzed with optical disk algorithm
        if st.button("Hard Exudates",use_container_width=True):
            
            if microaneurysmsdet is not None:
                st.image(microaneurysmsdet, caption="Hard Exudates found in eye", use_column_width=True)

