import streamlit as st
from openai import OpenAI
import json
import re

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Class για τα αποτελέσματα ανάλυσης
class DiseaseAnalysis:
    def __init__(self, symptoms, possible_diseases, explanation, recommended_actions):
        self.symptoms = symptoms
        self.possible_diseases = possible_diseases
        self.explanation = explanation
        self.recommended_actions = recommended_actions

# Function to safely parse GPT JSON responses
def safe_parse_json(gpt_text):
    match = re.search(r'{.*}', gpt_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

# Function to analyze symptoms using GPT
def analyze_symptoms(symptoms_input):
    gpt_prompt = '''
Generate a JSON response analyzing the patient's symptoms. 
Include possible diseases, explanation, and recommended actions. 
Format:

{
  "Symptoms": "List of symptoms",
  "PossibleDiseases": ["Disease1", "Disease2"],
  "Explanation": "Explanation of why these diseases are considered",
  "RecommendedActions": "Suggested actions like consulting a doctor, tests, lifestyle changes, etc."
}
'''
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": gpt_prompt},
                {"role": "user", "content": f"Analyze these symptoms: {symptoms_input}"}
            ]
        )
        gpt_text = response.choices[0].message.content
        gpt_response = safe_parse_json(gpt_text)
        if gpt_response:
            analysis = DiseaseAnalysis(
                symptoms=gpt_response["Symptoms"],
                possible_diseases=gpt_response["PossibleDiseases"],
                explanation=gpt_response.get("Explanation", ""),
                recommended_actions=gpt_response.get("RecommendedActions", "")
            )
            return analysis
        else:
            st.error("Failed to parse GPT response. Try again.")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Streamlit UI
st.title("🩺 Healthcare Disease Analysis App")
st.write("Enter your symptoms and get a possible analysis of diseases and recommended actions.")

# Input symptoms
symptoms_input = st.text_area("Enter your symptoms (comma-separated or description):")

if st.button("Analyze Symptoms"):
    if symptoms_input.strip():
        analysis = analyze_symptoms(symptoms_input)
        if analysis:
            st.subheader("🔹 Analysis Results")
            st.write(f"**Symptoms:** {analysis.symptoms}")
            st.write(f"**Possible Diseases:** {', '.join(analysis.possible_diseases)}")
            st.write(f"**Explanation:** {analysis.explanation}")
            st.write(f"**Recommended Actions:** {analysis.recommended_actions}")
    else:
        st.warning("Please enter your symptoms first.")

# Optional: Keep history of analyses in session_state
if 'history' not in st.session_state:
    st.session_state.history = []

if symptoms_input.strip() and analysis:
    st.session_state.history.append(analysis)

if st.session_state.history:
    st.subheader("🕘 Previous Analyses")
    for idx, item in enumerate(st.session_state.history[::-1], 1):
        st.write(f"**{idx}. Symptoms:** {item.symptoms}")
        st.write(f"**Possible Diseases:** {', '.join(item.possible_diseases)}")
        st.write("---")
