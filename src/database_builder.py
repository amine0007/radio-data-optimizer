"""
database_builder.py
-------------------
Génère une base de données SQLite locale simulée représentant un parc 
de 500 sites radio (3G, 4G, 5G) pour le réseau Bouygues Telecom.
"""

import os
import sqlite3
import random
import pandas as pd

# Répertoire cible pour la base de données
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "network_data.db")

DEGRADED_CELL_FRACTION = 0.04
DEGRADED_HOURS = {18, 19, 20, 21}

random.seed(42)


def create_schema(conn: sqlite3.Connection):
    """Crée la structure des tables 'topology' et 'pm_counters'."""
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topology (
        cell_id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        site_name TEXT NOT NULL,
        technology TEXT NOT NULL,
        frequency_band TEXT NOT NULL,
        azimuth INTEGER NOT NULL,
        height_m REAL NOT NULL,
        tilt_mechanical INTEGER NOT NULL,
        tilt_electrical INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pm_counters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cell_id TEXT NOT NULL,
        hour INTEGER NOT NULL,
        rsrp_dbm REAL NOT NULL,
        sinr_db REAL NOT NULL,
        user_throughput_mbps REAL NOT NULL,
        handover_success_rate REAL NOT NULL,
        call_drop_rate REAL NOT NULL,
        traffic_gb REAL NOT NULL,
        prb_utilization_rate REAL NOT NULL,
        FOREIGN KEY (cell_id) REFERENCES topology (cell_id)
    );
    """)

    conn.commit()


def generate_topology_data(num_sites: int = 500) -> pd.DataFrame:
    """Génère la topologie pour 500 sites avec 3 secteurs par site et multi-technologies."""
    topology_rows = []

    base_lat, base_lon = 33.9716, -6.8498

    technologies = [
        ("3G", "2100 MHz"),
        ("4G", "1800 MHz"),
        ("4G", "2600 MHz"),
        ("5G", "3500 MHz")
    ]

    for i in range(1, num_sites + 1):
        site_id = f"BYT_RAB_{i:03d}"
        site_name = f"Site_Rabat_Zone_{i:03d}"

        lat = base_lat + random.uniform(-0.15, 0.15)
        lon = base_lon + random.uniform(-0.15, 0.15)
        height = random.randint(18, 35)

        for sector, azimuth in enumerate([0, 120, 240], start=1):
            tilt_mech = random.randint(0, 3)
            tilt_elec = random.randint(2, 8)

            site_techs = random.sample(technologies, k=random.randint(2, 3))

            for tech, band in site_techs:
                band_code = band.split()[0]
                cell_id = f"{site_id}_{sector}_{tech}_{band_code}"

                topology_rows.append({
                    "cell_id": cell_id,
                    "site_id": site_id,
                    "site_name": site_name,
                    "technology": tech,
                    "frequency_band": band,
                    "azimuth": azimuth,
                    "height_m": height,
                    "tilt_mechanical": tilt_mech,
                    "tilt_electrical": tilt_elec,
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6)
                })

    return pd.DataFrame(topology_rows)


def generate_pm_counters(topology_df: pd.DataFrame) -> pd.DataFrame:
    """Génère des KPIs sur 24 heures en simulant des anomalies réseau et des profils de trafic nocturne."""
    pm_rows = []
    cell_ids = topology_df["cell_id"].unique()

    degraded_cells = set(
        random.sample(list(cell_ids), max(1, int(len(cell_ids) * DEGRADED_CELL_FRACTION)))
    )

    for cell_id in cell_ids:
        is_degraded = cell_id in degraded_cells

        for hour in range(24):
            if 1 <= hour <= 5:
                traffic_factor = random.uniform(0.01, 0.04)
            elif 18 <= hour <= 22:
                traffic_factor = random.uniform(0.85, 1.00)
            else:
                traffic_factor = random.uniform(0.30, 0.70)

            if is_degraded and hour in DEGRADED_HOURS:
                rsrp = round(random.uniform(-115, -100), 2)
                sinr = round(random.uniform(-5.0, 1.0), 2)
                throughput = round(random.uniform(0.5, 3.0), 2)
                hosr = round(random.uniform(88.0, 93.5), 2)
                cdr = round(random.uniform(1.2, 3.5), 2)
                prb_util = round(random.uniform(85.0, 98.0), 2)
            else:
                rsrp = round(random.uniform(-95, -78), 2)
                sinr = round(random.uniform(8.0, 25.0), 2)
                throughput = round(random.uniform(15.0, 120.0), 2)
                hosr = round(random.uniform(97.5, 99.9), 2)
                cdr = round(random.uniform(0.05, 0.4), 2)
                prb_util = round(traffic_factor * random.uniform(60.0, 80.0), 2)

            traffic_gb = round(traffic_factor * random.uniform(20, 50), 2)

            pm_rows.append({
                "cell_id": cell_id,
                "hour": hour,
                "rsrp_dbm": rsrp,
                "sinr_db": sinr,
                "user_throughput_mbps": throughput,
                "handover_success_rate": hosr,
                "call_drop_rate": cdr,
                "traffic_gb": traffic_gb,
                "prb_utilization_rate": prb_util
            })

    return pd.DataFrame(pm_rows)


def build_database():
    """Fonction principale de construction de la BDD."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🔄 Ancienne base supprimée : {DB_PATH}")

    print("⚙️ Initialisation de la base SQLite...")
    conn = sqlite3.connect(DB_PATH)

    create_schema(conn)

    print("🛰️ Génération de la topologie (500 sites radio)...")
    topo_df = generate_topology_data(num_sites=500)
    topo_df.to_sql("topology", conn, if_exists="append", index=False)
    print(f"   └─ {len(topo_df)} cellules insérées dans 'topology'.")

    print("📊 Génération des compteurs PM (sur 24 heures)...")
    pm_df = generate_pm_counters(topo_df)
    pm_df.to_sql("pm_counters", conn, if_exists="append", index=False)
    print(f"   └─ {len(pm_df)} enregistrements insérés dans 'pm_counters'.")

    conn.close()
    print(f"✅ Base de données générée avec succès : {DB_PATH}\n")


if __name__ == "__main__":
    build_database()