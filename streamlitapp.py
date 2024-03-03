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

intro_generation_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    You are tasked with providing a concise introduction that encapsulates the main points of the following text:

    {text}

    Generate an introduction of up to 50 words that summarizes the key information and significance of the text.

    ### Introduction:
    """
)

final_intro_generation_prompt = PromptTemplate(
    input_variables=["introduction"],
    template="""
    You have generated an introduction that encapsulates the main points of the text:

    {introduction}

    Now, based on this introduction, craft a final introduction that succinctly summarizes the key information and significance of the text. The final introduction should be between 20 to 50 words, ensuring it provides a clear and comprehensive overview without being fragmented or incomplete.

    ### Final Introduction:
    """
)

intro_chain = LLMChain(llm=llm, prompt=intro_generation_prompt, output_key="introduction", verbose=True)
final_intro_chain = LLMChain(llm=llm, prompt=final_intro_generation_prompt, output_key="finalIntroduction", verbose=True)

st.title("Text Summarization App")

if 'final_introduction' not in st.session_state:
    st.session_state['final_introduction'] = None

uploaded_file = st.file_uploader("Upload a PDF or txt file")

if st.button("Generate Introduction") and uploaded_file is not None:
    with st.spinner(".."):
        try:
            # Using parse_file function from utils.py to extract text from the PDF
            parsed_text = parse_file(uploaded_file)
            full_text = " ".join(parsed_text)

            # Split full text into chunks
            chunk_size = 16384
            chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

            # Generate initial introduction for each chunk
            introductions = []
            for chunk in chunks:
                introduction = intro_chain({"text": chunk})["introduction"].strip()
                introductions.append(introduction)

            # Concatenate introductions into a single string
            combined_intro = " ".join(introductions)

            # Generate final introduction from combined introduction
            final_introduction = final_intro_chain({"introduction": combined_intro})["finalIntroduction"].strip()

            # Ensure final introduction is no longer than 50 words
            final_intro_words = final_introduction.split(" ")[:50]
            final_introduction = " ".join(final_intro_words)

            st.session_state['final_introduction'] = final_introduction
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("Error occurred while generating introduction.")

# Printing final introduction
if st.session_state['final_introduction'] is not None:
    st.write("Generated Final Introduction:")
    st.write(st.session_state['final_introduction'])
