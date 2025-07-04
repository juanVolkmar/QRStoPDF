import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from uuid import uuid4
import io
from reportlab.lib.utils import ImageReader

left, right = st.columns(2)

with left:

    # Si no hay clave en sesión, crea una por defecto
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = str(uuid4())

    # Botón para limpiar
    if st.button("🧹 Limpiar archivos"):
        st.session_state.uploader_key = str(uuid4())

    uploaded_files = st.file_uploader("Subir imagenes a imprimir", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=st.session_state.uploader_key)
    
    if uploaded_files:
        with left:
            for img in uploaded_files:
                image = Image.open(img)
                st.image(image, use_container_width=True)
    with right:
        with st.form("Guardar PDF"):
            nombre = st.text_input("Nombre: ", key="pdf_name")
            pdf = st.form_submit_button("📦 Generar PDF")
            
        if pdf and uploaded_files and nombre:
            factor_escala = 3  # Aumentar resolución 2x
            ancho_pagina, alto_pagina = A4
            cols, rows = 2, 3
            padding = 10
            margen = 20
            ancho_imagen = (ancho_pagina - 2 * margen - (cols - 1) * padding) / cols
            alto_imagen = (alto_pagina - 2 * margen - (rows - 1) * padding) / rows

            # Crear PDF en memoria
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)

            for idx, f in enumerate(uploaded_files):
                # Abrir y aumentar resolución
                img = Image.open(f).convert("RGB")
                w, h = img.size
                img_mejorada = img.resize((w * factor_escala, h * factor_escala), Image.LANCZOS)

                # Guardar temporalmente en memoria
                temp_img = io.BytesIO()
                img_mejorada.save(temp_img, format="JPEG", dpi=(300, 300))
                temp_img.seek(0)
                img_reader = ImageReader(temp_img)

                # Calcular posición
                i = idx % (cols * rows)
                col = i % cols
                row = i // cols
                x = margen + col * (ancho_imagen + padding)
                y = alto_pagina - margen - (row + 1) * alto_imagen - row * padding

                # Dibujar imagen
                pdf.drawImage(img_reader, x, y, width=ancho_imagen, height=alto_imagen, preserveAspectRatio=True, mask='auto')

                # Nueva página cada 6 imágenes
                if (idx + 1) % (cols * rows) == 0:
                    pdf.showPage()

            pdf.save()
            buffer.seek(0)
            st.success("✅ PDF Guardado")

            if ".pdf" in nombre:
                st.download_button("📥 Descargar PDF", data=buffer, file_name=nombre, mime="application/pdf")
            else:
                st.download_button("📥 Descargar PDF", data=buffer, file_name=nombre + ".pdf", mime="application/pdf")       
