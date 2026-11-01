import pandas as pd import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE BASE DE DATOS EN LA NUBE (SUPABASE)
SUPABASE_URL = "https://ltlqsavejphagjbjteir.supabase.co"
SUPABASE_KEY = "sb_publishable__pvOHbpHtPZoJekPn_sRBw_NKwLzZ_j"

@st.cache_resource
def conectar_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = conectar_supabase()

# 2. CONFIGURACIÓN DE LA INTERFAZ WEB (OPTIMIZADA PARA MÓVIL)
st.set_page_config(page_title="Postres Andrea", page_icon="🍰", layout="centered")

# --- PARCHE DE CONTROL INVISIBLE: ELIMINA LA BARRA SUPERIOR Y CORRIGE EL DISEÑO MÓVIL ---
st.markdown("""
    <style>
    /* Ocultar barra superior de Streamlit (Fork, GitHub y menú de 3 puntos bugeado) */
    header, [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Forzar fondo claro permanente para evitar errores de modo oscuro del celular */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #faf6f0 !important;
    }
    
    /* Tipografía global limpia */
    h1, h2, h3, h4, p, span, label, div {
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif !important;
    }
    
    .main-title {
        text-align: center; 
        color: #4a3728; 
        font-weight: 800; 
        margin-top: 15px;
        margin-bottom: 0px;
        font-size: 28px;
    }
    .sub-title {
        text-align: center; 
        color: #8c7a6b; 
        font-size: 13px; 
        margin-bottom: 15px;
    }

    /* Botones adaptables y grandes para el dedo en celular */
    div.stButton > button:first-child {
        color: #4a3728 !important;
        font-weight: bold !important;
        border-radius: 14px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        padding: 12px 20px !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:first-child:active {
        transform: scale(0.97);
    }
    
    /* Configuración de pestañas en móvil */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        overflow-x: auto;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 14px !important;
        background-color: #ffffff !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #7a685a !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
    }
    
    /* Estilos de los contenedores por sección */
    .seccion-container {
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.03);
        margin-top: 10px;
        border: 1px solid rgba(0,0,0,0.02);
    }
    
    /* Tarjetas internas para datos */
    .tarjeta-blanca {
        background-color: #ffffff;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.02);
        border: 1px solid rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado Principal Limpio
st.markdown("<div class='main-title'>🍰 Postres Andrea</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Gestión Comercial Móvil Avanzada</div>", unsafe_allow_html=True)

# --- PANEL EXCLUSIVO DE CONTROL MÓVIL REPARADO ---
with st.expander("⚙️ Panel Administrativo Especial"):
    st.markdown("### 📄 Generar Informe Diario")
    
    try:
        res_v_ticket = supabase.table("produccion_ventas").select("*").execute()
        df_ticket_base = pd.DataFrame(res_v_ticket.data)
    except Exception:
        df_ticket_base = pd.DataFrame()
        
    if not df_ticket_base.empty:
        df_ticket_base['fecha'] = pd.to_datetime(df_ticket_base['fecha']).dt.date
        fechas_ticket = df_ticket_base['fecha'].unique()
        fecha_rep = st.selectbox("Elige la fecha para exportar:", fechas_ticket, key="fecha_rep")
        
        df_dia_t = df_ticket_base[df_ticket_base['fecha'] == fecha_rep]
        ticket_texto = f"================================\n"
        ticket_texto += f"       POSTRES ANDREA           \n"
        ticket_texto += f"   REPORTES DESDE EL CELULAR    \n"
        ticket_texto += f"================================\n"
        ticket_texto += f"Fecha Evaluada: {fecha_rep}\n"
        ticket_texto += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        ticket_texto += f"--------------------------------\n"
        
        total_efectivo = 0.0
        for _, r in df_dia_t.iterrows():
            ticket_texto += f"- {r['nombre_postre']}:\n"
            ticket_texto += f"  Preparados: {r['cantidad_preparada']} | Sobrantes: {r['cantidad_sobrante']}\n"
            ticket_texto += f"  Efectivo Caja: ${r['efectivo_real_recaudado']:.2f}\n"
            total_efectivo += float(r['efectivo_real_recaudado'])
            
        ticket_texto += f"--------------------------------\n"
        ticket_texto += f"TOTAL EFECTIVO RECAUDADO: ${total_efectivo:.2f}\n"
        ticket_texto += f"================================\n"
        
        st.download_button(
            label="📥 Bajar Reporte de Caja (.TXT)",
            data=ticket_texto,
            file_name=f"informe_{fecha_rep}.txt",
            mime="text/plain"
        )
    else:
        st.info("No hay datos cargados aún.")

    st.markdown("---")
    st.markdown("### 🚨 Limpieza General de Temporada")
    st.write("Usa esta casilla únicamente si deseas reiniciar el historial de ventas, gastos y compras de la nube.")
    
    seguridad_borrado = st.checkbox("Entiendo que esto vaciará los movimientos acumulados.")
    if seguridad_borrado:
        if st.button("🗑️ VACIAR BASE DE DATOS OPERATIVA"):
            try:
                supabase.table("produccion_ventas").delete().gt("id", 0).execute()
                supabase.table("inventario_compras").delete().gt("id", 0).execute()
                supabase.table("gastos_operacion").delete().gt("id", 0).execute()
                st.success("💥 Historial operativo vaciado con éxito.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# Inicializar Tabs con nombres cortos
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Salidas", 
    "🧁 Menú", 
    "🛒 Compras", 
    "🏢 Gastos", 
    "📊 Balance"
])

# --- PESTAÑA 1: OPERACIÓN DIARIA (Rosa Pastel) ---
with tab1:
    st.markdown("<style>.tab-rosa { background-color: #fff4f2; } .tab-rosa div.stButton > button:first-child { background-color: #ffdad6 !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='seccion-container tab-rosa'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #824943; margin-top:0;'>☀️ Registrar Salida Matutina</h3>", unsafe_allow_html=True)
    
    try:
        res_cat = supabase.table("catalogo_postres").select("nombre_postre").execute()
        df_cat_op = pd.DataFrame(res_cat.data)
    except Exception:
        df_cat_op = pd.DataFrame()
        
    if df_cat_op.empty:
        st.warning("⚠️ Ve a la pestaña '🧁 Menú' para dar de alta postres.")
    else:
        with st.form("form_salida_calle", clear_on_submit=True):
            fecha_op = st.date_input("Fecha", datetime.now(), key="fecha_op")
            postre_sel = st.selectbox("¿Qué postre se lleva?", df_cat_op['nombre_postre'].tolist())
            cant_prep = st.number_input("Cantidad Preparada", min_value=1, step=1)
            
            if st.form_submit_button("🚀 Confirmar Salida a Calle"):
                supabase.table("produccion_ventas").insert({
                    "fecha": str(fecha_op),
                    "nombre_postre": postre_sel,
                    "cantidad_preparada": cant_prep,
                    "cantidad_sobrante": 0,
                    "efectivo_real_recaudado": 0.0
                }).execute()
                st.success(f"Sincronizado: {cant_prep} {postre_sel}")
                st.rerun()
                
    st.markdown("<hr style='border-color:#ebdcd9; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #824943;'>🌙 Cierre de Venta Ambulante</h3>", unsafe_allow_html=True)
    
    if not df_ticket_base.empty:
        fechas_act = df_ticket_base['fecha'].unique()
        f_sel = st.selectbox("Selecciona Fecha de Cierre:", fechas_act)
        df_filtrado_cierre = df_ticket_base[df_ticket_base['fecha'] == f_sel]
        
        for idx, row in df_filtrado_cierre.iterrows():
            with st.expander(f"📦 {row['nombre_postre']} ({row['cantidad_preparada']} pzas)"):
                with st.form(f"form_cierre_{row['id']}"):
                    sob = st.number_input("Mermas (Sobrantes)", min_value=0, max_value=int(row['cantidad_preparada']), value=int(row['cantidad_sobrante']))
                    efec = st.number_input("Efectivo Contado ($)", min_value=0.0, value=float(row['efectivo_real_recaudado']))
                    
                    if st.form_submit_button("💾 Actualizar Valores"):
                        supabase.table("produccion_ventas").update({
                            "cantidad_sobrante": sob,
                            "efectivo_real_recaudado": efec
                        }).eq("id", row['id']).execute()
                        st.success("¡Guardado!")
                        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 2: CATÁLOGO (Vainilla) ---
with tab2:
    st.markdown("<style>.tab-crema { background-color: #faf4e8; } .tab-crema div.stButton > button:first-child { background-color: #f3e1c3 !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='seccion-container tab-crema'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #6e583f; margin-top:0;'>🧁 Catálogo Maestro</h3>", unsafe_allow_html=True)
    
    with st.form("form_catalogo", clear_on_submit=True):
        nuevo_postre = st.text_input("Nombre de la nueva delicia")
        p_lista = st.number_input("Precio al Público ($)", min_value=0.0, value=35.0)
        c_insumos = st.number_input("Costo Ingredientes ($)", min_value=0.0, value=10.0)
        c_empaque = st.number_input("Costo Envase/Cuchara ($)", min_value=0.0, value=3.0)
        if st.form_submit_button("✨ Agregar al Menú"):
            supabase.table("catalogo_postres").insert({
                "nombre_postre": nuevo_postre,
                "precio_lista": p_lista,
                "costo_insumos_promedio": c_insumos,
                "costo_empaque_promedio": c_empaque
            }).execute()
            st.success(f"{nuevo_postre} guardado.")
            st.rerun()
            
    st.markdown("<hr style='border-color:#e6dcce; margin: 20px 0;'>", unsafe_allow_html=True)
    
    try:
        res_c = supabase.table("catalogo_postres").select("*").execute()
        df_cat = pd.DataFrame(res_c.data)
    except Exception:
        df_cat = pd.DataFrame()
        
    if not df_cat.empty:
        st.markdown("<h4>Productos Activos</h4>", unsafe_allow_html=True)
        for idx, row in df_cat.iterrows():
            c_tot = row['costo_insumos_promedio'] + row['costo_empaque_promedio']
            st.markdown(f"""
                <div class="tarjeta-blanca">
                    <span style='float:right; font-size:11px; color:#9c8a77;'>ID: {row['id']}</span>
                    <b style='color:#54412d; font-size:16px;'>{row['nombre_postre']}</b><br>
                    <span style='color:#2e7d32; font-size:13px;'>💰 Venta: ${row['precio_lista']:.2f}</span> | 
                    <span style='color:#c62828; font-size:13px;'>📉 Costo: ${c_tot:.2f}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 3: COMPRAS (Azul Menta) ---
with tab3:
    st.markdown("<style>.tab-azul { background-color: #eff7f6; } .tab-azul div.stButton > button:first-child { background-color: #cce3de !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='seccion-container tab-azul'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #3b585c; margin-top:0;'>🛒 Compra de Insumos</h3>", unsafe_allow_html=True)
    
    with st.form("form_inv", clear_on_submit=True):
        fecha_inv = st.date_input("Fecha de Adquisición", datetime.now())
        concepto_inv = st.text_input("Detalle (Ej: Bulto de Azúcar, Domos)")
        monto_inv = st.number_input("Costo Total Abonado ($)", min_value=0.0)
        tipo_insumo = st.selectbox("Familia de Producto", ["Materia Prima", "Desechables", "Otros"])
        if st.form_submit_button("💾 Registrar Factura/Ticket"):
            supabase.table("inventario_compras").insert({
                "fecha": str(fecha_inv),
                "concepto": concepto_inv,
                "monto_gastado": monto_inv,
                "tipo_insumo": tipo_insumo
            }).execute()
            st.success("Compra almacenada en la nube.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 4: GASTOS OPERATIVOS (Lavanda) ---
with tab4:
    st.markdown("<style>.tab-lila { background-color: #f7f2fa; } .tab-lila div.stButton > button:first-child { background-color: #e8def8 !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='seccion-container tab-lila'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #554461; margin-top:0;'>🏢 Gastos Logísticos</h3>", unsafe_allow_html=True)
    
    with st.form("form_g", clear_on_submit=True):
        fecha_g = st.date_input("Fecha de Egreso", datetime.now())
        concepto_g = st.text_input("Concepto (Ej: Pasajes de Autobús)")
        monto_g = st.number_input("Importe ($)", min_value=0.0)
        tipo_g = st.selectbox("Clase de Gasto", ["Gasto Diario", "Sueldos", "Gasto Fijo Mensual Casa"])
        if st.form_submit_button("📌 Registrar Egreso"):
            supabase.table("gastos_operacion").insert({
                "fecha": str(fecha_g),
                "concepto": concepto_g,
                "monto": monto_g,
                "tipo_gasto": tipo_g
            }).execute()
            st.success("Gasto registrado.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 5: TABLERO FINANCIERO (Verde Pistache) ---
with tab5:
    st.markdown("<style>.tab-verde { background-color: #f4f9f4; }</style>", unsafe_allow_html=True)
    st.markdown("<div class='seccion-container tab-verde'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #3b5c3d; margin-top:0;'>📊 Resultados Comerciales</h3>", unsafe_allow_html=True)
    
    try:
        res_c = supabase.table("catalogo_postres").select("*").execute()
        df_c = pd.DataFrame(res_c.data)
        res_g = supabase.table("gastos_operacion").select("*").execute()
        df_g = pd.DataFrame(res_g.data)
    except Exception:
        df_c, df_g = pd.DataFrame(), pd.DataFrame()
        
    if df_ticket_base.empty or df_c.empty:
        st.info("Introduce registros de operaciones para visualizar las utilidades.")
    else:
        df_m = pd.merge(df_ticket_base, df_c, on='nombre_postre', how='left')
        df_m['piezas_vendidas'] = df_m['cantidad_preparada'] - df_m['cantidad_sobrante']
        df_m['costo_produccion_total'] = df_m['cantidad_preparada'] * (df_m['costo_insumos_promedio'].fillna(0) + df_m['costo_empaque_promedio'].fillna(0))
        
        fechas_disponibles = df_m['fecha'].unique()
        dia_sel = st.selectbox("Día de análisis comercial:", fechas_disponibles, key="tab5_dia")
        
        df_dia = df_m[df_m['fecha'] == dia_sel]
        
        if not df_g.empty:
            df_g['fecha'] = pd.to_datetime(df_g['fecha']).dt.date
            gastos_dia = df_g[(df_g['fecha'] == dia_sel) & (df_g['tipo_gasto'] != "Gasto Fijo Mensual Casa")]['monto'].sum()
            gastos_mes = df_g[df_g['tipo_gasto'] == "Gasto Fijo Mensual Casa"]['monto'].sum()
            costo_fijo_prorrateado = gastos_mes / 30 if gastos_mes > 0 else 0.0
        else:
            gastos_dia = 0.0
            costo_fijo_prorrateado = 0.0
            
        gastos_totales_fijos_dia = gastos_dia + costo_fijo_prorrateado
        
        if not df_dia.empty:
            ingresos_efectivo = df_dia['efectivo_real_recaudado'].sum()
            costo_prod_total = df_dia['costo_produccion_total'].sum()
            
            utilidad_bruta_dia = ingresos_efectivo - costo_prod_total
            utilidad_neta_dia = utilidad_bruta_dia - gastos_totales_fijos_dia
            m_neto = (utilidad_neta_dia / ingresos_efectivo) * 100 if ingresos_efectivo > 0 else 0
            
            st.markdown(f"""
                <div style='background-color:#ffffff; padding:14px; border-radius:12px; margin-bottom:8px; border-left:4px solid #4caf50;'>
                    <span style='color:#666; font-size:13px;'>💰 Ventas Totales Recaudadas</span><br>
                    <strong style='font-size:22px; color:#1b5e20;'>${ingresos_efectivo:,.2f}</strong>
                </div>
                <div style='background-color:#ffffff; padding:14px; border-radius:12px; margin-bottom:8px; border-left:4px solid #e53935;'>
                    <span style='color:#666; font-size:13px;'>📉 Inversión en Producción</span><br>
                    <strong style='font-size:20px; color:#b71c1c;'>${costo_prod_total:,.2f}</strong>
                </div>
                <div style='background-color:#ffffff; padding:14px; border-radius:12px; margin-bottom:12px; border-left:4px solid #ffb300;'>
                    <span style='color:#666; font-size:13px;'>🚌 Costos y Gastos Extra del Día</span><br>
                    <strong style='font-size:20px; color:#f57f17;'>${gastos_totales_fijos_dia:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(
                f"<div style='background-color:#e8f5e9; padding:16px; border-radius:16px; text-align:center; border: 2px solid #a5d6a7; margin-bottom:15px;'>"
                f"<p style='margin:0; color:#2e7d32; font-size:14px; font-weight:bold;'>💵 Ganancia Neta Real (Tu Bolsillo)</p>"
                f"<h1 style='margin:4px 0; color:#1b5e20; font-size:34px;'>${utilidad_neta_dia:,.2f}</h1>"
                f"<p style='margin:0; font-size:12px; color:#388e3c;'>Eficiencia del Margen Neto: {m_neto:.1f}%</p>"
                f"</div>", unsafe_allow_html=True
            )
            
            st.markdown("<h4>📋 Desglose Técnico</h4>", unsafe_allow_html=True)
            for idx, row in df_dia.iterrows():
                st.markdown(f"""
                    <div class="tarjeta-blanca">
                        <b style='color:#2e7d32;'>{row['nombre_postre']}</b><br>
                        <span style='font-size:13px; color:#555;'>Fabricado: {row['cantidad_preparada']} u. | Merma: {row['cantidad_sobrante']} u.</span><br>
                        <span style='font-size:13px; font-weight:bold; color:#155724;'>Entregado en Caja: ${row['efectivo_real_recaudado']:.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

