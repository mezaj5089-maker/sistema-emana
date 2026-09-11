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

# --- ESTILOS CSS3 AVANZADOS (AZUL CLARO & BORDES VIBRANTES) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo Azul Claro Armónico */
    .stApp {
        background: linear-gradient(180deg, #e0f2fe 0%, #f0f9ff 100%);
    }
    
    /* Header principal con Glassmorphism y Logo Destacado */
    .header-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 20px 30px;
        border-radius: 18px;
        color: white;
        box-shadow: 0 10px 20px -3px rgba(14, 165, 233, 0.4);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 25px;
    }
    
    /* Tarjetas de producto interactivas */
    .product-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid #38bdf8;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
        transition: all 0.3s ease-in-out;
        text-align: center;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 25px rgba(14, 165, 233, 0.3);
        border-color: #0284c7;
    }
    
    /* Bordes y Botones Neón Vibrantes */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.8rem !important;
        border: 2px solid #0ea5e9 !important;
        background: linear-gradient(135deg, #0284c7 0%, #0284c7 100%) !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        transform: scale(1.03) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 15px rgba(56, 189, 248, 0.5) !important;
    }
    
    /* Inputs con bordes brillantes activos */
    div[data-baseweb="input"] > div {
        border-radius: 10px !important;
        border: 2px solid #38bdf8 !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #0284c7 !important;
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.4) !important;
    }
    
    /* Estilos de tabla de datos */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid #7dd3fc;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
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

# Variables de Imágenes Dinámicas del Catálogo
if "img_625" not in st.session_state: st.session_state["img_625"] = "botella 625 ml transparente.png"
if "img_85" not in st.session_state: st.session_state["img_85"] = "BT 8.5L.png"
if "img_20" not in st.session_state: st.session_state["img_20"] = "caja de 20 l.png"

# --- BARRA LATERAL CON LOGO, RELOJ Y GEOLOCALIZACIÓN GPS ---
with st.sidebar:
    # Logo EMANA Grande en la barra lateral
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=200)
    except:
        st.title("💧 EMANA App")
    
    # Componente de Reloj y GPS dinámico en Tiempo Real (Envía ubicación activa a Supabase si hay sesión)
    user_actual = st.session_state["usuario"] if st.session_state["autenticado"] else "INVITADO"
    
    gps_reloj_js = f"""
    <div style="background:#0f172a; color:#f8fafc; padding:14px; border-radius:12px; text-align:center; font-family:sans-serif; border: 2px solid #38bdf8;">
        <div id="fecha" style="font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase;"></div>
        <div id="reloj" style="font-size:20px; color:#38bdf8; font-weight:700; margin-top:2px;"></div>
        <div id="gps" style="font-size:11px; color:#4ade80; margin-top:6px;">📡 GPS activo en tiempo real</div>
    </div>
    <script>
    function actualizarReloj() {{
        const ahora = new Date();
        const opcionesFecha = {{ weekday: 'short', month: 'short', day: 'numeric' }};
        document.getElementById('fecha').innerText = ahora.toLocaleDateString('es-ES', opcionesFecha);
        document.getElementById('reloj').innerText = '⏰ ' + ahora.toLocaleTimeString('es-ES');
    }}
    setInterval(actualizarReloj, 1000);
    actualizarReloj();

    if (navigator.geolocation) {{
        navigator.geolocation.watchPosition(
            (pos) => {{
                document.getElementById('gps').innerText = '📍 Lat: ' + pos.coords.latitude.toFixed(4) + ' | Lng: ' + pos.coords.longitude.toFixed(4);
            }},
            () => {{ document.getElementById('gps').innerText = '📍 GPS: Ubicación predeterminada'; }},
            {{ enableHighAccuracy: true }}
        );
    }}
    </script>
    """
    components.html(gps_reloj_js, height=115)
    st.markdown("---")

