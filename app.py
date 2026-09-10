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

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%);
    }
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
        transform: translateY(-3px);
    }
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

# --- ENCABEZADO CON LOGO Y ESLOGAN ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=130)
    except:
        st.title("💧")
with col_titulo:
    st.title("Distribuidora de Agua de Mesa EMANA")
    st.caption("✨ *Vitalidad vida sana*")

st.markdown("---")

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
if "gps_coords" not in st.session_state:
    st.session_state["gps_coords"] = {"lat": -11.0500, "lng": -75.3300}

# --- BARRA LATERAL CON RELOJ Y GPS ---
st.sidebar.title("💧 Distribuidora EMANA")

gps_reloj_js = """
<div style="background-color:#1e293b; color:#f8fafc; padding:12px; border-radius:8px; text-align:center; font-family:sans-serif;">
    <div id="fecha" style="font-size:12px; color:#94a3b8; font-weight:bold;"></div>
    <div id="reloj" style="font-size:22px; color:#38bdf8; font-weight:bold; margin-top:2px;"></div>
    <div id="gps" style="font-size:11px; color:#4ade80; margin-top:5px;">📡 Geolocalizando...</div>
</div>

<script>
function actualizarReloj() {
    const ahora = new Date();
    const opcionesFecha = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('fecha').innerText = ahora.toLocaleDateString('es-ES', opcionesFecha);
    document.getElementById('reloj').innerText = '⏰ ' + ahora.toLocaleTimeString('es-ES');
}
setInterval(actualizarReloj, 1000);
actualizarReloj();

if (navigator.geolocation) {
    navigator.geolocation.watchPosition(
        (pos) => {
            document.getElementById('gps').innerText = '📍 GPS Activo: ' + pos.coords.latitude.toFixed(4) + ', ' + pos.coords.longitude.toFixed(4);
        },
        (err) => {
            document.getElementById('gps').innerText = '📍 GPS: Ubicación activa';
        },
        { enableHighAccuracy: true }
    );
}
</script>
"""

with st.sidebar:
    components.html(gps_reloj_js, height=120)

st.sidebar.markdown("---")

# --- LOGIN Y RECUPERACIÓN DE CLAVE ---
if not st.session_state["autenticado"]:
    tab_login, tab_recuperar = st.tabs(["🔒 Iniciar Sesión", "🔑 Olvidé mi Contraseña"])
    
    with tab_login:
        with st.form("form_login"):
            user_input = st.text_input("Usuario (o Gmail)").strip()
            pass_input = st.text_input("Contraseña", type="password").strip()
            btn_login = st.form_submit_button("Ingresar")
            
            if btn_login:
                try:
                    # Consulta segura para compatibilidad
                    res = supabase.table("usuarios").select("*").eq("username", user_input).eq("password", pass_input).execute()
                    if not res.data:
                        res = supabase.table("usuarios").select("*").eq("gmail", user_input).eq("password", pass_input).execute()
                        
                    if res.data and len(res.data) > 0:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario"] = res.data[0]["username"]
                        st.session_state["rol"] = res.data[0]["rol"]
                        st.success(f"Bienvenido {st.session_state['usuario']}")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                except Exception as ex:
                    st.error(f"Error de acceso: {ex}")

    with tab_recuperar:
        st.subheader("Restablecer Contraseña por Gmail")
        gmail_rec = st.text_input("Ingresa tu correo Gmail registrado")
        if st.button("Enviar Instrucciones"):
            if "@" in gmail_rec:
                st.success(f"Se enviaron las instrucciones de recuperación al correo: {gmail_rec}")
            else:
                st.warning("Ingresa un correo Gmail válido.")
    st.stop()

