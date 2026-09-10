import streamlit as st
import streamlit.components.v1 as components
import datetime
import pandas as pd
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
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Error conectando a Supabase. Revisa tus Secrets en Streamlit.")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None

# --- BARRA LATERAL CON RELOJ DIGITAL EN TIEMPO REAL ---
st.sidebar.title("💧 Distribuidora EMANA")
st.sidebar.markdown("---")

reloj_js = """
<div style="background-color:#1e293b; color:#f8fafc; padding:12px; border-radius:8px; text-align:center; font-family:sans-serif;">
    <div id="fecha" style="font-size:13px; color:#94a3b8; font-weight:bold;"></div>
    <div id="reloj" style="font-size:24px; color:#38bdf8; font-weight:bold; margin-top:4px;"></div>
</div>

<script>
function actualizarReloj() {
    const ahora = new Date();
    const opcionesFecha = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const fechaTexto = ahora.toLocaleDateString('es-ES', opcionesFecha);
    const horaTexto = ahora.toLocaleTimeString('es-ES');
    
    document.getElementById('fecha').innerText = fechaTexto;
    document.getElementById('reloj').innerText = '⏰ ' + horaTexto;
}
setInterval(actualizarReloj, 1000);
actualizarReloj();
</script>
"""

# Renderizar el componente dinámico en la barra lateral
with st.sidebar:
    components.html(reloj_js, height=100)

st.sidebar.markdown("---")

# --- PANTALLA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.title("🔒 Iniciar Sesión - Sistema EMANA")
    with st.form("form_login"):
        user_input = st.text_input("Usuario").strip()
        pass_input = st.text_input("Contraseña", type="password").strip()
        btn_login = st.form_submit_button("Ingresar")
        
        if btn_login:
            try:
                res = supabase.table("usuarios").select("*").eq("username", user_input).eq("password", pass_input).execute()
                if res.data and len(res.data) > 0:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = res.data[0]["username"]
                    st.session_state["rol"] = res.data[0]["rol"]
                    st.success(f"Bienvenido {user_input}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            except Exception as ex:
                st.error(f"Error de conexión con la base de datos: {ex}")
    st.stop()

# --- NAVEGACIÓN Y PANEL DE CONTROL ---
st.sidebar.write(f"👤 **Usuario:** {st.session_state['usuario']}")
st.sidebar.write(f"🔰 **Rol:** {st.session_state['rol']}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["rol"] = None
    st.rerun()

opciones_menu = ["Registrar Pedido / Venta", "Consultar Mis Pedidos"]
if st.session_state["rol"] == "ADMIN":
    opciones_menu.extend(["Dashboard & Ventas Globales", "Papelera de Reciclaje"])

opcion = st.sidebar.radio("Navegación / Módulos", opciones_menu)

# --- MÓDULO 1: REGISTRAR PEDIDO ---
if opcion == "Registrar Pedido / Venta":
    st.header("📝 Registrar Nuevo Pedido")
    col1, col2 = st.columns(2)
    with col1:
        cliente_nombre = st.text_input("Nombre Completo / Razón Social *")
        cliente_doc = st.text_input("DNI / RUC")
        local_direccion = st.text_input("Dirección del Local *")
        tipo_comprobante = st.selectbox("Comprobante", ["BOLETA", "FACTURA", "NOTA"])
    
    with col2:
        fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
        rango_entrega = st.selectbox("Rango Horario", ["Mañana (8:00 AM - 12:00 PM)", "Tarde (2:00 PM - 6:00 PM)", "Inmediato"])
        total = st.number_input("Monto Total (S/.) *", min_value=0.0, step=0.5)

    st.subheader("📍 Geolocalización / GPS")
    c_lat, c_lng = st.columns(2)
    with c_lat:
        latitud = st.number_input("Latitud", value=-11.0500, format="%.6f")
    with c_lng:
        longitud = st.number_input("Longitud", value=-75.3300, format="%.6f")

    if st.button("💾 Guardar Pedido", type="primary"):
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
                "fecha_entrega": str(fecha_entrega),
                "rango_entrega": rango_entrega,
                "total": total,
                "estado": "ACTIVO"
            }
            supabase.table("pedidos").insert(nuevo_pedido).execute()
            st.success("✅ ¡Pedido registrado con éxito en la nube!")

# --- MÓDULO 2: CONSULTAR PEDIDOS ---
elif opcion == "Consultar Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data))
    else:
        st.info("No hay pedidos registrados.")

# --- MÓDULO 3: PAPELERA DE RECICLAJE (ADMIN) ---
elif opcion == "Papelera de Reciclaje" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Papelera de Reciclaje")
    res = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data))
    else:
        st.info("La papelera está vacía.")