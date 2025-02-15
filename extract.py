'''import fitz  # PyMuPDF
import re

def extract_courses(pdf_path):
    course_data = []
    current_description = []
    current_course_id = None
    skip_phrases = ["Duke University", "Name:", "Id:", "Career:", "Term:", "DESCRIPTION", "GRADING", "OFFICIAL", "No Grade", "GRADE POINTS", "0.00", "-"]
    
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
                
                # Collect two-line course descriptions
                if len(current_description) < 2:
                    if line and not line.isdigit() and not course_id_pattern.match(line):
                        current_description.append(line)
                        print(f"Appending to description: {line}")
                
                # After two description lines, collect the course ID
                elif len(current_description) == 2:
                    # Check if the line matches the course ID pattern (e.g., 'IDS' or 'GS')
                    if course_id_pattern.match(line):
                        current_course_id = line
                        full_description = " ".join(current_description).strip()
                        course_data.append({
                            'id': current_course_id,
                            'description': full_description
                        })
                        print(f"Added course: {current_course_id} - {full_description}")
                        
                        # Reset for the next course
                        current_description = []
                    else:
                        # In case we missed a course ID, clear the description
                        current_description = []
    
    return course_data

# Usage
pdf_path = "Grades.pdf"  # Path to the PDF file
courses = extract_courses(pdf_path)
print("Extracted courses:", courses)
'''

import fitz  # PyMuPDF
import re

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

# Usage
pdf_path = "Grades.pdf"  # Path to the PDF file
courses = extract_courses(pdf_path)
print("Extracted courses:", courses)


