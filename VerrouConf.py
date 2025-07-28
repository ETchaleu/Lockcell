from Tasks import Config
from pathlib import Path

class ConfigVerrou(Config):
    def __init__(self, nbRun=None):
        super().__init__(nbRun)
    
    def setInLinePath(self, path : str):
        self.InPath = path
    
    def setOutLinePath(self, path : str):
        self.OutPath = path
    
    def copy(self):
        res = ConfigVerrou(self.nbRun)
        res.InPath = self.InPath
        res.OutPath = self.OutPath

    def writeSource(self, lst : list):
        In = "./verrou" + self.InPath
        out = "./verrou" +  self.OutPath

        # On lit l'entièreté des lignes
        with open(In, 'r') as f:
            all_lines = f.readlines()

        # on selectionnes celles a perturber
        selected_lines = [all_lines[i] for i in lst if 0 <= i < len(all_lines)]

        # on écrit
        with open(out, 'w') as f:
            f.writelines(selected_lines)

    def Test(self, subspace: list) -> bool:
        self.writeSource(subspace)
        import os
        import subprocess

        # Dossier pour stocker les résultats
        REF_DIR = "ref"
        PERTURBED_DIR = "pert"
        LIGNE_FICHIER = self.OutPath  # Doit être au bon format (3 colonnes)

        # Définir les variables d’environnement pour le run perturbé
        env = os.environ.copy()
        env["VERROU_SOURCE"] = LIGNE_FICHIER
        env["VERROU_ROUNDING_MODE"] = "random"
        env["VERROU_FLOAT"] = "no"
        env["VERROU_UNFUSED"] = "no"
        env["VERROU_LIBM_NOINST_ROUNDING_MODE"] = "nearest"

        # Étape 3 — Lancer le run perturbé
        os.makedirs(PERTURBED_DIR, exist_ok=True)
        pert_result = subprocess.run(
            ["./verrou/DD_RUN", PERTURBED_DIR],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env
        )
        if pert_result.returncode != 0:
            raise RuntimeError("Error during the run")

        # Étape 4 — Comparaison avec DD_CMP
        cmp_result = subprocess.run(["./verrou/DD_CMP.py", REF_DIR, PERTURBED_DIR])


        # Code de retour global
        return cmp_result.returncode == 0