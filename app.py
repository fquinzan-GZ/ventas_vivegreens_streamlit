import streamlit as st
import pandas as pd
import sqlite3


st.set_page_config(
    page_title="Dashboard de Ventas Vivegreens",
    layout="wide", 
    menu_items={
        'Get help': 'https://www.vivegreens.es/faq/',
        'Report a Bug': 'https://vivegreens.es/contacto/'
    }
    )

#Conecto con SQL

conn=sqlite3.connect("ventas_2025.db")

@st.cache_data


def cargar_datos():
    return pd.read_sql_query("select * from ventas", conn)

df = cargar_datos()

st.title("📊  Dashboard de Ventas 2025")
st.markdown("Análisis de ventas reales usando SQL + Streamlit")


def page_1():


    st.image("LogoNuevo23-removebg-preview.png", caption=None)

def page_2():

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

    productos = ["TODOS"] + sorted(df["PRODUCTO"].unique().tolist())
    f_producto = st.sidebar.selectbox("PRODUCTO", productos)

    df["CODIGO_POSTAL"] = df["CODIGO_POSTAL"].astype("Int64")   # convierte float → entero
    df["CODIGO_POSTAL"] = df["CODIGO_POSTAL"].astype(str)       # convierte entero → string

    c_postal = ["TODOS"] + sorted(df["CODIGO_POSTAL"].unique().tolist())
    f_postal = st.sidebar.selectbox("CODIGO POSTAL", c_postal, )

    df_filtrado = df.copy()
    if f_cliente != "TODOS":
        df_filtrado = df_filtrado[df_filtrado["CLIENTE"] == f_cliente]

    if f_producto != "TODOS":
        df_filtrado = df_filtrado[df_filtrado["PRODUCTO"] == f_producto]

    if f_postal != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado["CODIGO_POSTAL"] == f_postal]


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

pg = st.navigation(
    {
        "Home":[st.Page(page_1, title="Inicio", icon="🌱")],
        "Data":[st.Page(page_2, title="Graficos", icon="📈")]
    }
)
pg.run()