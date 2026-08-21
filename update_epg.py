import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URL = (
    "https://dinamics.3cat.cat/wsarafem/arafem/tv/"
    "profile/noimage/geo/cat"
)

OUTPUT = Path("epg.json")

MAPA_CANALS = {
    "tvi": "tv3",
    "tv3": "tv3",
    "324": "324",
    "esport3": "esport3",
    "sx3": "sx3",
    "c33": "c33",
    "oca1": "oca1",
    "oca2": "oca2",
    "oca3": "oca3",
    "oca4": "oca4"
}

NOMS_CANALS = {
    "tv3": "TV3",
    "324": "3CatInfo",
    "esport3": "Esport3",
    "sx3": "SX3",
    "c33": "33",
    "oca1": "OCA 1",
    "oca2": "OCA 2",
    "oca3": "OCA 3",
    "oca4": "OCA 4"
}

CANALS_ESPERATS = [
    "tv3",
    "324",
    "esport3",
    "sx3",
    "c33",
    "oca1",
    "oca2",
    "oca3",
    "oca4"
]


def descarrega():
    request = Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=30) as resposta:
        return json.load(resposta)


def convertir_programa(programa):
    if not isinstance(programa, dict):
        return None

    if not programa.get("start_time"):
        return None

    if not programa.get("end_time"):
        return None

    if not programa.get("titol_programa"):
        return None

    classificacio = programa.get("classificacio") or {}

    return {
        "start": programa["start_time"],
        "stop": programa["end_time"],
        "title": programa["titol_programa"],
        "subtitle": programa.get("titol_capitol") or "",
        "description": programa.get("sinopsi") or "",
        "genre": classificacio.get("subgrup") or "",
        "image": programa.get("destacat_imatge") or ""
    }


def main():
    dades = descarrega()

    programes_per_canal = {}

    # Crear sempre tots els canals esperats
    for canal_id in CANALS_ESPERATS:
        programes_per_canal[canal_id] = []

    # Llegir canals retornats per l'API
    for entrada in dades.get("canal", []):
        atributs = entrada.get("@attributes") or {}
        canal_original = atributs.get("name")

        if not canal_original:
            continue

        canal_id = MAPA_CANALS.get(canal_original)

        if not canal_id:
            continue

        for nom_camp in ("ara_fem", "despres_fem"):
            programa = convertir_programa(
                entrada.get(nom_camp)
            )

            if programa:
                programes_per_canal[canal_id].append(programa)

    for canal_id in programes_per_canal:
        programes_per_canal[canal_id].sort(
            key=lambda programa: programa["start"]
        )

    channels = [
        {
            "id": canal_id,
            "name": NOMS_CANALS[canal_id]
        }
        for canal_id in CANALS_ESPERATS
    ]

    resultat = {
        "version": 1,
        "updated": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "channels": channels,
        "epg": programes_per_canal
    }

    OUTPUT.write_text(
        json.dumps(resultat, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
