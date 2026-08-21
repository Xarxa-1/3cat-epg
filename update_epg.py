import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URL = (
    "https://dinamics.3cat.cat/wsarafem/arafem/tv/"
    "profile/noimage/geo/cat"
)

OUTPUT = Path("epg.json")

NOMS = {
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

    inici = programa.get("start_time")
    final = programa.get("end_time")
    titol = programa.get("titol_programa")

    if not inici or not final or not titol:
        return None

    classificacio = programa.get("classificacio") or {}

    return {
        "start": inici,
        "stop": final,
        "title": titol,
        "subtitle": programa.get("titol_capitol") or "",
        "description": programa.get("sinopsi") or "",
        "genre": classificacio.get("subgrup") or "",
        "image": programa.get("destacat_imatge") or ""
    }


def main():
    dades = descarrega()

    canals = []
    epg = {}

    for entrada in dades.get("canal", []):
        atributs = entrada.get("@attributes") or {}
        canal_id = atributs.get("name")

        if not canal_id:
            continue

        # Afegir sempre el canal
        canals.append({
            "id": canal_id,
            "name": NOMS.get(canal_id, canal_id)
        })

        # Crear sempre l'entrada EPG
        epg[canal_id] = []

        for nom_camp in ("ara_fem", "despres_fem"):
            programa = convertir_programa(
                entrada.get(nom_camp)
            )

            if programa:
                epg[canal_id].append(programa)

        epg[canal_id].sort(
            key=lambda programa: programa["start"]
        )

    resultat = {
        "version": 1,
        "updated": datetime.now(timezone.utc).isoformat(),
        "source": URL,
        "channels": canals,
        "epg": epg
    }

    OUTPUT.write_text(
        json.dumps(resultat, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
