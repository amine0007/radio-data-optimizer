# 📡 5G/4G Radio Data Optimizer & RSE Tool

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Domain](https://img.shields.io/badge/Domain-Radio%20Engineering%20%26%20CSR-green?style=for-the-badge)]()

Un outil d'ingénierie radio et d'optimisation énergétique de niveau production, conçu pour automatiser l'analyse de performance (KPIs 3G/4G/5G), générer des recommandations de dimensionnement (compatibles ATOLL) et calculer l'impact RSE via des algorithmes d'économie d'énergie (*MIMO Sleep Mode*).

---

## 📊 Architecture du Projet & Workflow

```text
  [ Données Réseau Raw ]
            │
            ▼
 ┌──────────────────────┐
 │  database_builder    │ ──► Génération SQLite (500 sites / ~90k lignes PM)
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │   kpi_analyzer       │ ──► Détection d'anomalies (RSRP, SINR, Drop Rate)
 └──────────┬───────────┘
            ├────────────────────────────────────────┐
            ▼                                        ▼
 ┌──────────────────────┐               ┌────────────────────────┐
 │   atoll_exporter     │               │    rse_calculator      │
 └──────────┬───────────┘               └──────────┬─────────────┘
            │ Export CSV (ACP/AFP)                 │ Calcul kWh & CO2 évitables
            ▼                                      ▼
 ┌───────────────────────────────────────────────────────────────┐
 │                       excel_reporter                          │
 └──────────────────────────────┬────────────────────────────────┘
                                ▼
              [ Cockpit Excel Bouygues Telecom ]