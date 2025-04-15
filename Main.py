import streamlit as st 

# Page title and layout settings
st.set_page_config(page_title="Initiative Manager", layout="wide")
 
# Logo image path
LOGO_PATH = "logo.png"  # Replace with the actual path to your logo image

# Sidebar settings
st.sidebar.image(LOGO_PATH, use_container_width=True)  # Display the logo image

# Sidebar menu
st.sidebar.subheader("Pages")
st.sidebar.write("Select a page from the menu above.")

# Main page content
st.title("Initiative Manager")
st.write("Welcome to the Initiative Manager!")

# Add your page content here
