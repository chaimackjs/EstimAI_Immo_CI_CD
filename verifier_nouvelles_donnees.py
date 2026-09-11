import argparse
import json
from pathlib import Path

import requests


DVF_API_URL = "https://www.data.gouv.fr/api/1/datasets/demandes-de-valeurs-foncieres/"
DPE_API_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
STATE_PATH = Path("data_sources_state.json")


def recuperer_etat_distant():
    """Récupérer les versions actuelles des sources DVF et DPE."""
    dvf_response = requests.get(DVF_API_URL, timeout=60)
    dvf_response.raise_for_status()
    dvf_data = dvf_response.json()

    ressources_dvf = []
    for resource in dvf_data.get("resources", []):
        url = resource.get("url", "")
        if resource.get("format") == "txt.zip" and url.endswith(".txt.zip"):
            ressources_dvf.append(
                {
                    "title": resource.get("title"),
                    "url": url,
                    "last_modified": resource.get("last_modified"),
                }
            )

    dpe_response = requests.get(DPE_API_URL, params={"size": 1}, timeout=60)
    dpe_response.raise_for_status()
    dpe_data = dpe_response.json()

    return {
        "dvf": sorted(ressources_dvf, key=lambda resource: resource["title"] or ""),
        "dpe": {"total": dpe_data.get("total", 0)},
    }


def charger_etat_local():
    """Charger l’état de référence enregistré dans le dépôt."""
    if not STATE_PATH.exists():
        return {"dvf": [], "dpe": {"total": 0}}
    with STATE_PATH.open(encoding="utf-8") as state_file:
        return json.load(state_file)


def comparer_etats(etat_local, etat_distant):
    """Retourner la liste des changements entre les deux états."""
    changements = []
    if etat_local.get("dvf", []) != etat_distant.get("dvf", []):
        changements.append("DVF : ressources ou dates de mise à jour modifiées")

    total_local = etat_local.get("dpe", {}).get("total", 0)
    total_distant = etat_distant.get("dpe", {}).get("total", 0)
    if total_local != total_distant:
        changements.append(
            f"DPE : total modifié ({total_local} -> {total_distant})"
        )
    return changements


def main():
    """Comparer les sources distantes avec l’état de référence du projet."""
    parser = argparse.ArgumentParser(description="Vérifier les nouvelles données DVF/DPE")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Retourner le code 1 si une nouvelle donnée est détectée",
    )
    args = parser.parse_args()

    etat_local = charger_etat_local()
    etat_distant = recuperer_etat_distant()
    changements = comparer_etats(etat_local, etat_distant)

    print(f"Ressources DVF détectées : {len(etat_distant['dvf'])}")
    print(f"Diagnostics DPE détectés : {etat_distant['dpe']['total']}")

    if changements:
        print("Nouvelles données disponibles :")
        for changement in changements:
            print(f"- {changement}")
        return 1 if args.strict else 0

    print("Aucune nouvelle donnée détectée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
