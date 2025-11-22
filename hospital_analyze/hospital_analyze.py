import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Read the CSV file
admissions_data = pd.read_csv("hospital_admissions_data.csv")
# Convert admission_date and discharge_date to datetime
admissions_data['admission_date'] = pd.to_datetime(admissions_data['admission_date'])
admissions_data['discharge_date'] = pd.to_datetime(admissions_data['discharge_date'])
# Calculate length of stay
admissions_data['length_of_stay'] = (admissions_data['discharge_date'] - admissions_data['admission_date']).dt.days
# Calculate the average length of stay by diagnosis
avg_length_of_stay = admissions_data.groupby('diagnosis')['length_of_stay'].mean().reset_index()
print("Average Length of Stay by Diagnosis:")
print(avg_length_of_stay)
# Count the number of admissions for each diagnosis
diagnosis_counts = admissions_data.groupby('diagnosis')['admission_id'].count().reset_index().rename(columns={'admission_id': 'count'})
# Find the top 10 most common diagnoses
top_10_diagnoses = diagnosis_counts.nlargest(10, 'count')
print("Top 10 Most Common Diagnoses:")
print(top_10_diagnoses)
# Set up the histogram
plt.hist(admissions_data['age'], bins=20, edgecolor='black')
plt.xlabel("Age")
plt.ylabel("Frequency")
plt.title("Age Distribution of Patients")
# Display the histogram
plt.show()