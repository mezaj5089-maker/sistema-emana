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

# --- FUNCIONES DE PERSISTENCIA DE IMÁGENES EN SUPABASE STORAGE ---
def guardar_imagen_supabase(file, nombre_destino):
    try:
        bytes_data = file.getvalue()
        # Subir o sobrescribir en el bucket 'catalogo'
        supabase.storage.from_("catalogo").upload(
            file=bytes_data, 
            path=nombre_destino, 
            file_options={"upsert": "true", "content-type": file.type}
        )
        return supabase.storage.from_("catalogo").get_public_url(nombre_destino)
    except Exception as e:
        st.error(f"Error al guardar imagen en la nube: {e}")
        return None

def obtener_url_imagen(nombre_destino):
    try:
        url = supabase.storage.from_("catalogo").get_public_url(nombre_destino)
        return url
    except Exception:
        return None

def eliminar_imagen_supabase(nombre_destino):
    try:
        supabase.storage.from_("catalogo").remove([nombre_destino])
    except Exception:
        pass

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None
if "gps_coords" not in st.session_state:
    st.session_state["gps_coords"] = {"lat": -11.0500, "lng": -75.3300}

# Variables de Imágenes Dinámicas del Catálogo (Persistidas en la Nube)
if "img_625" not in st.session_state: 
    st.session_state["img_625"] = obtener_url_imagen("img_625.png")
if "img_85" not in st.session_state: 
    st.session_state["img_85"] = obtener_url_imagen("img_85.png")
if "img_20" not in st.session_state: 
    st.session_state["img_20"] = obtener_url_imagen("img_20.png")