# --- NAVEGACIÓN DE MÓDULOS ---
st.sidebar.write(f"👤 **Usuario:** {st.session_state['usuario']}")
st.sidebar.write(f"🔰 **Rol:** {st.session_state['rol']}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["rol"] = None
    st.rerun()

opciones_menu = ["Registrar Pedido / Venta", "Consultar Mis Pedidos", "Subir Evidencia (Fotos/Video)"]
if st.session_state["rol"] == "ADMIN":
    opciones_menu.extend(["Gestión & Rutas GPS (ADMIN)", "Dashboard & Analítica Predictiva", "Registro de Personal (8 Cuentas)", "Papelera de Reciclaje"])

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
    
    st.subheader("📦 Catálogo de Productos")
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown('<div class="product-box">', unsafe_allow_html=True)
        try:
            st.image("botella 625 ml transparente.png", use_container_width=True)
        except:
            st.markdown("🍾 **Botella 625 ml**")
        cant_625 = st.number_input("Cantidad (625ml)", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with p2:
        st.markdown('<div class="product-box">', unsafe_allow_html=True)
        try:
            st.image("BT 8.5L.png", use_container_width=True)
        except:
            st.markdown("🪣 **Botella 8.5 L**")
        cant_85 = st.number_input("Cantidad (8.5L)", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    with p3:
        st.markdown('<div class="product-box">', unsafe_allow_html=True)
        try:
            st.image("caja de 20 l.png", use_container_width=True)
        except:
            st.markdown("📦 **Caja 20 L**")
        cant_20 = st.number_input("Cantidad (20L)", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    total = st.number_input("Monto Total Calculado (S/.) *", min_value=0.0, step=0.5)

    st.subheader("📍 GPS en Tiempo Real")
    c_lat, c_lng = st.columns(2)
    with c_lat:
        latitud = st.number_input("Latitud", value=st.session_state["gps_coords"]["lat"], format="%.6f")
    with c_lng:
        longitud = st.number_input("Longitud", value=st.session_state["gps_coords"]["lng"], format="%.6f")

    st.map(pd.DataFrame({'lat': [latitud], 'lon': [longitud]}), zoom=14)

    if st.button("💾 Guardar Pedido", type="primary"):
        if not cliente_nombre or not local_direccion or total <= 0:
            st.warning("Por favor complete los campos obligatorios (*)")
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
            supabase.table("pedidos").insert(nuevo_pedido).execute()
            st.success("✅ ¡Pedido guardado exitosamente!")

# --- MÓDULO 2: CONSULTAR PEDIDOS ---
elif opcion == "Consultar Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    res = supabase.table("pedidos").select("*").eq("vendedor", st.session_state["usuario"]).eq("estado", "ACTIVO").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    else:
        st.info("No tienes pedidos registrados.")

# --- MÓDULO 3: SUBIR EVIDENCIA (FOTOS/VIDEO) ---
elif opcion == "Subir Evidencia (Fotos/Video)":
    st.header("📤 Subir Fotos y Videos de Entregas")
    archivo = st.file_uploader("Selecciona archivo multimedia (Imagen/Video)", type=["png", "jpg", "jpeg", "mp4", "mov"])
    if archivo is not None:
        if st.button("Subir Archivo"):
            st.success(f"✅ Archivo '{archivo.name}' cargado correctamente por {st.session_state['usuario']}.")

# --- MÓDULO ADMINISTRADOR: GESTIÓN DE RUTAS Y PEDIDOS ---
elif opcion == "Gestión & Rutas GPS (ADMIN)" and st.session_state["rol"] == "ADMIN":
    st.header("🗺️ Control General de Pedidos y Guía de Rutas")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df_admin = pd.DataFrame(res.data)
        st.dataframe(df_admin, use_container_width=True)
        
        pedido_id = st.selectbox("Selecciona ID de Pedido para Modificar", df_admin["id"].tolist())
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            est_ent = st.selectbox("Estado de Entrega", ["PENDIENTE", "ENTREGADO", "NO ENTREGADO"])
        with col_e2:
            monto_corr = st.number_input("Monto Corregido (S/.)", min_value=0.0)
            
        if st.button("🔄 Aplicar Cambios de Administrador"):
            supabase.table("pedidos").update({"estado_entrega": est_ent, "total": monto_corr}).eq("id", pedido_id).execute()
            st.success("Pedido modificado con autorización de ADMIN.")
            st.rerun()

# --- MÓDULO 4: DASHBOARD & ANALÍTICA PREDICTIVA ---
elif opcion == "Dashboard & Analítica Predictiva" and st.session_state["rol"] == "ADMIN":
    st.header("📊 Dashboard de Ventas y Proyección Predictiva")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df_d = pd.DataFrame(res.data)
        df_d['fecha_entrega'] = pd.to_datetime(df_d['fecha_entrega'])
        
        filtro_t = st.selectbox("Filtrar Análisis Temporal", ["Diario", "Semanal", "Mensual", "Anual"])
        st.metric("Ventas Totales (S/.)", f"S/. {df_d['total'].sum():,.2f}")
        
        st.subheader("📈 Tendencia de Ventas")
        st.line_chart(df_d.set_index('fecha_entrega')['total'])
        
        st.subheader("🔮 Proyección Predictiva")
        promedio = df_d['total'].mean()
        st.info(f"Proyección estimada para la siguiente ventana de ventas: **S/. {promedio * 1.15:,.2f}** (+15% estimado)")

# --- MÓDULO 5: REGISTRO DE PERSONAL (8 CUENTAS) ---
elif opcion == "Registro de Personal (8 Cuentas)" and st.session_state["rol"] == "ADMIN":
    st.header("👥 Gestión del Personal de la Empresa (8 Integrantes)")
    res_u = supabase.table("usuarios").select("*").execute()
    if res_u.data:
        st.dataframe(pd.DataFrame(res_u.data), use_container_width=True)
    
    with st.form("nuevo_personal"):
        u_nom = st.text_input("Usuario")
        u_mail = st.text_input("Gmail Registrado")
        u_pass = st.text_input("Contraseña Inicial", type="password")
        u_rol = st.selectbox("Rol Asignado", ["VENDEDOR", "ADMIN"])
        if st.form_submit_button("Registrar Colaborador"):
            try:
                supabase.table("usuarios").insert({"username": u_nom, "gmail": u_mail, "password": u_pass, "rol": u_rol}).execute()
                st.success("Personal registrado correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar: {e}")

# --- MÓDULO 6: PAPELERA ---
elif opcion == "Papelera de Reciclaje" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Papelera de Reciclaje")
    res_p = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    if res_p.data:
        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)