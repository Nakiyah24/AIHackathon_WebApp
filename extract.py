import fitz  # PyMuPDF

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
                
                # Debug print: Show each line being processed
                print(f"Processing line: {line}")
                
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
                        print(f"Added course: {subject_code} - {course_title}")
                    
                    # Update the current line as subject code
                    subject_code = line
                    print(f"Identified subject code: {subject_code}")
                    
                # Check if the line is part of the course title
                elif line and not any(char.isdigit() for char in line) and line != '-':
                    title_parts.append(line)  # Collect lines as part of title
                    print(f"Appending to title: {line}")
                    
            # After the loop, save any remaining title
            if title_parts and subject_code:
                course_title = " ".join(title_parts).strip()
                course_data.append({
                    'subject': subject_code,
                    'title': course_title
                })
                print(f"Added final course: {subject_code} - {course_title}")
    
    # Filter out any unrelated entries (comment this out for testing)
    filtered_data = [course for course in course_data if course['subject'] in {'IDS', 'GS'}]
    
    return filtered_data

# Usage
pdf_path = "Grades.pdf"  # Replace with your PDF file path
courses = extract_courses(pdf_path)
print("Extracted courses:", courses)
