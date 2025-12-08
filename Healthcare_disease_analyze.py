import streamlit as st
from openai import OpenAI
import json
import re


# Αρχικοποίηση OpenAI 

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


# Κλάση για τα αποτελέσματα ανάλυσης

class DiseaseAnalysis:
    def __init__(self, symptoms, possible_diseases, explanation, recommended_actions):
        self.symptoms = symptoms
        self.possible_diseases = possible_diseases
        self.explanation = explanation
        self.recommended_actions = recommended_actions


# Function για ασφαλές parsing JSON από το GPT

def safe_parse_json(gpt_text):
    match = re.search(r'{.*}', gpt_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


# Function που στέλνει τα συμπτώματα στο GPT για ανάλυση

def analyze_symptoms(symptoms_input):
    gpt_prompt = '''
Δημιούργησε ένα JSON με ανάλυση των συμπτωμάτων του ασθενούς. 
Πρέπει να περιλαμβάνει πιθανές ασθένειες, εξήγηση και προτεινόμενες ενέργειες.
Μορφή JSON:

{
  "Symptoms": "Λίστα συμπτωμάτων",
  "PossibleDiseases": ["Ασθένεια1", "Ασθένεια2"],
  "Explanation": "Εξήγηση γιατί αυτές οι ασθένειες επιλέχθηκαν",
  "RecommendedActions": "Προτεινόμενες ενέργειες όπως επίσκεψη γιατρού, εξετάσεις, lifestyle changes κλπ."
}
'''
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": gpt_prompt},
                {"role": "user", "content": f"Ανάλυσε τα εξής συμπτώματα: {symptoms_input}"}
            ]
        )
        gpt_text = response.choices[0].message.content
        gpt_response = safe_parse_json(gpt_text)
        if gpt_response:
            return DiseaseAnalysis(
                symptoms=gpt_response["Symptoms"],
                possible_diseases=gpt_response["PossibleDiseases"],
                explanation=gpt_response.get("Explanation", ""),
                recommended_actions=gpt_response.get("RecommendedActions", "")
            )
        else:
            st.error("Δεν ήταν δυνατή η ανάγνωση της απάντησης από το GPT.")
            return None
    except Exception as e:
        st.error(f"Παρουσιάστηκε σφάλμα: {str(e)}")
        return None


# Streamlit UI

st.title(" Εφαρμογή Ανάλυσης Συμπτωμάτων")
st.write("Πληκτρολογήστε τα συμπτώματά σας ώστε να λάβετε πιθανές ασθένειες και προτεινόμενες ενέργειες.")

# Πλαίσιο εισαγωγής συμπτωμάτων
symptoms_input = st.text_area("Συμπτώματα (π.χ. πυρετός, βήχας, πονοκέφαλος):")

# Αρχικοποίηση ιστορικού στο session_state
if 'history' not in st.session_state:
    st.session_state.history = []

# Κουμπί ανάλυσης συμπτωμάτων
if st.button("Ανάλυση Συμπτωμάτων"):
    if symptoms_input.strip():
        analysis = analyze_symptoms(symptoms_input)
        if analysis:
            # Αποθήκευση ανάλυσης στο ιστορικό
            st.session_state.history.append(analysis)

            # Εμφάνιση αποτελεσμάτων
            st.subheader("🔹 Αποτελέσματα Ανάλυσης")
            st.write(f"**Συμπτώματα:** {analysis.symptoms}")
            st.write(f"**Πιθανές Ασθένειες:** {', '.join(analysis.possible_diseases)}")
            st.write(f"**Εξήγηση:** {analysis.explanation}")
            st.write(f"**Προτεινόμενες Ενέργειες:** {analysis.recommended_actions}")
    else:
        st.warning("Παρακαλώ εισάγετε τα συμπτώματά σας πρώτα.")

# Εμφάνιση ιστορικού προηγούμενων αναλύσεων
if st.session_state.history:
    st.subheader("🕘 Προηγούμενες Αναλύσεις")
    for idx, item in enumerate(st.session_state.history[::-1], 1):
        st.write(f"**{idx}. Συμπτώματα:** {item.symptoms}")
        st.write(f"**Πιθανές Ασθένειες:** {', '.join(item.possible_diseases)}")
        st.write("---")
