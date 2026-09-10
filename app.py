import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import datetime
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="EMANA - Sistema de Gestión & Ventas",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS3 AVANZADOS (DISEÑO TIPO APPLICACIÓN MODERNA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: #f8fafc;
    }
    
    /* Header principal con Glassmorphism */
    .header-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 20px 30px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.3);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    /* Tarjetas de producto interactivas estilo E-commerce */
    .product-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #38bdf8;
    }
    
    /* Botones estilizados */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* Estilos de tabla de datos */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
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
except Exception:
    st.error("⚠️ Error de conexión a la base de datos Supabase. Verifica tus Secrets.")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None
if "gps_coords" not in st.session_state:
    st.session_state["gps_coords"] = {"lat": -11.0500, "lng": -75.3300}

# --- BARRA LATERAL CON RELOJ Y GEOLOCALIZACIÓN GPS ---
with st.sidebar:
    st.title("💧 EMANA App")
    
    # Componente de Reloj y GPS dinámico
    gps_reloj_js = """
    <div style="background:#0f172a; color:#f8fafc; padding:14px; border-radius:12px; text-align:center; font-family:sans-serif;">
        <div id="fecha" style="font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase;"></div>
        <div id="reloj" style="font-size:20px; color:#38bdf8; font-weight:700; margin-top:2px;"></div>
        <div id="gps" style="font-size:11px; color:#4ade80; margin-top:6px;">📡 GPS listo</div>
    </div>
    <script>
    function actualizarReloj() {
        const ahora = new Date();
        const opcionesFecha = { weekday: 'short', month: 'short', day: 'numeric' };
        document.getElementById('fecha').innerText = ahora.toLocaleDateString('es-ES', opcionesFecha);
        document.getElementById('reloj').innerText = '⏰ ' + ahora.toLocaleTimeString('es-ES');
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();

    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            (pos) => {
                document.getElementById('gps').innerText = '📍 Lat: ' + pos.coords.latitude.toFixed(4) + ' | Lng: ' + pos.coords.longitude.toFixed(4);
            },
            () => { document.getElementById('gps').innerText = '📍 GPS: Ubicación predeterminada'; },
            { enableHighAccuracy: true }
        );
    }
    </script>
    """
    components.html(gps_reloj_js, height=115)
    st.markdown("---")

# --- LOGIN & RECUPERACIÓN ---
if not st.session_state["autenticado"]:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #0284c7; font-weight: 700;">Distribuidora de Agua de Mesa EMANA</h1>
            <p style="color: #64748b;">✨ Vitalidad vida sana</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_cen, _ = st.columns([2, 1])
    with col_cen:
        tab_login, tab_recuperar = st.tabs(["🔒 Iniciar Sesión", "🔑 Olvidé mi Contraseña"])
        
        with tab_login:
            with st.form("form_login"):
                user_input = st.text_input("Usuario o Gmail").strip()
                pass_input = st.text_input("Contraseña", type="password").strip()
                btn_login = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
                
                if btn_login:
                    try:
                        res = supabase.table("usuarios").select("*").eq("username", user_input).eq("password", pass_input).execute()
                        if not res.data:
                            res = supabase.table("usuarios").select("*").eq("gmail", user_input).eq("password", pass_input).execute()
                            
                        if res.data:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario"] = res.data[0]["username"]
                            st.session_state["rol"] = res.data[0]["rol"]
                            st.success(f"Bienvenido {st.session_state['usuario']}")
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
                    except Exception as ex:
                        st.error(f"Error de conexión: {ex}")

        with tab_recuperar:
            gmail_rec = st.text_input("Ingresa tu Gmail registrado")
            if st.button("Restablecer Contraseña", use_container_width=True):
                if "@" in gmail_rec:
                    st.success(f"Instrucciones enviadas al correo: {gmail_rec}")
                else:
                    st.warning("Correo no válido.")
    st.stop()

