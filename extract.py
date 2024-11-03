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
