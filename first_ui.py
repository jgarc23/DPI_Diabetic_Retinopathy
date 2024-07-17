import streamlit as st
from PIL import Image

def main():
    # Title
    st.header("Diabetic Retinopathy Clinical Support Assisant",divider='gray')

    # Image uploader
    uploaded_file = st.file_uploader("Upload Image Here:",type=["jpg","jpeg","png"],help="help")

    # Upload Image to server for analysis
    bl1, upl, bl2 = st.columns([3,1,3])
    with upl:
        if st.button("Upload",use_container_width=True):
            st.write("Uploaded image for analysis...")

    # Display buttons for diagnostic categories
    col1, bl3, col2 = st.columns([2,3,2])
    
    with col1:
        if st.button("Microaneurysms",use_container_width=True):
            st.write("Microaneursysm category selected")
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Soft Exudates",use_container_width=True):
            st.write("Soft Exudates category selected")
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

    with col2:
        if st.button("Hemorrhage",use_container_width=True):
            st.write("Hemorrhage category selected")
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Hard Exudates",use_container_width=True):
            st.write("Hard Exudates category selected")
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

if __name__ == '__main__':
    main()
