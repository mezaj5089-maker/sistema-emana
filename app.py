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

# --- ESTILOS CSS3 AVANZADOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #e0f2fe 0%, #f0f9ff 100%);
    }
    
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
    
    div[data-baseweb="input"] > div {
        border-radius: 10px !important;
        border: 2px solid #38bdf8 !important;
        background-color: #ffffff !important;
    }
    
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid #7dd3fc;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .video-container {
        background: #ffffff;
        border-radius: 18px;
        padding: 15px;
        border: 2px solid #0284c7;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

# IMÁGENES POR DEFECTO DESDE TU BUCKET DE SUPABASE
SUPABASE_URL_BASE = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else ""
DEFAULT_IMAGES = {
    1: f"{SUPABASE_URL_BASE}/storage/v1/object/public/catalogo/img_625.png",
    2: f"{SUPABASE_URL_BASE}/storage/v1/object/public/catalogo/img_85.png",
    3: f"{SUPABASE_URL_BASE}/storage/v1/object/public/catalogo/img_20.png"
}

# --- FUNCIONES AUXILIARES DE IMAGEN Y BASE DE DATOS ---
def guardar_imagen_supabase(uploaded_file, nombre_destino):
    if not supabase or uploaded_file is None:
        return None
    try:
        file_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type or "image/png"
        
        supabase.storage.from_("catalogo").upload(
            path=nombre_destino,
            file=file_bytes,
            file_options={"upsert": "true", "content-type": mime_type}
        )
        return supabase.storage.from_("catalogo").get_public_url(nombre_destino)
    except Exception as e:
        st.error(f"Error al subir imagen a Supabase Storage: {e}")
        return None

def obtener_productos():
    productos_base = [
        {"id": 1, "nombre": "Paquete 625 ml (20 UND)", "precio_und": 12.50, "precio_mayor": 10.00, "min_mayor": 5, "imagen": DEFAULT_IMAGES[1]},
        {"id": 2, "nombre": "Botella 8.5 L", "precio_und": 9.00, "precio_mayor": 7.00, "min_mayor": 10, "imagen": DEFAULT_IMAGES[2]},
        {"id": 3, "nombre": "Caja 20 L", "precio_und": 20.00, "precio_mayor": 18.00, "min_mayor": 5, "imagen": DEFAULT_IMAGES[3]}
    ]
    if supabase:
        try:
            res = supabase.table("products").select("*").execute()
            if res.data:
                for p in res.data:
                    if not p.get("imagen") and p.get("imagen_url"):
                        p["imagen"] = p["imagen_url"]
                    elif not p.get("imagen"):
                        p["imagen"] = DEFAULT_IMAGES.get(p["id"], DEFAULT_IMAGES[1])
                return res.data
        except Exception:
            pass
    return productos_base

def actualizar_imagen_producto(prod_id, url_o_file):
    url_final = url_o_file
    if not isinstance(url_o_file, str):
        nombre_file = f"prod_{prod_id}_{int(datetime.datetime.now().timestamp())}.png"
        url_final = guardar_imagen_supabase(url_o_file, nombre_file)
    
    if url_final and supabase:
        try:
            supabase.table("products").update({"imagen": url_final}).eq("id", prod_id).execute()
            st.success("✅ Imagen actualizada en la base de datos.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al actualizar la base de datos: {e}")

def mostrar_imagen_producto(url_imagen):
    if url_imagen and isinstance(url_imagen, str) and url_imagen.strip().startswith("http"):
        st.image(url_imagen, use_container_width=True)
    else:
        st.image(DEFAULT_IMAGES[1], use_container_width=True)

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "rol" not in st.session_state:
    st.session_state["rol"] = None
if "modo_cliente" not in st.session_state:
    st.session_state["modo_cliente"] = True
if "promo_video_url" not in st.session_state:
    st.session_state["promo_video_url"] = "https://www.w3schools.com/html/mov_bbb.mp4"

WA_LINK = "https://wa.me/qr/ZEJEN3EUZZQRF1"

