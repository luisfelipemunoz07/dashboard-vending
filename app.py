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
# CARGA Y LIMPIEZA
# -----------------------------
@st.cache_data
def load_and_clean_excel(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name="HOJA PARA TABLA DINÁMICA")

    # quitar columnas basura
    df = df.loc[:, ~df.columns.astype(str).str.contains(
        r"^Unnamed", case=False, regex=True)]

    # normalizar nombres
    df.columns = [str(c).strip() for c in df.columns]

    # validar columnas mínimas
    required = ["FECHA", "PRODUCTO", "CATEGORIA",
                "VENTA UNIDADES", "VENTA $", "UTILIDAD $"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Faltan columnas en el Excel: {missing}")
        st.stop()

    # conversión segura fecha (evita datetime.time)
    def parse_fecha(x):
        if isinstance(x, dt.time):
            return pd.NaT
        if isinstance(x, (dt.datetime, dt.date, pd.Timestamp)):
            return pd.to_datetime(x, errors="coerce")
        return pd.to_datetime(x, errors="coerce")

    df["FECHA"] = df["FECHA"].apply(parse_fecha)
    df = df.dropna(subset=["FECHA"])

    # asegurar numéricas
    for col in ["VENTA UNIDADES", "VENTA $", "UTILIDAD $"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # asegurar texto en PRODUCTO / CATEGORIA
    df["PRODUCTO"] = df["PRODUCTO"].astype(
        str).str.strip().replace("nan", "Sin producto")
    df["CATEGORIA"] = df["CATEGORIA"].astype(
        str).str.strip().replace("nan", "Sin categoría")

    # columnas tiempo
    df["SEMANA"] = df["FECHA"].dt.to_period("W")
    df["MES"] = df["FECHA"].dt.to_period("M")

    return df


# -----------------------------
# SUBIR ARCHIVO
# -----------------------------
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo ventas.xlsx", type=["xlsx"])

if uploaded_file is None:
    st.info("Sube tu archivo para comenzar.")
    st.stop()

df = load_and_clean_excel(uploaded_file)

# -----------------------------
# SIDEBAR (FILTROS)
# -----------------------------
st.sidebar.header("Filtros")

producto = st.sidebar.selectbox(
    "Selecciona producto",
    sorted(df["PRODUCTO"].unique())
)

fecha_min = df["FECHA"].min().date()
fecha_max = df["FECHA"].max().date()

rango_fecha = st.sidebar.date_input(
    "Rango de fechas",
    [fecha_min, fecha_max]
)

# Validar rango
if not isinstance(rango_fecha, (list, tuple)) or len(rango_fecha) != 2:
    st.error("Selecciona un rango de fechas (inicio y fin).")
    st.stop()

inicio = pd.to_datetime(rango_fecha[0])
fin = pd.to_datetime(rango_fecha[1])

# -----------------------------
# FILTRADO
# -----------------------------
df_filtrado = df[
    (df["PRODUCTO"] == producto) &
    (df["FECHA"] >= inicio) &
    (df["FECHA"] <= fin)
].copy()

if df_filtrado.empty:
    st.warning("No hay datos para ese producto en el rango seleccionado.")
    st.stop()

# -----------------------------
# MÉTRICAS
# -----------------------------
st.subheader(f"📦 Producto: {producto}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Unidades totales", int(df_filtrado["VENTA UNIDADES"].sum()))
col2.metric("Ventas ($)", round(df_filtrado["VENTA $"].sum(), 2))
col3.metric("Utilidad ($)", round(df_filtrado["UTILIDAD $"].sum(), 2))

ventas_total = float(df_filtrado["VENTA $"].sum())
utilidad_total = float(df_filtrado["UTILIDAD $"].sum())
margen = (utilidad_total / ventas_total * 100) if ventas_total > 0 else 0
col4.metric("Margen (%)", f"{margen:.1f}%")

# -----------------------------
# HISTÓRICO DIARIO
# -----------------------------
st.subheader("📈 Histórico de ventas (unidades por día)")

hist = df_filtrado.groupby("FECHA")["VENTA UNIDADES"].sum().sort_index()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(hist.index, hist.values, marker="o")
ax.set_ylabel("Unidades")
ax.set_xlabel("Fecha")
plt.xticks(rotation=25, ha="right")
st.pyplot(fig)

# -----------------------------
# PROMEDIO SEMANAL
# -----------------------------
st.subheader("📊 Ventas semanales + promedio semanal")

semana = df_filtrado.groupby("SEMANA")["VENTA UNIDADES"].sum().sort_index()
prom_semanal = semana.mean() if len(semana) else 0
st.write(f"Promedio semanal: **{prom_semanal:.2f} unidades**")

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(semana.index.astype(str), semana.values)
ax.set_xlabel("Semana")
ax.set_ylabel("Unidades")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

# -----------------------------
# PROMEDIO MENSUAL
# -----------------------------
st.subheader("📊 Ventas mensuales + promedio mensual")

mes = df_filtrado.groupby("MES")["VENTA UNIDADES"].sum().sort_index()
prom_mensual = mes.mean() if len(mes) else 0
st.write(f"Promedio mensual: **{prom_mensual:.2f} unidades**")

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(mes.index.astype(str), mes.values)
ax.set_xlabel("Mes")
ax.set_ylabel("Unidades")
plt.xticks(rotation=25, ha="right")
st.pyplot(fig)
