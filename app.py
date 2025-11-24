import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Dashboard de Ventas Vivegreens", layout="wide")

#Conecto con SQL

conn=sqlite3.connect("ventas_2025.db")

@st.cache_data
def cargar_datos():
    return pd.read_sql_query("select * from ventas", conn)

df = cargar_datos()

st.title("📊  Dashboard de Ventas 2025")
st.markdown("Análisis de ventas reales usando SQL + Streamlit")


#====KPIs=====

ventas_totales = df["CANTIDAD"].multiply(df["PRECIO_VENTA"]).sum()

col1, col2 = st.columns(2)
col1.metric("💰  Ventas Totales", f"{ventas_totales:,.2f} €")
col2.metric("💰 Total de pedidos", len(df))

#====Filtros====

st.sidebar.header("Filtros")

clientes = ["TODOS"] + sorted(df["CLIENTE"].unique().tolist())
f_cliente = st.sidebar.selectbox("CLIENTE", clientes)

df["PRODUCTO"] = df["PRODUCTO"].fillna("Desconocido")

productos = ["Todos"] + sorted(df["PRODUCTO"].unique().tolist())
f_producto = st.sidebar.selectbox("PRODUCTO", productos)

df_filtrado = df.copy()
if f_cliente != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["CLIENTE"] == f_cliente]

if f_producto != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["PRODUCTO"] == f_producto]

# ==== Ventas mensuales ====
df_filtrado["mes"] = pd.to_datetime(df_filtrado["FECHA_PEDIDO"]).dt.strftime("%Y-%m")
ventas_mensuales = df_filtrado.groupby("mes")["PRECIO_VENTA"].sum()

st.subheader("📈 Ventas mensuales")
st.line_chart(ventas_mensuales)

# ==== Top productos ====
top_productos = (
    df_filtrado.groupby("PRODUCTO")
    .agg({"CANTIDAD": "sum", "PRECIO_VENTA": "sum"})
    .sort_values("PRECIO_VENTA", ascending=False)
)

st.subheader("🏆 Top productos")
st.bar_chart(top_productos["PRECIO_VENTA"])

# ==== Tabla final ====
st.subheader("📋 Datos filtrados")
st.dataframe(df_filtrado)