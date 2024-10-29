import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import traceback
import os
import random


from utils import parse_file

load_dotenv()


OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")
OPENAI_API_DEPLOYMENT = os.getenv("OPENAI_API_DEPLOYMENT")
OPENAI_API_TEMPERATURE = os.getenv("OPENAI_API_TEMPERATURE")


llm = AzureChatOpenAI(
    openai_api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_API_ENDPOINT,
    model=OPENAI_API_MODEL,
    azure_deployment=OPENAI_API_DEPLOYMENT,
    api_key=OPENAI_API_KEY,
    temperature=OPENAI_API_TEMPERATURE
)


cumulative_lesson_plan_prompt_template = """
Chapters Selected: {chapters}
As an expert educator, you will create a unified lesson plan by including the key concepts from each selected chapter. Follow the instructions below carefully:

1. If there are 2 selected chapters, include 3 points under each section for each chapter.
2. If there are more than 2 selected chapters, include 2 points under each section for each chapter.

Ensure each chapter contributes equally within each section. Avoid focusing on one chapter more than the others. Here is the structure:

1. **Bridge-In**: Provide an introduction that integrates ideas from each selected chapter, ensuring each chapter is represented with {bridge_points} key points.
2. **Objectives**: Outline learning objectives with {objectives_points} key points per chapter, reflecting each chapter’s main ideas equally.
3. **Pre-assessment**: List questions or scenarios that include {pre_assessment_points} key points per chapter to assess foundational knowledge.
4. **Participatory Teaching Activities**: Design activities with {activities_points} key points per chapter, each activity incorporating concepts from all selected chapters.
5. **Post-assessment**: Provide assessment questions with {post_assessment_points} key points per chapter to evaluate understanding across all topics.
6. **Summary/Closure**: Summarize the lesson plan by covering {summary_points} key points per chapter, explaining how all chapters interrelate to give a holistic view.

Do not use subsections. Instead, blend each chapter’s concepts seamlessly within each section, ensuring balanced representation of all selected chapters.
"""



def calculate_points(num_chapters):
    if num_chapters <= 2:
        return 3  # For 2 or fewer chapters, 3 points per chapter in each section
    else:
        return 2  # For more than 2 chapters, 2 points per chapter in each section



st.title("Customizable Cumulative Lesson Plan Generator")


if 'chapter_names' not in st.session_state:
    st.session_state['chapter_names'] = []
if 'cumulative_lesson_plan' not in st.session_state:
    st.session_state['cumulative_lesson_plan'] = None

uploaded_file = st.file_uploader("Upload a PDF file with chapter names")


if uploaded_file and uploaded_file.type == "application/pdf":
    try:
        st.session_state['chapter_names'] = parse_file(uploaded_file)
    except Exception as e:
        st.error("Error reading the file. Please upload a valid PDF with chapter names.")
        traceback.print_exception(type(e), e, e.__traceback__)


if st.session_state['chapter_names']:
    st.write("### Select Chapters to Include in the Lesson Plan")
    selected_chapters = []
    for chapter in st.session_state['chapter_names']:
        if st.checkbox(chapter):
            selected_chapters.append(chapter)


    if st.button("Generate Cumulative Lesson Plan") and selected_chapters:
        with st.spinner("Generating cumulative lesson plan..."):
            try:

                points_per_chapter = calculate_points(len(selected_chapters))
                chapters_text = "\n".join(selected_chapters)


                cumulative_lesson_plan_prompt = PromptTemplate(
                    input_variables=["chapters", "bridge_points", "objectives_points", "pre_assessment_points",
                                     "activities_points", "post_assessment_points", "summary_points"],
                    template=cumulative_lesson_plan_prompt_template
                )


                lesson_plan_chain = LLMChain(llm=llm, prompt=cumulative_lesson_plan_prompt,
                                             output_key="cumulative_lesson_plan", verbose=True)

                response = lesson_plan_chain({
                    "chapters": chapters_text,
                    "bridge_points": points_per_chapter,
                    "objectives_points": points_per_chapter,
                    "pre_assessment_points": points_per_chapter,
                    "activities_points": points_per_chapter,
                    "post_assessment_points": points_per_chapter,
                    "summary_points": points_per_chapter
                })

                st.session_state['cumulative_lesson_plan'] = response['cumulative_lesson_plan']
                st.session_state['selected_chapter_names'] = ", ".join(selected_chapters)
            except Exception as e:
                st.error("Error occurred while generating the lesson plan.")
                traceback.print_exception(type(e), e, e.__traceback__)
            else:
                st.success("Cumulative lesson plan generated successfully!")


if st.session_state['cumulative_lesson_plan']:
    st.write(f"### Cumulative Lesson Plan for: {st.session_state['selected_chapter_names']}")
    st.markdown(st.session_state['cumulative_lesson_plan'])


    st.download_button(
        label="Download Cumulative Lesson Plan",
        data=st.session_state['cumulative_lesson_plan'],
        file_name="cumulative_lesson_plan.txt",
        mime="text/plain"
    )
