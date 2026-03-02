import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

# -----------------------------
# CONFIG APP
# -----------------------------
st.set_page_config(page_title="Dashboard Vending", layout="wide")

st.title("📊 Dashboard Ventas - Room 24.7")

# -----------------------------
# CARGAR DATA
# -----------------------------


def load_data():
    df = pd.read_excel("ventas.xlsx", sheet_name="HOJA PARA TABLA DINÁMICA")

    df = df.loc[:, ~df.columns.astype(str).str.contains("Unnamed")]

    def parse_fecha(x):
        if isinstance(x, dt.time):
            return pd.NaT
        if isinstance(x, (dt.datetime, dt.date, pd.Timestamp)):
            return pd.to_datetime(x, errors="coerce")
        return pd.to_datetime(x, errors="coerce", dayfirst=True)

    df["FECHA"] = df["FECHA"].apply(parse_fecha)
    df = df.dropna(subset=["FECHA"])

# Ahora sí creamos semana y mes
    df["SEMANA"] = df["FECHA"].dt.to_period("W")
    df["MES"] = df["FECHA"].dt.to_period("M")

    return df


df = load_data()
df["PRODUCTO"] = df["PRODUCTO"].astype(str).str.strip()
# -----------------------------
# SIDEBAR (FILTROS)
# -----------------------------
st.sidebar.header("Filtros")

producto = st.sidebar.selectbox(
    "Selecciona producto",
    sorted(df["PRODUCTO"].unique())
)

fecha_min = df["FECHA"].min()
fecha_max = df["FECHA"].max()

rango_fecha = st.sidebar.date_input(
    "Rango de fechas",
    [fecha_min, fecha_max]
)

# -----------------------------
# FILTRADO
# -----------------------------
df_filtrado = df[
    (df["PRODUCTO"] == producto) &
    (df["FECHA"] >= pd.to_datetime(rango_fecha[0])) &
    (df["FECHA"] <= pd.to_datetime(rango_fecha[1]))
]

# -----------------------------
# MÉTRICAS
# -----------------------------
st.subheader(f"📦 Producto: {producto}")

col1, col2, col3 = st.columns(3)

col1.metric("Unidades totales", int(df_filtrado["VENTA UNIDADES"].sum()))
col2.metric("Ventas ($)", round(df_filtrado["VENTA $"].sum(), 2))
col3.metric("Utilidad ($)", round(df_filtrado["UTILIDAD $"].sum(), 2))

# -----------------------------
# HISTÓRICO DIARIO
# -----------------------------
st.subheader("📈 Histórico de ventas")

hist = df_filtrado.groupby("FECHA")["VENTA UNIDADES"].sum()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(hist.index, hist.values)
ax.set_ylabel("Unidades")
ax.set_xlabel("Fecha")

st.pyplot(fig)

# -----------------------------
# PROMEDIO SEMANAL
# -----------------------------
st.subheader("📊 Promedio semanal")

semana = df_filtrado.groupby("SEMANA")["VENTA UNIDADES"].sum()

prom_semanal = semana.mean()
st.write(f"Promedio semanal: **{prom_semanal:.2f} unidades**")

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(semana.index.astype(str), semana.values)
ax.set_xticklabels(semana.index.astype(str), rotation=45)

st.pyplot(fig)

# -----------------------------
# PROMEDIO MENSUAL
# -----------------------------
st.subheader("📊 Promedio mensual")

mes = df_filtrado.groupby("MES")["VENTA UNIDADES"].sum()

prom_mensual = mes.mean()
st.write(f"Promedio mensual: **{prom_mensual:.2f} unidades**")

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(mes.index.astype(str), mes.values)

st.pyplot(fig)
