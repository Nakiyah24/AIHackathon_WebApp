
# **Course Recommendation System Using NLP & Transformers**

## **Overview**

This project is an AI-based **course recommendation system** designed to help students find the most relevant courses based on their interests and career goals. The system leverages **Natural Language Processing (NLP)** models like **Sentence-BERT** and **Cross-Encoder** for semantic search, cosine similarity for course ranking, and OpenAI's **GPT-3.5-turbo** for natural language-based recommendations. The system recommends courses by analyzing user queries and course descriptions from a local database of courses.

## **Key Features**

- **Semantic Search**: Uses a transformer-based bi-encoder model to compute similarity between the user's query and course descriptions.
- **Cross-Encoder Re-ranking**: Re-ranks top course candidates using a cross-encoder for more accurate recommendations.
- **Language Model-based Recommendations**: Utilizes OpenAI's GPT-3.5-turbo to refine the results and suggest the top 5 most relevant courses based on user query.
- **Exclusion of Courses**: Allows excluding specific courses or subjects from the recommendation pool.
  
## **Tech Stack**

- **Python**
- **Sentence Transformers** (Bi-Encoder and Cross-Encoder)
- **SQLite** (For storing and querying courses)
- **LangChain** (For prompt generation and interaction with GPT-3.5-turbo)
- **OpenAI API** (GPT-3.5-turbo model for language-based recommendations)
- **Pandas** (For data handling)
- **Scikit-learn** (Cosine similarity calculations)

## **Installation**

### **Prerequisites**

- Python 3.7+
- Git
- A valid **OpenAI API Key**
  
### **Steps to Set Up the Project Locally**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nakiyah24/AIHackathon_WebApp.git
   cd AIHackathon_WebApp
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   - Ensure you have a valid `courses.db` SQLite database containing course information.
   - The `courses` table should have the following columns:
     - `subject`
     - `crse_id`
     - `catalog_nbr`
     - `title`
     - `description`
     - `semester`

5. **Set the OpenAI API key**:
   - Open your terminal and set the environment variable for the OpenAI API key:
     ```bash
     export OPENAI_API_KEY="your-api-key-here"
     ```
   - Alternatively, you can replace the placeholder in the script directly:
     ```python
     os.environ["OPENAI_API_KEY"] = "your-api-key-here"
     ```

### **Project Structure**

- `main.py`: The main application code handling course retrieval, semantic search, and recommendations.
- `courses.db`: The SQLite database containing the course data.
- `requirements.txt`: A list of dependencies for the project.

## **Usage**

### **1. User Query and Recommendations**

You can use this system to get course recommendations by providing a natural language query. For example:

```python
user_query = "I need to look for courses that help me build a career in data science and ML and work as a Machine learning engineer in biomed."
print(get_course_recommendations(user_query))
```

This will return a list of top 5 courses relevant to the user’s query.

### **2. Excluding Specific Courses**

If you want to exclude specific subjects or courses from the recommendation, modify the `remove_dict` in the script:

```python
remove_dict= [
    {'subject':'Political Science', 'title':'The politics of four of the United States principal racial minority groups'}
]
```

### **3. Customizing the Recommendations**

- You can modify the `subjects` list to add/remove course subjects relevant to your institution.
- Modify `sem_var` to filter courses based on the semester (e.g., `fall`, `spring`).

### **4. Example Output**

A sample output might look like:

```python
Course ID | Catalog Number | Title                              | Description                                            | Subject
--------- | ---------------|----------------------------------- | ------------------------------------------------------ | -------
BIO301    | 301            | Biomedical Data Analysis           | Learn the principles of data science in biomedicine... | BIOSTAT
MLH401    | 401            | Machine Learning in Healthcare     | A course focused on applying ML techniques in healt... | MENG
DS201     | 201            | Data Structures and Algorithms     | An advanced course on data structures and algorithms. | COMPSCI
...
```

### **5. Using GPT for Better Recommendations**

After filtering and ranking the courses, the final list is refined using GPT-3.5 to recommend the most relevant courses based on the user’s career goals.

### **6. Prompt for GPT-3.5-turbo**

The prompt is dynamically generated and structured as follows:

```python
template = '''
You are an expert course advisor for university students.
Below are examples of users seeking courses and the recommendations provided:
---
**User Query:** "I want to become a data analyst proficient in Python."
**Recommended Courses:**
1. Python Programming Fundamentals
2. Data Analysis with Pandas
...
---
Based on the following user query, recommend **top 5 courses** from the courses pool that would best suit their needs.
**User Query:** {query}
**Courses pool:**
{courses}
{format_instructions}
'''
```

## **Dependencies**

- **LangChain**: To manage prompts and queries to OpenAI's models.
- **Sentence Transformers**: For embedding course descriptions and user queries.
- **OpenAI API**: For querying GPT-3.5-turbo for recommendations.
- **Pandas**: For data handling and filtering.
- **SQLite**: As the database to store and retrieve course information.

## **License**

This project is licensed under the MIT License.

## **Contact**

For any questions or suggestions, please feel free to contact the project maintainers through the GitHub repository or by email.

