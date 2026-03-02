from __future__ import annotations

import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# Carga y limpieza
# -----------------------------
def load_and_clean_excel(path: str, sheet_name: str = "HOJA PARA TABLA DINÁMICA") -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name)

    # Quitar columnas "basura": tipo Unnamed o columnas sin nombre útil
    df = df.loc[:, ~df.columns.astype(str).str.contains(
        r"^Unnamed", case=False, regex=True)]
    # A veces viene una columna con nombre numérico (ej. 44599) casi vacía
    df = df.loc[:, [c for c in df.columns if not (
        isinstance(c, (int, float)))]]

    # Normalizar nombres (opcional pero ayuda)
    df.columns = [str(c).strip() for c in df.columns]

    # Asegurar FECHA
    if "FECHA" not in df.columns:
        raise ValueError("No encontré la columna FECHA en el archivo.")
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

    # Columnas clave esperadas
    expected = ["MÁQUINA", "PRODUCTO", "CATEGORIA",
                "VENTA UNIDADES", "VENTA $", "UTILIDAD $"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esperadas: {missing}")

    # Convertir numéricas
    for col in ["VENTA UNIDADES", "VENTA $", "COSTO DE VENTA $", "UTILIDAD $", "utilidad x dia", "UTILIDAD X SEMANA"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Limpiar strings
    for col in ["MÁQUINA", "PRODUCTO", "CATEGORIA"]:
        df[col] = df[col].astype(str).str.strip()

    # Features de tiempo
    df["SEMANA"] = df["FECHA"].dt.to_period(
        "W-MON")  # semanas de lunes a domingo
    df["MES"] = df["FECHA"].dt.to_period("M")
    df["DIA_SEMANA"] = df["FECHA"].dt.day_name()

    # Métricas derivadas
    df["PRECIO_PROM_UNIDAD"] = np.where(
        df["VENTA UNIDADES"] > 0, df["VENTA $"] / df["VENTA UNIDADES"], np.nan)
    df["MARGEN_%"] = np.where(
        df["VENTA $"] > 0, (df["UTILIDAD $"] / df["VENTA $"]) * 100, np.nan)

    return df


# -----------------------------
# Helpers de plots
# -----------------------------
def save_or_show(fig, outpath: str | None):
    if outpath:
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        fig.savefig(outpath, dpi=200, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


def plot_top_products_by_period(
    df: pd.DataFrame,
    period_col: str,            # "SEMANA" o "MES"
    metric_col: str = "VENTA UNIDADES",
    top_n: int = 10,
    outdir: str | None = None,
):
    # Top por periodo -> genera una figura por cada periodo
    periods = df[period_col].dropna().sort_values().unique()

    for p in periods:
        tmp = df[df[period_col] == p].groupby(
            "PRODUCTO", as_index=False)[metric_col].sum()
        tmp = tmp.sort_values(metric_col, ascending=False).head(top_n)

        fig = plt.figure(figsize=(10, 5))
        plt.barh(tmp["PRODUCTO"][::-1], tmp[metric_col][::-1])
        plt.title(
            f"Top {top_n} productos por {metric_col} | {period_col} = {p}")
        plt.xlabel(metric_col)
        plt.ylabel("PRODUCTO")

        outpath = None
        if outdir:
            outpath = os.path.join(
                outdir, f"top_{top_n}_productos_{metric_col}_{period_col}_{str(p).replace('/', '-')}.png")
        save_or_show(fig, outpath)


def plot_units_by_product(df: pd.DataFrame, top_n: int = 25, outpath: str | None = None):
    tmp = df.groupby("PRODUCTO", as_index=False)["VENTA UNIDADES"].sum()
    tmp = tmp.sort_values("VENTA UNIDADES", ascending=False).head(top_n)

    fig = plt.figure(figsize=(10, 6))
    plt.barh(tmp["PRODUCTO"][::-1], tmp["VENTA UNIDADES"][::-1])
    plt.title(f"Top {top_n} productos por unidades vendidas (total)")
    plt.xlabel("VENTA UNIDADES")
    plt.ylabel("PRODUCTO")
    save_or_show(fig, outpath)


def plot_units_by_category(df: pd.DataFrame, outpath: str | None = None):
    tmp = df.groupby("CATEGORIA", as_index=False)["VENTA UNIDADES"].sum()
    tmp = tmp.sort_values("VENTA UNIDADES", ascending=False)

    fig = plt.figure(figsize=(9, 5))
    plt.bar(tmp["CATEGORIA"], tmp["VENTA UNIDADES"])
    plt.title("Unidades vendidas por categoría (total)")
    plt.xlabel("CATEGORIA")
    plt.ylabel("VENTA UNIDADES")
    plt.xticks(rotation=25, ha="right")
    save_or_show(fig, outpath)


# -----------------------------
# Extras recomendados
# -----------------------------
def plot_sales_profit_by_machine(df: pd.DataFrame, outpath: str | None = None):
    tmp = df.groupby("MÁQUINA", as_index=False)[
        ["VENTA $", "UTILIDAD $", "VENTA UNIDADES"]].sum()
    tmp = tmp.sort_values("VENTA $", ascending=False)

    fig = plt.figure(figsize=(10, 5))
    plt.bar(tmp["MÁQUINA"], tmp["VENTA $"])
    plt.title("Ventas ($) por máquina (total)")
    plt.xlabel("MÁQUINA")
    plt.ylabel("VENTA $")
    save_or_show(fig, outpath)


def plot_trend_monthly(df: pd.DataFrame, outpath: str | None = None):
    tmp = df.groupby("MES", as_index=False)[
        ["VENTA $", "UTILIDAD $", "VENTA UNIDADES"]].sum()
    tmp = tmp.sort_values("MES")
    x = tmp["MES"].astype(str)

    fig = plt.figure(figsize=(10, 5))
    plt.plot(x, tmp["VENTA $"], marker="o")
    plt.title("Tendencia mensual de ventas ($)")
    plt.xlabel("MES")
    plt.ylabel("VENTA $")
    plt.xticks(rotation=25, ha="right")
    save_or_show(fig, outpath)


def pareto_products(df: pd.DataFrame, outpath: str | None = None):
    tmp = df.groupby("PRODUCTO", as_index=False)["VENTA $"].sum()
    tmp = tmp.sort_values("VENTA $", ascending=False)
    tmp["%_acum"] = tmp["VENTA $"].cumsum() / tmp["VENTA $"].sum() * 100
    tmp["rank"] = np.arange(1, len(tmp) + 1)

    fig = plt.figure(figsize=(10, 5))
    plt.plot(tmp["rank"], tmp["%_acum"])
    plt.axhline(80, linestyle="--")
    plt.title("Pareto de productos (ventas $) – ¿cuántos productos hacen el 80%?")
    plt.xlabel("Ranking de producto")
    plt.ylabel("% acumulado de ventas $")
    save_or_show(fig, outpath)


def export_summary_tables(df: pd.DataFrame, outpath: str):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)

    resumen_producto = df.groupby(["CATEGORIA", "PRODUCTO"], as_index=False)[
        ["VENTA UNIDADES", "VENTA $", "UTILIDAD $"]].sum()
    resumen_producto["MARGEN_%"] = np.where(
        resumen_producto["VENTA $"] > 0, resumen_producto["UTILIDAD $"] / resumen_producto["VENTA $"] * 100, np.nan)

    resumen_maquina = df.groupby("MÁQUINA", as_index=False)[
        ["VENTA UNIDADES", "VENTA $", "UTILIDAD $"]].sum()
    resumen_maquina["MARGEN_%"] = np.where(
        resumen_maquina["VENTA $"] > 0, resumen_maquina["UTILIDAD $"] / resumen_maquina["VENTA $"] * 100, np.nan)

    with pd.ExcelWriter(outpath, engine="openpyxl") as writer:
        resumen_producto.to_excel(
            writer, sheet_name="resumen_producto", index=False)
        resumen_maquina.to_excel(
            writer, sheet_name="resumen_maquina", index=False)


# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True,
                        help="Ruta del Excel (ventas.xlsx)")
    parser.add_argument("--outdir", default="outputs_ventas",
                        help="Carpeta para guardar imágenes y resumen")
    parser.add_argument("--top", type=int, default=10,
                        help="Top N productos en charts por periodo")
    args = parser.parse_args()

    df = load_and_clean_excel(args.file)

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # 1) Productos más vendidos semanalmente y mensualmente
    plot_top_products_by_period(
        df, "SEMANA", "VENTA UNIDADES", top_n=args.top, outdir=outdir)
    plot_top_products_by_period(
        df, "MES", "VENTA UNIDADES", top_n=args.top, outdir=outdir)

    # 2) Unidades por producto y por categoría
    plot_units_by_product(df, top_n=25, outpath=os.path.join(
        outdir, "top_25_productos_unidades_total.png"))
    plot_units_by_category(df, outpath=os.path.join(
        outdir, "unidades_por_categoria_total.png"))

    # Extras recomendados
    plot_sales_profit_by_machine(df, outpath=os.path.join(
        outdir, "ventas_por_maquina_total.png"))
    plot_trend_monthly(df, outpath=os.path.join(
        outdir, "tendencia_mensual_ventas.png"))
    pareto_products(df, outpath=os.path.join(
        outdir, "pareto_productos_ventas.png"))

    export_summary_tables(df, outpath=os.path.join(
        outdir, "resumen_ventas.xlsx"))

    print(f"Listo. Revisa la carpeta: {outdir}")


if __name__ == "__main__":
    main()
