import streamlit as st
import pandas as pd
import requests
from PIL import Image


# Load department and major lists
departments = pd.read_csv("department_list.csv")[
    "Department"
].tolist()
majors = pd.read_csv("major_list.csv")[
    "Major"
].tolist()
years = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate", "PhD", "Professional"]
semesters = ["Fall", "Spring", "Summer"]

# Load logos
duke_name_path = "Duke_name.png"
duke_name = Image.open(duke_name_path)
hack_logo_path = "Duke_Hackathon.png"
hack_logo = Image.open(hack_logo_path)
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    # Display the image on the left side, resized to be smaller
    st.image(duke_name, width=150)  # Adjust width as needed for size

with col2:
    # Place the "Duke AI Hackathon 2024" next to the image on the left
    st.markdown(
        "<h1 style='text-align: center; font-size: 20px; padding-top: 20px;'>Duke AI Hackathon 2024</h1>",
        unsafe_allow_html=True,
    )  # Hackathon text in the middle

with col3:
    # Display the image on the right side, resized to be smaller
    st.image(hack_logo, width=70)  # Adjust width as needed for size


# Add space between "Hackathon 2024" text and the main header
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# "Duke Course Recommendation" title centered below
st.markdown(
    "<h2 style='text-align: center;padding-top: -15px;'>Duke Course Recommendation</h2>",
    unsafe_allow_html=True,
)

# Increase font size and bold for questions and add line spacing
st.markdown(
    "<style> div.stSelectbox label {font-size: 1.4em; font-weight: bold; margin-top: 10px;} </style>",
    unsafe_allow_html=True,
)

# Form questions
education_level = st.selectbox(
    "Are you an undergraduate or graduate?", ["Undergraduate", "Graduate"]
)
department = st.selectbox("Which department are you in?", departments)
major = st.selectbox("Which major are you in?", majors)
year = st.selectbox("Which year are you in?", years)
semester = st.selectbox("Which semester are you planning?", semesters)

# Transcript upload
transcript = st.file_uploader("Upload your transcript", type=["pdf", "docx", "txt"])

# Use columns to position the Submit button on the right
col_empty, col_submit = st.columns([3, 1])


# Function to submit data to backend
def submit_data():
    files = {"transcript": transcript.getvalue()} if transcript else None
    data = {
        "education_level": education_level,
        "department": department,
        "major": major,
        "year": year,
        "semester": semester,
    }
    response = requests.post("http://localhost:8501", data=data, files=files)

    # # Check if the response was successful
    # if response.status_code == 200:
    #     try:
    #         return response.json()
    #     except ValueError:
    #         st.error(
    #             "Failed to decode JSON response. The server may not have returned JSON."
    #         )
    #         return None
    # else:
    #     st.error(f"Request failed with status code {response.status_code}")
    #     return None


# Empty space on the left, button on the right
with col_submit:
    if st.button("Submit"):
        result = submit_data()
        # st.write("Recommended Courses:", result.get("courses"))
        if result is not None:
            st.write("Recommended Courses:", result.get("courses"))
        else:
            st.write("No course recommendations available.")
