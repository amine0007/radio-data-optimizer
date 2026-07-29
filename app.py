import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import st_folium
import plotly.express as px
from src.propagation_model import process_propagation_analysis

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Radio Network & Green Telecom Cockpit",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Radio Performance & Green Telecom Cockpit")
st.caption("Supervision en temps réel des KPIs Radio, Modélisation Hata/Cost-231 & Optimisation Énergétique (MIMO Sleep Mode)")

# --- CHARGEMENT DES DONNÉES DEPUIS SQLITE ---
@st.cache_data
def load_data():
    conn = sqlite3.connect("data/network_data.db")
    df_topo = pd.read_sql("SELECT * FROM topology", conn)
    df_pm = pd.read_sql("SELECT * FROM pm_counters", conn)
    conn.close()
    
    # Fusion & calcul du modèle de propagation
    df_merged = pd.merge(df_pm, df_topo, on="cell_id")
    df_enriched = process_propagation_analysis(df_merged)
    return df_topo, df_pm, df_enriched

try:
    df_topo, df_pm, df_merged = load_data()
except Exception as e:
    st.error(f"Erreur lors du chargement de la base SQLite. Assure-toi d'avoir exécuté `python main.py` au préalable. Détails : {e}")
    st.stop()

# --- SIDEBAR / FILTRES ---
st.sidebar.header("🎛️ Filtres Réseau")
tech_filter = st.sidebar.multiselect(
    "Technologie :",
    options=df_topo['technology'].unique(),
    default=df_topo['technology'].unique()
)

band_filter = st.sidebar.multiselect(
    "Bande de fréquence :",
    options=df_topo['frequency_band'].unique(),
    default=df_topo['frequency_band'].unique()
)

# Application des filtres
filtered_topo = df_topo[
    (df_topo['technology'].isin(tech_filter)) & 
    (df_topo['frequency_band'].isin(band_filter))
]
filtered_cell_ids = filtered_topo['cell_id'].tolist()
filtered_merged = df_merged[df_merged['cell_id'].isin(filtered_cell_ids)]

# --- VUE D'ENSEMBLE (METRIQUES CLÉS) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

total_sites = filtered_topo['site_id'].nunique()
total_cells = filtered_topo['cell_id'].nunique()

degraded_cells = filtered_merged[
    (filtered_merged['rsrp_dbm'] < -105) | 
    (filtered_merged['sinr_db'] < 3) | 
    (filtered_merged['call_drop_rate'] > 1.5)
]['cell_id'].nunique()

pct_degraded = (degraded_cells / total_cells * 100) if total_cells > 0 else 0

col1.metric("Sites Radio Actifs", f"{total_sites}")
col2.metric("Cellules Supervisées", f"{total_cells}")
col3.metric("Cellules Dégradées", f"{degraded_cells}", delta=f"{pct_degraded:.1f}%", delta_color="inverse")

# Simulation RSE interactive
hours_sleep = st.sidebar.slider("Heures de Sleep Mode nocturne / jour :", 1, 8, 6)
kwh_saved_annual = (total_cells * 0.05 * hours_sleep * 365)
co2_avoided_tonnes = (kwh_saved_annual * 0.055) / 1000

col4.metric("Économie CO₂ Estimée", f"{co2_avoided_tonnes:.1f} t/an 🍃")

# --- NAVIGATION PAR ONGLETS ---
tab1, tab2 = st.tabs(["🗺️ Supervision Réseau & KPIs", "📐 Modélisation de Propagation (Cost-231 Hata)"])

