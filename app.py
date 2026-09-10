import streamlit as st
import datetime
import time
import pandas as pd
from PIL import Image
from supabase import create_client, Client

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Sistema EMANA - Gestión de Ventas",
    page_icon="💧",
    layout="wide"
)

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL") or "https://tu-proyecto.supabase.co"
    key = st.secrets.get("SUPABASE_KEY") or "tu-clave-anon"
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Error al conectar con Supabase. Verifica tus credenciales en Secrets.")

# --- ESTADO DE SESIÓN Y LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None

# --- RELOJ Y FECHA EN TIEMPO REAL ---
st.sidebar.title("💧 Distribuidora EMANA")
st.sidebar.markdown("---")

ahora = datetime.datetime.now()
st.sidebar.markdown(
    f"""
    <div style="background-color:#1e293b; color:#f8fafc; padding:12px; border-radius:8px; text-align:center;">
        <h4 style="margin:0; font-size: 14px; color: #94a3b8;">📅 {ahora.strftime('%A, %d de %B %Y')}</h4>
        <h2 style="margin:5px 0 0 0; font-size: 24px; color: #38bdf8;">⏰ {ahora.strftime('%H:%M:%S')}</h2>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# --- CONTROL DE INICIO DE SESIÓN ---
if not st.session_state["autenticado"]:
    st.title("🔒 Iniciar Sesión - Sistema EMANA")
    with st.form("form_login"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        btn_login = st.form_submit_button("Ingresar")
        
        if btn_login:
            res = supabase.table("usuarios").select("*").eq("username", user_input).eq("password", pass_input).execute()
            if res.data:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = res.data[0]["username"]
                st.session_state["rol"] = res.data[0]["rol"]
                st.success(f"Bienvenido {user_input} ({res.data[0]['rol']})")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- BARRA LATERAL (USUARIO AUTENTICADO) ---
st.sidebar.write(f"👤 **Usuario:** {st.session_state['usuario']}")
st.sidebar.write(f"🔰 **Rol:** {st.session_state['rol']}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["rol"] = None
    st.rerun()

# --- MENÚ DE NAVEGACIÓN ---
opciones_menu = ["Registrar Pedido / Venta", "Consultar Mis Pedidos"]
if st.session_state["rol"] == "ADMIN":
    opciones_menu.extend(["Dashboard & Ventas Globales", "Papelera de Reciclaje"])

opcion = st.sidebar.radio("Navegación / Módulos", opciones_menu)

# --- MÓDULO 1: REGISTRAR PEDIDO ---
if opcion == "Registrar Pedido / Venta":
    st.header("📝 Registrar Nuevo Pedido")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente_nombre = st.text_input("Nombre Completo o Razón Social del Cliente *")
        cliente_doc = st.text_input("DNI / RUC")
        local_direccion = st.text_input("Dirección / Referencia del Local *")
        tipo_comprobante = st.selectbox("Comprobante Requerido", ["BOLETA", "FACTURA", "NOTA"])
    
    with col2:
        fecha_entrega = st.date_input("Fecha Programada de Entrega", min_value=datetime.date.today())
        rango_entrega = st.selectbox("Rango Horario de Entrega", ["Mañana (8:00 AM - 12:00 PM)", "Tarde (2:00 PM - 6:00 PM)", "Inmediato"])
        total = st.number_input("Monto Total del Pedido (S/.) *", min_value=0.0, step=0.5)

    st.subheader("📍 Captura de GPS / Ubicación en Tiempo Real")
    c_lat, c_lng = st.columns(2)
    with c_lat:
        latitud = st.number_input("Latitud", value=-11.0500, format="%.6f")
    with c_lng:
        longitud = st.number_input("Longitud", value=-75.3300, format="%.6f")

    st.subheader("📷 Fotografía del Lugar / Fachada")
    foto_file = st.file_uploader("Tomar o subir foto", type=["png", "jpg", "jpeg"])
    foto_url = ""
    if foto_file is not None:
        st.image(foto_file, caption="Vista previa de la imagen", width=250)
        # Aquí se gestiona la URL temporal o carga al bucket
        foto_url = f"https://emana-media.s3.amazonaws.com/{foto_file.name}"

    if st.button("💾 Guardar y Confirmar Pedido", type="primary"):
        if not cliente_nombre or not local_direccion or total <= 0:
            st.warning("Por favor complete los campos obligatorios (*)")
        else:
            nuevo_pedido = {
                "vendedor": st.session_state["usuario"],
                "cliente_nombre": cliente_nombre,
                "cliente_doc": cliente_doc,
                "local_direccion": local_direccion,
                "latitud": latitud,
                "longitud": longitud,
                "tipo_comprobante": tipo_comprobante,
                "foto_url": foto_url,
                "fecha_entrega": str(fecha_entrega),
                "rango_entrega": rango_entrega,
                "total": total,
                "estado": "ACTIVO"
            }
            res = supabase.table("pedidos").insert(nuevo_pedido).execute()
            st.success("✅ ¡Pedido registrado con éxito en la nube!")

# --- MÓDULO 2: CONSULTAR PEDIDOS ---
elif opcion == "Consultar Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df[["vendedor", "cliente_nombre", "tipo_comprobante", "fecha_entrega", "rango_entrega", "total"]])
    else:
        st.info("No hay pedidos activos registrados.")

# --- MÓDULO 3: PAPELERA DE RECICLAJE (SOLO ADMIN) ---
elif opcion == "Papelera de Reciclaje" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Papelera de Reciclaje (Registros Eliminados)")
    res = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    
    if res.data:
        df_papelera = pd.DataFrame(res.data)
        st.dataframe(df_papelera)
        
        col_res, col_del = st.columns(2)
        with col_res:
            id_restaurar = st.selectbox("Seleccione ID para Restaurar", [item["id"] for item in res.data])
            if st.button("♻️ Restaurar Pedido"):
                supabase.table("pedidos").update({"estado": "ACTIVO", "eliminado_en": None}).eq("id", id_restaurar).execute()
                st.success("Pedido restaurado correctamente.")
                st.rerun()
                
        with col_del:
            id_eliminar = st.selectbox("Seleccione ID para Eliminar Definitivamente", [item["id"] for item in res.data])
            if st.button("🔥 Eliminar Permanentemente", type="primary"):
                supabase.table("pedidos").delete().eq("id", id_eliminar).execute()
                st.success("Pedido eliminado definitivamente de la base de datos.")
                st.rerun()
    else:
        st.info("La papelera de reciclaje está vacía.")
