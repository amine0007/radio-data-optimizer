"""
main.py
-------
Orchestrateur principal du projet 'Mobile Radio Performance & Carbon Footprint Optimizer'.
Exécute la chaîne complète étape par étape :
1. Génération de la base SQLite simulée (500 sites).
2. Extraction SQL & Nettoyage Pandas.
3. Analyse des KPIs Radio & Algorithme RSE (MIMO Sleep Mode).
4. Dimensionnement Radio & Export compatible ATOLL (ACP/AFP).
5. Génération du Dashboard Excel aux couleurs de Bouygues Telecom.
"""

import sys
import time
from config.settings import DB_PATH, EXCEL_OUTPUT_PATH, ATOLL_CSV_PATH
from src.database_builder import build_database
from src.data_ingestion import fetch_merged_network_data
from src.kpi_analyzer import analyze_radio_performance, calculate_decarbonization_impact
from src.radio_dimensioning import generate_radio_recommendations, export_to_atoll_format
from src.excel_reporter import create_styled_excel_report


def print_banner():
    """Affiche la bannière d'introduction dans la console."""
    print("=" * 80)
    print(" 📡 BTECHNOLOGIE / BOUYGUES TELECOM - RADIO DATA OPTIMIZER & RSE TOOL ")
    print("=" * 80)
    print(" Projet d'Ingénierie Radio, Data Analytics & Optimisation Énergétique (5G/4G/3G)")
    print("=" * 80 + "\n")


def run_pipeline():
    """Exécute l'ensemble du pipeline de données."""
    start_time = time.time()
    print_banner()

    # -------------------------------------------------------------------------
    # ÉTAPE 1 : Génération de la BDD SQLite & Ingestion
    # -------------------------------------------------------------------------
    print("🚀 [Étape 1/5] Initialisation & Ingestion des données réseau...")
    build_database()
    raw_df = fetch_merged_network_data()
    print("   └─ Dataframe brut chargé avec succès.\n")

    # -------------------------------------------------------------------------
    # ÉTAPE 2 : Analyse de Performance & Calcul RSE
    # -------------------------------------------------------------------------
    print("🔍 [Étape 2/5] Analyse des KPIs Radio & Impact Décarbonation...")
    perf_summary = analyze_radio_performance(raw_df)
    eco_metrics = calculate_decarbonization_impact(raw_df)

    # -------------------------------------------------------------------------
    # ÉTAPE 3 : Dimensionnement Radio & Export ATOLL
    # -------------------------------------------------------------------------
    print("🛠️ [Étape 3/5] Recommandations de Design & Génération Export ATOLL...")
    reco_summary = generate_radio_recommendations(perf_summary)
    atoll_file = export_to_atoll_format(reco_summary)

    # -------------------------------------------------------------------------
    # ÉTAPE 4 : Génération du Rapport Excel
    # -------------------------------------------------------------------------
    print("📊 [Étape 4/5] Génération du Cockpit Excel Bouygues Telecom...")
    excel_file = create_styled_excel_report(perf_summary, reco_summary, eco_metrics)

    # -------------------------------------------------------------------------
    # ÉTAPE 5 : Bilan d'exécution
    # -------------------------------------------------------------------------
    elapsed_time = round(time.time() - start_time, 2)
    print("=" * 80)
    print(f"🎉 PIPELINE EXÉCUTÉ AVEC SUCCÈS EN {elapsed_time} SECONDES !")
    print("=" * 80)
    print(f"📁 Fichiers générés prêts pour la démonstration :")
    print(f"   ├─ Base SQLite : {DB_PATH}")
    print(f"   ├─ Fichier Import ATOLL : {atoll_file}")
    print(f"   └─ Rapport Excel Final : {excel_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"\n❌ Erreur critique pendant l'exécution du pipeline : {e}")
        sys.exit(1)