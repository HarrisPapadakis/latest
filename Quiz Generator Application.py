import streamlit as st
from openai import OpenAI
import json
import re

# Initialize OpenAI client securely
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Question class
class Question:
    def __init__(self, question, options, correct_answer, explanation=None):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation

# Quiz class
class Quiz:
    def __init__(self):
        self.questions = self.load_or_generate_questions()
        self.initialize_session_state()

    def load_or_generate_questions(self):
        if 'questions' not in st.session_state:
            st.session_state.questions = [
                Question(
                    "What is the capital of France?",
                    ["London", "Paris", "Berlin", "Madrid"],
                    "Paris",
                    "Paris is the capital and most populous city of France."
                ),
                Question(
                    "Who developed the theory of relativity?",
                    ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Marie Curie"],
                    "Albert Einstein",
                    "Albert Einstein is known for developing the theory of relativity."
                )
            ]
        return st.session_state.questions

    def initialize_session_state(self):
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'answers_submitted' not in st.session_state:
            st.session_state.answers_submitted = 0
        if 'quiz_initialized' not in st.session_state:
            st.session_state.quiz_initialized = True

    def display_quiz(self):
        self.update_progress_bar()
        if st.session_state.answers_submitted >= len(self.questions):
            self.display_results()
        else:
            self.display_current_question()

    def display_current_question(self):
        question = self.questions[st.session_state.current_question_index]
        st.write(f"**Q{st.session_state.current_question_index + 1}:** {question.question}")
        answer = st.radio(
            "Choose one:",
            question.options,
            key=f"question_{st.session_state.current_question_index}"
        )

        if st.button("Submit Answer", key=f"submit_{st.session_state.current_question_index}"):
            self.check_answer(answer)
            st.session_state.answers_submitted += 1
            if st.session_state.current_question_index < len(self.questions) - 1:
                st.session_state.current_question_index += 1
            st.experimental_rerun()

    def check_answer(self, user_answer):
        correct_answer = self.questions[st.session_state.current_question_index].correct_answer
        if user_answer == correct_answer:
            st.session_state.score += 1
            st.success("Correct!")
        else:
            st.error(f"Wrong! The correct answer is: {correct_answer}")
        explanation = self.questions[st.session_state.current_question_index].explanation
        if explanation:
            st.info(explanation)

    def display_results(self):
        st.write(f"**Quiz completed!** Your score: {st.session_state.score}/{len(self.questions)}")
        if st.session_state.score == len(self.questions):
            st.success("🎉 Perfect score! Congrats!")
            st.balloons()
        else:
            st.warning("You can try again to improve your score.")
        if st.button("Restart Quiz"):
            self.restart_quiz()

    def update_progress_bar(self):
        progress = st.session_state.answers_submitted / len(self.questions)
        st.progress(progress)

    def restart_quiz(self):
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.answers_submitted = 0
        st.experimental_rerun()

# Function to safely parse GPT JSON responses
def safe_parse_json(gpt_text):
    # Remove unwanted characters before parsing
    match = re.search(r'{.*}', gpt_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

# Generate a new GPT question
def generate_and_append_question(user_prompt):
    history = ""
    for q in st.session_state.questions:
        history += f"Question: {q.question} Answer: {q.correct_answer}\n"

    gpt_prompt = '''Generate a JSON response for a trivia question including question, options, correct answer, and explanation. Format:

{
  "Question": "The actual question text",
  "Options": ["Option1", "Option2", "Option3", "Option4"],
  "CorrectAnswer": "TheCorrectAnswer",
  "Explanation": "Detailed explanation"
}'''

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": gpt_prompt},
                {"role": "user", "content": f"Create a question about: {user_prompt} that is different from: {history}"}
            ]
        )
        gpt_text = response.choices[0].message.content
        gpt_response = safe_parse_json(gpt_text)
        if gpt_response:
            new_question = Question(
                question=gpt_response["Question"],
                options=gpt_response["Options"],
                correct_answer=gpt_response["CorrectAnswer"],
                explanation=gpt_response.get("Explanation", "")
            )
            st.session_state.questions.append(new_question)
            st.success("New question generated successfully!")
        else:
            st.error("Failed to parse GPT response. Try again.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Main app
st.title("📝 Dynamic Quiz App")

if 'quiz' not in st.session_state:
    st.session_state.quiz = Quiz()

user_input = st.text_input("Enter topic for a new question:")

if st.button("Generate New Question"):
    if user_input.strip():
        generate_and_append_question(user_input)
    else:
        st.warning("Please enter a topic first.")

st.session_state.quiz.display_quiz()
