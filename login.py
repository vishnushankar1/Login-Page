import streamlit as st
import smtplib
from pymongo import MongoClient  # Import pymongo for MongoDB connection
import re
from email.message import EmailMessage

# Replace with your actual MongoDB connection string
mongo_uri = "mongodb+srv://admin:7FVAIpyDACCG9FWv@cluster0.9flctdw.mongodb.net/"

# Create a MongoDB client
client = MongoClient(mongo_uri)

# Access the database and collection (replace with your desired names)
db = client["practice"]
collection = db["dummy"]

# Email validation function using regex
def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

# Function to suggest corrections for common domain typos
def suggest_domain(email):
    # Common email domains
    common_domains = {
        "gmail.com": ["gamil.com", "gmial.com", "gmai.com", "gm.com"],
        "yahoo.com": ["yaho.com", "yaoo.com", "yhoo.com", "yah.com"],
        "outlook.com": ["outlok.com", "outlok.co", "otlouk.com", "out.com"],
        "hotmail.com": ["hotmil.com", "hotmal.com", "hot.com"]
    }
    
    if "@" in email:
        user_part, domain_part = email.split("@")
        if domain_part not in common_domains and all(domain_part not in typos for typos in common_domains.values()):
            return "Invalid domain. Please use a common domain like gmail.com, yahoo.com, outlook.com, or hotmail.com."
        
        for correct_domain, typo_list in common_domains.items():
            if domain_part in typo_list:
                return correct_domain  # Suggest the correct domain if a typo is found
    return None

# Send reset email function
def send_reset_email(user_email, reset_link):
    try:
        msg = EmailMessage()
        msg.set_content(f"Please click the following link to reset your password: {reset_link}")
        msg['Subject'] = "Password Reset Request"
        msg['From'] = "youremail@gmail.com"  # Replace with your email
        msg['To'] = user_email

        # Set up the server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("youremail@gmail.com", "yourpassword")  # Replace with your email and password
        server.send_message(msg)
        server.quit()

        st.success("Password reset email sent! Please check your inbox.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Forgot password function
def forgot_password():
    st.subheader("Forgot Password")
    
    email = st.text_input("Enter your registered email address")
    
    if st.button("Send Reset Link"):
        if not validate_email(email):
            st.error("Invalid email format. Please enter a valid email.")
        else:
            user = collection.find_one({"email": email})
            if user:
                reset_link = f"http://example.com/reset-password/{user['_id']}"  # Mock reset link
                send_reset_email(email, reset_link)
            else:
                st.error("No account found with that email address.")

# Register user function
def register_user(name, email, password, stream):
    if collection.find_one({"email": email}):
        st.error("User with this email already exists. Please try logging in.")
    else:
        registration_data = {
            "name": name,
            "email": email,
            "password": password,
            "stream": stream
        }
        result = collection.insert_one(registration_data)
        if result.acknowledged:
            st.success("Registration successful!")
        else:
            st.error("Error occurred during registration.")

# Login user function
def login_user(email, password):
    user = collection.find_one({"email": email, "password": password})
    if user:
        st.success(f"Welcome back, {user['name']}!")
    else:
        st.error("Invalid email or password.")

def main():
    st.title("User Authentication System")

    option = st.sidebar.selectbox("Select an option", ["Register", "Login", "Forgot Password"])

    if option == "Register":
        st.subheader("Register")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        stream = st.selectbox("Stream", ["CSE", "ECE", "EEE", "ME", "CE"])

        if st.button("Register"):
            if not validate_email(email):
                st.error("Invalid email format. Please enter a valid email.")
            else:
                suggested_domain = suggest_domain(email)
                if suggested_domain and email.split("@")[1] != suggested_domain:
                    st.warning(f"Did you mean {email.split('@')[0]}@{suggested_domain}?")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    register_user(name, email, password, stream)

    elif option == "Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not validate_email(email):
                st.error("Invalid email format. Please enter a valid email.")
            else:
                login_user(email, password)

    elif option == "Forgot Password":
        forgot_password()

if __name__ == "__main__":
    main()
