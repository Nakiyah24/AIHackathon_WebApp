

import sqlite3
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder, models
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder, models
from sklearn.metrics.pairwise import cosine_similarity
import os
from langchain import PromptTemplate, LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
from typing import List

import sqlite3
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder, models
from sklearn.metrics.pairwise import cosine_similarity



sem_var= "fall"
user_query = "I need to look for courses that help me build a career in data science and ML and work as a Machine learning engineer in biomed."
remove_dict= [{'subject':'Political Science' , 'title':'The politics of four of the United States principal racial minority groupsÔøΩÔøΩÔøΩblacks, Latinos, Asians, and American In' }]






# Load models
word_embedding_model = models.Transformer('gsarti/scibert-nli')
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
bi_encoder = SentenceTransformer(modules=[word_embedding_model, pooling_model])
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Connect to the database and load the data
conn = sqlite3.connect("courses.db")
# Variables
subjects = [
    'COMPSCI', 'AIPI', 'POLSCI', 'BIOSTAT', 'CYBERSEC',
    'ECON', 'FINANCE', 'MATH', 'IDS', 'MENG', 'ECE'
]
# Prepare placeholders for the subjects list
subject_placeholders = ', '.join(['?'] * len(subjects))

semester_pattern = f'%{sem_var}%'

# Prepare exclusion conditions
exclusion_conditions = ''
exclusion_params = []
remove_dict= [{'subject':'Political Science' , 'title':'The politics of four of the United States principal racial minority groupsÔøΩÔøΩÔøΩblacks, Latinos, Asians, and American In' }]
if remove_dict:
    exclusion_clauses = []
    for entry in remove_dict:
        exclusion_clauses.append('(subject = ? AND title = ?)')
        exclusion_params.extend([entry['subject'], entry['title']])
    exclusion_conditions = ' AND NOT (' + ' OR '.join(exclusion_clauses) + ')'

# Updated query with placeholders
query = f"""
SELECT subject, crse_id, catalog_nbr, title, description
FROM courses
WHERE subject IN ({subject_placeholders})
AND LOWER(semester) LIKE ?
{exclusion_conditions}
"""

# Combine parameters
params = subjects + [semester_pattern] + exclusion_params

# Execute the query with parameters
df_courses = pd.read_sql_query(query, conn, params=params)

# Compute embeddings for course descriptions
df_courses['embedding'] = df_courses['description'].apply(lambda x: bi_encoder.encode(x))

# Continue with your query encoding and similarity computation as before
user_query = "I need to look for courses that help me build a career in data science and ML and work as a Machine learning engineer in biomed."
query_embedding = bi_encoder.encode(user_query)
course_embeddings = np.vstack(df_courses['embedding'].values)
similarities = cosine_similarity([query_embedding], course_embeddings)[0]
df_courses['similarity'] = similarities

# Retrieve top-N candidates based on similarity scores
top_n = 8
top_n_candidates = df_courses.nlargest(100, 'similarity').reset_index(drop=True)

# Prepare pairs for the cross-encoder
cross_pairs = list(zip([user_query] * len(top_n_candidates), top_n_candidates['description'].tolist()))

# Compute cross-encoder scores
cross_scores = cross_encoder.predict(cross_pairs)
top_n_candidates['cross_score'] = cross_scores

# Re-rank based on cross-encoder scores
final_recommendations = top_n_candidates.sort_values(by='cross_score', ascending=False).head(top_n)

# Display the final recommendations
print(final_recommendations[['crse_id', 'catalog_nbr','title', 'description', 'cross_score','subject']])


#





# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = (
    "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"  # Replace with your actual API key
)
# Define the output schema
# class CourseRecommendations(BaseModel):
#     recommended_course_ids: list[str] = Field(
#         ..., description="A list of recommended course IDs"
#     )
class CourseRecommendation(BaseModel):
    crse_id: str = Field(..., description="Course ID")
    catalog_nbr: str = Field(..., description="Catalog number")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    subject: str = Field(..., description="Subject code")

class CourseRecommendations(BaseModel):
    recommended_courses: List[CourseRecommendation]

# Create the output parser
output_parser = PydanticOutputParser(pydantic_object=CourseRecommendations)
# # Sample course data
# course_data = [
#     {"id": "CS101", "description": "Introduction to Computer Science"},
#     {"id": "DS201", "description": "Data Structures and Algorithms"},
#     {"id": "ML101", "description": "Machine Learning Basics"},
#     {"id": "AI201", "description": "Introduction to Artificial Intelligence"},
#     {"id": "DS301", "description": "Data Science in Healthcare"},
#     {"id": "PY101", "description": "Python Programming Fundamentals"},
#     {"id": "STAT201", "description": "Statistical Methods for Data Science"},
#     {"id": "MLH401", "description": "Machine Learning in Healthcare"},
#     {"id": "BIO301", "description": "Biomedical Data Analysis"},
# ]
# # Create the course list string
# course_list = "\n".join(
#     [
#         f"Course ID: {course['id']}\nDescription: {course['description']}\n"
#         for course in course_data
#     ]
# )
# Get the format instructions
format_instructions = output_parser.get_format_instructions()
# Define the prompt template
template = """
You are an expert course advisor for university students.
Below are examples of users seeking courses and the recommendations provided:
---
**User Query:** "I want to become a data analyst proficient in Python."
**Recommended Courses:**
1. Python Programming Fundamentals
2. Data Analysis with Pandas
3. Data Visualization with Matplotlib
4. Statistical Analysis in Python
5. Database Management
---
**User Query:** "I'm interested in machine learning and artificial intelligence fundamentals."
**Recommended Courses:**
1. Machine Learning Basics
2. Neural Networks and Deep Learning
3. Introduction to Artificial Intelligence
4. Applied Machine Learning
5. Ethics in AI
---
Based on the following user query, recommend **top 5 courses** from the courses pool that would best suit their needs based on what they have mentioned below in their query. Return ONLY the course IDs from the available pool. Make sure to prioritize courses that are most relevant to the user's specific needs and career goals.
**User Query:** {query}
**Courses pool:**
{courses}
{format_instructions}
"""
# Initialize the Chat model and LLMChain
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
prompt = PromptTemplate(
    input_variables=["query", "courses"],
    template=template,
    partial_variables={"format_instructions": format_instructions},
)
llm_chain = LLMChain(llm=llm, prompt=prompt)
def get_course_recommendations(user_query):
    try:
        # Run the LLM chain
        response = llm_chain.run(query=user_query, courses=final_recommendations[['crse_id', 'catalog_nbr','title', 'description', 'subject']])
        # Parse the response
        parsed_output = output_parser.parse(response)
        # Access the recommended course IDs
        recommended_courses = parsed_output.recommended_courses

        # Convert to DataFrame
        df_recommended = pd.DataFrame([course.dict() for course in recommended_courses])


        return df_recommended
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)



print(get_course_recommendations(user_query))




