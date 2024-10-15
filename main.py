import streamlit as st
from profile_manager import manage_profiles

# Sample user data
users = {
    "a": "a",
    "b": "b",
}

# Function to check if the username and password are valid
def check_login(username, password):
    return username in users and users[username] == password

# Create a login form
def login():
    #st.subheader("Login")
    st.write("P❤lease Whatsapp to get your username and password")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("Login successful!")
            st.session_state["show_tools"] = True  # Flag to show tools
            st.rerun()  # Refresh the app to load new profiles
            return True  # Login successful
        else:
            st.error("Invalid username or password")
    return False  # Login failed

def logout_user():
    """Function to log out the user."""
    # Clear the session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("You have been logged out successfully.")
    st.session_state["logged_out"] = True  # Set logged out flag
    st.rerun()  # Rerun the app to reflect the logout


def main():
    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.button("Log Out"):
            logout_user()  # Call the logout function

        st.title("Your Receipt Extractor")
        st.write(f"Hello, {st.session_state['username']}! You are logged in.")

        # Sidebar content
        selected_profile = None



        # Display selected profile (just for demonstration)
        st.write(f"Selected Profile: {selected_profile}")

        # Rest of the app content
        with st.expander("Show - Guide to use this app"):
            st.write("""
            ### How to Use:
            1. Upload your receipt by clicking the 'Upload' button.
            2. The app will automatically extract the relevant information such as date, total amount, and items.
            3. You can review and edit the extracted information before saving it to your profile.
            4. Manage your saved receipts in the 'Profiles' section.
            5. For any issues, refer to the help section or contact support.
            """)

        manage_profiles()

    else:
        st.title("Please Login")
        login()  # Show login form if not logged in

# Run the app
if __name__ == "__main__":
    main()
