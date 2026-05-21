import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Verificar variables
print("HOST:", os.getenv("DB_HOST"))
print("PORT:", os.getenv("DB_PORT"))
print("DB:", os.getenv("DB_NAME"))
print("USER:", os.getenv("DB_USER"))

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

tablas = {
    "transacciones": "transacciones_raw",
    "resumen_mensual": "resumen_mensual_calc",
    "gastos_categoria": "gastos_categoria_calc",
    "comparacion_presupuesto": "comparacion_presupuesto"
}

for nombre, tabla in tablas.items():
    df = pd.read_sql(f"SELECT * FROM {tabla}", engine)
    ruta = f"data/processed/{nombre}.csv"
    df.to_csv(ruta, index=False, decimal=',', sep=';')
    print(f"Exportado: {ruta}")

print("Todos los CSV exportados!")