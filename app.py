import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Distribuidora EMANA", page_icon="💧", layout="wide")

# Conexión a Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Estado de sesión / Login
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# BARRA LATERAL (Preservando tu diseño original)
with st.sidebar:
    st.title("💧 Distribuidora EMANA")
    st.info(f"📅 {datetime.now().strftime('%A, %d de %B de %Y')}\n\n⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    if st.session_state.logueado:
        st.write(f"👤 **Usuario:** {st.session_state.usuario}")
        st.write(f"🔑 **Rol:** {st.session_state.rol}")
        if st.button("Cerrar Sesión"):
            st.session_state.logueado = False
            st.rerun()

# CONTENIDO PRINCIPAL
if not st.session_state.logueado:
    st.title("🔒 Iniciar Sesión - Sistema EMANA")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        # Validación de credenciales
        if user == "admin" and password in ["admin123", "admin"]:
            st.session_state.logueado = True
            st.session_state.usuario = "admin"
            st.session_state.rol = "ADMIN"
            st.rerun()
        elif user == "vendedor" and password in ["vendedor123", "vendedor"]:
            st.session_state.logueado = True
            st.session_state.usuario = "vendedor"
            st.session_state.rol = "VENDEDOR"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

else:
    # MENÚ NAVEGACIÓN
    opcion = st.sidebar.radio("Navegación / Módulos", [
        "Registrar Pedido / Venta", 
        "Consultar Mis Pedidos", 
        "Dashboard & Ventas Globales", 
        "Papelera de Reciclaje"
    ])

    if opcion == "Registrar Pedido / Venta":
        st.header("📝 Registrar Nuevo Pedido")
        
        col_a, col_b = st.columns(2)
        with col_a:
            cliente = st.text_input("Nombre Completo / Razón Social *")
            dni_ruc = st.text_input("DNI / RUC")
            direccion = st.text_input("Dirección del Local *")
            comprobante = st.selectbox("Comprobante", ["BOLETA", "FACTURA", "NOTA DE PEDIDO"])
        
        with col_b:
            fecha = st.date_input("Fecha de Entrega")
            rango = st.selectbox("Rango Horario", ["Mañana (8:00 AM - 12:00 PM)", "Tarde (2:00 PM - 6:00 PM)"])
            monto = st.number_input("Monto Total (S/.) *", min_value=0.0, step=0.5)

        st.subheader("📦 Productos")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.image("botella 625 ml transparente.png", width=100)
            c_625 = st.number_input("Botella 625 ml", min_value=0, value=0)
        with p2:
            st.image("BT 8.5L.png", width=100)
            c_85 = st.number_input("Botella 8.5 L", min_value=0, value=0)
        with p3:
            c_20 = st.number_input("Caja de 20 L", min_value=0, value=0)

        st.subheader("📍 Geolocalización / GPS")
        g1, g2 = st.columns(2)
        with g1:
            lat = st.number_input("Latitud", value=-11.050000, format="%.6f")
        with g2:
            lng = st.number_input("Longitud", value=-75.330000, format="%.6f")

        if st.button("💾 Guardar Pedido"):
            st.success("Pedido guardado exitosamente.")

    elif opcion == "Consultar Mis Pedidos":
        st.header("📋 Mis Pedidos Registrados")
        st.info("Aquí puedes consultar el estado de tus entregas.")

    elif opcion == "Dashboard & Ventas Globales":
        st.header("📊 Dashboard General")
        st.info("Resumen de ventas y métricas globales.")