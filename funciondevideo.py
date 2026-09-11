import streamlit as st
import datetime
from supabase import create_client

# --- FUNCIÓN PARA OBTENER EL VIDEO DESDE SUPABASE ---
def obtener_url_video_promo():
    try:
        res = supabase.table("configuracion").select("valor").eq("clave", "promo_video_url").execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["valor"]
    except Exception as e:
        st.error(f"Error al obtener video de la BD: {e}")
    return "https://www.w3schools.com/html/mov_bbb.mp4"

# --- FUNCIÓN PARA GUARDAR LA NUEVA URL EN SUPABASE ---
def actualizar_url_video_promo(nueva_url):
    try:
        supabase.table("configuracion").upsert({
            "clave": "promo_video_url",
            "valor": nueva_url
        }).execute()
        st.session_state["promo_video_url"] = nueva_url
        return True
    except Exception as e:
        st.error(f"Error al actualizar la URL en la BD: {e}")
        return False