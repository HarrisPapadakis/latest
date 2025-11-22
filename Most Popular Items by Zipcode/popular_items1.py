# Εισαγωγή Βιβλιοθηκών
import pandas as pd
import matplotlib.pyplot as plt

# Ανάγνωση δεδομένων 
df = pd.read_csv('finance_liquor_sales.csv')

# Καθαρισμός Δεδομένων, 
# η γραμμή κώδικα αφαιρεί οποιεσδήποτε γραμμές στο DataFrame που περιέχουν τιμές που λείπουν
df.dropna(inplace=True)

# Ομαδοποίηση ανά zip code και προϊόν, αθροίζοντας τις φιάλες που πουλήθηκαν
grouped = df.groupby(['zip_code', 'item_description'])['bottles_sold'].sum().reset_index()

# Ευρεση πιο δημοφιλούς προϊόντος ανά zip code (με μέγιστες πωλήσεις)
top_products_per_zip = grouped.loc[grouped.groupby('zip_code')['bottles_sold'].idxmax()]

# Ταξινόμηση κατά zip code για καλύτερη εμφάνιση
top_products_per_zip = top_products_per_zip.sort_values('zip_code')

# Προβολή των πρώτων 20 αποτελεσμάτων
print(top_products_per_zip.head(20))

# Οπτικοποίηση με matplotlib
plt.figure(figsize=(14, 7))

plt.scatter(
    top_products_per_zip['zip_code'],
    top_products_per_zip['bottles_sold'],
    s=top_products_per_zip['bottles_sold'] / 10,  # μέγεθος σημείων αναλογικό με πωλήσεις
    c=top_products_per_zip['zip_code'],           # χρώμα ανά zip code
    cmap='plasma',
    alpha=0.7,
    edgecolors='w'
)

plt.colorbar(label='Zip Code')
plt.xlabel('Zip Code')
plt.ylabel('Bottles Sold')
plt.title('Top Selling Product Bottles Sold by Zip Code')
plt.show()
