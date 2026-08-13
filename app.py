import os
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Distribuidora de agua de mesa EMANA",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para buscar imágenes en diferentes carpetas y extensiones
def buscar_imagen(nombre_base):
    extensiones = [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]
    rutas_base = [".", "..", "../.."]
    
    for ruta in rutas_base:
        for ext in extensiones:
            path_intent = os.path.join(ruta, nombre_base + ext)
            if os.path.exists(path_intent):
                return path_intent
    return None

# Buscar imagen de fondo nevado
bg_nevado = buscar_imagen("nevado")
bg_style = ""
if bg_nevado:
    bg_nevado_path = bg_nevado.replace("\\", "/")
    bg_style = f"""
        background-image: linear-gradient(rgba(230, 242, 255, 0.85), rgba(200, 225, 255, 0.90)), url('{bg_nevado_path}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    """
else:
    bg_style = "background: linear-gradient(180deg, #e6f2ff 0%, #c8e1ff 100%);"

# Estilos CSS con fondo degradado nevado y tonos Emana
st.markdown(f"""
<style>
    .stApp {{
        {bg_style}
    }}
    .main-title {{
        color: #002b5b;
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 0px;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }}
    .slogan-title {{
        color: #0056b3;
        font-weight: 700;
        font-size: 1.25rem;
        margin-top: -8px;
        margin-bottom: 25px;
        font-style: italic;
    }}
    .metric-card {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 51, 102, 0.12);
        border-top: 4px solid #0056b3;
        text-align: center;
    }}
    .metric-card h4 {{
        color: #444444;
        margin-bottom: 5px;
        font-size: 1rem;
    }}
    .metric-card h2 {{
        color: #002b5b;
        font-weight: 700;
        margin: 0;
    }}
    .stButton>button {{
        background-color: #0056b3;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        height: 46px;
        border: none;
    }}
    .stButton>button:hover {{
        background-color: #002b5b;
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

DB_NAME = "emana_local.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Crear tablas si no existen
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE,
                    direccion TEXT,
                    distrito TEXT,
                    referencia TEXT)''')
                    
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                    id TEXT PRIMARY KEY,
                    producto TEXT,
                    presentacion TEXT,
                    stock INTEGER,
                    precio_unitario REAL,
                    precio_mayor REAL,
                    cant_mayor INTEGER,
                    imagen_base TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    mes TEXT,
                    cliente TEXT,
                    vendedor TEXT,
                    producto TEXT,
                    cantidad INTEGER,
                    total REAL,
                    metodo_pago TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    mes TEXT,
                    concepto TEXT,
                    destino TEXT,
                    monto REAL)''')

    # 2. Migración automática de la estructura antigua de la tabla productos
    c.execute("PRAGMA table_info(productos)")
    columnas_existentes = [col[1] for col in c.fetchall()]
    
    columnas_necesarias = {
        "precio_unitario": "REAL DEFAULT 0.0",
        "precio_mayor": "REAL DEFAULT 0.0",
        "cant_mayor": "INTEGER DEFAULT 1",
        "imagen_base": "TEXT DEFAULT ''"
    }

    for col_nombre, col_tipo in columnas_necesarias.items():
        if col_nombre not in columnas_existentes:
            c.execute(f"ALTER TABLE productos ADD COLUMN {col_nombre} {col_tipo}")

    # Migración de la columna mes en ventas y gastos
    for tabla in ["ventas", "gastos"]:
        c.execute(f"PRAGMA table_info({tabla})")
        cols_t = [col[1] for col in c.fetchall()]
        if "mes" not in cols_t:
            c.execute(f"ALTER TABLE {tabla} ADD COLUMN mes TEXT")

    # 3. Catálogo de Productos con Reglas de Precio EMANA
    productos_base = [
        ("PROD01", "Botella 625 ml", "Paquete x 20 un", 200, 12.0, 10.0, 5, "botella 625 ml transparente"),
        ("PROD02", "Bidón 8.5 L", "Bidón individual", 150, 9.0, 7.0, 4, "BT 8.5L"),
        ("PROD03", "Caja Agua 20 L", "Caja con dispensador", 100, 20.0, 18.0, 5, "1773327635518")
    ]
    
    for prod in productos_base:
        c.execute("""INSERT INTO productos (id, producto, presentacion, stock, precio_unitario, precio_mayor, cant_mayor, imagen_base)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                     ON CONFLICT(id) DO UPDATE SET 
                     producto=excluded.producto,
                     presentacion=excluded.presentacion,
                     stock=excluded.stock,
                     precio_unitario=excluded.precio_unitario,
                     precio_mayor=excluded.precio_mayor,
                     cant_mayor=excluded.cant_mayor,
                     imagen_base=excluded.imagen_base""", prod)
                     
    conn.commit()
    conn.close()

init_db()

# --- BARRA LATERAL ---
path_logo = buscar_imagen("LOGO agua Emana VECTOR 01")
if path_logo:
    st.sidebar.image(path_logo, use_container_width=True)
else:
    st.sidebar.markdown("<h2 style='color:#002b5b; text-align:center;'>EMANA</h2>", unsafe_allow_html=True)

st.sidebar.markdown("---")

opcion = st.sidebar.radio("Navegación / Módulos", [
    "📊 Dashboard Interactivo", 
    "🛒 Registrar Venta", 
    "💸 Registrar Gasto", 
    "📦 Catálogo & Inventario", 
    "👥 Gestión de Clientes"
])

st.sidebar.markdown("---")

path_chica = buscar_imagen("chica emana 04 2026")
if path_chica:
    st.sidebar.image(path_chica, caption="Vitalidad, vida sana", use_container_width=True)

# Encabezado Principal
st.markdown("<h1 class='main-title'>Distribuidora de agua de mesa EMANA</h1>", unsafe_allow_html=True)
st.markdown("<p class='slogan-title'>Vitalidad, vida sana</p>", unsafe_allow_html=True)

conn = sqlite3.connect(DB_NAME)

# --- MÓDULO 1: DASHBOARD ---
if opcion == "📊 Dashboard Interactivo":
    st.subheader("📊 Panel de Control Operativo y Resumen")
    
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        meses_lista = ["TODOS", "2026-08 (AGOSTO)", "2026-07 (JULIO)", "2026-09 (SETIEMBRE)"]
        mes_sel = st.selectbox("📅 Seleccionar Mes de Operación", meses_lista)
        
    if mes_sel != "TODOS":
        filtro_mes = mes_sel.split()[0]
        df_ventas = pd.read_sql_query("SELECT * FROM ventas WHERE mes = ?", conn, params=(filtro_mes,))
        df_gastos = pd.read_sql_query("SELECT * FROM gastos WHERE mes = ?", conn, params=(filtro_mes,))
    else:
        df_ventas = pd.read_sql_query("SELECT * FROM ventas", conn)
        df_gastos = pd.read_sql_query("SELECT * FROM gastos", conn)

    total_v = df_ventas['total'].sum() if not df_ventas.empty else 0.0
    total_g = df_gastos['monto'].sum() if not df_gastos.empty else 0.0
    saldo_neto = total_v - total_g

    # Tarjetas Métricas
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"<div class='metric-card'><h4>Total Ventas</h4><h2>S/. {total_v:.2f}</h2></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-card' style='border-top-color: #dc3545;'><h4>Total Gastos</h4><h2>S/. {total_g:.2f}</h2></div>", unsafe_allow_html=True)
    with m3:
        color_saldo = "#28a745" if saldo_neto >= 0 else "#dc3545"
        st.markdown(f"<div class='metric-card' style='border-top-color: {color_saldo};'><h4>Balance Neto</h4><h2>S/. {saldo_neto:.2f}</h2></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Gráficos Interactivos Nativos
    if not df_ventas.empty:
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("##### Ventas por Producto (S/.)")
            v_prod = df_ventas.groupby("producto")["total"].sum()
            st.bar_chart(v_prod)
            
        with g2:
            st.markdown("##### Ventas por Método de Pago (S/.)")
            v_metodo = df_ventas.groupby("metodo_pago")["total"].sum()
            st.bar_chart(v_metodo)
    else:
        st.info("Registra ventas para activar las visualizaciones de gráficos.")

    tab1, tab2 = st.tabs(["🛒 Reporte Ventas", "💸 Reporte Gastos"])
    with tab1:
        st.dataframe(df_ventas, use_container_width=True)
    with tab2:
        st.dataframe(df_gastos, use_container_width=True)

# --- MÓDULO 2: REGISTRAR VENTA ---
elif opcion == "🛒 Registrar Venta":
    st.subheader("🛒 Formulario de Registro de Ventas")
    
    df_prod = pd.read_sql_query("SELECT * FROM productos", conn)
    
    col_form, col_preview = st.columns([3, 2])
    
    with col_form:
        fecha_input = st.date_input("Fecha de Venta", datetime.now())
        mes_str = fecha_input.strftime("%Y-%m")
        
        cliente = st.text_input("Nombre / Razón Social del Cliente")
        vendedor = st.selectbox("Vendedor Asignado", ["Rocio Mejia", "Daniel", "Otro"])
        
        prod_lista = df_prod['producto'].tolist() if not df_prod.empty else []
        prod_sel = st.selectbox("Seleccionar Producto", prod_lista)
        
        cant = st.number_input("Cantidad", min_value=1, value=1, step=1)
        metodo = st.selectbox("Método de Pago", ["Efectivo", "Yape / Plin", "Transferencia Bancaria"])
        
        # Lógica de Precios Dinámicos según producto y cantidad
        if prod_sel and not df_prod.empty:
            row_prod = df_prod[df_prod['producto'] == prod_sel].iloc[0]
            p_unit = float(row_prod['precio_unitario'])
            p_mayor = float(row_prod['precio_mayor'])
            c_mayor = int(row_prod['cant_mayor'])
            img_base = row_prod['imagen_base']
            
            if cant >= c_mayor:
                precio_aplicado = p_mayor
                es_por_mayor = True
            else:
                precio_aplicado = p_unit
                es_por_mayor = False
        else:
            precio_aplicado = 0.0
            es_por_mayor = False
            img_base = None

        total = cant * precio_aplicado
        
        if es_por_mayor:
            st.info(f"🎉 ¡Aplica Precio por Mayor! (A partir de {c_mayor} un/paq a S/. {p_mayor:.2f} c/u)")
        else:
            st.caption(f"Precio regular: S/. {p_unit:.2f} (Por mayor a S/. {p_mayor:.2f} desde {c_mayor} un/paq)")

        st.markdown(f"### Total Calculado: **S/. {total:.2f}**")
        
        if st.button("Confirmar y Registrar Venta"):
            if cliente.strip() == "":
                st.error("Por favor, ingresa el nombre del cliente.")
            else:
                c = conn.cursor()
                c.execute("INSERT INTO ventas (fecha, mes, cliente, vendedor, producto, cantidad, total, metodo_pago) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (str(fecha_input), mes_str, cliente, vendedor, prod_sel, cant, total, metodo))
                conn.commit()
                st.success(f"✅ Venta registrada con éxito (Período {mes_str}).")

    with col_preview:
        st.markdown("#### Vista Previa del Producto")
        path_prod = buscar_imagen(img_base) if img_base else None
        if path_prod:
            st.image(path_prod, caption=f"{prod_sel} - Precio aplicado: S/. {precio_aplicado:.2f} c/u", width=250)
        else:
            st.info("Imagen no disponible.")

# --- MÓDULO 3: REGISTRAR GASTO ---
elif opcion == "💸 Registrar Gasto":
    st.subheader("💸 Formulario de Registro de Gastos")
    
    with st.form("form_gasto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha_input = st.date_input("Fecha del Gasto", datetime.now())
            mes_str = fecha_input.strftime("%Y-%m")
            concepto = st.text_input("Concepto (Ej. Movilidad, Embalaje, Personal)")
        with col2:
            destino = st.selectbox("Destino / Ruta", ["San Ramón", "La Merced", "Chanchamayo", "Almacén Central", "Otro"])
            monto = st.number_input("Monto (S/.)", min_value=0.01, format="%.2f")
            
        submitted = st.form_submit_button("Guardar Gasto")
        if submitted:
            if concepto.strip() == "":
                st.error("Por favor completa el concepto del gasto.")
            else:
                c = conn.cursor()
                c.execute("INSERT INTO gastos (fecha, mes, concepto, destino, monto) VALUES (?, ?, ?, ?, ?)",
                          (str(fecha_input), mes_str, concepto, destino, monto))
                conn.commit()
                st.success("✅ Gasto guardado exitosamente.")

# --- MÓDULO 4: CATÁLOGO & INVENTARIO ---
elif opcion == "📦 Catálogo & Inventario":
    st.subheader("📦 Lista de Precios y Presentaciones EMANA")
    
    df_p = pd.read_sql_query("SELECT * FROM productos", conn)
    
    cols = st.columns(3)
    for index, row in df_p.iterrows():
        with cols[index % 3]:
            st.markdown(f"### {row['producto']}")
            img_p = buscar_imagen(row['imagen_base'])
            if img_p:
                st.image(img_p, use_container_width=True)
            st.write(f"**Presentación:** {row['presentacion']}")
            st.write(f"**Precio Unitario:** S/. {row['precio_unitario']:.2f}")
            st.write(f"**Precio x Mayor (A partir de {row['cant_mayor']} un):** S/. {row['precio_mayor']:.2f}")
            st.write(f"**Stock:** {row['stock']} unidades")
            st.markdown("---")

# --- MÓDULO 5: CLIENTES ---
elif opcion == "👥 Gestión de Clientes":
    st.subheader("👥 Directorio de Clientes")
    
    with st.expander("➕ Agregar Nuevo Cliente"):
        with st.form("form_cliente", clear_on_submit=True):
            nom = st.text_input("Nombre Completo o Empresa")
            dir_c = st.text_input("Dirección")
            dis = st.text_input("Distrito")
            ref = st.text_input("Referencia")
            
            btn_c = st.form_submit_button("Guardar Cliente")
            if btn_c:
                if nom.strip() != "":
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO clientes (nombre, direccion, distrito, referencia) VALUES (?, ?, ?, ?)",
                                  (nom, dir_c, dis, ref))
                        conn.commit()
                        st.success("✅ Cliente registrado con éxito.")
                    except sqlite3.IntegrityError:
                        st.error("Este cliente ya se encuentra en el sistema.")
                else:
                    st.error("El nombre es requerido.")

    df_c = pd.read_sql_query("SELECT * FROM clientes", conn)
    st.dataframe(df_c, use_container_width=True)

conn.close()