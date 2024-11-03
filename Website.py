import streamlit as st
import pandas as pd
import requests
from PIL import Image
from datetime import datetime, timedelta
from ics import Calendar, Event
import base64
import io
from st_aggrid import AgGrid, GridOptionsBuilder
import fitz  # PyMuPDF
from PIL import Image
import re

def load_images():
    # Load logos
    duke_name_path = "Duke_name.png"
    hack_logo_path = "Duke_Hackathon.png"
    duke_name = Image.open(duke_name_path)
    hack_logo = Image.open(hack_logo_path)
    return duke_name, hack_logo

def load_data():
    try:
        departments = pd.read_csv("department_list.csv")["Department"].tolist()
        majors = pd.read_csv("major_list.csv")["Major"].tolist()
        years = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate", "PhD", "Professional"]
        semesters = ["Fall", "Spring"]
        return departments, majors, years, semesters
    except FileNotFoundError:
        st.error("Required files not found. Please make sure 'department_list.csv' and 'major_list.csv' are available.")
        return [], [], [], []

def display_header(duke_name, hack_logo):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.image(duke_name, width=150)

    with col2:
        st.markdown(
            "<h1 style='text-align: center; font-size: 20px; padding-top: 20px;'>Duke AI Hackathon 2024</h1>",
            unsafe_allow_html=True,
        )

    with col3:
        st.image(hack_logo, width=70)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: center;padding-top: -15px;'>Duke Course Recommendation</h2>",
        unsafe_allow_html=True,
    )

def create_form(departments, majors, years, semesters):
    st.markdown(
        "<style> div.stSelectbox label {font-size: 1.4em; font-weight: bold; margin-top: 10px;} </style>",
        unsafe_allow_html=True,
    )

    education_level = st.selectbox("Select Education Level", ["Undergraduate", "Graduate"])
    department = st.selectbox("Select Department", departments)
    major = st.selectbox("Select Major", majors)
    year = st.selectbox("Select Year", years)
    semester = st.selectbox("Select Semester", semesters)
    transcript = st.file_uploader("Upload your transcript PDF", type=["pdf"])

    return education_level, department, major, year, semester, transcript

'''    education_level = st.selectbox("Are you an undergraduate or graduate?", ["Undergraduate", "Graduate"])
    department = st.selectbox("Which department are you in?", departments)
    major = st.selectbox("Which major are you in?", majors)
    year = st.selectbox("Which year are you in?", years)
    semester = st.selectbox("Which semester are you planning?", semesters)
    
    transcript = st.file_uploader("Upload your transcript", type=["pdf", "docx", "txt"])

    return education_level, department, major, year, semester, transcript
'''
def parse_merged_days(merged_days):
    day_map = {
        'm': 'Mon', 't': 'Tue', 'w': 'Wed', 'th': 'Thu', 'f': 'Fri', 's': 'Sat', 'su': 'Sun'
    }
    days = []
    i = 0
    while i < len(merged_days):
        if i < len(merged_days) - 1 and merged_days[i:i+2] in day_map:
            days.append(day_map[merged_days[i:i+2]])
            i += 2
        elif merged_days[i] in day_map:
            days.append(day_map[merged_days[i]])
            i += 1
        else:
            i += 1
    return days

def parse_merged_days(merged_days):
    day_map = {
        'm': 'Mon', 't': 'Tue', 'w': 'Wed', 'th': 'Thu', 'f': 'Fri', 's': 'Sat', 'su': 'Sun'
    }
    days = []
    i = 0
    while i < len(merged_days):
        if i < len(merged_days) - 1 and merged_days[i:i+2] in day_map:
            days.append(day_map[merged_days[i:i+2]])
            i += 2
        elif merged_days[i] in day_map:
            days.append(day_map[merged_days[i]])
            i += 1
        else:
            i += 1
    return days


def generate_ics(course_data):
    cal = Calendar()
    today = datetime.now()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    day_map = {
        "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
    }

    for course in course_data:
        merged_days = course["day"]
        start_time = course["start_time"]
        end_time = course["end_time"]
        course_name = course["course_name"]
        
        days = parse_merged_days(merged_days)
        
        for day in days:
            day_index = day_map[day]
            for day in range(1, last_day.day + 1):
                current_date = first_day.replace(day=day)
                if current_date.weekday() == day_index:
                    event = Event()
                    event.name = course_name
                    event.begin = f"{current_date.date()}T{start_time}:00"
                    event.end = f"{current_date.date()}T{end_time}:00"
                    
                    cal.events.add(event)
    return cal

def save_excel(course_data):
    df = pd.DataFrame(course_data)
    days_expanded = df["day"].apply(lambda x: pd.Series(parse_merged_days(x)))
    days_expanded.columns = [f"Day {i+1}" for i in range(days_expanded.shape[1])]
    df = pd.concat([df, days_expanded], axis=1).drop(columns="day")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Courses")
    output.seek(0)
    return output

