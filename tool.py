import streamlit as st  # Correct import

import pandas as pd
import os
from io import BytesIO
import openai
import pytesseract
from PIL import Image
import tiktoken  # Make sure to import tiktoken


# Set up OpenAI API key
openai.api_key = 'sk-IZ1KCfWiLtZ87FdTiEWSzQxUhsWgPneZD0ZeScTWV1T3BlbkFJUsA0IyG1Uk5qnCKQFrj_PbRAQ2CIY1mTzOrj5pVjcA'


def get_text_response(extracted_text):
    """Get a response from OpenAI based on the extracted text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Extract Store Name: /n, Item Purchase: /n, Price: /n. no other symbol. Show Store Name: only once"},
                {
                    "role": "user",
                    "content": extracted_text,
                },
            ],
        )
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"Error getting response from OpenAI: {e}")
        return None


# Function to calculate the token count accurately
def calculate_token_count(messages):
    enc = tiktoken.encoding_for_model("gpt-4o-mini")  # Use the appropriate model
    token_count = 0
    for message in messages:
        token_count += len(enc.encode(message['content']))  # Accurate token count
    return token_count


def save_to_excel(username, profile_name, data_to_save):
    """Save extracted data to an Excel file named according to 'username_profilename.xlsx'."""
    # Define the directory path
    directory = os.path.join('profiles', username)

    # Check if the directory exists; if not, create it
    os.makedirs(directory, exist_ok=True)

    # Format the Excel file name as 'username_profilename.xlsx'
    excel_file = os.path.join(directory, f"{username}_{profile_name}_data.xlsx")
    df = pd.DataFrame(data_to_save)

    if os.path.exists(excel_file):
        # If file already exists, append the new data
        existing_df = pd.read_excel(excel_file)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_excel(excel_file, index=False)
    else:
        # If file doesn't exist, create a new one
        df.to_excel(excel_file, index=False)

    # Return an in-memory version for download
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output




def process_uploaded_file(uploaded_file, username, profile_name):
    """Process the uploaded file and extract text."""
    try:
        image = Image.open(uploaded_file)
        extracted_text = pytesseract.image_to_string(image)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        response_data = get_text_response(extracted_text)
        st.subheader("Extracted Details:")
        st.write(response_data)

        # Optionally, save extracted data
        if st.button("Save to Excel"):
            data_to_save = [{"Extracted Text": response_data}]  # Structure data as needed
            save_to_excel(username, profile_name, data_to_save)
            st.success(f"Data saved to {username}_{profile_name}_data.xlsx successfully.")
            st.rerun()
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
