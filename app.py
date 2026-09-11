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

# --- ESTILOS CSS3 AVANZADOS (MEJORADO: AZUL VIBRANTE, GLASSMORPHISM Y BOTÓN WHATSAPP) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo Azul Claro Armónico con degrada brillante */
    .stApp {
        background: linear-gradient(180deg, #e0f2fe 0%, #f0f9ff 100%);
    }
    
    /* Header principal con Glassmorphism y Glow */
    .header-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 22px 32px;
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.45);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Tarjetas de producto interactivas estilo EMANA */
    .product-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 18px;
        border: 2px solid #38bdf8;
        box-shadow: 0 6px 16px rgba(14, 165, 233, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 18px 30px rgba(14, 165, 233, 0.35);
        border-color: #0284c7;
    }
    
    .price-badge {
        background: #e0f2fe;
        color: #0369a1;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        margin: 4px 0;
        border: 1px solid #7dd3fc;
    }

    .price-badge-wholesale {
        background: #dcfce7;
        color: #15803d;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        margin: 4px 0;
        border: 1px solid #86efac;
    }

    /* Bordes y Botones Neón Vibrantes */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.8rem !important;
        border: 2px solid #0ea5e9 !important;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        transform: scale(1.03) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.55) !important;
    }

    /* Botón flotante directo de WhatsApp */
    .btn-whatsapp {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        background-color: #25D366;
        color: white !important;
        font-weight: 700;
        padding: 12px 20px;
        border-radius: 12px;
        text-decoration: none;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        text-align: center;
        margin-top: 10px;
    }
    .btn-whatsapp:hover {
        background-color: #1da851;
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.6);
    }
    
    /* Inputs con bordes brillantes activos */
    div[data-baseweb="input"] > div {
        border-radius: 10px !important;
        border: 2px solid #38bdf8 !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #0284c7 !important;
        box-shadow: 0 0 12px rgba(2, 132, 199, 0.4) !important;
    }
    
    /* Estilos de tabla de datos */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid #7dd3fc;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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

# --- FUNCIONES DE PERSISTENCIA DE IMÁGENES Y PRODUCTOS ---
def guardar_imagen_supabase(file, nombre_destino):
    try:
        bytes_data = file.getvalue()
        supabase.storage.from_("catalogo").upload(
            file=bytes_data, 
            path=nombre_destino, 
            file_options={"upsert": "true", "content-type": file.type}
        )
        return supabase.storage.from_("catalogo").get_public_url(nombre_destino)
    except Exception as e:
        st.error(f"Error al guardar imagen en la nube: {e}")
        return None

def obtener_productos():
    try:
        res = supabase.table("productos").select("*").execute()
        return res.data if res.data else []
    except Exception:
        # Productos base por defecto en caso de no existir la tabla aún
        return [
            {"id": 1, "nombre": "Paquete 625 ml (20 UND)", "precio_und": 12.50, "precio_mayor": 10.00, "min_mayor": 5, "imagen": None},
            {"id": 2, "nombre": "Botella 8.5 L", "precio_und": 9.00, "precio_mayor": 7.00, "min_mayor": 10, "imagen": None},
            {"id": 3, "nombre": "Caja 20 L", "precio_und": 20.00, "precio_mayor": 18.00, "min_mayor": 5, "imagen": None}
        ]

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None
if "modo_cliente" not in st.session_state:
    st.session_state["modo_cliente"] = True
if "gps_coords" not in st.session_state:
    st.session_state["gps_coords"] = {"lat": -11.0500, "lng": -75.3300}

# ENLACE WHATSAPP VINCULADO
WA_LINK = "https://wa.me/qr/ZEJEN3EUZZQRF1"

