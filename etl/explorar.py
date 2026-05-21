import pandas as pd

# Explorar transacciones
print("=== TRANSACCIONES ===")
df_trans = pd.read_csv("data/raw/personal_transactions.csv")
print(df_trans.head(10))
print("\nColumnas:", df_trans.columns.tolist())
print("Shape:", df_trans.shape)
print("Tipos:\n", df_trans.dtypes)
print("Nulos:\n", df_trans.isnull().sum())

# Explorar presupuesto
print("\n=== PRESUPUESTO ===")
df_budget = pd.read_csv("data/raw/Budget.csv")
print(df_budget.head())
print("\nColumnas:", df_budget.columns.tolist())