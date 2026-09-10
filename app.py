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

# --- ESTILOS CSS PERSONALIZADOS Y DISEÑO ---
st.markdown("""
    <style>
    /* Fondo principal con gradiente EMANA */
    .stApp {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%);
    }
    
    /* Tarjetas de productos */
    .product-box {
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .product-box:hover {
        border-color: #0284c7;
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.2);
        transform: translateY(-2px);
    }

    /* Botones interactivos con foco y hover */
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        border: 2px solid transparent;
    }
    .stButton > button:hover {
        border-color: #0284c7 !important;
        background-color: #0284c7 !important;
        color: white !important;
        transform: scale(1.02);
    }
    .stButton > button:focus {
        border-color: #0369a1 !important;
        box-shadow: 0 0 0 3px rgba(3, 105, 161, 0.4) !important;
    }

    /* Entradas de texto e insumos */
    div[data-baseweb="input"] > div {
        border-radius: 8px;
        border: 1.5px solid #94a3b8;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

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
    opciones_menu.extend(["Gestión & Rutas GPS (ADMIN)", "Dashboard & Ventas Globales", "Papelera de Reciclaje"])

opcion = st.sidebar.radio("Navegación / Módulos", opciones_menu)

# --- MÓDULO 1: REGISTRAR PEDIDO ---
if opcion == "Registrar Pedido / Venta":
    st.header("📝 Registrar Nuevo Pedido")
    col1, col2 = st.columns(2)
    with col1:
        cliente_nombre = st.text_input("Nombre Completo / Razón Social *")
        cliente_doc = st.text_input("DNI / RUC")
        local_direccion = st.text_input("Dirección del Local *")
        tipo_comprobante = st.selectbox("Comprobante", ["BOLETA", "FACTURA", "NOTA DE PEDIDO"])
    
    with col2:
        fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
        rango_entrega = st.selectbox("Rango Horario", ["Mañana (8:00 AM - 12:00 PM)", "Tarde (2:00 PM - 6:00 PM)", "Inmediato"])
    
    # --- SECCIÓN DE PRODUCTOS CON IMÁGENES Y SELECCIÓN ---
    st.subheader("📦 Catálogo de Productos")
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown('<div class="product-box">', unsafe_allow_html=True)
        try:
            st.image("botella 625 ml transparente.png", use_container_width=True)
        except:
            st.markdown("🍾 **Botella 625 ml**")
        st.write("**Botella 625 ml**")
        cant_625 = st.number_input("Cantidad (625ml)", min_value=0, value=0, step=1)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with p2:
        st.markdown('<div class="product-box">', unsafe_allow_html=True)
        try:
            st.image("BT 8.5L.png", use_container_width=True)
        except:
            st.markdown("🪣 **Botella 8.5 L**")
        st.write("**Botella 8.5 L**")
        cant_85 = st.number_input("Cantidad (8.5L)", min_value=0, value=0, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

    with p3:
        st.markdown('<div class="product-box">', unsafe_allow_html=True)
        try:
            st.image("LOGO agua Emana VECTOR 01.png", use_container_width=True)
        except:
            st.markdown("📦 **Caja 20 L**")
        st.write("**Caja de 20 L**")
        cant_20 = st.number_input("Cantidad (20L)", min_value=0, value=0, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

    total = st.number_input("Monto Total Calculado (S/.) *", min_value=0.0, step=0.5)

    # --- GEOLOCALIZACIÓN Y MAPA ---
    st.subheader("📍 Geolocalización / GPS Guía de Ruta")
    c_lat, c_lng = st.columns(2)
    with c_lat:
        latitud = st.number_input("Latitud", value=-11.0500, format="%.6f")
    with c_lng:
        longitud = st.number_input("Longitud", value=-75.3300, format="%.6f")

    # Visualización previa del mapa para el vendedor
    map_data = pd.DataFrame({'lat': [latitud], 'lon': [longitud]})
    st.map(map_data, zoom=14)

    if st.button("💾 Guardar Pedido", type="primary"):
        if not cliente_nombre or not local_direccion or total <= 0:
            st.warning("Por favor complete los campos obligatorios (*) y asegúrese de que el total sea mayor a 0")
        else:
            resumen_prod = f"625ml: {cant_625} | 8.5L: {cant_85} | 20L: {cant_20}"
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
                "productos": resumen_prod,
                "estado": "ACTIVO",
                "estado_entrega": "PENDIENTE"
            }
            try:
                supabase.table("pedidos").insert(nuevo_pedido).execute()
                st.success("✅ ¡Pedido registrado con éxito en la nube!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# --- MÓDULO 2: CONSULTAR PEDIDOS ---
elif opcion == "Consultar Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    res = supabase.table("pedidos").select("*").eq("vendedor", st.session_state["usuario"]).eq("estado", "ACTIVO").execute()
    if res.data:
        df_pedidos = pd.DataFrame(res.data)
        st.dataframe(df_pedidos, use_container_width=True)
    else:
        st.info("No tienes pedidos activos registrados.")

# --- MÓDULO 3: GESTIÓN DE PEDIDOS Y RUTAS GPS (ADMIN) ---
elif opcion == "Gestión & Rutas GPS (ADMIN)" and st.session_state["rol"] == "ADMIN":
    st.header("🗺️ Control General de Pedidos y Guía de Rutas GPS")
    
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df_admin = pd.DataFrame(res.data)
        
        # Filtros por vendedor y estado
        vendedores_list = ["Todos"] + list(df_admin["vendedor"].unique()) if "vendedor" in df_admin.columns else ["Todos"]
        v_sel = st.selectbox("Filtrar por Vendedor", vendedores_list)
        
        if v_sel != "Todos":
            df_filtrado = df_admin[df_admin["vendedor"] == v_sel]
        else:
            df_filtrado = df_admin

        st.subheader("📍 Ruta de Entregas en Tiempo Real")
        if "latitud" in df_filtrado.columns and "longitud" in df_filtrado.columns:
            map_df = df_filtrado[['latitud', 'longitud']].rename(columns={'latitud': 'lat', 'longitud': 'lon'})
            st.map(map_df)

        st.subheader("✏️ Modificar o Corregir Pedidos")
        st.dataframe(df_filtrado, use_container_width=True)
        
        pedido_id = st.selectbox("Selecciona ID de Pedido para Editar", df_filtrado["id"].tolist())
        
        col_ed1, col_ed2, col_ed3 = st.columns(3)
        with col_ed1:
            nuevo_estado_ent = st.selectbox("Estado de Entrega", ["PENDIENTE", "ENTREGADO", "NO ENTREGADO", "CANCELADO"])
        with col_ed2:
            nuevo_vendedor = st.text_input("Reasignar Vendedor", value=st.session_state["usuario"])
        with col_ed3:
            nuevo_monto = st.number_input("Corregir Monto (S/.)", min_value=0.0, step=0.5)

        c_act1, c_act2 = st.columns(2)
        with c_act1:
            if st.button("🔄 Actualizar Pedido"):
                supabase.table("pedidos").update({
                    "estado_entrega": nuevo_estado_ent,
                    "vendedor": nuevo_vendedor,
                    "total": nuevo_monto
                }).eq("id", pedido_id).execute()
                st.success("Pedido actualizado correctamente.")
                st.rerun()
                
        with c_act2:
            if st.button("🗑️ Mover a Papelera"):
                supabase.table("pedidos").update({"estado": "PAPELERA"}).eq("id", pedido_id).execute()
                st.warning("Pedido movido a la Papelera de Reciclaje.")
                st.rerun()
    else:
        st.info("No hay pedidos registrados para gestionar.")

# --- MÓDULO 4: DASHBOARD GENERAL ---
elif opcion == "Dashboard & Ventas Globales" and st.session_state["rol"] == "ADMIN":
    st.header("📊 Dashboard & Ventas Globales")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df_dash = pd.DataFrame(res.data)
        st.metric("Total Recaudado (S/.)", f"S/. {df_dash['total'].sum():,.2f}")
        st.metric("Total de Pedidos", len(df_dash))
        st.dataframe(df_dash)
    else:
        st.info("Sin datos para métricas.")

# --- MÓDULO 5: PAPELERA DE RECICLAJE (ADMIN) ---
elif opcion == "Papelera de Reciclaje" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Papelera de Reciclaje")
    res = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    if res.data:
        df_pap = pd.DataFrame(res.data)
        st.dataframe(df_pap, use_container_width=True)
        rec_id = st.selectbox("Selecciona ID para restaurar", df_pap["id"].tolist())
        if st.button("♻️ Restaurar Pedido"):
            supabase.table("pedidos").update({"estado": "ACTIVO"}).eq("id", rec_id).execute()
            st.success("Pedido restaurado.")
            st.rerun()
    else:
        st.info("La papelera está vacía.")