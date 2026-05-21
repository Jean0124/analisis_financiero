import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# Conexión a PostgreSQL
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def limpiar_transacciones():
    print("Cargando transacciones...")
    df = pd.read_csv("data/raw/personal_transactions.csv")

    # Renombrar columnas
    df.columns = ["fecha", "descripcion", "monto", "tipo", "categoria", "cuenta"]

    # Convertir fecha
    df["fecha"] = pd.to_datetime(df["fecha"], format="%m/%d/%Y")

    # Normalizar tipo a español
    df["tipo"] = df["tipo"].map({
        "debit": "gasto",
        "credit": "ingreso"
    })

    # Limpiar montos negativos
    df["monto"] = df["monto"].abs()

    # Agregar columnas de tiempo
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["mes_nombre"] = df["fecha"].dt.strftime("%B")

    print(f"Transacciones limpias: {len(df)}")
    return df

def limpiar_presupuesto():
    print("Cargando presupuesto...")
    df = pd.read_csv("data/raw/Budget.csv")
    df.columns = ["categoria", "presupuesto"]
    print(f"Categorías con presupuesto: {len(df)}")
    return df

def cargar_a_postgres(df_trans, df_budget):
    print("Cargando a PostgreSQL...")

    # Cargar transacciones
    df_trans.to_sql(
        "transacciones_raw",
        engine,
        if_exists="replace",
        index=False
    )
    print("Transacciones cargadas")

    # Cargar presupuesto
    df_budget.to_sql(
        "presupuesto",
        engine,
        if_exists="replace",
        index=False
    )
    print("Presupuesto cargado")

def main():
    df_trans = limpiar_transacciones()
    df_budget = limpiar_presupuesto()

    print("\n--- Vista previa de transacciones limpias ---")
    print(df_trans.head())
    print("\nTipos de transacción:")
    print(df_trans["tipo"].value_counts())
    print("\nTop categorías:")
    print(df_trans["categoria"].value_counts().head(10))

    cargar_a_postgres(df_trans, df_budget)
    print("\nETL completado exitosamente!")

if __name__ == "__main__":
    main()