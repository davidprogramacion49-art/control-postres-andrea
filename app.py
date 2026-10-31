import streamlit as st
import pandas as pd
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

# --- ESTILOS CSS PERSONALIZADOS (Diseño Bonito y Botones Grandes para Celular) ---
st.markdown("""
    <style>
    /* Fondo global suave y tipografía limpia */
    .stApp {
        background-color: #faf6f0;
    }
    
    /* Títulos elegantes */
    h1, h2, h3 {
        color: #5c3d2e;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
    }
    
    /* Tarjetas de postres y datos */
    .card-postre {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border-left: 5px solid #ffb7b2;
    }
    
    /* Botones más grandes y fáciles de presionar en pantalla táctil */
    div.stButton > button:first-child {
        background-color: #ffb7b2 !important;
        color: #5c3d2e !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 20px !important;
        width: 100% !important; /* Ancho completo en móvil */
        box-shadow: 0 3px 6px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:active {
        transform: scale(0.98);
    }
    
    /* Pestañas más móviles-friendly */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        overflow-x: auto; /* Desplazamiento horizontal si no caben */
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado Minimalista
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🧁 Postres Andrea</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8d7b68; font-size: 14px;'>Control Diario desde tu Celular</p>", unsafe_allow_html=True)

# Gastos Fijos Diarios Base
GASTOS_FIJOS_DIARIOS = 15.0

# Pestañas con emojis cortos para que quepan bien en barra móvil
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Salida/Cierre", 
    "🧁 Catálogo", 
    "🛒 Compras", 
    "🏢 Gastos", 
    "📊 Balance"
])

# --- PESTAÑA 1: OPERACIÓN DIARIA ---
with tab1:
    st.markdown("<h3 style='margin-top:10px;'>☀️ 1. Salida por la Mañana</h3>", unsafe_allow_html=True)
    try:
        res_cat = supabase.table("catalogo_postres").select("nombre_postre, precio_lista").execute()
        df_cat_op = pd.DataFrame(res_cat.data)
    except Exception:
        df_cat_op = pd.DataFrame()
        
    if df_cat_op.empty:
        st.warning("⚠️ Primero da de alta un postre en la pestaña 'Catálogo'.")
    else:
        with st.form("form_salida_calle", clear_on_submit=True):
            fecha_op = st.date_input("Fecha de Operación", datetime.now(), key="fecha_op")
            postre_sel = st.selectbox("¿Qué postre sale?", df_cat_op['nombre_postre'].tolist())
            cant_prep = st.number_input("Cantidad Preparada", min_value=1, step=1)
            
            if st.form_submit_button("🚀 Registrar Salida a Calle"):
                supabase.table("produccion_ventas").insert({
                    "fecha": str(fecha_op),
                    "nombre_postre": postre_sel,
                    "cantidad_preparada": cant_prep,
                    "cantidad_sobrante": 0,
                    "efectivo_real_recaudado": 0.0
                }).execute()
                st.success(f"📦 ¡Registradas {cant_prep} pzas de {postre_sel}!")
                st.rerun()
                    
    st.markdown("<hr style='margin:20px 0; border-color:#e6dfd5;'>", unsafe_allow_html=True)
    st.markdown("<h3>🌙 2. Cierre de Caja</h3>", unsafe_allow_html=True)
    
    try:
        res_v = supabase.table("produccion_ventas").select("*").execute()
        df_actual = pd.DataFrame(res_v.data)
    except Exception:
        df_actual = pd.DataFrame()
        
    if not df_actual.empty:
        fechas_act = df_actual['fecha'].unique()
        f_sel = st.selectbox("Elige la fecha a cerrar:", fechas_act)
        df_filtrado_cierre = df_actual[df_actual['fecha'] == f_sel]
        
        for idx, row in df_filtrado_cierre.iterrows():
            with st.expander(f"🍰 {row['nombre_postre']} ({row['cantidad_preparada']} pzas)"):
                with st.form(f"form_cierre_{row['id']}"):
                    sob = st.number_input("Sobraron (Merma)", min_value=0, max_value=int(row['cantidad_preparada']), value=int(row['cantidad_sobrante']))
                    efec = st.number_input("Efectivo Recaudado ($)", min_value=0.0, value=float(row['efectivo_real_recaudado']))
                    
                    if st.form_submit_button("💾 Guardar este Producto"):
                        supabase.table("produccion_ventas").update({
                            "cantidad_sobrante": sob,
                            "efectivo_real_recaudado": efec
                        }).eq("id", row['id']).execute()
                        st.success("¡Guardado!")
                        st.rerun()
                    
                    if st.checkbox("⚠️ Activar botón de borrar", key=f"del_{row['id']}"):
                        if st.form_submit_button("🗑️ ELIMINAR REGISTRO PERMANENTEMENTE"):
                            supabase.table("produccion_ventas").delete().eq("id", row['id']).execute()
                            st.warning("Eliminado de la nube.")
                            st.rerun()

# --- PESTAÑA 2: CATÁLOGO ---
with tab2:
    st.markdown("<h3 style='margin-top:10px;'>➕ Nuevo Producto</h3>", unsafe_allow_html=True)
    with st.form("form_catalogo", clear_on_submit=True):
        nuevo_postre = st.text_input("Nombre del Postre (Ej: Chocoflan)")
        p_lista = st.number_input("Precio de Venta ($)", min_value=0.0, value=35.0)
        c_insumos = st.number_input("Costo Ingredientes por Vaso ($)", min_value=0.0, value=10.0)
        c_empaque = st.number_input("Costo Desechables por Vaso ($)", min_value=0.0, value=3.0)
        if st.form_submit_button("✨ Guardar en Catálogo"):
            supabase.table("catalogo_postres").insert({
                "nombre_postre": nuevo_postre,
                "precio_lista": p_lista,
                "costo_insumos_promedio": c_insumos,
                "costo_empaque_promedio": c_empaque
            }).execute()
            st.success(f"¡{nuevo_postre} agregado!")
            st.rerun()
                
    st.markdown("<hr style='margin:20px 0; border-color:#e6dfd5;'>", unsafe_allow_html=True)
    st.markdown("<h3>📋 Lista de Postres</h3>", unsafe_allow_html=True)
    try:
        res_c = supabase.table("catalogo_postres").select("*").execute()
        df_cat = pd.DataFrame(res_c.data)
    except Exception:
        df_cat = pd.DataFrame()
        
    if not df_cat.empty:
        for idx, row in df_cat.iterrows():
            costo_total = row['costo_insumos_promedio'] + row['costo_empaque_promedio']
            st.markdown(f"""
                <div class="card-postre">
                    <span style='font-size:12px; color:#8d7b68; float:right;'>ID: {row['id']}</span>
                    <strong style='font-size:18px; color:#5c3d2e;'>{row['nombre_postre']}</strong><br>
                    <span style='color:#4caf50;'>💰 Venta: ${row['precio_lista']:.2f}</span> | 
                    <span style='color:#f44336;'>📉 Costo: ${costo_total:.2f}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with st.expander("🗑️ Dar de baja un producto"):
            id_borrar = st.number_input("ID del producto a eliminar:", min_value=1, step=1)
            if st.button("Confirmar Eliminación"):
                supabase.table("catalogo_postres").delete().eq("id", id_borrar).execute()
                st.success("Eliminado con éxito.")
                st.rerun()

# --- PESTAÑA 3: COMPRAS ---
with tab3:
    st.markdown("<h3 style='margin-top:10px;'>🛒 Registrar Compra / Inversión</h3>", unsafe_allow_html=True)
    with st.form("form_inv", clear_on_submit=True):
        fecha_inv = st.date_input("Fecha de Compra", datetime.now())
        concepto_inv = st.text_input("¿Qué compraste? (Ej: Fresas, Vasos de 8oz)")
        monto_inv = st.number_input("Monto Gastado ($)", min_value=0.0)
        tipo_insumo = st.selectbox("Categoría", ["Materia Prima", "Desechables", "Otros"])
        if st.form_submit_button("✅ Sincronizar Compra"):
            supabase.table("inventario_compras").insert({
                "fecha": str(fecha_inv),
                "concepto": concepto_inv,
                "monto_gastado": monto_inv,
                "tipo_insumo": tipo_insumo
            }).execute()
            st.success("¡Compra registrada correctamente!")

# --- PESTAÑA 4: GASTOS OPERATIVOS ---
with tab4:
    st.header("🏢 Gastos Operativos")
    with st.form("form_g", clear_on_submit=True):
        fecha_g = st.date_input("Fecha del Gasto", datetime.now())
        concepto_g = st.text_input("Concepto (Ej: Pasajes, Gasolina)")
        monto_g = st.number_input("Monto ($)", min_value=0.0)
        tipo_g = st.selectbox("Tipo", ["Gasto Diario", "Sueldos", "Gasto Fijo Mensual Casa"])
        if st.form_submit_button("💾 Guardar Gasto"):
            supabase.table("gastos_operacion").insert({
                "fecha": str(fecha_g),
                "concepto": concepto_g,
                "monto": monto_g,
                "tipo_gasto": tipo_g
            }).execute()
            st.success("Gasto guardado.")

# --- PESTAÑA 5: TABLERO FINANCIERO (VISTA MÓVIL OPTIMIZADA) ---
with tab5:
    st.markdown("<h3 style='margin-top:10px;'>📊 Resultados del Día</h3>", unsafe_allow_html=True)
    try:
        res_v = supabase.table("produccion_ventas").select("*").execute()
        df_v = pd.DataFrame(res_v.data)
        res_c = supabase.table("catalogo_postres").select("*").execute()
        df_c = pd.DataFrame(res_c.data)
        res_g = supabase.table("gastos_operacion").select("*").execute()
        df_g = pd.DataFrame(res_g.data)
    except Exception:
        df_v, df_c, df_g = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
    if df_v.empty or df_c.empty:
        st.info("Registra datos de ventas hoy para generar el reporte diario.")
    else:
        df_m = pd.merge(df_v, df_c, on='nombre_postre', how='left')
        df_m['piezas_vendidas'] = df_m['cantidad_preparada'] - df_m['cantidad_sobrante']
        df_m['costo_produccion_total'] = df_m['cantidad_preparada'] * (df_m['costo_insumos_promedio'].fillna(0) + df_m['costo_empaque_promedio'].fillna(0))
        
        df_m['fecha'] = pd.to_datetime(df_m['fecha']).dt.date
        fechas_disponibles = df_m['fecha'].unique()
        dia_sel = st.selectbox("Fecha a evaluar:", fechas_disponibles, key="tab5_dia")
        
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
                <div style='background-color:#e8f4f8; padding:15px; border-radius:12px; margin-bottom:10px; border-left:5px solid #2196f3;'>
                    <span style='color:#555; font-size:14px;'>💰 Efectivo Recaudado</span><br>
                    <strong style='font-size:24px; color:#0d47a1;'>${ingresos_efectivo:,.2f}</strong>
                </div>
                <div style='background-color:#fdf2f2; padding:15px; border-radius:12px; margin-bottom:10px; border-left:5px solid #f44336;'>
                    <span style='color:#555; font-size:14px;'>📉 Inversión Insumos/Vasos</span><br>
                    <strong style='font-size:22px; color:#b71c1c;'>${costo_prod_total:,.2f}</strong>
                </div>
                <div style='background-color:#fff9db; padding:15px; border-radius:12px; margin-bottom:15px; border-left:5px solid #f59f00;'>
                    <span style='color:#555; font-size:14px;'>🚌 Gastos Operativos del Día</span><br>
                    <strong style='font-size:22px; color:#f59f00;'>${gastos_totales_fijos_dia:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(
                f"<div style='background-color:#d4edda; padding:18px; border-radius:16px; text-align:center; border: 2px solid #c3e6cb; margin-bottom:15px;'>"
                f"<p style='margin:0; color:#155724; font-size:16px; font-weight:bold;'>✨ Utilidad Neta (Tu Bolsillo) ✨</p>"
                f"<h1 style='margin:5px 0 0 0; color:#155724; font-size:36px;'>${utilidad_neta_dia:,.2f}</h1>"
                f"<p style='margin:0; font-size:13px; color:#155724;'>Margen Real Neto: {m_neto:.1f}%</p>"
                f"</div>", unsafe_allow_html=True
            )
            
            st.markdown("<h4>📋 Rendimiento por Producto</h4>", unsafe_allow_html=True)
            for idx, row in df_dia.iterrows():
                st.markdown(f"""
                    <div style='background-color:#fff; padding:12px; border-radius:10px; margin-bottom:8px; border:1px solid #ebdcd0;'>
                        <strong>{row['nombre_postre']}</strong><br>
                        <span style='font-size:13px; color:#666;'>Prep: {row['cantidad_preparada']} pzas | Sobró: {row['cantidad_sobrante']} mermas</span><br>
                        <span style='font-size:14px; color:#4caf50; font-weight:bold;'>Vendidas: {row['piezas_vendidas']} pzas → Recaudado: ${row['efectivo_real_recaudado']:.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            mermas_totales = df_dia['cantidad_sobrante'].sum()
            if mermas_totales > 0:
                st.warning(f"⚠️ Hoy tuviste {mermas_totales} mermas. ¡Intenta ajustar la producción mañana!")
