import streamlit as st
import easyocr
from PIL import Image
import numpy as np

# Initialize EasyOCR Reader (with English language support)
reader = easyocr.Reader(['en'], gpu=False)

st.title("Image to Text Converter")

# Upload image
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    # Display uploaded image
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Convert image to NumPy array for EasyOCR
    image_np = np.array(image)
    
    # Extract text button
    if st.button("Extract Text"):
        with st.spinner("Extracting text..."):
            try:
                # Perform OCR on the image
                result = reader.readtext(image_np)
                
                # Check if text is detected
                if result:
                    extracted_text = "\n".join([detection[1] for detection in result])
                    st.subheader("Extracted Text")
                    st.text(extracted_text)
                else:
                    st.warning("No text detected. Please try another image.")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Please upload an image.")
