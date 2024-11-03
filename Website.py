import streamlit as st
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
    gb.configure_column("days", hide=True)  # Hides the 'days' column
    grid_options = gb.build()
    
    st.subheader("Course List")
    # Display the DataFrame using AgGrid, including 'formatted_days'
    AgGrid(df_courses[['course_name', 'start_time', 'end_time', 'formatted_days']], gridOptions=grid_options, allow_unsafe_jscode=True)

def upload_transcript():
    st.subheader("Upload Transcript")
    uploaded_file = st.file_uploader("Choose a transcript file", type=["pdf", "csv", "txt"])
    
    if uploaded_file is not None:
        if uploaded_file.type == "text/csv":
            transcript_data = pd.read_csv(uploaded_file)
            st.write("Transcript Data:")
            st.dataframe(transcript_data)
        elif uploaded_file.type == "application/pdf":
            st.write("PDF format detected. Processing...")
            # PDF processing logic can go here (using libraries like PyPDF2 or pdfplumber)
        elif uploaded_file.type == "text/plain":
            transcript_data = uploaded_file.read().decode("utf-8")
            st.write("Transcript Text:")
            st.text(transcript_data)

def main():
    departments, majors, years, semesters = load_data()
    duke_name, hack_logo = load_images()
    
    if departments and majors and duke_name and hack_logo:
        display_header(duke_name, hack_logo)

        # User input selection
        st.subheader("Select Your Preferences")
        selected_department = st.selectbox("Department", departments)
        selected_major = st.selectbox("Major", majors)
        selected_year = st.selectbox("Year", years)
        selected_semester = st.selectbox("Semester", semesters)

        # Upload transcript section
        upload_transcript()

        # Processing button to trigger backend actions
        if st.button("Generate Recommendations"):
            st.write("Processing your inputs and generating recommendations...")
            
            course_data = [
                {"day": "mowe", "start_time": "10:00", "end_time": "11:30", "course_name": "Data Science 101"},
                {"day": "tuth", "start_time": "14:00", "end_time": "15:30", "course_name": "Machine Learning"},
                {"day": "f", "start_time": "09:00", "end_time": "10:30", "course_name": "Statistical Analysis"},
            ]
            
            display_courses(course_data)
            download_files(course_data)

if __name__ == "__main__":
    main()
