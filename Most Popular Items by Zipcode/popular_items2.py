# Εισαγωγή Βιβλιοθηκών
import pandas as pd
import matplotlib.pyplot as plt

# Ανάγνωση δεδομένων
df = pd.read_csv('finance_liquor_sales.csv')

# Καθαρισμός Δεδομένων
df.dropna(inplace=True)

# Ομαδοποίηση ανά κατάστημα και άθροιση πωλήσεων
store_sales = df.groupby('store_number')['sale_dollars'].sum().reset_index()

# Υπολογισμός ποσοστιαίου μεριδίου κάθε καταστήματος
total_sales = store_sales['sale_dollars'].sum()
store_sales['sales_pct'] = (store_sales['sale_dollars'] / total_sales) * 100

# Ταξινόμηση κατά ποσοστό πωλήσεων (προαιρετικό)
store_sales = store_sales.sort_values('sales_pct', ascending=False)

# Προβολή αποτελεσμάτων
print(store_sales.head(20))

# Οπτικοποίηση ποσοστού πωλήσεων ανά κατάστημα
plt.figure(figsize=(14, 7))
plt.bar(store_sales['store_number'].astype(str), store_sales['sales_pct'], color='skyblue')
plt.xlabel('Store Number')
plt.ylabel('Sales Percentage (%)')
plt.title('Percentage of Total Sales by Store')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