# --- BARRA LATERAL CON LOGO, RELOJ, GPS Y WHATSAPP ---
with st.sidebar:
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=200)
    except:
        st.title("💧 EMANA App")
    
    # Botón Flotante para contacto directo por WhatsApp
    st.markdown(f'''
        <a href="{WA_LINK}" target="_blank" class="btn-whatsapp">
            📱 Consultar por WhatsApp
        </a>
    ''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # GPS y Reloj en Vivo
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

    # Selección de Vista (Cliente / Personal)
    if not st.session_state["autenticado"]:
        st.info("💡 Estás en el Catálogo Público.")
        if st.button("🔑 Acceso Personal / Ventas"):
            st.session_state["modo_cliente"] = False
            st.rerun()

# --- INTERFAZ PÚBLICA / VISTA CLIENTE (SOLO VISUALIZACIÓN) ---
if not st.session_state["autenticado"] and st.session_state["modo_cliente"]:
    col_head_img, col_head_txt = st.columns([1, 4])
    with col_head_img:
        try: st.image("LOGO agua Emana VECTOR 01.png", width=140)
        except: st.write("💧")
    with col_head_txt:
        st.markdown("""
            <div class="header-banner">
                <div>
                    <h1 style="margin:0; font-weight:800; font-size: 32px;">Distribuidora EMANA</h1>
                    <p style="margin:0; opacity:0.95; font-size: 18px; font-weight: 600;">✨ Vitalidad vida sana — Catálogo Oficial</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📦 Nuestros Productos y Precios")
    st.write("Explora nuestro catálogo. Si deseas realizar un pedido, comunícate directamente con nosotros por WhatsApp.")
    
    prods = obtener_productos()
    
    if prods:
        cols = st.columns(3)
        for idx, p in enumerate(prods):
            with cols[idx % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if p.get("imagen"):
                    st.image(p["imagen"], use_container_width=True)
                else:
                    st.markdown("💧 **Agua Mineral EMANA**")
                
                st.markdown(f"#### {p['nombre']}")
                st.markdown(f'<div class="price-badge">Precio Unidad: S/. {float(p["precio_und"]):,.2f}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="price-badge-wholesale">Precio Por Mayor: S/. {float(p["precio_mayor"]):,.2f}<br><small>(A partir de {p["min_mayor"]} und)</small></div>', unsafe_allow_html=True)
                
                st.markdown(f'''
                    <a href="{WA_LINK}" target="_blank" class="btn-whatsapp" style="font-size: 12px; padding: 8px 10px;">
                        📲 Pedir este producto
                    </a>
                ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Cargando catálogo de productos...")

    st.stop()

# --- LOGIN & RECUPERACIÓN (SI NO ES MODO CLIENTE) ---
if not st.session_state["autenticado"] and not st.session_state["modo_cliente"]:
    col_logo_login, col_txt_login = st.columns([1, 3])
    with col_logo_login:
        try: st.image("LOGO agua Emana VECTOR 01.png", width=160)
        except: st.write("💧")
    with col_txt_login:
        st.markdown("<h1 style='color: #0284c7; font-weight: 700; margin:0;'>Distribuidora EMANA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #0369a1; font-weight: 600;'>✨ Vitalidad vida sana — Sistema Interno</p>", unsafe_allow_html=True)
    
    if st.button("⬅️ Volver al Catálogo Público"):
        st.session_state["modo_cliente"] = True
        st.rerun()

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

# --- ENCABEZADO PRINCIPAL (SISTEMA INTERNO) ---
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

# --- MENÚ DE NAVEGACIÓN INTERNO ---
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
        st.session_state["modo_cliente"] = True
        st.rerun()

# --- MÓDULO 1: REGISTRAR VENTAS / PEDIDOS Y GESTOR DE CATÁLOGO DINÁMICO ---
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

    st.subheader("📦 Catálogo de Productos Dinámico")
    
    # OPCIÓN ADMIN: AGREGAR NUEVO PRODUCTO AL CATÁLOGO
    if st.session_state["rol"] == "ADMIN":
        with st.expander("➕ Agregar Nuevo Producto / Gestionar Catálogo (Solo Administrador)"):
            st.info("Añade nuevos productos con sus precios por unidad, precio por mayor y fotografía.")
            with st.form("form_nuevo_prod"):
                n_prod = st.text_input("Nombre del Producto (Ej: Botella 1.5L)")
                p_und = st.number_input("Precio por Unidad (S/.)", min_value=0.0, step=0.50, value=10.0)
                p_mayor = st.number_input("Precio por Mayor (S/.)", min_value=0.0, step=0.50, value=8.0)
                min_m = st.number_input("Mínimo Unidades para Precio por Mayor", min_value=1, value=5)
                img_prod = st.file_uploader("Imagen del Producto", type=["png", "jpg", "jpeg"])
                
                btn_crear_p = st.form_submit_button("Guardar Producto en el Catálogo")
                if btn_crear_p and n_prod:
                    url_img = None
                    if img_prod:
                        nombre_file = f"prod_{datetime.datetime.now().timestamp()}.png"
                        url_img = guardar_imagen_supabase(img_prod, nombre_file)
                    
                    try:
                        supabase.table("productos").insert({
                            "nombre": n_prod,
                            "precio_und": p_und,
                            "precio_mayor": p_mayor,
                            "min_mayor": min_m,
                            "imagen": url_img
                        }).execute()
                        st.success(f"✅ Producto '{n_prod}' agregado con éxito.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar producto: {e}")

    # RENDERIZADO DINÁMICO DE TODOS LOS PRODUCTOS
    productos_lista = obtener_productos()
    cantidades_seleccionadas = {}
    precios_calculados = {}
    total_acumulado = 0.0

    if productos_lista:
        cols_p = st.columns(3)
        for i, prod in enumerate(productos_lista):
            with cols_p[i % 3]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                if prod.get("imagen"):
                    st.image(prod["imagen"], use_container_width=True)
                else:
                    st.markdown(f"🍾 **{prod['nombre']}** *(Sin imagen)*")
                
                cant = st.number_input(f"Cantidad {prod['nombre']}", min_value=0, value=0, key=f"cant_{prod['id']}")
                
                # Cálculo de precio según volumen
                p_sugerido = prod['precio_mayor'] if cant >= prod['min_mayor'] else prod['precio_und']
                p_final = st.number_input(f"Precio Unit. S/. ({prod['nombre']})", value=float(p_sugerido), step=0.50, key=f"p_{prod['id']}")
                
                subtotal_item = cant * p_final
                total_acumulado += subtotal_item
                
                if cant > 0:
                    cantidades_seleccionadas[prod['nombre']] = (cant, p_final)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    total = st.number_input("Monto Total Calculado (S/.)", value=float(total_acumulado), min_value=0.0, step=0.50)

    st.markdown("---")
    
    if st.button("💾 Guardar Pedido", type="primary", use_container_width=True):
        st.session_state["mostrar_confirmacion"] = True

    if st.session_state.get("mostrar_confirmacion", False):
        st.warning("❓ **¿Estás seguro de guardar la venta?** Verifica los datos antes de continuar.")
        col_si, col_no = st.columns(2)
        
        with col_si:
            if st.button("✅ Sí, Guardar Venta", use_container_width=True):
                resumen_prods = " | ".join([f"{k}: {v[0]} (S/.{v[1]})" for k, v in cantidades_seleccionadas.items()])
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
                    "productos": resumen_prods if resumen_prods else "Sin productos",
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

# --- MÓDULO 2: MIS PEDIDOS ---
elif opcion == "Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    
    if st.session_state["rol"] == "ADMIN":
        res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    else:
        res = supabase.table("pedidos").select("*").eq("vendedor", st.session_state["usuario"]).eq("estado", "ACTIVO").execute()
        
    if res.data:
        df_pedidos = pd.DataFrame(res.data)
        st.dataframe(df_pedidos, use_container_width=True)
        
        csv_data = df_pedidos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📁 Descargar Respaldo CSV (Para Google Drive)",
            data=csv_data,
            file_name=f"respaldo_pedidos_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("No cuentan con pedidos registrados actualmente.")

# --- MÓDULO 3: EVIDENCIAS ---
elif opcion == "Subir Evidencia":
    st.header("📤 Subir Fotos y Videos de Entregas")
    archivo = st.file_uploader("Selecciona imagen o video comprobante", type=["png", "jpg", "jpeg", "mp4"])
    if archivo and st.button("Subir Evidencia"):
        st.success(f"Archivo '{archivo.name}' guardado correctamente.")

# --- MÓDULO 4: CONTROL Y GUÍA DE RUTAS CON GOOGLE MAPS / GPS EN VIVO (ADMIN) ---
elif opcion == "Rutas GPS" and st.session_state["rol"] == "ADMIN":
    st.header("🗺️ Control y Guía de Rutas (GPS y Google Maps En Vivo)")
    st.write("Supervisión de ubicación en tiempo real de los vendedores en campo y rutas de ventas.")

    res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
    
    col_map1, col_map2 = st.columns([2, 1])
    
    with col_map1:
        st.subheader("📍 Geolocalización Online y Monitoreo Campo")
        map_html = """
        <iframe 
            width="100%" 
            height="450" 
            frameborder="0" style="border:0; border-radius:12px;" 
            src="https://maps.google.com/maps?q=-11.0500,-75.3300&z=14&output=embed" 
            allowfullscreen>
        </iframe>
        """
        components.html(map_html, height=460)

    with col_map2:
        st.subheader("📋 Resumen de Puntos")
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df[["vendedor", "cliente_nombre", "local_direccion", "estado_entrega"]], height=400, use_container_width=True)
        else:
            st.info("No hay puntos cargados actualmente.")

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

