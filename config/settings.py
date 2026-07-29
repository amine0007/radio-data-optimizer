"""
settings.py
-----------
Fichier de configuration centralisé du projet.
Contient les chemins d'accès, les seuils KPI radio et les paramètres d'optimisation énergétique.
"""

import os

# =============================================================================
# 1. ARBORESCENCE & CHEMINS DU PROJET
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
ATOLL_EXPORT_DIR = os.path.join(DATA_DIR, "atoll_exports")

DB_PATH = os.path.join(DATA_DIR, "network_data.db")
EXCEL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "Rapport_Performance_Reseau.xlsx")
ATOLL_CSV_PATH = os.path.join(ATOLL_EXPORT_DIR, "atoll_import_sites.csv")

# S'assurer que les dossiers nécessaires existent
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ATOLL_EXPORT_DIR, exist_ok=True)


# =============================================================================
# 2. SEUILS DE PERFORMANCE RADIO & KPI (3G / 4G / 5G)
# =============================================================================
KPI_THRESHOLDS = {
    # Couverture & Qualité du signal
    "RSRP_POOR_DBM": -100.0,       # Couverture critique si RSRP <= -100 dBm
    "RSRP_GOOD_DBM": -85.0,        # Bonne couverture si RSRP >= -85 dBm
    "SINR_POOR_DB": 0.0,           # Interférence/Pollution pilote si SINR <= 0 dB
    
    # Qualité de service (QoS)
    "CDR_CRITICAL_PCT": 1.0,       # Alerte Taux de Coupure (Call Drop Rate) > 1.0%
    "HOSR_MIN_PCT": 95.0,          # Alerte Succès Handover (HOSR) < 95.0%
    
    # Capacité & Charge
    "PRB_SATURATED_PCT": 80.0,     # Seuil de saturation des bloc-ressources PRB (> 80%)
    
    # RSE - Seuil d'activation du Sleep Mode
    "SLEEP_MODE_TRAFFIC_PCT": 5.0  # Heures creuses : Trafic <= 5% du pic quotidien
}


# =============================================================================
# 3. PARAMÈTRES ÉNERGÉTIQUES & DÉCARBONATION (MIMO SLEEP MODE)
# =============================================================================
ENERGY_PARAMS = {
    # Puissance économisée par secteur en veille nocturne (ex: coupure de 2 à 4 voies RF sur MIMO 4x4)
    "POWER_SAVED_PER_CELL_W": 150.0,
    
    # Mix énergétique - Empreinte Carbone
    "CO2_KG_PER_KWH_FRANCE": 0.055,  # ~55g CO2 / kWh (Réseau décarboné en France / Mix Bouygues)
    
    # Facteur d'équivalence écologique
    "CO2_ABSORBED_BY_TREE_KG_YEAR": 25.0  # Un arbre adulte absorbe environ 25 kg de CO2/an
}


# =============================================================================
# 4. CHARTE GRAPHIQUE BOUYGUES TELECOM (POUR EXCEL & VISUELS)
# =============================================================================
BRAND_COLORS = {
    "NAVY": "003366",        # Bleu Marine principal
    "SKY_BLUE": "0099CC",    # Bleu Ciel secondaire
    "ORANGE": "FF6600",      # Orange Accent Bouygues
    "LIGHT_GRAY": "F2F4F7",  # Fond de lignes alternées
    "RED_ALERT": "FADBD8",   # Alerte cellules dégradées
    "GREEN_OK": "D4EFDF"     # Validation / Actions ATOLL
}