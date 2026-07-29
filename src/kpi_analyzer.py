"""
kpi_analyzer.py
---------------
Module d'analyse des KPIs radio et d'optimisation énergétique (RSE).
"""

import pandas as pd
from config.settings import KPI_THRESHOLDS, ENERGY_PARAMS


def analyze_radio_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrège les métriques par cellule et détecte les cellules réellement dégradées
    basées sur les pires conditions observées dans la journée (min/max).
    """
    print("🔍 Analyse globale de la performance radio du réseau...")

    cell_summary = (
        df.groupby(
            [
                "site_id",
                "site_name",
                "cell_id",
                "technology",
                "frequency_band",
                "azimuth",
                "tilt_electrical",
            ],
            as_index=False,
        )
        .agg(
            avg_rsrp=("rsrp_dbm", "mean"),
            min_rsrp=("rsrp_dbm", "min"),
            avg_sinr=("sinr_db", "mean"),
            min_sinr=("sinr_db", "min"),
            max_prb_util=("prb_utilization_rate", "max"),
            max_cdr=("call_drop_rate", "max"),
            avg_cdr=("call_drop_rate", "mean"),
            min_hosr=("handover_success_rate", "min"),
            avg_hosr=("handover_success_rate", "mean"),
            total_traffic_gb=("traffic_gb", "sum"),
            avg_throughput=("user_throughput_mbps", "mean"),
        )
    )

    def tag_issues(row):
        issues = []

        # 1. Couverture & Qualité
        if row["min_rsrp"] <= KPI_THRESHOLDS["RSRP_POOR_DBM"] and row["min_sinr"] <= KPI_THRESHOLDS["SINR_POOR_DB"]:
            issues.append("Trou de Couverture / Signal Très Faible")
        elif row["min_sinr"] <= KPI_THRESHOLDS["SINR_POOR_DB"] and row["avg_rsrp"] > -95.0:
            issues.append("Pollution Pilote / Interférence")

        # 2. Saturation PRB (Seuil strict à 90% en pic)
        if row["max_prb_util"] >= 90.0:
            issues.append("Saturation PRB (Busy Hour)")

        # 3. Qualité de service
        if row["max_cdr"] >= KPI_THRESHOLDS["CDR_CRITICAL_PCT"]:
            issues.append("Taux de Coupure Élevé (CDR > 1%)")

        if row["min_hosr"] < KPI_THRESHOLDS["HOSR_MIN_PCT"]:
            issues.append("Handover Défaillant (HOSR < 95%)")

        return " | ".join(issues) if issues else "Nominal (OK)"

    cell_summary["diagnostic"] = cell_summary.apply(tag_issues, axis=1)
    cell_summary["is_degraded"] = cell_summary["diagnostic"] != "Nominal (OK)"

    degraded_count = int(cell_summary["is_degraded"].sum())
    total_cells = len(cell_summary)
    print(
        f"   └─ {degraded_count} cellules dégradées détectées sur {total_cells} "
        f"({degraded_count / total_cells * 100:.1f}%)."
    )

    return cell_summary


def calculate_decarbonization_impact(df: pd.DataFrame) -> dict:
    """
    Algorithme 'Bouygues Telecom - Économie Décarbonée' :
    Calcule le trafic relatif par rapport au PIC DE LA JOURNÉE pour activer le Sleep Mode.
    """
    print("🌱 Calcul de l'empreinte carbone évitée (MIMO Sleep Mode)...")

    # 1. Calcul du trafic max de la journée par cellule (sur 24h)
    df_copy = df.copy()
    max_daily_traffic = df_copy.groupby("cell_id")["traffic_gb"].transform("max")
    
    # 2. Ratio du trafic horaire par rapport au pic quotidien
    df_copy["traffic_ratio_pct"] = (df_copy["traffic_gb"] / (max_daily_traffic + 1e-5)) * 100

    # 3. Sélection des créneaux éligibles la nuit (01h-05h)
    eligible_night_slots = df_copy[
        (df_copy["hour"].isin([1, 2, 3, 4, 5])) &
        (df_copy["traffic_ratio_pct"] <= KPI_THRESHOLDS["SLEEP_MODE_TRAFFIC_PCT"])
    ]

    total_eligible_hours = len(eligible_night_slots)
    unique_cells_affected = eligible_night_slots["cell_id"].nunique()

    # Calculs énergétiques
    power_saved_w = ENERGY_PARAMS["POWER_SAVED_PER_CELL_W"]
    kwh_saved_daily = (total_eligible_hours * power_saved_w) / 1000.0
    kwh_saved_annual = kwh_saved_daily * 365.0

    co2_saved_kg_annual = kwh_saved_annual * ENERGY_PARAMS["CO2_KG_PER_KWH_FRANCE"]
    co2_saved_tons_annual = co2_saved_kg_annual / 1000.0

    decarbonization_kpis = {
        "eligible_hours_per_day": total_eligible_hours,
        "unique_cells_optimized": unique_cells_affected,
        "daily_kwh_saved": round(kwh_saved_daily, 2),
        "annual_kwh_saved": round(kwh_saved_annual, 2),
        "annual_co2_saved_tons": round(co2_saved_tons_annual, 2),
        "equivalent_trees_planted": int(co2_saved_kg_annual / 25.0),
    }

    print(f"   ├─ Cellules optimisées la nuit : {unique_cells_affected}")
    print(f"   ├─ Énergie économisée : {decarbonization_kpis['annual_kwh_saved']:,} kWh / an")
    print(f"   └─ Impact Carbone Évité : {decarbonization_kpis['annual_co2_saved_tons']} tonnes CO2 / an 🍃\n")

    return decarbonization_kpis