with tab1:
    # --- CARTE INTERACTIVE DES SITES (FOLIUM) ---
    st.subheader("Carte Interactive des Sites Radio")

    site_map_data = filtered_topo.groupby('site_id').first().reset_index()
    avg_lat = site_map_data['latitude'].mean()
    avg_lon = site_map_data['longitude'].mean()

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=11, tiles="OpenStreetMap")

    for _, site in site_map_data.iterrows():
        site_cells = filtered_topo[filtered_topo['site_id'] == site['site_id']]['cell_id']
        is_degraded = filtered_merged[
            (filtered_merged['cell_id'].isin(site_cells)) & 
            ((filtered_merged['rsrp_dbm'] < -105) | (filtered_merged['call_drop_rate'] > 1.5))
        ].shape[0] > 0

        color = "red" if is_degraded else "green"
        status_text = "⚠️ Dégradation détectée" if is_degraded else "✅ Nominal"

        folium.CircleMarker(
            location=[site['latitude'], site['longitude']],
            radius=6,
            popup=f"<b>Site :</b> {site['site_name']} ({site['site_id']})<br><b>Techno :</b> {site['technology']}<br><b>Statut :</b> {status_text}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)

    st_folium(m, width=1300, height=450)

    # --- GRAPHIQUES PERFORMANCES ---
    st.subheader("Distribution de la Qualité Signal (SINR) & Trafic")
    col_left, col_right = st.columns(2)

    with col_left:
        fig_sinr = px.histogram(
            filtered_merged, 
            x="sinr_db", 
            nbins=30, 
            title="Distribution du SINR (dB)",
            color_discrete_sequence=['#3366CC']
        )
        fig_sinr.add_vline(x=3, line_dash="dash", line_color="red", annotation_text="Seuil Critique (3dB)")
        st.plotly_chart(fig_sinr, use_container_width=True)

    with col_right:
        fig_traffic = px.box(
            filtered_merged, 
            x="technology", 
            y="traffic_gb", 
            color="technology",
            title="Trafic Évolutif par Technologie (GB)"
        )
        st.plotly_chart(fig_traffic, use_container_width=True)

with tab2:
    st.subheader("📐 Modélisation Théorique Cost-231 Hata vs Télémesures Reelles")
    st.markdown("""
    Cette section compare le **RSRP mesuré sur le terrain** au **RSRP théorique prédit par le modèle Cost-231 Hata** 
    afin de détecter les anomalies physiques (masquage, problème de tilt ou pertes feeders).
    """)

    col_m1, col_m2, col_m3 = st.columns(3)
    
    critical_path_loss_count = (filtered_merged['propagation_diag'] == "CRITICAL_PATH_LOSS").sum()
    over_coverage_count = (filtered_merged['propagation_diag'] == "OVER_COVERAGE_RISK").sum()
    nominal_count = (filtered_merged['propagation_diag'] == "NOMINAL").sum()

    col_m1.metric("Anomalies de Masquage / Pertes", f"{critical_path_loss_count}", delta="Action Recommandée", delta_color="inverse")
    col_m2.metric("Risques de Sur-couverture (Overshooting)", f"{over_coverage_count}")
    col_m3.metric("Conformes au Modèle Théorique", f"{nominal_count}")

    st.markdown("---")
    
    # Graphique comparatif RSRP Mesuré vs Théorique
    fig_comp = px.scatter(
        filtered_merged,
        x="rsrp_theoretical_dbm",
        y="rsrp_dbm",
        color="propagation_diag",
        labels={
            "rsrp_theoretical_dbm": "RSRP Théorique Cost-231 (dBm)",
            "rsrp_dbm": "RSRP Mesuré Terrain (dBm)",
            "propagation_diag": "Diagnostic Radio"
        },
        title="Analyse d'Écart : RSRP Mesuré vs RSRP Théorique Cost-231 Hata",
        color_discrete_map={
            "NOMINAL": "green",
            "CRITICAL_PATH_LOSS": "red",
            "OVER_COVERAGE_RISK": "orange"
        }
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Tableau détaillé des cellules en anomalie
    st.subheader("📋 Liste des Cellules en Déficit de Propagation (Top 10)")
    anomaly_df = filtered_merged[filtered_merged['propagation_diag'] == "CRITICAL_PATH_LOSS"][
        ['cell_id', 'site_id', 'technology', 'frequency_band', 'rsrp_dbm', 'rsrp_theoretical_dbm', 'path_loss_cost231_db']
    ].head(10)
    
    st.dataframe(anomaly_df, use_container_width=True)