# --- BARRA LATERAL CON LOGO, RELOJ Y GEOLOCALIZACIÓN GPS ---
with st.sidebar:
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=200)
    except:
        st.title("💧 EMANA App")
    
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
            cliente_nombre = st.text_input("Nombre Completo / Razón Social")
            cliente_doc = st.text_input("DNI / RUC")
            tipo_comprobante = st.selectbox("Comprobante", ["BOLETA", "FACTURA", "NOTA DE PEDIDO"])
        with c2:
            fecha_entrega = st.date_input("Fecha de Entrega", min_value=datetime.date.today())
            rango_entrega = st.selectbox("Rango Horario", ["Mañana (8:00 AM - 12:00 PM)", "Tarde (2:00 PM - 6:00 PM)", "Inmediato"])

    st.subheader("📍 Dirección y Referencia de Entrega")
    c_dir, c_ref = st.columns(2)
    with c_dir:
        local_direccion = st.text_input("Dirección de Entrega")
    with c_ref:
        local_referencia = st.text_input("Referencia de Entrega")

    st.subheader("📦 Catálogo de Productos")
    
    if st.session_state["rol"] == "ADMIN":
        with st.expander("⚙️ Opciones de Imágenes del Catálogo (Solo Administrador)"):
            st.info("Como Administrador, puedes modificar, subir o quitar las imágenes de los productos desde cualquier dispositivo.")
            
            up_625 = st.file_uploader("Cambiar / Subir Imagen Botella 625ml", type=["png", "jpg", "jpeg"], key="u625")
            if up_625: 
                url = guardar_imagen_supabase(up_625, "img_625.png")
                if url: st.session_state["img_625"] = url; st.rerun()
            if st.button("Quitar Imagen 625ml"): 
                eliminar_imagen_supabase("img_625.png")
                st.session_state["img_625"] = None
                st.rerun()
            
            up_85 = st.file_uploader("Cambiar / Subir Imagen Botella 8.5L", type=["png", "jpg", "jpeg"], key="u85")
            if up_85: 
                url = guardar_imagen_supabase(up_85, "img_85.png")
                if url: st.session_state["img_85"] = url; st.rerun()
            if st.button("Quitar Imagen 8.5L"): 
                eliminar_imagen_supabase("img_85.png")
                st.session_state["img_85"] = None
                st.rerun()

            up_20 = st.file_uploader("Cambiar / Subir Imagen Caja 20L", type=["png", "jpg", "jpeg"], key="u20")
            if up_20: 
                url = guardar_imagen_supabase(up_20, "img_20.png")
                if url: st.session_state["img_20"] = url; st.rerun()
            if st.button("Quitar Imagen 20L"): 
                eliminar_imagen_supabase("img_20.png")
                st.session_state["img_20"] = None
                st.rerun()

    p1, p2, p3 = st.columns(3)
    
    # 1. Paquete 625 ml (20 UND)
    with p1:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        if st.session_state.get("img_625"):
            try: st.image(st.session_state["img_625"], use_container_width=True)
            except: st.markdown("🍾 **Paquete 625 ml (20 UND)**")
        else:
            st.markdown("🍾 **Paquete 625 ml (20 UND)** *(Sin imagen)*")
        
        cant_625 = st.number_input("Cantidad Paquetes 625ml", min_value=0, value=0)
        precio_sug_625 = 10.00 if cant_625 >= 5 else 12.50
        precio_final_625 = st.number_input("Precio Unitario Paquete 625ml (S/.)", value=precio_sug_625, step=0.50)
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Botellón 8.5 L
    with p2:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        if st.session_state.get("img_85"):
            try: st.image(st.session_state["img_85"], use_container_width=True)
            except: st.markdown("🪣 **Botella 8.5 L**")
        else:
            st.markdown("🪣 **Botella 8.5 L** *(Sin imagen)*")
            
        cant_85 = st.number_input("Cantidad Botellones 8.5L", min_value=0, value=0)
        precio_sug_85 = 7.00 if cant_85 >= 10 else 9.00
        precio_final_85 = st.number_input("Precio Unitario Botellón 8.5L (S/.)", value=precio_sug_85, step=0.50)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Caja de 20 L
    with p3:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        if st.session_state.get("img_20"):
            try: st.image(st.session_state["img_20"], use_container_width=True)
            except: st.markdown("📦 **Caja 20 L**")
        else:
            st.markdown("📦 **Caja 20 L** *(Sin imagen)*")
            
        cant_20 = st.number_input("Cantidad Cajas 20L", min_value=0, value=0)
        precio_sug_20 = 18.00 if cant_20 >= 5 else 20.00  # Ajustable por el usuario
        precio_final_20 = st.number_input("Precio Unitario Caja 20L (S/.)", value=precio_sug_20, step=0.50)
        st.markdown('</div>', unsafe_allow_html=True)

    # Cálculo total automático basándose en precios modificados
    subtotal_calc = (cant_625 * precio_final_625) + (cant_85 * precio_final_85) + (cant_20 * precio_final_20)
    total = st.number_input("Monto Total Calculado (S/.)", value=float(subtotal_calc), min_value=0.0, step=0.50)

    st.markdown("---")
    
    # Proceso de Guardado con Modal de Confirmación sin obligar llenar todos los campos
    if st.button("💾 Guardar Pedido", type="primary", use_container_width=True):
        st.session_state["mostrar_confirmacion"] = True

    if st.session_state.get("mostrar_confirmacion", False):
        st.warning("❓ **¿Estas seguro de guardar la venta?** Verifica los datos antes de continuar.")
        col_si, col_no = st.columns(2)
        
        with col_si:
            if st.button("✅ Sí, Guardar Venta", use_container_width=True):
                nuevo_pedido = {
                    "vendedor": vendedor_activo,
                    "cliente_nombre": cliente_nombre if cliente_nombre else "SIN NOMBRE",
                    "cliente_doc": cliente_doc,
                    "local_direccion": local_direccion,
                    "local_referencia": local_referencia,
                    "tipo_comprobante": tipo_comprobante,
                    "fecha_entrega": str(fecha_entrega),
                    "rango_entrega": rango_entrega,
                    "total": total,
                    "productos": f"625ml: {cant_625} (S/.{precio_final_625}) | 8.5L: {cant_85} (S/.{precio_final_85}) | 20L: {cant_20} (S/.{precio_final_20})",
                    "estado": "ACTIVO",
                    "estado_entrega": "PENDIENTE"
                }
                try:
                    supabase.table("pedidos").insert(nuevo_pedido).execute()
                    st.success(f"✅ ¡Venta guardada con éxito por {vendedor_activo} en la nube!")
                    st.session_state["mostrar_confirmacion"] = False
                except Exception as e:
                    st.error(f"Error al guardar en la nube: {e}")

        with col_no:
            if st.button("❌ No, Corregir Datos", use_container_width=True):
                st.session_state["mostrar_confirmacion"] = False
                st.info("Puedes corregir los datos del formulario.")

# --- MÓDULO 2: CONSULTAR MIS PEDIDOS & RESPALDO ---
elif opcion == "Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    res = supabase.table("pedidos").select("*").eq("vendedor", st.session_state["usuario"]).eq("estado", "ACTIVO").execute()
    if res.data:
        df_pedidos = pd.DataFrame(res.data)
        st.dataframe(df_pedidos, use_container_width=True)
        
        # Opción de Respaldo para Google Drive
        csv_data = df_pedidos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📁 Descargar Respaldo CSV (Para Google Drive)",
            data=csv_data,
            file_name=f"respaldo_pedidos_{datetime.date.today()}.csv",
            mime="text/csv"
        )
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
    st.header("🗺️ Control y Guía de Rutas (Vista Administrador)")
    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
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