# --- BARRA LATERAL ---
with st.sidebar:
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=200)
    except Exception:
        st.title("💧 EMANA App")
    
    st.markdown(f'''
        <a href="{WA_LINK}" target="_blank" class="btn-whatsapp">
            📱 Consultar por WhatsApp
        </a>
    ''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    gps_reloj_js = """
    <div style="background:#0f172a; color:#f8fafc; padding:14px; border-radius:12px; text-align:center; font-family:sans-serif; border: 2px solid #38bdf8;">
        <div id="fecha" style="font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase;"></div>
        <div id="reloj" style="font-size:20px; color:#38bdf8; font-weight:700; margin-top:2px;"></div>
        <div id="gps" style="font-size:11px; color:#4ade80; margin-top:6px;">📡 GPS activo en tiempo real</div>
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
    </script>
    """
    components.html(gps_reloj_js, height=115)
    st.markdown("---")

    if not st.session_state["autenticado"]:
        st.info("💡 Estás en el Catálogo Público.")
        if st.button("🔑 Acceso Personal / Ventas", use_container_width=True):
            st.session_state["modo_cliente"] = False
            st.rerun()

# --- VISTA CLIENTE (CATÁLOGO PÚBLICO) ---
if not st.session_state["autenticado"] and st.session_state["modo_cliente"]:
    col_head_img, col_head_txt = st.columns([1, 4])
    with col_head_img:
        try:
            st.image("LOGO agua Emana VECTOR 01.png", width=140)
        except Exception:
            st.write("💧")
    with col_head_txt:
        st.markdown("""
            <div class="header-banner">
                <div>
                    <h1 style="margin:0; font-weight:800; font-size: 32px;">Distribuidora EMANA</h1>
                    <p style="margin:0; opacity:0.95; font-size: 18px; font-weight: 600;">✨ Vitalidad vida sana — Catálogo Oficial</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    col_cat_pub, col_vid_pub = st.columns([2.7, 1.3], gap="medium")
    
    with col_cat_pub:
        st.markdown("### 📦 Nuestros Productos y Precios")
        st.write("Explora nuestro catálogo. Si deseas realizar un pedido, comunícate directamente con nosotros por WhatsApp.")
        
        prods = obtener_productos()
        if prods:
            cols = st.columns(3)
            for idx, p in enumerate(prods):
                with cols[idx % 3]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    img_url = p.get("imagen") or p.get("imagen_url")
                    mostrar_imagen_producto(img_url)
                    
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

    with col_vid_pub:
        st.markdown("### 🎬 Spot Promocional")
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        st.video(st.session_state["promo_video_url"])
        st.caption("✨ Agua EMANA - Vitalidad y Vida Sana")
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# --- LOGIN Y RECUPERACIÓN DE CONTRASEÑA ---
if not st.session_state["autenticado"] and not st.session_state["modo_cliente"]:
    col_logo_login, col_txt_login = st.columns([1, 3])
    with col_logo_login:
        try:
            st.image("LOGO agua Emana VECTOR 01.png", width=160)
        except Exception:
            st.write("💧")
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
                    if supabase:
                        try:
                            res = supabase.table("usuarios").select("*").eq("username", user_input).eq("password", pass_input).execute()
                            if not res.data:
                                res = supabase.table("usuarios").select("*").eq("gmail", user_input).eq("password", pass_input).execute()
                                
                            if res.data:
                                st.session_state["autenticado"] = True
                                st.session_state["usuario"] = res.data[0]["username"]
                                st.session_state["rol"] = res.data[0].get("rol", "VENDEDOR")
                                st.success(f"Bienvenido {st.session_state['usuario']}")
                                st.rerun()
                            else:
                                st.error("Credenciales incorrectas")
                        except Exception as ex:
                            st.error(f"Error de conexión: {ex}")
                    else:
                        if user_input in ["admin", "vendedor"] and pass_input != "":
                            st.session_state["autenticado"] = True
                            st.session_state["usuario"] = user_input
                            st.session_state["rol"] = "ADMIN" if user_input == "admin" else "VENDEDOR"
                            st.rerun()

        with tab_recuperar:
            gmail_rec = st.text_input("Ingresa tu Gmail registrado").strip()
            nueva_pass = st.text_input("Nueva Contraseña", type="password").strip()
            if st.button("Restablecer Contraseña", use_container_width=True):
                if "@" in gmail_rec and nueva_pass and supabase:
                    try:
                        res = supabase.table("usuarios").update({"password": nueva_pass}).eq("gmail", gmail_rec).execute()
                        if res.data:
                            st.success(f"✅ Contraseña actualizada para {gmail_rec}.")
                        else:
                            st.error("Correo no encontrado.")
                    except Exception as ex:
                        st.error(f"Error: {ex}")
                else:
                    st.warning("Completa los datos correctamente o verifica la conexión.")
    st.stop()

# --- HEADER INTERNO DE NAVEGACIÓN ---
col_head_img, col_head_txt = st.columns([1, 4])
with col_head_img:
    try:
        st.image("LOGO agua Emana VECTOR 01.png", width=140)
    except Exception:
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

# --- MENÚ LATERAL INTERNO ---
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

# --- MÓDULO 1: REGISTRAR VENTAS Y CATÁLOGO INTERNO ---
if opcion == "Nuevas Ventas":
    st.header("📝 Registrar Nuevo Pedido")
    
    col_v1, col_v2 = st.columns([2, 2])
    with col_v1:
        if st.session_state["rol"] == "ADMIN":
            vendedor_activo = st.text_input("👤 Vendedor que Registra (Modo Admin):", value=st.session_state["usuario"])
        else:
            st.text_input("👤 Vendedor que Registra:", value=st.session_state["usuario"], disabled=True)
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

    col_cat_int, col_vid_int = st.columns([2.7, 1.3], gap="medium")

    with col_cat_int:
        st.subheader("📦 Catálogo de Productos Dinámico")
        
        # AGREGAR NUEVO PRODUCTO (SOLO ADMIN)
        if st.session_state["rol"] == "ADMIN":
            with st.expander("➕ Agregar Nuevo Producto al Catálogo"):
                with st.form("form_nuevo_prod"):
                    n_prod = st.text_input("Nombre del Producto")
                    p_und = st.number_input("Precio por Unidad (S/.)", min_value=0.0, step=0.50, value=10.0)
                    p_mayor = st.number_input("Precio por Mayor (S/.)", min_value=0.0, step=0.50, value=8.0)
                    min_m = st.number_input("Mínimo Unidades para Precio por Mayor", min_value=1, value=5)
                    img_prod = st.file_uploader("Imagen del Producto", type=["png", "jpg", "jpeg"])
                    
                    btn_crear_p = st.form_submit_button("Guardar Producto en el Catálogo")
                    if btn_crear_p and n_prod:
                        url_img = None
                        if img_prod:
                            nombre_file = f"prod_{int(datetime.datetime.now().timestamp())}.png"
                            url_img = guardar_imagen_supabase(img_prod, nombre_file)
                        if not url_img:
                            url_img = DEFAULT_IMAGES[1]
                        
                        if supabase:
                            try:
                                supabase.table("products").insert({
                                    "nombre": n_prod,
                                    "precio_und": p_und,
                                    "precio_mayor": p_mayor,
                                    "min_mayor": min_m,
                                    "imagen": url_img
                                }).execute()
                                st.success(f"✅ Producto '{n_prod}' agregado.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar producto: {e}")

        productos_lista = obtener_productos()
        cantidades_seleccionadas = {}
        total_acumulado = 0.0

        if productos_lista:
            cols_p = st.columns(3)
            for i, prod in enumerate(productos_lista):
                with cols_p[i % 3]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    img_url = prod.get("imagen") or prod.get("imagen_url")
                    mostrar_imagen_producto(img_url)
                    
                    # EDITAR IMAGEN DE PRODUCTO (SOLO ADMIN)
                    if st.session_state["rol"] == "ADMIN":
                        with st.expander(f"✏️ Editar Imagen"):
                            nueva_img_file = st.file_uploader("Subir imagen", type=["png", "jpg", "jpeg"], key=f"up_img_{prod['id']}")
                            nueva_img_url = st.text_input("O pegar URL", value=img_url if isinstance(img_url, str) else "", key=f"url_img_{prod['id']}")
                            
                            if st.button("💾 Cambiar Imagen", key=f"btn_img_{prod['id']}"):
                                if nueva_img_file:
                                    actualizar_imagen_producto(prod['id'], nueva_img_file)
                                elif nueva_img_url:
                                    actualizar_imagen_producto(prod['id'], nueva_img_url)

                    cant = st.number_input(f"Cantidad {prod['nombre']}", min_value=0, value=0, key=f"cant_{prod['id']}")
                    p_sugerido = prod['precio_mayor'] if cant >= prod['min_mayor'] else prod['precio_und']
                    p_final = st.number_input(f"Precio Unit. S/. ({prod['nombre']})", value=float(p_sugerido), step=0.50, key=f"p_{prod['id']}")
                    
                    subtotal_item = cant * p_final
                    total_acumulado += subtotal_item
                    
                    if cant > 0:
                        cantidades_seleccionadas[prod['nombre']] = (cant, p_final)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

        total = st.number_input("Monto Total Calculado (S/.)", value=float(total_acumulado), min_value=0.0, step=0.50)

    with col_vid_int:
        st.subheader("🎬 Spot Promocional")
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        st.video(st.session_state["promo_video_url"])

        if st.session_state["rol"] == "ADMIN":
            st.divider()
            st.caption("⚙️ **Configuración de Video (Solo Admin)**")
            v_input = st.text_input("Enlace (YouTube / URL MP4)", value=st.session_state["promo_video_url"] if isinstance(st.session_state["promo_video_url"], str) else "")
            if st.button("Actualizar Enlace"):
                st.session_state["promo_video_url"] = v_input
                st.success("Enlace actualizado")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    if st.button("💾 Guardar Pedido", type="primary", use_container_width=True):
        st.session_state["mostrar_confirmacion"] = True

    if st.session_state.get("mostrar_confirmacion", False):
        st.warning("❓ **¿Estás seguro de guardar la venta?**")
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
                if supabase:
                    try:
                        supabase.table("pedidos").insert(nuevo_pedido).execute()
                        st.success(f"✅ ¡Venta guardada con éxito por {vendedor_activo}!")
                        st.session_state["mostrar_confirmacion"] = False
                    except Exception as e:
                        st.error(f"Error al guardar pedido: {e}")
                else:
                    st.success("✅ Venta registrada (Modo Simulación local).")
                    st.session_state["mostrar_confirmacion"] = False

        with col_no:
            if st.button("❌ No, Corregir Datos", use_container_width=True):
                st.session_state["mostrar_confirmacion"] = False

# --- MÓDULO 2: MIS PEDIDOS ---
elif opcion == "Mis Pedidos":
    st.header("📋 Mis Pedidos Registrados")
    if supabase:
        try:
            if st.session_state["rol"] == "ADMIN":
                res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
            else:
                res = supabase.table("pedidos").select("*").eq("vendedor", st.session_state["usuario"]).eq("estado", "ACTIVO").execute()
            
            if res.data:
                df_pedidos = pd.DataFrame(res.data)
                st.dataframe(df_pedidos, use_container_width=True)
                st.download_button("📁 Descargar Respaldo CSV", data=df_pedidos.to_csv(index=False).encode('utf-8'), file_name="pedidos.csv", mime="text/csv")
            else:
                st.info("No hay pedidos registrados en la base de datos.")
        except Exception as e:
            st.error(f"Error al consultar pedidos: {e}")
    else:
        st.info("Base de datos no disponible en modo offline.")

# --- MÓDULO 3: SUBIR EVIDENCIA ---
elif opcion == "Subir Evidencia":
    st.header("📤 Subir Fotos y Videos de Entregas")
    archivo = st.file_uploader("Selecciona comprobante o foto de entrega", type=["png", "jpg", "jpeg", "mp4"])
    if archivo and st.button("Subir Evidencia"):
        if supabase:
            nombre_ev = f"evidencia_{int(datetime.datetime.now().timestamp())}_{archivo.name}"
            url_ev = guardar_imagen_supabase(archivo, nombre_ev)
            if url_ev:
                st.success("✅ Evidencia guardada en Supabase Storage.")
            else:
                st.error("No se pudo completar la carga.")
        else:
            st.success("✅ Archivo cargado correctamente (Simulación).")

# --- MÓDULO 4: RUTAS GPS ---
elif opcion == "Rutas GPS" and st.session_state["rol"] == "ADMIN":
    st.header("🗺️ Control y Guía de Rutas GPS")
    map_html = '<iframe width="100%" height="450" frameborder="0" style="border:0; border-radius:12px;" src="https://maps.google.com/maps?q=-11.0500,-75.3300&z=14&output=embed"></iframe>'
    components.html(map_html, height=460)

# --- MÓDULO 5: ANALÍTICA PREDICTIVA ---
elif opcion == "Analítica Predictiva" and st.session_state["rol"] == "ADMIN":
    st.header("📊 Tablero Analítico Dinámico")
    if supabase:
        try:
            res = supabase.table("pedidos").select("*").eq("estado", "ACTIVO").execute()
            if res.data:
                df_a = pd.DataFrame(res.data)
                df_a['fecha_entrega'] = pd.to_datetime(df_a['fecha_entrega'])
                m1, m2 = st.columns(2)
                m1.metric("Ingresos Totales", f"S/. {df_a['total'].sum():,.2f}")
                m2.metric("Promedio por Pedido", f"S/. {df_a['total'].mean():,.2f}")
                fig = px.line(df_a, x="fecha_entrega", y="total", title="Evolución de Ventas", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos suficientes para la analítica.")
        except Exception as e:
            st.error(f"Error al cargar analítica: {e}")

# --- MÓDULO 6: PERSONAL ---
elif opcion == "Personal (8 Cuentas)" and st.session_state["rol"] == "ADMIN":
    st.header("👥 Gestión de Colaboradores EMANA")
    if supabase:
        try:
            res_u = supabase.table("usuarios").select("id, username, gmail, rol").execute()
            if res_u.data:
                st.dataframe(pd.DataFrame(res_u.data), use_container_width=True)
        except Exception as e:
            st.error(f"Error al cargar usuarios: {e}")

# --- MÓDULO 7: PAPELERA ---
elif opcion == "Papelera" and st.session_state["rol"] == "ADMIN":
    st.header("🗑️ Registro de Eliminados")
    if supabase:
        try:
            res_p = supabase.table("pedidos").select("*").eq("estado", "PAPELERA").execute()
            if res_p.data:
                st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)
            else:
                st.info("La papelera está vacía.")
        except Exception as e:
            st.error(f"Error al cargar papelera: {e}")