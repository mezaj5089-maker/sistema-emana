# componentes.py
import streamlit as st
import streamlit.components.v1 as components

def activar_rastreo_gps(usuario_activo, supabase_url, supabase_anon_key):
    """
    Inyecta un script JavaScript que monitorea la ubicación del usuario 
    y envía las coordenadas a la tabla 'ubicaciones_vendedores' en Supabase.
    """
    js_code = f"""
    <script>
    const USUARIO = "{usuario_activo}";
    const SUPABASE_URL = "{supabase_url}";
    const SUPABASE_KEY = "{supabase_anon_key}";

    async function enviarUbicacion(lat, lng) {{
        try {{
            await fetch(`${{SUPABASE_URL}}/rest/v1/ubicaciones_vendedores`, {{
                method: 'POST',
                headers: {{
                    'apikey': SUPABASE_KEY,
                    'Authorization': `Bearer ${{SUPABASE_KEY}}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'resolution=merge-duplicates'
                }},
                body: JSON.stringify({{
                    vendedor: USUARIO,
                    latitud: lat,
                    longitud: lng,
                    updated_at: new Date().toISOString()
                }})
            }});
            console.log("GPS sincronizado correctamente para:", USUARIO);
        }} catch (error) {{
            console.error("Error al enviar coordenadas:", error);
        }}
    }}

    if ("geolocation" in navigator) {{
        navigator.geolocation.watchPosition(
            (position) => {{
                enviarUbicacion(position.coords.latitude, position.coords.longitude);
            }},
            (error) => {{
                console.error("Error obteniendo GPS:", error.message);
            }},
            {{
                enableHighAccuracy: true,
                maximumAge: 10000,
                timeout: 5000
            }}
        );
    }}
    </script>
    """
    components.html(js_code, height=0)