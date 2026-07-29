"""
data_ingestion.py
-----------------
Module d'extraction et de nettoyage des données réseau (SQLite -> Pandas).
Effectue la jointure entre la topologie des sites et les PM Counters.
"""

import os
import pandas as pd
from sqlalchemy import create_engine

# Chemin vers la BDD SQLite
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "network_data.db")


def get_db_engine():
    """Crée et retourne le moteur de connexion SQLAlchemy."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"❌ La base de données est introuvable au chemin : {DB_PATH}\n"
            "Veuillez exécuter 'src/database_builder.py' d'abord."
        )
    return create_engine(f"sqlite:///{DB_PATH}")


def fetch_merged_network_data() -> pd.DataFrame:
    """
    Extrait et fusionne la topologie et les compteurs PM via une requête SQL optimisée.
    
    Returns:
        pd.DataFrame: DataFrame consolidé contenant l'ensemble des données radio sur 24h.
    """
    engine = get_db_engine()

    query = """
    SELECT 
        t.site_id,
        t.site_name,
        t.cell_id,
        t.technology,
        t.frequency_band,
        t.azimuth,
        t.height_m,
        t.tilt_mechanical,
        t.tilt_electrical,
        t.latitude,
        t.longitude,
        p.hour,
        p.rsrp_dbm,
        p.sinr_db,
        p.user_throughput_mbps,
        p.handover_success_rate,
        p.call_drop_rate,
        p.traffic_gb,
        p.prb_utilization_rate
    FROM topology t
    INNER JOIN pm_counters p ON t.cell_id = p.cell_id
    ORDER BY t.site_id, t.cell_id, p.hour;
    """

    print("📥 Extraction des données consolidées depuis SQLite (SQLAlchemy)...")
    df = pd.read_sql_query(query, con=engine)
    print(f"   └─ {len(df)} lignes récupérées ({df['cell_id'].nunique()} cellules uniques).")
    
    return clean_network_data(df)


def clean_network_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et valide les données extraites :
    - Gestion des valeurs manquantes / aberrantes.
    - Contrôle des types de données.
    """
    initial_count = len(df)

    # 1. Traitement des valeurs manquantes (si présentes)
    df = df.dropna(subset=['cell_id', 'site_id', 'hour'])

    # 2. Imputation intelligente si besoin (médiane ou valeur par défaut)
    df['rsrp_dbm'] = df['rsrp_dbm'].fillna(-105.0)
    df['sinr_db'] = df['sinr_db'].fillna(0.0)
    df['traffic_gb'] = df['traffic_gb'].fillna(0.0)

    # 3. Validation des bornes physiques des KPI
    df['handover_success_rate'] = df['handover_success_rate'].clip(lower=0.0, upper=100.0)
    df['call_drop_rate'] = df['call_drop_rate'].clip(lower=0.0, upper=100.0)
    df['prb_utilization_rate'] = df['prb_utilization_rate'].clip(lower=0.0, upper=100.0)

    # 4. Conversion explicite des types
    df['hour'] = df['hour'].astype(int)
    df['azimuth'] = df['azimuth'].astype(int)
    df['tilt_electrical'] = df['tilt_electrical'].astype(int)

    cleaned_count = len(df)
    if initial_count != cleaned_count:
        print(f"🧹 Nettoyage terminé : {initial_count - cleaned_count} lignes invalides supprimées.")

    return df


if __name__ == "__main__":
    # Test autonome du script
    try:
        network_df = fetch_merged_network_data()
        print("\nAperçu des 5 premières lignes du dataset :")
        print(network_df[['site_id', 'cell_id', 'technology', 'hour', 'rsrp_dbm', 'sinr_db']].head())
    except Exception as e:
        print(f"⚠️ Erreur lors de l'exécution : {e}")