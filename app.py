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
st.title("🧁 Control Postres Andrea (Nube)")
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
                    st.rerun()
        
        with col_f2:
            st.subheader("2. Cierre de Caja y Modificaciones")
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
                    with st.expander(f"⚙️ {row['nombre_postre']} ({row['cantidad_preparada']} pzas) - ID: {row['id']}"):
                        with st.form(f"form_cierre_{row['id']}"):
                            sob = st.number_input("Piezas SOBRANTES (Merma)", min_value=0, max_value=int(row['cantidad_preparada']), value=int(row['cantidad_sobrante']))
                            efec = st.number_input("Efectivo TOTAL Real Recaudado ($)", min_value=0.0, value=float(row['efectivo_real_recaudado']))
                            
                            c_btn1, c_btn2 = st.columns(2)
                            if c_btn1.form_submit_button("💾 Guardar Cierre"):
                                supabase.table("produccion_ventas").update({
                                    "cantidad_sobrante": sob, "efectivo_real_recaudado": efec
                                }).eq("id", row['id']).execute()
                                st.success("¡Guardado!")
                                st.rerun()
                                
                            if c_btn2.form_submit_button("🗑️ BORRAR Registro"):
                                supabase.table("produccion_ventas").delete().eq("id", row['id']).execute()
                                st.warning("Registro eliminado de la nube.")
                                st.rerun()

# --- PESTAÑA 2: CATÁLOGO ---
with tab2:
    st.header("Catálogo Maestro de Postres y Costos Estándar")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("Agregar Nuevo Producto")
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
            df_cat['Costo Total'] = df_cat['costo_insumos_promedio'] + df_cat['costo_empaque_promedio']
            st.subheader("Tus Postres Registrados")
            st.dataframe(df_cat[['id', 'nombre_postre', 'precio_lista', 'Costo Total']], use_container_width=True)
            
            with st.form("form_borrar_cat"):
                id_borrar = st.number_input("Escribe el ID del postre que deseas ELIMINAR:", min_value=1, step=1)
                if st.form_submit_button("🗑️ Eliminar del Catálogo"):
                    supabase.table("catalogo_postres").delete().eq("id", id_borrar).execute()
                    st.success("Producto eliminado del catálogo.")
                    st.rerun()

# --- PESTAÑA 3: COMPRAS ---
with tab3:
    st.header("Registro de Compras e Inventarios")
    with st.form("form_inv", clear_on_submit=True):
        fecha_inv = st.date_input("Fecha de Compra", datetime.now())
        concepto_inv = st.text_input("¿Qué compraste?")
        monto_inv = st.number_input("Monto Gastado ($)", min_value=0.0)
        tipo_insumo = st.selectbox("Categoría", ["Materia Prima", "Desechables", "Otros"])
        
        if st.form_submit_button("Registrar Compra") and concepto_inv:
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

# --- PESTAÑA 5: TABLERO FINANCIERO CORREGIDO Y COMPLETO ---
with tab5:
    st.header("Finanzas Líquidas en Tiempo Real")
    
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
        st.info("Registra tus datos de producción y catálogo para ver los balances matemáticos.")
    else:
        df_m = pd.merge(df_v, df_c, on='nombre_postre', how='left')
        df_m['piezas_vendidas'] = df_m['cantidad_preparada'] - df_m['cantidad_sobrante']
        df_m['costo_produccion_total'] = df_m['cantidad_preparada'] * (df_m['costo_insumos_promedio'].fillna(0) + df_m['costo_empaque_promedio'].fillna(0))
        df_m['utilidad_bruta'] = df_m['efectivo_real_recaudado'] - df_m['costo_produccion_total']
        
        df_m['fecha'] = pd.to_datetime(df_m['fecha']).dt.date
        fechas_disponibles = df_m['fecha'].unique()
        
        dia_sel = st.selectbox("Selecciona la fecha a evaluar:", fechas_disponibles, key="tab5_dia")
        df_dia = df_m[df_m['fecha'] == dia_sel]
        
        if not df_g.empty:
            df_g['fecha'] = pd.to_datetime(df_g['fecha']).dt.date
            gastos_dia = df_g[(df_g['fecha'] == dia_sel) & (df_g['tipo_gasto'] != "Gasto Fijo Mensual Casa")]['monto'].sum()
            gastos_mes = df_g[df_g['tipo_gasto'] == "Gasto Fijo Mensual Casa"]['monto'].sum()
            costo_fijo_prorrateado = gastos_mes / 30 if gastos_mes > 0 else 25.0
        else:
            gastos_dia = 0.0
            costo_fijo_prorrateado = 25.0
            
        gastos_totales_fijos_dia = gastos_dia + costo_fijo_prorrateado
        
        if not df_dia.empty:
            ingresos_efectivo = df_dia['efectivo_real_recaudado'].sum()
            costo_prod_total = df_dia['costo_produccion_total'].sum()
            utilidad_bruta_dia = ingresos_efectivo - costo_prod_total
            utilidad_neta_dia = utilidad_bruta_dia - gastos_totales_fijos_dia
            
            m_bruto = (utilidad_bruta_dia / ingresos_efectivo) * 100 if ingresos_efectivo > 0 else 0
            m_neto = (utilidad_neta_dia / ingresos_efectivo) * 100 if ingresos_efectivo > 0 else 0
            
            st.write(f"### Resumen de Operación Financiera del Día: {dia_sel}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Efectivo Recaudado (Ingresos)", f"${ingresos_efectivo:,.2f}")
            c2.metric("Inversión Insumos (Materia Prima + Vasos)", f"${costo_prod_total:,.2f}")
            c3.metric("Costos Operativos + Prorrateo Casa", f"${gastos_totales_fijos_dia:,.2f}")
            
            c4, c5, c6 = st.columns(3)
            c4.metric("Utilidad Bruta", f"${utilidad_bruta_dia:,.2f}")
            c5.markdown(
                f"<div style='background-color:#d4edda; padding:12px; border-radius:8px; text-align:center; border: 1px solid #c3e6cb;'>"
                f"<p style='margin:0; color:#155724; font-size:16px; font-weight:bold;'>Utilidad Neta (Tu Bolsillo)</p>"
                f"<h2 style='margin:0; color:#155724;'>${utilidad_neta_dia:,.2f}</h2>"
                f"</div>", 
                unsafe_allow_html=True
            )
            c6.metric("Margen Neto Real", f"{m_neto:.1f}%")
            
            st.write("---")
            st.subheader("Desglose detallado por producto")
            st.dataframe(df_dia[['nombre_postre', 'cantidad_preparada', 'cantidad_sobrante', 'piezas_vendidas', 'efectivo_real_recaudado']], use_container_width=True)
            
            mermas_totales = df_dia['cantidad_sobrante'].sum()
            if mermas_totales > 0:
                st.warning(f"⚠️ Hoy regresaron {mermas_totales} piezas sobrantes de la calle. Eso disminuyó tu ganancia neta.")