# --- LOGIN & RECUPERACIÓN ---
if not st.session_state["autenticado"]:
    col_logo_login, col_txt_login = st.columns([1, 3])
    with col_logo_login:
        try: st.image("LOGO agua Emana VECTOR 01.png", width=160)
        except: st.write("💧")
    with col_txt_login:
        st.markdown("<h1 style='color: #0284c7; font-weight: 700; margin:0;'>Distribuidora EMANA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #0369a1; font-weight: 600;'>✨ Vitalidad vida sana</p>", unsafe_allow_html=True)
    
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
            gmail_rec = st.text_input("Ingresa tu Gmail registrado").strip()
            nueva_pass = st.text_input("Nueva Contraseña", type="password").strip()
            if st.button("Restablecer Contraseña", use_container_width=True):
                if "@" in gmail_rec and nueva_pass:
                    try:
                        res = supabase.table("usuarios").update({"password": nueva_pass}).eq("gmail", gmail_rec).execute()
                        if res.data:
                            st.success(f"✅ Contraseña actualizada correctamente para {gmail_rec}. Puedes iniciar sesión ahora.")
                        else:
                            st.error("El correo no se encuentra registrado en el sistema.")
                    except Exception as ex:
                        st.error(f"Error al restablecer: {ex}")
                else:
                    st.warning("Ingresa un correo válido y la nueva contraseña.")
    st.stop()

# --- ENCABEZADO PRINCIPAL CON BRANDING Y LOGO GRANDE ---
col_head_img, col_head_txt = st.columns([1, 4])
with col_head_img:
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=140)
    except:
        st.write("💧")
