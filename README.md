# 📡 5G/4G/3G Radio Data Optimizer & RSE Cockpit

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Domain](https://img.shields.io/badge/Domain-Radio%20Engineering%20%26%20CSR-green?style=for-the-badge)]()

Un outil d’ingénierie radio, de modélisation de propagation et d’optimisation énergétique de niveau production.  
Conçu pour automatiser l’analyse de performance des KPI 3G/4G/5G, comparer les télémétries aux modèles théoriques (*Cost-231 Hata*), générer des recommandations de dimensionnement compatibles ATOLL ACP/AFP, et calculer l’impact RSE via des algorithmes d’économie d’énergie (*MIMO Sleep Mode*).

## 📊 Architecture du projet

```text
[ Données Réseau Raw ]
          │
          ▼
┌──────────────────────────────────┐
│        database_builder          │ ──► Génération SQLite
└────────────────┬─────────────────┘
                 ▼
┌──────────────────────────────────┐
│        propagation_model         │ ──► Calcul théorique Cost-231 Hata
└────────────────┬─────────────────┘
                 ▼
┌──────────────────────────────────┐
│          kpi_analyzer            │ ──► Détection d'anomalies (RSRP, SINR, Drop Rate, Root Cause)
└────────────────┬─────────────────┘
          ┌──────┴──────────────────────────┐
          ▼                                 ▼
┌──────────────────────────────────┐  ┌────────────────────────┐
│       radio_dimensioning         │  │    rse_calculator      │
└────────────────┬─────────────────┘  └──────────┬─────────────┘
                 │ Export CSV ATOLL              │ Calcul kWh & CO2 évitables
                 ▼                               ▼
┌────────────────────────────────────────────────────────────────┐
│             excel_reporter / Streamlit Cockpit                 │
└───────────────────────────────┬────────────────────────────────┘
                                ▼
      [ Dashboards interactifs & cockpit Excel Bouygues Telecom ]
```

## 📐 Modélisation radio & root cause analysis

Le projet intègre une couche d’ingénierie radio avancée permettant de comparer le signal réellement reçu sur le terrain \(RSRP_{\text{mesuré}}\) avec les prédictions théoriques issues du modèle **Cost-231 Hata**.

```tex
\text{Path Loss (dB)} = 46.3 + 33.9 \log_{10}(f) - 13.82 \log_{10}(h_b) - a(h_m) + (44.9 - 6.55 \log_{10}(h_b)) \log_{10}(d)
```

### Analyse d’écart & root cause

- **CRITICAL_PATH_LOSS** : écart négatif significatif entre \(RSRP_{\text{théorique}}\) et \(RSRP_{\text{mesuré}}\), pouvant indiquer un masquage urbain, un problème de feeder ou un tilt excessif.
- **OVER_COVERAGE_RISK** : signal anormalement fort générant des interférences sur les cellules voisines, typiquement lié à l’overshooting.
- **NOMINAL** : propagation conforme aux modèles empiriques.

## 🚀 Structure du répertoire

```text
radio-data-optimizer/
│
├── data/                      # Données binaires et exports (ignoré par Git)
│   ├── atoll_exports/         # Fichiers d'import ATOLL générés (ACP/AFP)
│   └── network_data.db        # Base SQLite simulée
│
├── outputs/                   # Rapports consolidés (Excel Bouygues Telecom, etc.)
│
├── src/                       # Modules Python métier
│   ├── __init__.py
│   ├── database_builder.py    # Génération et ingestion SQLite
│   ├── data_ingestion.py      # Extraction SQL & requêtes optimisées
│   ├── propagation_model.py   # Modélisation électromagnétique Cost-231 Hata
│   ├── kpi_analyzer.py        # Analyse radio & détection d'anomalies
│   ├── radio_dimensioning.py  # Recommandations de design & exports compatibles ATOLL
│   └── excel_reporter.py      # Dashboard Excel stylisé openpyxl (charte Bouygues)
│
├── app.py                     # Cockpit web interactif Streamlit & Folium
├── main.py                    # Script orchestrateur principal du pipeline CLI
├── requirements.txt           # Dépendances Python
└── README.md                  # Documentation du projet
```

## ⚡ Quick Start

### 1) Cloner le projet et installer les dépendances

```bash
git clone https://github.com/amine007/radio-data-optimizer.git
cd radio-data-optimizer
pip install -r requirements.txt
```

### 2) Exécuter le pipeline complet

```bash
python main.py
```

### 3) Lancer le cockpit web interactif

```bash
streamlit run app.py
```

## 📈 Résultats du pipeline

Exemple de sortie console :

```text
================================================================================
 📡 BTECHNOLOGIE / BOUYGUES TELECOM - RADIO DATA OPTIMIZER & RSE TOOL
================================================================================
🚀 [Étape 1/5] Initialisation, ingestion & modélisation de propagation...
   └─ Modèle Cost-231 Hata appliqué avec succès.

🔍 [Étape 2/5] Analyse des KPIs radio & impact décarbonation...
🛠️ [Étape 3/5] Recommandations de design & génération export ATOLL...
📊 [Étape 4/5] Génération du cockpit Excel Bouygues Telecom...

================================================================================
🎉 PIPELINE EXÉCUTÉ AVEC SUCCÈS EN 12.16 SECONDES !
================================================================================
📁 Fichiers générés prêts pour la démonstration :
   ├─ Base SQLite : data/network_data.db
   ├─ Fichier import ATOLL : data/atoll_exports/atoll_import_recommendations.csv
   └─ Rapport Excel final : outputs/Bouygues_Telecom_Radio_Optimization_Report.xlsx
================================================================================
```

## 🌐 Fonctionnalités du dashboard Streamlit

- **Supervision réseau & cartographie** : carte interactive Folium avec géolocalisation des sites 3G/4G/5G et statut de dégradation coloré en temps réel.
- **Analyse de propagation Cost-231 Hata** : visualisation Plotly comparant \(RSRP_{\text{mesuré}}\) et \(RSRP_{\text{théorique}}\), avec identification du top 10 des cellules en déficit de couverture.
- **Simulateur RSE interactif** : estimation en direct des économies d’énergie \(kWh\) et des émissions de \(CO_2\) évitées selon le réglage nocturne du *MIMO Sleep Mode*.

## 🛠️ Points techniques clés

- **Base SQLite industrialisée** : structuration et ingestion des données réseau pour analyse batch.
- **Modélisation radio empirique** : calcul de path loss avec le modèle Cost-231 Hata.
- **Détection d’anomalies radio** : classement automatique des cellules en surcharge, sous-couverture ou zone nominale.
- **Dimensionnement compatible ATOLL** : génération de recommandations exportables en ACP/AFP.
- **Reporting exécutif** : génération d’un rapport Excel stylisé adapté à un usage opérationnel.
- **Visualisation temps réel** : cockpit web clair, interactif et orienté décision.
