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
```

## 🚀 Structure du Répertoire
```Bash
radio-data-optimizer/
│
├── data/                      # Stockage des données binaires et exports (ignoré par Git)
│   ├── atoll_exports/
│   └── network_data.db
│
├── outputs/                   # Rapports consolidés (Excel, etc.)
│
├── src/                       # Modules Python métier
│   ├── __init__.py
│   ├── database_builder.py    # Génération et ingestion SQLite
│   ├── data_ingestion.py      # Extraction SQL & requêtes optimisées
│   ├── kpi_analyzer.py        # Moteur d'analyse radio & détection d'anomalies
│   ├── rse_calculator.py      # Algorithmes d'efficacité énergétique (MIMO Sleep)
│   ├── atoll_exporter.py      # Générateur d'exports d'ingénierie ATOLL
│   └── excel_reporter.py      # Mise en forme du rapport final openpyxl
│
├── main.py                    # Script orchestrateur principal
├── requirements.txt           # Dépendances Python
└── README.md                  # Documentation du projet
```

## ⚡ Quick Start
#### 1) Cloner le projet & Installer les dépendances

```Bash
git clone [https://github.com/amine007/radio-data-optimizer.git](https://github.com/amine007/radio-data-optimizer.git)
cd radio-data-optimizer
pip install -r requirements.txt
```

#### 2) Exécuter le pipeline complet

```Bash
python main.py
```

## 📈 Résultats du Pipeline (Exemple de Run)
```bash
================================================================================
📊 Rapport Exécutif d'Optimisation Réseau
================================================================================
└─ Cellules analysées : 3,746 sur 500 sites radio
└─ Cellules dégradées détectées : 149 (4.0%)
└─ Énergie économisée : 1,020,211.5 kWh / an
└─ Impact Carbone Évité : 56.11 tonnes CO2 / an 🍃
└─ Temps d'exécution total : 12.16s
================================================================================
```
