import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Sistema EMANA", page_icon="💧", layout="wide")

# 2. Conexión a Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 3. Estilos CSS Personalizados
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%);
    }
    .product-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        border: 2px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        text-align: center;
    }
    .product-card:hover {
        border-color: #007bff;
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,123,255,0.15);
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border-color: #004085;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Formulario de Pedido con Catálogo e Imágenes
st.title("🛒 Registrar Nuevo Pedido - EMANA")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150?text=Botella+625ml", width=120)
    st.subheader("Botella 625 ml")
    cant_625 = st.number_input("Cantidad", min_value=0, value=0, key="c625")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150?text=Botella+8.5L", width=120)
    st.subheader("Botella 8.5 L")
    cant_85 = st.number_input("Cantidad", min_value=0, value=0, key="c85")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/150?text=Caja+20L", width=120)
    st.subheader("Caja de 20 L")
    cant_20 = st.number_input("Cantidad", min_value=0, value=0, key="c20")
    st.markdown('</div>', unsafe_allow_html=True)

# 5. Vista de Administrador para Modificar Pedidos
if st.session_state.get("rol") == "ADMIN":
    st.divider()
    st.header("🛠️ Panel de Control - Modificar Pedidos")
    
    # Obtener pedidos desde Supabase
    res = supabase.table("pedidos").select("*").execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        st.dataframe(df)
        
        pedido_id = st.selectbox("Selecciona ID de Pedido para modificar", df["id"])
        nuevo_estado = st.selectbox("Estado del Pedido", ["Pendiente", "Entregado", "No Entregado", "Cancelado"])
        vendedor_asignado = st.text_input("Vendedor a cargo", value="admin")
        
        if st.button("Actualizar Pedido"):
            supabase.table("pedidos").update({
                "estado": nuevo_estado,
                "vendedor": vendedor_asignado
            }).eq("id", pedido_id).execute()
            st.success("Pedido actualizado correctamente.")