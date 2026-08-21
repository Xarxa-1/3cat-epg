import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URL = (
    "https://dinamics.3cat.cat/wsarafem/arafem/tv/"
    "profile/noimage/geo/cat"
)

OUTPUT = Path("epg.json")


def descarrega_dades():
    request = Request(
        URL,
        headers={"User-Agent": "3cat-epg/1.0"}
    )

    with urlopen(request, timeout=30) as resposta:
        return json.load(resposta)


def converteix_programa(programa):
    if not isinstance(programa, dict):
        return None

    if not all([
        programa.get("start_time"),
        programa.get("end_time"),
        programa.get("titol_programa")
    ]):
        return None

    classificacio = programa.get("classificacio") or {}

    return {
        "start": programa["start_time"],
        "stop": programa["end_time"],
        "title": programa["titol_programa"],
        "subtitle": programa.get("titol_capitol") or None,
        "description": programa.get("sinopsi") or None,
        "genre": classificacio.get("subgrup") or None,
        "image": programa.get("destacat_imatge") or None
    }


def main():
    dades = descarrega_dades()
    epg = {}

    for canal in dades.get("canal", []):
        atributs = canal.get("@attributes") or {}
        canal_id = atributs.get("name")

        if not canal_id:
            continue

        programes = []

        for camp in ("ara_fem", "despres_fem"):
            programa = converteix_programa(canal.get(camp))

            if programa:
                programes.append(programa)

        programes.sort(key=lambda programa: programa["start"])

        if programes:
            epg[canal_id] = programes

    resultat = {
        "version": 1,
        "updated": datetime.now(timezone.utc).isoformat(),
        "epg": epg
    }

    OUTPUT.write_text(
        json.dumps(resultat, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
