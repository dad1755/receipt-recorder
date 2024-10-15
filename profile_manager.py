import streamlit as st  # Correct import

import pandas as pd
import os
from PIL import Image
from tool import get_text_response, calculate_token_count
import pytesseract

def manage_profiles():
    # Check if the user is logged in
    if "username" in st.session_state:
        username = st.session_state["username"]

        st.sidebar.subheader("Profile Management")

        profiles = load_profiles(username)

        options = ["None", "Create New Profile"] + profiles

        selected_profile = st.sidebar.selectbox("Select Profile", options, index=0, key="profile_selection")

        if "current_profile" in st.session_state and st.session_state["current_profile"] != selected_profile:
            # Clear previous states when the profile changes
            st.session_state.pop('current_profile', None)
            st.session_state.pop('uploaded_file', None)
            st.session_state.pop('upload_history', None)
            st.rerun()

        st.session_state["current_profile"] = selected_profile

        if selected_profile == "Create New Profile":
            create_new_profile(username)
        elif selected_profile != "None":
            st.sidebar.success("You can modify this profile.")
            st.write(f"You selected profile: {selected_profile}")

            # Show design upload tools for the selected profile
            show_design_upload_tools(username, selected_profile)

        if selected_profile and selected_profile != "None" and selected_profile != "Create New Profile":
            if st.sidebar.button("Delete Profile", key=f"delete_{selected_profile}"):
                delete_profile(username, selected_profile)
                st.success(f"Profile '{selected_profile}' has been deleted.")
                st.rerun()

        # Show the total sum of prices for the selected profile
        if selected_profile and selected_profile != "None" and selected_profile != "Create New Profile":
            total_sum = calculate_total_sum(username, selected_profile)
            st.sidebar.write(f"Total Sum of Prices: RM{total_sum:.2f}")

            # Add a download button
            download_file_path = os.path.join('record', 'direct_base_' + username, f"{username}_{selected_profile}_data.xlsx")
            if os.path.exists(download_file_path):
                with open(download_file_path, "rb") as f:
                    st.sidebar.download_button(
                        label="Download Excel File",
                        data=f,
                        file_name=f"{username}_{selected_profile}_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.sidebar.warning("No data available to download.")
    else:
        st.write("Please log in to manage your profiles.")


def calculate_total_sum(username, profile_name):
    """Calculate the total sum of prices from the user's profile."""
    filename = os.path.join('record', f"{username}_{profile_name}_data.xlsx")
    total_sum = 0.0

    if os.path.exists(filename):
        df = pd.read_excel(filename,engine='openpyxl')

        # Check if 'Price' column exists
        if 'Price' in df.columns:
            # Clean the price data by removing non-numeric characters
            df['Price'] = df['Price'].replace({r'\$': '', ',': ''}, regex=True)  # Remove $ and commas
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')  # Convert to numeric, coercing errors to NaN
            total_sum = df['Price'].sum()  # Sum the cleaned prices

    return total_sum

def load_profiles(username):
    """Load profiles from a single Excel file."""
    profiles = []
    if username:
        filename = os.path.join('profiles', f"{username}.xlsx")
        if os.path.exists(filename):
            df = pd.read_excel(filename)
            profiles = df['Profile Name'].tolist()  # Assuming the Excel has a column 'Profile Name'
    return profiles

def create_new_profile(username):
    """Create a new profile."""
    new_profile_name = st.text_input("Enter new profile name")

    if st.button("Create Profile", key="create_profile"):
        if new_profile_name:
            filename = os.path.join('profiles', f"{username}.xlsx")
            user_directory = os.path.dirname(filename)
            os.makedirs(user_directory, exist_ok=True)

            # Check if the file already exists
            if os.path.exists(filename):
                df = pd.read_excel(filename)
            else:
                df = pd.DataFrame(columns=['Profile Name'])  # Create a new DataFrame if file does not exist

            # Create a DataFrame for the new profile
            new_profile_df = pd.DataFrame({'Profile Name': [new_profile_name]})
            df = pd.concat([df, new_profile_df], ignore_index=True)  # Concatenate the DataFrames
            df.to_excel(filename, index=False)
            st.success(f"Profile '{new_profile_name}' created successfully.")
            st.rerun()
        else:
            st.error("Please enter a profile name.")

def delete_profile(username, profile_name):
    """Delete a specified profile."""
    filename = os.path.join('profiles', f"{username}.xlsx")
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        df = df[df['Profile Name'] != profile_name]  # Remove the profile
        df.to_excel(filename, index=False)
    else:
        st.error("Profile file not found.")

def show_design_upload_tools(username, profile_name):
    """Display the design upload tools."""
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None

    uploaded_file = st.file_uploader("Upload your design file (e.g., .png, .jpg)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image.thumbnail((900, 900))

        extracted_text = pytesseract.image_to_string(image)

        messages = [
            {"role": "user", "content": "Extract store name, items, and prices."},
            {"role": "user", "content": extracted_text}
        ]

        total_tokens = calculate_token_count(messages)

        st.write(f"Total Token Count: {total_tokens}")

        if total_tokens > 128000:
            st.error("Token count exceeds the model's maximum context length. Please reduce the message length.")
            return  # Stop further processing if token count is too high

        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption='Uploaded Image', width=300)

        with st.spinner("Analyzing image..."):
            extracted_data = get_text_response(extracted_text)

        if extracted_data is not None:
            with col2:
                st.subheader("Extracted Details:")
                st.write(extracted_data)

                try:
                    lines = extracted_data.split('\n')

                    store_name = next((line.split(":")[1].strip() for line in lines if "Store Name" in line), None)
                    items = []

                    for i in range(len(lines)):
                        if "Item Purchase" in lines[i]:
                            item_name = lines[i].split(":")[1].strip()
                            if i + 1 < len(lines) and "Price" in lines[i + 1]:
                                price = lines[i + 1].split(":")[1].strip()
                                items.append({"Store Name": store_name, "Item Purchased": item_name, "Price": price})

                    if items:
                        save_to_excel(username, profile_name, items)
                        st.success("Items extracted and saved successfully!")
                        # Update the total sum after extraction
                    else:
                        st.error("No items could be extracted.")
                except IndexError:
                    st.error("Could not extract all details. Please check the text format.")
        else:
            st.error("Failed to extract text. Please try again.")
    else:
        st.warning("No file uploaded. Please upload a design file.")



def save_to_excel(username, profile_name, items):
    """Save extracted items to the user's profile in a single Excel file."""

    # Create the directory path
    dir_path = os.path.join('record', 'direct_base_' + username)

    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    # Define the filename with the new path
    filename = os.path.join(dir_path, f"{username}_{profile_name}_data.xlsx")

    # Check if the file exists
    if os.path.exists(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame(columns=['Store Name', 'Item Purchased', 'Price'])  # Initialize DataFrame with correct columns

    # Convert items to DataFrame
    items_df = pd.DataFrame(items)

    # Concatenate the new items to the existing DataFrame
    df = pd.concat([df, items_df], ignore_index=True)

    # Save back to the same Excel file
    df.to_excel(filename, index=False)


# Call the manage_profiles function to run the app
if __name__ == "__main__":
    manage_profiles()
