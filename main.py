import streamlit as st
import easyocr
from PIL import Image
import numpy as np

# Set up EasyOCR reader (supporting English and multiple languages)
reader = easyocr.Reader(['en'], gpu=False)  # Use GPU=True if you have a compatible GPU

# Title of the Streamlit app
st.title("Image to Text Converter using EasyOCR")

# Upload image
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_image is not None:
    # Display the uploaded image
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert the image to a NumPy array for OCR processing
    image_np = np.array(image)

    # Button to start the text extraction
    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            # Perform OCR on the image
            result = reader.readtext(image_np)

            # Display extracted text
            extracted_text = ""
            for detection in result:
                extracted_text += detection[1] + "\n"
            
            # Show the extracted text in the Streamlit app
            st.subheader("Extracted Text")
            st.text(extracted_text)
else:
    st.write("Please upload an image to extract text.")