'''import streamlit as st
import pandas as pd
import requests
from PIL import Image
from datetime import datetime, timedelta
from ics import Calendar, Event
import base64
import io
from st_aggrid import AgGrid, GridOptionsBuilder
import calplot  # Calendar heatmap
import matplotlib.pyplot as plt
import fitz  # PyMuPDF

def load_data():
    # Load department and major lists
    try:
        departments = pd.read_csv("department_list.csv")["Department"].tolist()
        majors = pd.read_csv("major_list.csv")["Major"].tolist()
        years = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate", "PhD", "Professional"]
        semesters = ["Fall", "Spring"]
        return departments, majors, years, semesters
    except FileNotFoundError:
        st.error("Required files not found. Please make sure 'department_list.csv' and 'major_list.csv' are available.")
        return [], [], [], []


def create_form(departments, majors, years, semesters):
    # Increase font size and bold for questions and add line spacing
    st.markdown(
        "<style> div.stSelectbox label {font-size: 1.4em; font-weight: bold; margin-top: 10px;} </style>",
        unsafe_allow_html=True,
    )

    # Form questions
    education_level = st.selectbox("Are you an undergraduate or graduate?", ["Undergraduate", "Graduate"])
    department = st.selectbox("Which department are you in?", departments)
    major = st.selectbox("Which major are you in?", majors)
    year = st.selectbox("Which year are you in?", years)
    semester = st.selectbox("Which semester are you planning?", semesters)
    
    # Transcript upload
    transcript = st.file_uploader("Upload your transcript", type=["pdf", "docx", "txt"])

    return education_level, department, major, year, semester, transcript


def submit_data(education_level, department, major, year, semester, transcript):
    files = {"transcript": transcript.getvalue()} if transcript else None
    data = {
        "education_level": education_level,
        "department": department,
        "major": major,
        "year": year,
        "semester": semester,
    }
    response = requests.post("http://localhost:8501", data=data, files=files)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Failed to decode JSON response. The server may not have returned JSON.")
            return None
    else:
        st.error(f"Request failed with status code {response.status_code}")
        return None


def load_images():
    # Load logos
    try:
        duke_name = Image.open("Duke_name.png")
        hack_logo = Image.open("Duke_Hackathon.png")
        return duke_name, hack_logo
    except FileNotFoundError:
        st.error("Image files not found. Please make sure 'Duke_name.png' and 'Duke_Hackathon.png' are available.")
        return None, None

def display_header(duke_name, hack_logo):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if duke_name:
            st.image(duke_name, width=150)
    with col2:
        st.markdown(
            "<h1 style='text-align: center; font-size: 20px; padding-top: 20px;'>Duke AI Hackathon 2024</h1>",
            unsafe_allow_html=True,
        )
    with col3:
        if hack_logo:
            st.image(hack_logo, width=70)
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align: center;padding-top: -15px;'>Duke Course Recommendation</h2>",
        unsafe_allow_html=True,
    )

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
    # Split the days string into separate columns for each day
    days_expanded = df["day"].apply(lambda x: pd.Series(parse_merged_days(x)))
    days_expanded.columns = [f"Day {i+1}" for i in range(days_expanded.shape[1])]
    df = pd.concat([df, days_expanded], axis=1).drop(columns="day")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Courses")
    output.seek(0)
    return output

def save_ics(calendar):
    with open("calendar.ics", "w") as f:
        f.writelines(calendar)

def download_files(course_data):
    calendar = generate_ics(course_data)
    save_ics(calendar)  # This will save the .ics file locally
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

def display_courses(course_data):
    # Create a DataFrame to display course details
    df_courses = pd.DataFrame(course_data)
    
    # Expand days into a more readable format (not displayed in AgGrid)
    df_courses['days'] = df_courses['day'].apply(parse_merged_days)
    df_courses['formatted_days'] = df_courses['days'].apply(lambda x: ', '.join(x))
    
    # Prepare the AgGrid and hide the original 'days' column
    gb = GridOptionsBuilder.from_dataframe(df_courses)
    
    # Hide the 'days' column
    gb.configure_column("days", hide=True)  # Hides the 'days' column
    grid_options = gb.build()
    
    st.subheader("Course List")
    
    # Display the DataFrame using AgGrid, including 'formatted_days'
    AgGrid(df_courses[['course_name', 'start_time', 'end_time', 'formatted_days']], gridOptions=grid_options, allow_unsafe_jscode=True)

def extract_courses(pdf_path):
    course_data = []
    title_parts = []
    subject_code = None
    
    # Open the PDF
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text = page.get_text("text")
            
            # Split text into lines
            lines = text.splitlines()
            
            for i in range(len(lines)):
                line = lines[i].strip()
                
                # Check if line is a likely subject code (e.g., 'IDS', 'GS')
                if line.isupper() and len(line.split()) <= 4 and line.isalpha() and not line.startswith("DESCRIPTION"):
                    # Save any previously accumulated course data
                    if title_parts and subject_code:
                        course_title = " ".join(title_parts).strip()
                        course_data.append({
                            'subject': subject_code,
                            'title': course_title
                        })
                        title_parts = []  # Reset for the next course
                    
                    # Update the current line as subject code
                    subject_code = line
                    
                # Check if the line is part of the course title
                elif line and not any(char.isdigit() for char in line) and line != '-':
                    title_parts.append(line)  # Collect lines as part of title
                    
            # After the loop, save any remaining title
            if title_parts and subject_code:
                course_title = " ".join(title_parts).strip()
                course_data.append({
                    'subject': subject_code,
                    'title': course_title
                })
    
    # Filter out any unrelated entries
    filtered_data = [course for course in course_data if course['subject'] in {'IDS', 'GS'}]
    
    return filtered_data




def main():
    departments, majors, years, semesters = load_data()
    duke_name, hack_logo = load_images()
    
    if departments and majors and duke_name and hack_logo:
        display_header(duke_name, hack_logo)

        education_level, department, major, year, semester, transcript = create_form(departments, majors, years, semesters)
        st.subheader("Upload Course PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            # Extract courses from uploaded PDF
            extracted_courses = extract_courses(uploaded_file)
            if extracted_courses:
                st.success("Courses extracted successfully!")
                display_courses(extracted_courses)
                download_files(extracted_courses)
            else:
                st.error("No courses found in the PDF.")

if __name__ == "__main__":
    main()'''
    