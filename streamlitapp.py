import json
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
import pandas as pd
import traceback
from utils import parse_file, RESPONSE_JSON, get_table_data
import os

load_dotenv()

# Configure OpenAI parameters
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")
OPENAI_API_DEPLOYMENT = os.getenv("OPENAI_API_DEPLOYMENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_TEMPERATURE = os.getenv("OPENAI_API_TEMPERATURE")
# api_base = "https://openai-cogbooks.openai.azure.com/"
# model_name = "gpt-35-turbo-16k"
# model_version = "0613"
# deployment = "gpt-35-turbo-16k-CBSIR"
# deployment_type = "Standard"


llm = AzureChatOpenAI(
        openai_api_version=OPENAI_API_VERSION,
        azure_endpoint=OPENAI_API_ENDPOINT,
        model=OPENAI_API_MODEL,
        azure_deployment=OPENAI_API_DEPLOYMENT,
        api_key= OPENAI_API_KEY,
        temperature=OPENAI_API_TEMPERATURE
        )

template = """
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

quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)

template = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {grade} grade students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz if the students
will be able to understand the questions and answer them. Only use at max 50 words for complexity analysis. 
if the quiz is not at par with the cognitive and analytical abilities of the students,\
update the quiz questions which need to be changed  and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Critique from an expert English Writer of the above quiz:
"""

quiz_evaluation_prompt = PromptTemplate(input_variables=["grade", "quiz"], template=template)
review_chain = LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)

generate_evaluate_chain = SequentialChain(chains=[quiz_chain, review_chain],
                                          input_variables=["text", "number", "grade", "tone", "response_json"],
                                          output_variables=["quiz", "review"], verbose=True)

st.title("MCQs Creator App")

if 'quiz' not in st.session_state:
    st.session_state['quiz'] = None
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}
if 'correct_answers' not in st.session_state:
    st.session_state['correct_answers'] = []

uploaded_file = st.file_uploader("Upload a PDF or txt file")
mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
grade = st.number_input("Insert Grade", min_value=1, max_value=10)
tone = st.text_input("Insert Quiz Tone", max_chars=100, placeholder="simple")

if st.button("Create MCQs") and uploaded_file is not None and mcq_count:
    with st.spinner(".."):
        try:
            text = parse_file(uploaded_file)
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
            st.error("Error occurred while generating MCQs.")
        else:
            if isinstance(response, dict):
                st.session_state['quiz'] = response.get("quiz", None)
                st.session_state['correct_answers'] = []  # Reset correct_answers when a new quiz is created

if st.session_state['quiz'] is not None:
    table_data = get_table_data(st.session_state['quiz'])
    print(table_data)
    with st.form(key="quiz_form"):
        for i, data in enumerate(table_data):
            st.write(f"{i + 1}. {data['MCQ']}")
            options = data['Choices'].split(' | ')
            correct_option = data['Correct']
            selected_option = st.radio("", options, key=f"question {i}", index=None)
        submit = st.form_submit_button("Submit answers")

    if submit:
        user_answers = [str(st.session_state[f"question {i}"]) for i in range(len(table_data))]
        print(user_answers)
        correct_answers = [str(data['Correct']) for data in table_data]
        print(correct_answers)
        matches = 0
        for i in range(len(correct_answers)):
            if correct_answers[i] in user_answers[i]:
                matches += 1
        st.write(f"You have selected {matches} correct answers.")