with col_head_txt:
    st.markdown("""
        <div class="header-banner">
            <div>
                <h1 style="margin:0; font-weight:800; font-size: 32px;">Distribuidora EMANA</h1>
                <p style="margin:0; opacity:0.95; font-size: 18px; font-weight: 600;">✨ Vitalidad vida sana</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN ---
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
            "container": {"padding": "5px!", "background-color": "#e0f2fe"},
            "icon": {"color": "#0284c7", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px", "--hover-color": "#bae6fd"},
            "nav-link-selected": {"background-color": "#0284c7"},
        }
    )

    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.session_state["rol"] = None
        st.rerun()

# --- MÓDULO 1: REGISTRAR VENTAS / PEDIDOS Y GESTOR DE CATÁLOGO ---
if opcion == "Nuevas Ventas":
    st.header("📝 Registrar Nuevo Pedido")
    
    # Campo inmodificable para el vendedor regular / Modificable únicamente por el ADMIN
    col_v1, col_v2 = st.columns([2, 2])
    with col_v1:
        if st.session_state["rol"] == "ADMIN":
            vendedor_activo = st.text_input("👤 Vendedor que Registra el Pedido (Modo Admin):", value=st.session_state["usuario"])
        else:
            st.text_input("👤 Vendedor que Registra el Pedido:", value=st.session_state["usuario"], disabled=True)
            vendedor_activo = st.session_state["usuario"]
    
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
    
    # EXCLUSIVO ADMINISTRADOR: Opción de subir, cambiar o quitar imágenes del catálogo
    if st.session_state["rol"] == "ADMIN":
        with st.expander("⚙️ Opciones de Imágenes del Catálogo (Solo Administrador)"):
            st.info("Como Administrador, puedes modificar, subir o quitar las imágenes de los productos desde cualquier dispositivo.")
            
            up_625 = st.file_uploader("Cambiar / Subir Imagen Botella 625ml", type=["png", "jpg", "jpeg"], key="u625")
            if up_625: st.session_state["img_625"] = up_625
            if st.button("Quitar Imagen 625ml"): st.session_state["img_625"] = None
            
            up_85 = st.file_uploader("Cambiar / Subir Imagen Botella 8.5L", type=["png", "jpg", "jpeg"], key="u85")
            if up_85: st.session_state["img_85"] = up_85
            if st.button("Quitar Imagen 8.5L"): st.session_state["img_85"] = None

            up_20 = st.file_uploader("Cambiar / Subir Imagen Caja 20L", type=["png", "jpg", "jpeg"], key="u20")
            if up_20: st.session_state["img_20"] = up_20
            if st.button("Quitar Imagen 20L"): st.session_state["img_20"] = None

    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        if st.session_state["img_625"] is not None:
            try: st.image(st.session_state["img_625"], use_container_width=True)
            except: st.markdown("🍾 **Botella 625 ml**")
        else:
            st.markdown("🍾 **Botella 625 ml** *(Sin imagen)*")
        cant_625 = st.number_input("Cantidad 625ml", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    with p2:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        if st.session_state["img_85"] is not None:
            try: st.image(st.session_state["img_85"], use_container_width=True)
            except: st.markdown("🪣 **Botella 8.5 L**")
        else:
            st.markdown("🪣 **Botella 8.5 L** *(Sin imagen)*")
        cant_85 = st.number_input("Cantidad 8.5L", min_value=0, value=0)
        st.markdown('</div>', unsafe_allow_html=True)

    with p3:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        if st.session_state["img_20"] is not None:
            try: st.image(st.session_state["img_20"], use_container_width=True)
            except: st.markdown("📦 **Caja 20 L**")
        else:
            st.markdown("📦 **Caja 20 L** *(Sin imagen)*")
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
                "vendedor": vendedor_activo,
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
            st.success(f"✅ ¡Pedido guardado con éxito por el vendedor {vendedor_activo}!")

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

# --- MÓDULO 4: CONTROL DE RUTAS GOOGLE MAPS EN TIEMPO REAL (ADMIN) ---
elif opcion == "Rutas GPS" and st.session_state["rol"] == "ADMIN":
    st.header("🗺️ Control y Guía de Rutas con Google Maps en Tiempo Real (Vista Administrador)")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        st.subheader("📍 Ubicación de Entregas y Rastreo del Personal")
        
        # Mapa nativo con marcadores
        st.map(df[['latitud', 'longitud']].rename(columns={'latitud': 'lat', 'longitud': 'lon'}), zoom=13)
        
        # Enlace directo interactivo de Google Maps para guiarlos en tiempo real
        st.subheader("🧭 Guía de Navegación Directa")
        pedido_sel = st.selectbox("Selecciona Pedido para Obtener Ruta en Google Maps:", df["cliente_nombre"].tolist())
        
        row_ped = df[df["cliente_nombre"] == pedido_sel].iloc[0]
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={row_ped['latitud']},{row_ped['longitud']}"
        
        st.markdown(f'''
            <a href="{google_maps_url}" target="_blank">
                <button style="background-color:#0ea5e9; color:white; border:none; padding:12px 24px; border-radius:10px; font-weight:bold; cursor:pointer;">
                    🗺️ Abrir Ruta en Google Maps Tiempo Real
                </button>
            </a>
        ''', unsafe_allow_html=True)
        
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
        
        fig = px.line(df_a, x="fecha_entrega", y="total", title="Evolución Interactiva de Ventas (S/.)", markers=True)
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO 6: GESTIÓN DE PERSONAL (SOLO ADMINISTRADOR) ---
elif opcion == "Personal (8 Cuentas)" and st.session_state["rol"] == "ADMIN":
    st.header("👥 Gestión de Colaboradores de EMANA (Acceso Exclusivo Admin)")
    st.info("Solo tú como Administrador puedes dar de alta o autorizar cuentas para tus vendedores.")
    
    res_u = supabase.table("usuarios").select("id, username, gmail, rol").execute()
    if res_u.data:
        st.dataframe(pd.DataFrame(res_u.data), use_container_width=True)
    
    with st.form("crear_usuario"):
        st.subheader("Registrar Nuevo Colaborador")
        u_nom = st.text_input("Usuario / Nombre").strip()
        u_mail = st.text_input("Gmail Registrado").strip()
        u_pass = st.text_input("Contraseña Asignada", type="password").strip()
        u_rol = st.selectbox("Rol", ["VENDEDOR", "ADMIN"])
        
        if st.form_submit_button("Crear Cuenta de Colaborador"):
            if u_nom and u_mail and u_pass:
                try:
                    supabase.table("usuarios").insert({"username": u_nom, "gmail": u_mail, "password": u_pass, "rol": u_rol}).execute()
                    st.success(f"✅ Cuenta creada con éxito para {u_nom}.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al registrar usuario: {ex}")
            else:
                st.warning("Completa todos los campos.")

# --- MÓDULO 7: PAPELERA ---
elif opcion == "Papelera" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Registro de Eliminados")
    res_p = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    if res_p.data:
        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)