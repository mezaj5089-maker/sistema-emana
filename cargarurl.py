with col_vid_int:
    st.subheader("🎬 Spot Promocional")
    st.markdown('<div class="video-container">', unsafe_allow_html=True)

    # 1. Cargar URL persistente desde Supabase
    url_actual_video = obtener_url_video_promo()
    st.video(url_actual_video)

    # 2. Control exclusivo para ADMIN
    if st.session_state.get("rol") == "ADMIN":
        st.divider()
        st.caption("⚙️ **Configuración de Video (Solo Admin)**")

        # Opción A: Actualizar mediante enlace (YouTube o MP4 directo)
        v_input = st.text_input("Enlace (YouTube / URL MP4)", value=url_actual_video)
        if st.button("Actualizar Enlace"):
            if actualizar_url_video_promo(v_input):
                st.success("✅ Enlace actualizado y visible para todos los usuarios.")
                st.rerun()

        # Opción B: Subir desde la PC a Supabase Storage + BD
        v_file = st.file_uploader("O subir video desde la PC (MP4 / MOV)", type=["mp4", "mov"])
        if v_file is not None:
            if st.button("🚀 Subir Video a Supabase"):
                with st.spinner("Subiendo video al bucket y actualizando base de datos..."):
                    nombre_archivo = f"video_promo_{int(datetime.datetime.now().timestamp())}.mp4"
                    url_publica = guardar_video_supabase(v_file, nombre_archivo)

                    if url_publica:
                        if actualizar_url_video_promo(url_publica):
                            st.success("✅ Video subido y sincronizado globalmente.")
                            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)