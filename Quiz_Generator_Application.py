import streamlit as st
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import uuid


# CONFIG

st.set_page_config(page_title="AI Quiz Platform", page_icon="🧠")

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


# DATA MODELS

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


# SESSION STATE INIT

def init_state():
    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "score" not in st.session_state:
        st.session_state.score = 0

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if "quiz_id" not in st.session_state:
        st.session_state.quiz_id = str(uuid.uuid4())

init_state()


# AI SERVICE


def generate_question(topic: str, history: List[str]) -> QuizQuestion:
    response = client.responses.create(
        model="gpt-4.1-mini",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "quiz_question",
                "schema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "correct_answer": {"type": "string"},
                        "explanation": {"type": "string"}
                    },
                    "required": [
                        "question",
                        "options",
                        "correct_answer",
                        "explanation"
                    ]
                }
            }
        },
        input=f"""
Create a trivia question about {topic}.
Avoid repeating these questions:
{history}
"""
    )

    return QuizQuestion(**response.output_parsed)


# QUIZ LOGIC


def submit_answer(selected: str):
    question = st.session_state.questions[st.session_state.current_index]
    st.session_state.submitted = True

    if selected == question.correct_answer:
        st.session_state.score += 1
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Wrong! Correct answer: {question.correct_answer}")

    st.info(question.explanation)

def next_question():
    st.session_state.current_index += 1
    st.session_state.submitted = False
    st.rerun()

def restart_quiz():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# UI


st.title("🧠 AI-Powered Quiz Platform")

# ---- Question Generator ----
with st.sidebar:
    st.header("➕ Generate Question")
    topic = st.text_input("Topic")

    if st.button("Generate"):
        if not topic.strip():
            st.warning("Enter a topic")
        else:
            history = [q.question for q in st.session_state.questions]
            with st.spinner("Generating question..."):
                try:
                    question = generate_question(topic, history)
                    st.session_state.questions.append(question)
                    st.success("Question added!")
                except Exception as e:
                    st.error(str(e))

# ---- Quiz Area ----
if not st.session_state.questions:
    st.info("👈 Generate questions to start the quiz.")
    st.stop()

question = st.session_state.questions[st.session_state.current_index]

st.subheader(
    f"Question {st.session_state.current_index + 1} of {len(st.session_state.questions)}"
)
st.write(question.question)

choice = st.radio(
    "Choose one:",
    question.options,
    key=f"choice_{st.session_state.current_index}"
)

# ---- Submission ----
if not st.session_state.submitted:
    if st.button("Submit Answer"):
        submit_answer(choice)
else:
    if st.session_state.current_index < len(st.session_state.questions) - 1:
        st.button("Next Question →", on_click=next_question)
    else:
        st.divider()
        st.subheader("🏁 Quiz Completed")
        st.write(
            f"Final Score: **{st.session_state.score} / {len(st.session_state.questions)}**"
        )

        if st.session_state.score == len(st.session_state.questions):
            st.balloons()
            st.success("🎉 Perfect Score!")
        else:
            st.warning("Good job! Try again to improve.")

        st.button("Restart Quiz", on_click=restart_quiz)

# ---- Progress ----
progress = st.session_state.current_index / len(st.session_state.questions)
st.progress(progress)