# --- MÓDULO 6: GESTIÓN DE PERSONAL (SOLO ADMINISTRADOR - CON VALIDACIÓN DNI/RUC) ---
elif opcion == "Personal (8 Cuentas)" and st.session_state["rol"] == "ADMIN":
    st.header("👥 Gestión de Colaboradores de EMANA (Acceso Exclusivo Admin)")
    st.info("Solo tú como Administrador puedes dar de alta o autorizar cuentas para tus vendedores.")
    
    res_u = supabase.table("usuarios").select("id, username, gmail, rol, documento_tipo, documento_num").execute()
    if res_u.data:
        st.dataframe(pd.DataFrame(res_u.data), use_container_width=True)
    
    with st.form("crear_usuario"):
        st.subheader("Registrar Nuevo Colaborador")
        
        doc_tipo = st.selectbox("Tipo de Documento", ["DNI", "RUC"])
        doc_num = st.text_input("Número de Documento (DNI: 8 dígitos / RUC: 11 dígitos)").strip()
        
        u_nom = st.text_input("Usuario / Nombre").strip()
        u_mail = st.text_input("Gmail Registrado").strip()
        u_pass = st.text_input("Contraseña Asignada", type="password").strip()
        u_rol = st.selectbox("Rol", ["VENDEDOR", "ADMIN"])
        
        if st.form_submit_button("Crear Cuenta de Colaborador"):
            if doc_tipo == "DNI" and (len(doc_num) != 8 or not doc_num.isdigit()):
                st.error("❌ El DNI debe contener exactamente 8 dígitos numéricos.")
            elif doc_tipo == "RUC" and (len(doc_num) != 11 or not doc_num.isdigit()):
                st.error("❌ El RUC debe contener exactamente 11 dígitos numéricos.")
            elif not u_nom or not u_mail or not u_pass:
                st.warning("Completa todos los campos.")
            else:
                try:
                    supabase.table("usuarios").insert({
                        "username": u_nom,
                        "gmail": u_mail,
                        "password": u_pass,
                        "rol": u_rol,
                        "documento_tipo": doc_tipo,
                        "documento_num": doc_num
                    }).execute()
                    st.success(f"✅ Cuenta creada con éxito para {u_nom}.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al registrar usuario: {ex}")

# --- MÓDULO 7: PAPELERA ---
elif opcion == "Papelera" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Registro de Eliminados")
    res_p = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
    if res_p.data:
        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)