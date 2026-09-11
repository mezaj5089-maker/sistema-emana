import time
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


def componente_rastreo_gps(vendedor_id, url_supabase, anon_key_supabase):
    """Componente JavaScript invisible para rastreo GPS en tiempo real.

    Captura las coordenadas del navegador y las envía directamente a Supabase.
    """
    javascript_gps = f"""
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script>
      const SUPABASE_URL = "{url_supabase}";
      const SUPABASE_KEY = "{anon_key_supabase}";
      const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
      const idVendedor = "{vendedor_id}";

      async function enviarUbicacion(lat, lng) {{
        try {{
          const {{ data, error }} = await supabase
            .from('ubicaciones_vendedores')
            .upsert(
              {{
                vendedor: idVendedor,
                latitud: lat,
                longitud: lng,
                updated_at: new Date().toISOString()
              }},
              {{ onConflict: 'vendedor' }}
            );

          if (error) console.error("Error GPS Supabase:", error.message);
          else console.log("Ubicación GPS sincronizada:", lat, lng);
        }} catch (err) {{
          console.error("Error de conexión GPS:", err);
        }}
      }}

      if ("geolocation" in navigator) {{
        navigator.geolocation.watchPosition(
          (position) => {{
            enviarUbicacion(position.coords.latitude, position.coords.longitude);
          }},
          (error) => {{
            console.warn("Error en lectura GPS: " + error.message);
          }},
          {{
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
          }}
        );
      }} else {{
        console.error("El navegador no soporta geolocalización.");
      }}
    </script>
    """
    components.html(javascript_gps, height=0, width=0)


def mostrar_modulo_rutas_gps(supabase_client):
    """Muestra el monitoreo en vivo para Administradores y activa el rastreo

    GPS si el usuario es un Vendedor/Colaborador.
    """
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("📍 Monitoreo y Rutas GPS en Vivo")
    with col2:
        if st.button("🔄 Actualizar Mapa"):
            st.rerun()

    # 1. Si el usuario logueado es un colaborador/vendedor, se activa el rastreo
    usuario_actual = st.session_state.get("usuario") or st.session_state.get("user_id") or "vendedor_anonimo"
    
    # Obtención de credenciales desde Streamlit Secrets o Variables de Entorno
    url_supabase = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key_supabase = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

    if url_supabase and key_supabase:
        componente_rastreo_gps(usuario_actual, url_supabase, key_supabase)

    # 2. Visualización y Control de Datos desde Supabase
    try:
        res = supabase_client.table("ubicaciones_vendedores").select("*").execute()
        datos = res.data

        if not datos:
            st.info("No hay registros de ubicaciones activas en este momento.")
            return

        df = pd.DataFrame(datos)

        # Mapa interactivo
        st.write("### 🗺️ Vendedores Activos")
        st.map(df, latitude="latitud", longitude="longitud")

        # Tabla detallada
        st.dataframe(df, use_container_width=True)

        # 3. Panel de Administrador: Editar parámetros manualmente
        if st.session_state.get("rol") == "ADMIN":
            st.divider()
            st.write("⚙️ **Modificar Ubicación Manualmente (Modo Administrador)**")

            vendedores_lista = df["vendedor"].unique().tolist()
            vendedor_sel = st.selectbox("Seleccionar Vendedor/Colaborador", vendedores_lista)

            if vendedor_sel:
                row_sel = df[df["vendedor"] == vendedor_sel].iloc[0]
                nueva_lat = st.number_input("Latitud", value=float(row_sel["latitud"]), format="%.6f")
                nueva_lng = st.number_input("Longitud", value=float(row_sel["longitud"]), format="%.6f")

                if st.button("Guardar Cambios de Ubicación"):
                    supabase_client.table("ubicaciones_vendedores").update({
                        "latitud": nueva_lat,
                        "longitud": nueva_lng
                    }).eq("vendedor", vendedor_sel).execute()

                    st.success(f"Ubicación de {vendedor_sel} actualizada correctamente.")
                    st.rerun()

    except Exception as e:
        st.error(f"Error al cargar las rutas GPS: {e}")