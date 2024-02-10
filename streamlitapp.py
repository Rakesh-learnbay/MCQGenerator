import json
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
import pandas as pd
import traceback
from utils import parse_file, RESPONSE_JSON, get_table_data
load_dotenv()

llm=OpenAI(model_name="gpt-3.5-turbo", temperature=0)

template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for grade {grade} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "grade", "tone", "response_json"],
    template=template

)


quiz_chain=LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)


template="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {grade} grade students.\
You need to evaluate the complexity of teh question and give a complete analysis of the quiz if the students
will be able to unserstand the questions and answer them. Only use at max 50 words for complexity analysis. 
if the quiz is not at par with the cognitive and analytical abilities of the students,\
update teh quiz questions which needs to be changed  and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Critique from an expert English Writer of the above quiz:
"""

quiz_evaluation_prompt=PromptTemplate(input_variables=["grade", "quiz"], template=template)
review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)

generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text", "number", "grade", "tone", "response_json"],
                                        output_variables=["quiz", "review"], verbose=True,)

st.title("MCQs Creator Application with LangChain 🦜⛓️")

print("TEST PRINT LINE 58")
if 'quiz' not in st.session_state:
    st.session_state['quiz'] = None
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}
if 'correct_answers' not in st.session_state:
    st.session_state['correct_answers'] = []
print("TEST PRINT LINE 66")
# File uploader and input fields
uploaded_file = st.file_uploader("Upload a PDF or txt file")
mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
grade = st.number_input("Insert Grade", min_value=1, max_value=10)
tone = st.text_input("Insert Quiz Tone", max_chars=100, placeholder="simple")
print("TEST PRINT LINE 72")
# Create MCQs button
if st.button("Create MCQs") and uploaded_file is not None and mcq_count:
    with st.spinner(".."):
        try:
            text = parse_file(uploaded_file)
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "grade": grade,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("r")
        else:
            if isinstance(response, dict):
                st.session_state['quiz'] = response.get("quiz", None)
                st.session_state['correct_answers'] = []  # Reset correct_answers when new quiz is created
print("TEST PRINT LINE 95")
# Display quiz and store user answers
# Display quiz and store user answers
# Display quiz and store user answers
# Display quiz and store user answers
# Display quiz and store user answers
# Display quiz and store user answers
if st.session_state['quiz'] is not None:
    table_data = get_table_data(st.session_state['quiz'])
    # Create a form container
    with st.form(key="quiz_form"):
        for i, data in enumerate(table_data):
            st.write(f"{i + 1}. {data['MCQ']}")
            options = data['Choices'].split(' | ')
            correct_option = data['Correct']
            # Use a unique key for each radio button
            selected_option = st.radio("", options, key=f"question {i}", index=None)
        # Add a submit button
        submit = st.form_submit_button("Submit answers")
    # Check if the submit button was clicked
    if submit:
        # Convert the values of the radio buttons to strings
        user_answers = [str(st.session_state[f"question {i}"]) for i in range(len(table_data))]
        # Convert the values of 'Correct' for each MCQ to strings
        correct_answers = [str(data['Correct']) for data in table_data]
        # Initialize a counter for the number of matches
        matches = 0
        # Loop through the arrays using the same index
        for i in range(len(correct_answers)):
            # Check if the correct_answer is a substring of the user_answer
            if correct_answers[i] in user_answers[i]:
                # If yes, increment the counter by one
                matches += 1
        # Print the number of matches in the terminal
        print(matches)
        st.write(f"You have selected {matches} correct answers.")
        # Or print the number of matches in the app
        # st.write(matches)










