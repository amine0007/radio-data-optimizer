"""
radio_dimensioning.py
---------------------
Module de dimensionnement radio & Générateur d'export compatible ATOLL (ACP/AFP).
1. Traduit les diagnostics KPI en préconisations d'ingénierie (Tilts, Azimuths, Ajouts de bandes 5G).
2. Produit un fichier d'export au format CSV structuré selon les tables d'import ATOLL (Transmitters/Cells).
"""

import os
import pandas as pd

# Répertoire de sortie pour les exports ATOLL
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ATOLL_EXPORT_DIR = os.path.join(DATA_DIR, "atoll_exports")


def generate_radio_recommendations(perf_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse les cellules sous-performantes et génère les modifications physiques ou logiques recommandées.
    
    Args:
        perf_df (pd.DataFrame): DataFrame issu de 'kpi_analyzer.py' contenant les diagnostics par cellule.
        
    Returns:
        pd.DataFrame: Table des préconisations avec les nouveaux paramètres radio proposés.
    """
    print("🛠️ Calcul des actions correctives de dimensionnement radio...")

    recommendations = []

    for _, row in perf_df.iterrows():
        cell_id = row['cell_id']
        site_id = row['site_id']
        tech = row['technology']
        curr_tilt_elec = row['tilt_electrical']
        curr_azimuth = row['azimuth']
        diagnostic = row['diagnostic']

        # Paramètres recommandés (Valeurs initiales)
        new_tilt_elec = curr_tilt_elec
        new_azimuth = curr_azimuth
        action_type = "No Action"
        comment = "Cellule conforme"
        status = "Active"

        # Logique décisionnelle radio
        if "Pollution Pilote" in diagnostic:
            # Augmentation du tilt électrique pour réduire le lobe de couverture de la cellule et éliminer le surcouverture
            new_tilt_elec = curr_tilt_elec + 2
            action_type = "Tilt Electrical Increase (+2°)"
            comment = f"Réduction pollution pilote (SINR actuel: {row['avg_sinr']:.1f} dB)"
            status = "Modified"

        elif "Saturation PRB" in diagnostic:
            if tech == "4G":
                # Ajout de la bande 5G n78 (3.5 GHz) pour soulager la macro 4G saturée
                action_type = "Capacity Layer Upgrade (Add 5G NR 3.5 GHz)"
                comment = f"Saturation PRB ({row['max_prb_util']:.1f}%). Recommandation ouverture couche 5G."
                status = "Proposed"
            else:
                new_tilt_elec = max(0, curr_tilt_elec - 1)
                action_type = "Tilt Electrical Decrease (-1°)"
                comment = "Expansion de couverture pour soulagement trafic."
                status = "Modified"

        elif "Trou de Couverture" in diagnostic:
            # Réduction du tilt électrique pour augmenter la portée physique de la cellule
            new_tilt_elec = max(0, curr_tilt_elec - 2)
            action_type = "Tilt Electrical Decrease (-2°)"
            comment = f"Extension de couverture (RSRP actuel: {row['avg_rsrp']:.1f} dBm)"
            status = "Modified"

        elif "Handover Défaillant" in diagnostic:
            # Ajustement d'azimuth léger ou vérification des voisins
            action_type = "Neighbor List / Azimuth Review"
            comment = f"HOSR dégradé ({row['avg_hosr']:.1f}%). Optimisation des relations d'adjacence."
            status = "To Review"

        recommendations.append({
            "site_id": site_id,
            "cell_id": cell_id,
            "technology": tech,
            "frequency_band": row['frequency_band'],
            "current_tilt_elec": curr_tilt_elec,
            "proposed_tilt_elec": new_tilt_elec,
            "current_azimuth": curr_azimuth,
            "proposed_azimuth": new_azimuth,
            "action_type": action_type,
            "diagnostic": diagnostic,
            "comment": comment,
            "atoll_status": status
        })

    reco_df = pd.DataFrame(recommendations)
    
    modified_count = len(reco_df[reco_df['atoll_status'] != "Active"])
    print(f"   └─ {modified_count} propositions d'ingénierie générées.")

    return reco_df


def export_to_atoll_format(reco_df: pd.DataFrame, filename: str = "atoll_import_sites.csv") -> str:
    """
    Génère un fichier CSV d'importation compatible avec les tables 'Transmitters' / 'Cells' d'ATOLL (ACP/AFP).
    
    Format standardisé ATOLL :
    Transmitter Name, Site Name, Azimuth, Electrical Tilt, Mechanical Tilt, Status, Action Comment
    
    Returns:
        str: Chemin d'accès au fichier CSV généré.
    """
    os.makedirs(ATOLL_EXPORT_DIR, exist_ok=True)
    export_filepath = os.path.join(ATOLL_EXPORT_DIR, filename)

    print("📄 Formatage du fichier d'export structuré pour ATOLL (ACP/AFP)...")

    # Mappage vers la nomenclature standard des attributs ATOLL
    atoll_export_df = pd.DataFrame({
        "Site Name": reco_df['site_id'],
        "Transmitter Name": reco_df['cell_id'],
        "Technology": reco_df['technology'],
        "Frequency Band": reco_df['frequency_band'],
        "Azimuth (deg)": reco_df['proposed_azimuth'],
        "Electrical Tilt (deg)": reco_df['proposed_tilt_elec'],
        "Status": reco_df['atoll_status'],
        "Action Plan": reco_df['action_type'],
        "Engineering Remarks": reco_df['comment']
    })

    # Export au format CSV avec séparateur point-virgule (Standard ATOLL/Excel Europe)
    atoll_export_df.to_csv(export_filepath, index=False, sep=";", encoding="utf-8-sig")

    print(f"✅ Fichier ATOLL prêt à l'importation : {export_filepath}\n")
    return export_filepath


if __name__ == "__main__":
    from data_ingestion import fetch_merged_network_data
    from kpi_analyzer import analyze_radio_performance

    try:
        raw_data = fetch_merged_network_data()
        perf_summary = analyze_radio_performance(raw_data)
        reco_summary = generate_radio_recommendations(perf_summary)
        csv_file = export_to_atoll_format(reco_summary)

        print("Aperçu des 5 premières lignes du fichier d'export ATOLL :")
        print(pd.read_csv(csv_file, sep=";").head())
    except Exception as e:
        print(f"⚠️ Erreur lors du test autonome : {e}")