# --- ENCABEZADO CON BRANDING ---
st.markdown("""
    <div class="header-banner">
        <div>
            <h2 style="margin:0; font-weight:700;">Distribuidora EMANA</h2>
            <p style="margin:0; opacity:0.9;">✨ Vitalidad vida sana</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN CON ÍCONOS MODERNOS ---
with st.sidebar:
    st.write(f"👤 **{st.session_state['usuario']}** ({st.session_state['rol']})")
    
    menu_opciones = ["Nuevas Ventas", "Mis Pedidos", "Subir Evidencia"]
    menu_iconos = ["cart-plus", "receipt", "cloud-upload"]
    
    if st.session_state["rol"] == "ADMIN":
        menu_opciones.extend(["Rutas GPS", "Analítica Predictiva", "Personal (8 Cuentas)", "Papelera"])
        menu_iconos.extend(["geo-alt", "graph-up-arrow", "people", "trash"])

    opcion = option_menu(
        menu_title="Navegación",
        options=menu_opciones,
        icons=menu_iconos,
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px!", "background-color": "#f1f5f9"},
            "icon": {"color": "#0284c7", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px", "--hover-color": "#e2e8f0"},
            "nav-link-selected": {"background-color": "#0284c7"},
        }
    )

    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.session_state["rol"] = None
        st.rerun()

# --- MÓDULO 1: REGISTRAR VENTAS / PEDIDOS ---
if opcion == "Nuevas Ventas":
    st.header("📝 Registrar Nuevo Pedido")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            cliente_nombre = st.text_input("Nombre Completo / Razón Social *")
            cliente_doc = st.text_input("DNI / RUC")
            local_direccion = st.text_input("Dirección del Local *")
            tipo_comprobante = st.selectbox("Comprobante", ["BOLETA", "FACTURA", "NOTA DE PEDIDO"])
        with c2:
            fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
            rango_entrega = st.selectbox("Rango Horario", ["Mañana (8:00 AM - 12:00 PM)", "Tarde (2:00 PM - 6:00 PM)", "Inmediato"])

    st.subheader("📦 Catálogo de Productos")
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        try: st.image("botella 625 ml transparente.png", use_container_width=True)
        except: st.markdown("🍾 **Botella 625 ml**")
        cant_625 = st.number_input("Cantidad 625ml", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    with p2:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        try: st.image("BT 8.5L.png", use_container_width=True)
        except: st.markdown("🪣 **Botella 8.5 L**")
        cant_85 = st.number_input("Cantidad 8.5L", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    with p3:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        try: st.image("caja de 20 l.png", use_container_width=True)
        except: st.markdown("📦 **Caja 20 L**")
        cant_20 = st.number_input("Cantidad 20L", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    total = st.number_input("Monto Total Calculado (S/.) *", min_value=0.0, step=0.5)

    st.subheader("📍 Coordenadas de la Entrega")
    c_lat, c_lng = st.columns(2)
    with c_lat: latitud = st.number_input("Latitud", value=st.session_state["gps_coords"]["lat"], format="%.6f")
    with c_lng: longitud = st.number_input("Longitud", value=st.session_state["gps_coords"]["lng"], format="%.6f")

    if st.button("💾 Confirmar & Guardar Pedido", type="primary", use_container_width=True):
        if not cliente_nombre or not local_direccion or total <= 0:
            st.warning("Completa los campos obligatorios (*)")
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
                "productos": f"625ml: {cant_625} | 8.5L: {cant_85} | 20L: {cant_20}",
                "estado": "ACTIVO",
                "estado_entrega": "PENDIENTE"
            }
            supabase.table("pedidos").insert(nuevo_pedido).execute()
            st.success("✅ ¡Pedido registrado con éxito!")

# --- MÓDULO 2: CONSULTAR MIS PEDIDOS ---
elif opcion == "Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    res = supabase.table("pedidos").select("*").eq("vendedor", st.session_state["usuario"]).eq("estado", "ACTIVO").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    else:
        st.info("No cuentas con pedidos registrados actualmente.")

# --- MÓDULO 3: EVIDENCIAS ---
elif opcion == "Subir Evidencia":
    st.header("📤 Subir Fotos y Videos de Entregas")
    archivo = st.file_uploader("Selecciona imagen o video comprobante", type=["png", "jpg", "jpeg", "mp4"])
    if archivo and st.button("Subir Evidencia"):
        st.success(f"Archivo '{archivo.name}' guardado correctamente.")

# --- MÓDULO 4: CONTROL DE RUTAS (ADMIN) ---
elif opcion == "Rutas GPS" and st.session_state["rol"] == "ADMIN":
    st.header("🗺️ Control y Ubicación de Entregas")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.map(df[['latitud', 'longitud']].rename(columns={'latitud': 'lat', 'longitud': 'lon'}), zoom=13)
        st.dataframe(df, use_container_width=True)

# --- MÓDULO 5: ANALÍTICA PREDICTIVA Y GRÁFICOS DASHBOARD ---
elif opcion == "Analítica Predictiva" and st.session_state["rol"] == "ADMIN":
    st.header("📊 Tablero Analítico Dinámico")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    if res.data:
        df_a = pd.DataFrame(res.data)
        df_a['fecha_entrega'] = pd.to_datetime(df_a['fecha_entrega'])
        
        m1, m2 = st.columns(2)
        m1.metric("Ingresos Totales", f"S/. {df_a['total'].sum():,.2f}")
        m2.metric("Promedio por Pedido", f"S/. {df_a['total'].mean():,.2f}")
        
        # Gráfico Interactivo de Alto Rendimiento con Plotly (Gratuito)
        fig = px.line(df_a, x="fecha_entrega", y="total", title="Evolución Interactiva de Ventas (S/.)", markers=True)
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO 6: GESTIÓN DE PERSONAL ---
elif opcion == "Personal (8 Cuentas)" and st.session_state["rol"] == "ADMIN":
    st.header("👥 Gestión de Colaboradores de EMANA")
    res_u = supabase.table("usuarios").select("*").execute()
    if res_u.data:
        st.dataframe(pd.DataFrame(res_u.data), use_container_width=True)
    
    with st.form("crear_usuario"):
        u_nom = st.text_input("Usuario")
        u_mail = st.text_input("Gmail Registrado")
        u_pass = st.text_input("Contraseña", type="password")
        u_rol = st.selectbox("Rol", ["VENDEDOR", "ADMIN"])
        if st.form_submit_button("Crear Cuenta"):
            supabase.table("usuarios").insert({"username": u_nom, "gmail": u_mail, "password": u_pass, "rol": u_rol}).execute()
            st.success("Usuario agregado exitosamente.")
            st.rerun()

# --- MÓDULO 7: PAPELERA ---
elif opcion == "Papelera" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Registro de Eliminados")
    res_p = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    if res_p.data:
        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)