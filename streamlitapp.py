import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import traceback
import os

# Importing parse_file from utils.py
from utils import parse_file

load_dotenv()

# Configure OpenAI parameters
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")
OPENAI_API_DEPLOYMENT = os.getenv("OPENAI_API_DEPLOYMENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_TEMPERATURE = os.getenv("OPENAI_API_TEMPERATURE")

llm = AzureChatOpenAI(
    openai_api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_API_ENDPOINT,
    model=OPENAI_API_MODEL,
    azure_deployment=OPENAI_API_DEPLOYMENT,
    api_key=OPENAI_API_KEY,
    temperature=OPENAI_API_TEMPERATURE
)

# Prompt template for summarizing the entire text
summary_generation_prompt = PromptTemplate(
    input_variables=["texts"],
    template="""
    You are provided with summaries of multiple text chunks extracted from a PDF file.

    The summaries of individual chunks are as follows:

    {texts}

    Your task is to generate a consolidated summary that comprehensively analyzes each line and provides a detailed explanation of the content. Ensure that the consolidated summary encapsulates all key points, ideas, and details discussed in the entire text.

    Analyze each line of the provided summaries to understand the context and meaning. Focus on identifying important concepts, relationships, and insights conveyed in the text.

    Based on this detailed analysis, craft a consolidated summary that exceeds 200 words. Include explanations, interpretations, and connections between different parts of the text to provide a comprehensive overview.

    ### Consolidated Summary:
    """
)

summary_chain = LLMChain(llm=llm, prompt=summary_generation_prompt, output_key="summary", verbose=True)

st.title("PDF Summarization App")

if 'file_summary' not in st.session_state:
    st.session_state['file_summary'] = []

uploaded_file = st.file_uploader("Upload a PDF file")

if st.button("Generate Summary") and uploaded_file is not None:
    with st.spinner(".."):
        try:
            # Using parse_file function from utils.py to extract text from the PDF
            parsed_text = parse_file(uploaded_file)

            # Generate summary for each chunk of text
            summaries = []
            max_context_length = 16384
            current_context_length = 0
            for chunk in parsed_text:
                summary = summary_chain({"texts": summaries + [chunk]})["summary"].strip()
                current_context_length += len(summary.split())
                if current_context_length <= max_context_length:
                    summaries.append(summary)
                else:
                    break

            st.session_state['file_summary'] = summaries
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("Error occurred while generating summary.")

# Printing the generated consolidated summary
if st.session_state['file_summary']:
    st.write("Generated Consolidated Summary:")
    st.write(st.session_state['file_summary'][-1])  # Displaying the last summary in the list
