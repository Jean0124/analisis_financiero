import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(
     f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
     f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def cargar_datos():
    df = pd.read_sql("SELECT * FROM transacciones_raw", engine)
    df["fecha"] = pd.to_datetime(df['fecha'])
    return df

def kpi_general(df):
    print("\n========== KPIs GENERALES ==========")

    ingresos = df[df["tipo"] == "ingreso"]["monto"].sum()
    gastos = df[df["tipo"] == "gasto"]["monto"].sum()
    ahorro = ingresos - gastos
    tasa_ahorro = (ahorro / ingresos * 100 ) if ingresos > 0 else 0

    print(f"Total ingresos:    ${ingresos:,.2f}")
    print(f"Total gastos:      ${gastos:,.2f}")
    print(f"Ahorro neto:       ${ahorro:,.2f}")
    print(f"Tasa de ahorro:    {tasa_ahorro:.1f}%")

    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "ahorro": ahorro,
        "tasa_ahorro": tasa_ahorro
    }

def analisis_mensual (df):
     print("\n========== RESUMEN MENSUAL ==========")

     mensual = df.groupby(["anio", "mes", "tipo"])["monto"].sum().unstack(fill_value=0)


     if "ingreso" not in mensual.columns:
         mensual["ingreso"] = 0
     if("gasto" not in mensual.columns):
         mensual["gasto"] = 0

     mensual["ahorro"] = mensual["ingreso"] - mensual["gasto"]
     mensual["tasa_ahorro_%"] = (mensual["ahorro"] / mensual["ingreso"] * 100).round(1)

     print(mensual.tail(12))
     return mensual


def gastos_por_categoria (df):
    print("\n========== GASTOS POR CATEGORIA ==========")

    gastos = df[df["tipo"] == "gasto"].groupby("categoria").agg(
        total=("monto", "sum"),
        transacciones=("monto", "count"),
        promedio=("monto", "mean")
    ).sort_values("total", ascending=False)

    gastos["porcentaje_%"] = (gastos["total"] / gastos["total"].sum() * 100).round(2)

    print(gastos.head(10))
    return gastos

def comparar_presupuesto(df):
    print("\n========== PRESUPUESTO VS REAL ==========")

    df_budget = pd.read_sql("SELECT * FROM presupuesto", engine)

    # Gasto mensual promedio por categoria
    gastos_cat = df[df["tipo"] == "gasto"].groupby("categoria")["monto"].sum()
    meses = df["fecha"].dt.to_period("M").nunique()
    gastos_mensual = (gastos_cat / meses).reset_index()
    gastos_mensual.columns = ["categoria", "gasto_mensual_promedio"]

    comparacion = df_budget.merge(gastos_mensual, on="categoria", how="left").fillna(0)
    comparacion["diferencia"] = comparacion["presupuesto"] - comparacion["gasto_mensual_promedio"]
    comparacion["estado"] = comparacion["diferencia"].apply(
        lambda x: "OK" if x >= 0 else "EXCEDIDO"
    )

    print(comparacion.sort_values("diferencia"))
    return comparacion

def tendencia_ahorro(df):
    print("\n========== TENDENCIA DE AHORRO ==========")

    mensual = df.groupby(["anio", "mes", "tipo"])["monto"].sum().unstack(fill_value=0)

    if "ingreso" not in mensual.columns:
        mensual["ingreso"] = 0
    if "gasto" not in mensual.columns:
        mensual["gasto"] = 0

    mensual["ahorro"] = mensual["ingreso"] - mensual["gasto"]
    mensual["ahorro_acumulado"] = mensual["ahorro"].cumsum()

    print(mensual[["ingreso", "gasto", "ahorro", "ahorro_acumulado"]].tail(12))
    return mensual

def guardar_resultados(mensual, gastos_cat, comparacion):
    print("\nGuardando resultados procesados...")

    mensual.reset_index().to_sql("resumen_mensual_calc", engine, if_exists="replace", index=False)
    gastos_cat.reset_index().to_sql("gastos_categoria_calc", engine, if_exists="replace", index=False)
    comparacion.to_sql("comparacion_presupuesto", engine, if_exists="replace", index=False)

    print("Resultados guardados en PostgreSQL")

def main():
    df = cargar_datos()

    kpi_general(df)
    mensual = analisis_mensual(df)
    gastos_cat = gastos_por_categoria(df)
    comparacion = comparar_presupuesto(df)
    tendencia_ahorro(df)
    guardar_resultados(mensual, gastos_cat, comparacion)

    print("\nAnalisis completado!")

if __name__ == "__main__":
    main()
    
