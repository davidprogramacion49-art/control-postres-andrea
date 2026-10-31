import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE BASE DE DATOS EN LA NUBE (SUPABASE)
# Vuelve a colocar tus llaves reales aquí dentro de las comillas:
SUPABASE_URL = "https://ltlqsavejphagjbjteir.supabase.co"
SUPABASE_KEY = "sb_publishable__pvOHbpHtPZoJekPn_sRBw_NKwLzZ_j"

@st.cache_resource
def conectar_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = conectar_supabase()

# 2. CONFIGURACIÓN DE LA INTERFAZ WEB PERSONALIZADA
st.set_page_config(page_title="Control Postres Andrea", page_icon="🍰", layout="wide")
st.title("🧁 Control Postres Andrea")
st.write("Sistema en la nube para venta ambulante con control de mermas e inventario seguro.")

# Gastos Fijos Diarios Base
GASTOS_FIJOS_DIARIOS = 15.0

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Operación Diaria (Ventas y Mermas)",
    "🧁 Catálogo y Recetas Promedio",
    "🛒 Compras e Inventario",
    "🏢 Gastos de Operación",
    "📊 Tablero de Análisis y Utilidades"
])

# --- PESTAÑA 1: OPERACIÓN DIARIA ---
with tab1:
    st.header("Registro de Salida a Calle y Cierre de Caja")
    try:
        res_cat = supabase.table("catalogo_postres").select("nombre_postre, precio_lista").execute()
        df_cat_op = pd.DataFrame(res_cat.data)
    except Exception:
        df_cat_op = pd.DataFrame()
    
    if df_cat_op.empty:
        st.warning("⚠️ Primero debes dar de alta al menos un postre en la pestaña 'Catálogo y Recetas Promedio' para operar.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.subheader("1. Registrar salida por la mañana")
            with st.form("form_salida_calle", clear_on_submit=True):
                fecha_op = st.date_input("Fecha de Operación", datetime.now(), key="fecha_op")
                postre_sel = st.selectbox("Selecciona el Postre", df_cat_op['nombre_postre'].tolist())
                cant_prep = st.number_input("Cantidad Total Preparada", min_value=1, step=1)
                
                if st.form_submit_button("Registrar Salida a Calle"):
                    supabase.table("produccion_ventas").insert({
                        "fecha": str(fecha_op), "nombre_postre": postre_sel, 
                        "cantidad_preparada": cant_prep, "cantidad_sobrante": 0, "efectivo_real_recaudado": 0.0
                    }).execute()
                    st.success(f"📦 Registradas {cant_prep} unidades de {postre_sel}.")
        
        with col_f2:
            st.subheader("2. Cierre de Caja (Al regresar)")
            try:
                res_v = supabase.table("produccion_ventas").select("*").execute()
                df_actual = pd.DataFrame(res_v.data)
            except Exception:
                df_actual = pd.DataFrame()
                
            if not df_actual.empty:
                fechas_act = df_actual['fecha'].unique()
                f_sel = st.selectbox("Filtrar por fecha", fechas_act)
                df_filtrado_cierre = df_actual[df_actual['fecha'] == f_sel]
                
                for idx, row in df_filtrado_cierre.iterrows():
                    with st.expander(f"Editar: {row['nombre_postre']} ({row['cantidad_preparada']} pzas)"):
                        with st.form(f"form_cierre_{row['id']}"):
                            sob = st.number_input("Piezas SOBRANTES (Merma)", min_value=0, max_value=int(row['cantidad_preparada']), value=int(row['cantidad_sobrante']))
                            efec = st.number_input("Efectivo TOTAL Real Recaudado ($)", min_value=0.0, value=float(row['efectivo_real_recaudado']))
                            
                            if st.form_submit_button("Actualizar Cierre"):
                                supabase.table("produccion_ventas").update({
                                    "cantidad_sobrante": sob, "efectivo_real_recaudado": efec
                                }).eq("id", row['id']).execute()
                                st.success("¡Cierre de caja guardado en la nube!")
                                st.rerun()

# --- PESTAÑA 2: CATÁLOGO ---
with tab2:
    st.header("Catálogo Maestro de Postres y Costos Estándar")
    st.write("Agrega aquí tus postres con un costo estimado promedio por vaso/pieza (ingredientes + empaques como vasos o topers) y tu precio sugerido.")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        with st.form("form_catalogo", clear_on_submit=True):
            nuevo_postre = st.text_input("Nombre del Postre")
            p_lista = st.number_input("Precio de Venta Regular ($)", min_value=0.0, value=35.0)
            c_insumos = st.number_input("Costo de Ingredientes por Vaso ($)", min_value=0.0, value=10.0)
            c_empaque = st.number_input("Costo de Desechables por Vaso ($)", min_value=0.0, value=3.0)
            
            if st.form_submit_button("Guardar en Catálogo") and nuevo_postre:
                supabase.table("catalogo_postres").insert({
                    "nombre_postre": nuevo_postre, "precio_lista": p_lista,
                    "costo_insumos_promedio": c_insumos, "costo_empaque_promedio": c_empaque
                }).execute()
                st.success(f"¡{nuevo_postre} guardado en internet!")
                st.rerun()
    with col_c2:
        try:
            res_c = supabase.table("catalogo_postres").select("*").execute()
            df_cat = pd.DataFrame(res_c.data)
        except Exception:
            df_cat = pd.DataFrame()
        if not df_cat.empty:
            df_cat['Costo Total Estimado'] = df_cat['costo_insumos_promedio'] + df_cat['costo_empaque_promedio']
            df_cat['Margen Teórico (%)'] = ((df_cat['precio_lista'] - df_cat['Costo Total Estimado']) / df_cat['precio_lista']) * 100
            st.subheader("Tus Postres Registrados")
            st.dataframe(df_cat, use_container_width=True)

# --- PESTAÑA 3: COMPRAS ---
with tab3:
    st.header("Registro de Compras e Inventarios")
    with st.form("form_inv", clear_on_submit=True):
        fecha_inv = st.date_input("Fecha de Compra", datetime.now())
        concepto_inv = st.text_input("¿Qué compraste?")
        monto_inv = st.number_input("Monto Gastado ($)", min_value=0.0)
        tipo_insumo = st.selectbox("Categoría", ["Materia Prima", "Desechables", "Otros"])
        
        if st.form_submit_button("Registrar Comra") and concepto_inv:
            supabase.table("inventario_compras").insert({
                "fecha": str(fecha_inv), "concepto": concepto_inv, "monto_gastado": monto_inv, "tipo_insumo": tipo_insumo
            }).execute()
            st.success("Compra sincronizada con internet.")

# --- PESTAÑA 4: GASTOS OPERATIVOS ---
with tab4:
    st.header("Gastos del Hogar, Pasajes y Sueldos")
    with st.form("form_g", clear_on_submit=True):
        fecha_g = st.date_input("Fecha del Gasto", datetime.now())
        concepto_g = st.text_input("Concepto")
        monto_g = st.number_input("Monto ($)", min_value=0.0)
        tipo_g = st.selectbox("Tipo", ["Gasto Diario", "Sueldos", "Gasto Fijo Mensual Casa"])
        
        if st.form_submit_button("Guardar Gasto") and concepto_g:
            supabase.table("gastos_operacion").insert({
                "fecha": str(fecha_g), "concepto": concepto_g, "monto": monto_g, "tipo_gasto": tipo_g
            }).execute()
            st.success("Gasto operativo registrado.")

# --- PESTAÑA 5: TABLERO FINANCIERO ---
with tab5:
    st.header("Finanzas Líquidas en Tiempo Real")
    st.info("Aquí verás tus utilidades netas reflejadas directamente desde tu servidor seguro en internet.")
