# rutas.py
import pandas as pd
import streamlit as st


def mostrar_modulo_rutas_gps(supabase_client):
    """
    Muestra la interfaz de monitoreo GPS en el panel de Administración.
    """
    st.subheader("📍 Monitoreo y Rutas GPS en Vivo")

    try:
        # Consultar ubicaciones registradas en Supabase
        res = (
            supabase_client.table("ubicaciones_vendedores")
            .select("*")
            .execute()
        )
        datos = res.data

        if not datos:
            st.info(
                "No hay registros de ubicaciones activas en este momento."
            )
            return

        df = pd.DataFrame(datos)

        # Desplegable para elegir a cualquier colaborador que haya reportado GPS
        usuarios = df["vendedor"].unique().tolist()
        usuario_sel = st.selectbox("Seleccionar Personal en Campo:", usuarios)

        info = df[df["vendedor"] == usuario_sel].iloc[0]
        lat, lng, ultima_act = info["latitud"], info["longitud"], info["updated_at"]

        st.caption(f"🕒 **Última señal recibida:** {ultima_act}")

        # Mapa centrado en la posición real
        df_mapa = pd.DataFrame([{"lat": lat, "lon": lng}])
        st.map(df_mapa, zoom=15)

        # Enlace directo
        st.markdown(
            f"[🗺️ Ver punto exacto en Google Maps](https://www.google.com/maps?q={lat},{lng})",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"Error al cargar las ubicaciones: {e}")