def download_files(course_data):
    calendar = generate_ics(course_data)
    with open("calendar.ics", "w") as f:
        f.writelines(calendar)
        
    with open("calendar.ics", "rb") as f:
        ics_data = f.read()
    ics_b64 = base64.b64encode(ics_data).decode()
    ics_link = f'<a href="data:text/calendar;base64,{ics_b64}" download="calendar.ics">Download Calendar (.ics)</a>'
    
    excel_data = save_excel(course_data)
    excel_b64 = base64.b64encode(excel_data.read()).decode()
    excel_link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="courses.xlsx">Download Course Details (.xlsx)</a>'
    
    st.markdown("### Download Options:")
    st.markdown(ics_link, unsafe_allow_html=True)
    st.markdown(excel_link, unsafe_allow_html=True)

def extract_courses(pdf_path):
    course_data = []
    current_description = []
    current_course_id = None
    skip_phrases = ["Duke University", "Name:", "Id:", "Career:", "Term:", "DESCRIPTION", "GRADING", "OFFICIAL", 
                    "No Grade", "GRADE POINTS", "-", "Units", "Cum", "Graded:", "Credit / No Credit", "Graded"]
    
    # Regular expression to identify subject codes (e.g., IDS, GS)
    course_id_pattern = re.compile(r'^[A-Z]{2,3}$')
    
    # Open the PDF
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text = page.get_text("text")
            
            # Split text into lines
            lines = text.splitlines()
            
            for i in range(len(lines)):
                line = lines[i].strip()
                
                # Debug print: Show each line being processed
                print(f"Processing line: {line}")
                
                # Skip lines that contain irrelevant information
                if any(skip in line for skip in skip_phrases) or not line:
                    continue
                
                # Check if the line matches the course ID pattern (e.g., 'IDS' or 'GS')
                if course_id_pattern.match(line):
                    # If there's already an accumulated description, save the previous course
                    if current_course_id and current_description:
                        full_description = " ".join(current_description).strip()
                        course_data.append({
                            'id': current_course_id,
                            'description': full_description
                        })
                        print(f"Added course: {current_course_id} - {full_description}")
                    
                    # Set the new course ID and reset the description
                    current_course_id = line
                    current_description = []
                    print(f"Identified course ID: {current_course_id}")
                
                # If the line is not a course ID, assume it's part of the description
                else:
                    if line and not any(char.isdigit() for char in line):  # Avoid numeric or unrelated lines
                        current_description.append(line)
                        print(f"Appending to description: {line}")
            
            # After processing all lines, save the last course
            if current_course_id and current_description:
                full_description = " ".join(current_description).strip()
                course_data.append({
                    'id': current_course_id,
                    'description': full_description
                })
                print(f"Added final course: {current_course_id} - {full_description}")
    
    return course_data

def display_courses_pdf(course_data):
    if course_data:
        # Create a DataFrame from the course data
        df = pd.DataFrame(course_data)
        
        # Display the DataFrame in Streamlit
        st.subheader("Course List")
        st.dataframe(df)  # Displays the DataFrame as an interactive table
    else:
        st.warning("No courses available to display.")

def display_courses(course_data):
    df_courses = pd.DataFrame(course_data)
    
    # Ensure the 'day' column exists
    if 'day' in df_courses.columns:
        df_courses['days'] = df_courses['day'].apply(parse_merged_days)
        df_courses['formatted_days'] = df_courses['days'].apply(lambda x: ', '.join(x))
    else:
        st.error("No 'day' data available in the extracted course information.")
        return

    gb = GridOptionsBuilder.from_dataframe(df_courses)
    gb.configure_column("days", hide=True)
    grid_options = gb.build()
    
    st.subheader("Course List")
    
    AgGrid(df_courses[['course_name', 'start_time', 'end_time', 'formatted_days']], gridOptions=grid_options, allow_unsafe_jscode=True)
    
def main():
    departments, majors, years, semesters = load_data()
    duke_name, hack_logo = load_images()
    
    if departments and majors and duke_name and hack_logo:
        display_header(duke_name, hack_logo)

    # Create a form
    with st.form("my_form"):
        # Create form fields
        education_level, department, major, year, semester, transcript = create_form(departments, majors, years, semesters)

        # Input box for user query
        user_query = st.text_input("Enter your query:")

        # Submit button
        submit_button = st.form_submit_button("Submit")
        # Input box for user query

        if transcript is not None:
            # Extract courses from uploaded transcript PDF
            extracted_courses = extract_courses(transcript)
            print(extracted_courses)
            if extracted_courses:
                st.success("Courses extracted successfully!")
                #display_courses_pdf(extracted_courses)
            else:
                st.error("No courses found in the transcript.")

        # Sample course data
        course_data = [
            {"day": "mowe", "start_time": "10:00", "end_time": "11:30", "course_name": "Data Science 101"},
            {"day": "tuth", "start_time": "14:00", "end_time": "15:30", "course_name": "Machine Learning"},
            {"day": "f", "start_time": "09:00", "end_time": "10:30", "course_name": "Statistical Analysis"},
        ]

        # You may need to define this function based on your requirements
        display_courses(course_data)  # New function to display course info
        download_files(course_data)

if __name__ == "__main__":
    main()
