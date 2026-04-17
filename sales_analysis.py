import pandas as pd

# Load CSV file
df = pd.read_csv("sales_data.csv")

print("Original Data:")
print(df)

# CLEANING DATA
df = df.drop_duplicates()

df["region"] = df["region"].fillna("NA")

df["revenue"] = df["revenue"].fillna(df["quantity"] * df["price"])

df["quantity"] = df["quantity"].fillna((df["revenue"] / df["price"]).round())

df["order_date"] = pd.to_datetime(df["order_date"])

df["month"] = df["order_date"].dt.month_name()

# TOP 5 PRODUCTS BY REVENUE
top_products = df.groupby("product")["revenue"].sum().nlargest(5)

print("\nTop 5 Products by Revenue:")
print(top_products)

# MONTH WITH HIGHEST ORDERS
month_counts = df["month"].value_counts()

print("\nMonth with Highest Orders:")
print(month_counts.idxmax(), "-", month_counts.max(), "orders")

# NULL % PER COLUMN
null_percent = (df.isnull().sum() / len(df)) * 100

print("\nNull Percentage Per Column:")
print(null_percent)







