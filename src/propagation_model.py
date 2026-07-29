import numpy as np
import pandas as pd

class Cost231HataModel:
    """
    Modèle de propagation radio Cost-231 Hata pour le calcul du Path Loss 
    et l'analyse d'écart couverture (Urbain / Suburbain / Rural).
    """

    def __init__(self, default_hb: float = 30.0, default_hm: float = 1.5):
        """
        :param default_hb: Hauteur moyenne des antennes BTS (en mètres)
        :param default_hm: Hauteur de l'équipement utilisateur/MS (en mètres)
        """
        self.hb = default_hb
        self.hm = default_hm

    def calculate_path_loss(
        self, 
        frequency_mhz: float, 
        distance_km: float, 
        environment: str = "urban"
    ) -> float:
        """
        Calcule l'affaiblissement de propagation (Path Loss Lb en dB) via Cost-231 Hata.
        """
        # Limites d'application du modèle (ajustement automatique si hors bornes)
        d = max(distance_km, 0.1)  # min 100m
        f = frequency_mhz
        
        # 1. Facteur de correction pour la hauteur du mobile a(hm)
        # Formule pour grande/moyenne ville à des fréquences GHz
        a_hm = (1.1 * np.log10(f) - 0.7) * self.hm - (1.56 * np.log10(f) - 0.8)

        # 2. Constante d'environnement (Cm)
        if environment.lower() in ["urban", "dense_urban"]:
            cm = 3.0
        elif environment.lower() in ["suburban", "rural"]:
            cm = 0.0
        else:
            cm = 0.0

        # 3. Équation maîtresse Cost-231 Hata
        path_loss = (
            46.3 
            + 33.9 * np.log10(f) 
            - 13.82 * np.log10(self.hb) 
            - a_hm 
            + (44.9 - 6.55 * np.log10(self.hb)) * np.log10(d) 
            + cm
        )

        return float(path_loss)

    def estimate_theoretical_rsrp(
        self, 
        tx_power_dbm: float, 
        path_loss_db: float, 
        antenna_gain_dbi: float = 18.0
    ) -> float:
        """
        Estime le RSRP théorique reçu par l'UE.
        RSRP_th (dBm) = Tx_Power (dBm) + Antenna_Gain (dBi) - Path_Loss (dB)
        """
        return tx_power_dbm + antenna_gain_dbi - path_loss_db

    def diagnose_coverage_gap(
        self, 
        measured_rsrp: float, 
        theoretical_rsrp: float, 
        tolerance_db: float = 12.0
    ) -> dict:
        """
        Analyse la cause racine en comparant la mesure terrain au modèle théorique.
        """
        gap = theoretical_rsrp - measured_rsrp

        if gap > tolerance_db:
            status = "CRITICAL_PATH_LOSS"
            recommendation = "Vérifier obstacles physiques (bâtiment/masque), vérifier feeder/connectique ou réduire le tilt électrique."
        elif gap < -tolerance_db:
            status = "OVER_COVERAGE_RISK"
            recommendation = "Couverture anormalement forte. Risque d'interférence inter-cellulaire (Overshooting). Augmenter le tilt."
        else:
            status = "NOMINAL"
            recommendation = "Propagation conforme au modèle théorique."

        return {
            "rsrp_gap_db": round(gap, 2),
            "status": status,
            "recommendation": recommendation
        }

def process_propagation_analysis(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction helper pour enrichir un DataFrame avec les calculs du modèle.
    """
    model = Cost231HataModel()
    
    # Données par défaut pour la simulation si absentes
    default_tx_power = 46.0  # 46 dBm (~40W)
    default_distance = 1.2   # 1.2 km du site
    
    path_losses = []
    rsrp_theoriques = []
    diagnostics = []

    for _, row in df_merged.iterrows():
        # Extrait la fréquence numérique à partir de la chaîne (ex: "1800 MHz" -> 1800.0)
        freq_val = float(str(row.get('frequency_band', '1800')).split()[0])
        
        pl = model.calculate_path_loss(frequency_mhz=freq_val, distance_km=default_distance)
        rsrp_th = model.estimate_theoretical_rsrp(tx_power_dbm=default_tx_power, path_loss_db=pl)
        diag = model.diagnose_coverage_gap(measured_rsrp=row['rsrp_dbm'], theoretical_rsrp=rsrp_th)
        
        path_losses.append(round(pl, 2))
        rsrp_theoriques.append(round(rsrp_th, 2))
        diagnostics.append(diag['status'])

    df_merged['path_loss_cost231_db'] = path_losses
    df_merged['rsrp_theoretical_dbm'] = rsrp_theoriques
    df_merged['propagation_diag'] = diagnostics
    
    return df_merged

if __name__ == "__main__":
    # Test unitaire rapide du module
    hata = Cost231HataModel(default_hb=30.0, default_hm=1.5)
    pl = hata.calculate_path_loss(frequency_mhz=1800.0, distance_km=1.5, environment="urban")
    rsrp_th = hata.estimate_theoretical_rsrp(tx_power_dbm=46.0, path_loss_db=pl)
    diag = hata.diagnose_coverage_gap(measured_rsrp=-112.0, theoretical_rsrp=rsrp_th)
    
    print("--- TEST UNITAIRE COST-231 HATA ---")
    print(f"Path Loss (1.8GHz, 1.5km, Urbain): {pl:.2f} dB")
    print(f"RSRP Théorique Estimé: {rsrp_th:.2f} dBm")
    print(f"Diagnostic (pour RSRP mesuré -112 dBm): {diag['status']}")
    print(f"Recommandation: {diag['recommendation']}")