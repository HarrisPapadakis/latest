# Εισαγωγή απαραίτητων βιβλιοθηκών
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Ανάγνωση του αρχείου CSV και  φορτώση σε ένα DataFrame
admissions_data = pd.read_csv("hospital_admissions_data.csv")
# Μετατροπή στηλών ημερομηνίας σε datetime για να μπορούμε να κάνουμε υπολογισμούς με αυτές
admissions_data['admission_date'] = pd.to_datetime(admissions_data['admission_date'])
admissions_data['discharge_date'] = pd.to_datetime(admissions_data['discharge_date'])
# Υπολογισμός διάρκειας παραμονής σε ημέρες αφαιρώντας την ημερομηνία εισαγωγής από την ημερομηνία εξαγωγής
admissions_data['length_of_stay'] = (admissions_data['discharge_date'] - admissions_data['admission_date']).dt.days
# Υπολογισμός μέσης διάρκειας παραμονής ανά διάγνωση, ομαδοποιηση δεδομένων ανά διάγνωση και υπολογίσμος με  τη μέση διάρκεια παραμονή
avg_length_of_stay = admissions_data.groupby('diagnosis')['length_of_stay'].mean().reset_index()
print("Average Length of Stay by Diagnosis:")
print(avg_length_of_stay)
# Καταμέτρηση εισαγωγών ανά διάγνωση, Ομαδοποιηση  ανά διάγνωση για να μετρήσουμε τον αριθμό των εισαγωγών για κάθε μίας 
diagnosis_counts = admissions_data.groupby('diagnosis')['admission_id'].count().reset_index().rename(columns={'admission_id': 'count'})
# Εύρεση των 10 πιο συχνών διαγνώσεων με τις περισσότερες εισαγωγές
top_10_diagnoses = diagnosis_counts.nlargest(10, 'count')
print("Top 10 Most Common Diagnoses:")
print(top_10_diagnoses)
# Δημιουργία ιστογράμματος της στήλης 'age' για  οπτικοποιήση σύμφωνα με  την κατανομή ηλικίας των ασθενών
plt.hist(admissions_data['age'], bins=20, edgecolor='black')
plt.xlabel("Age")
plt.ylabel("Frequency")
plt.title("Age Distribution of Patients")
# Προβολή ιστογράμματος
plt.show()
