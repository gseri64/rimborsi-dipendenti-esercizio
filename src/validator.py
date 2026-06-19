"""Regole di validazione delle richieste di rimborso."""

from datetime import date, timedelta

from src import rules


def valida(richiesta):
    """Restituisce (True, "") se la richiesta è valida, altrimenti (False, motivazione)."""
    if not richiesta.get("dipendente"):
        return False, "dipendente mancante"

    categoria = richiesta.get("categoria")
    if categoria not in rules.CATEGORIE:
        return False, "categoria non riconosciuta"

    importo = richiesta.get("importo")
    if importo is None or importo <= 0:
        return False, "importo non positivo"

    try:
        data_richiesta = date.fromisoformat(richiesta.get("data") or "")
    except ValueError:
        return False, "data mancante o non valida"

    # lavoro_agile non ammesso per giornate anteriori al 01/01/2026
    if categoria == "lavoro_agile" and data_richiesta < rules.DATA_DECORRENZA_2026:
        return False, "categoria non riconosciuta"

    if categoria in rules.CATEGORIE_A_GIORNATE:
        giorni = richiesta.get("giorni")
        if not giorni or giorni <= 0:
            return False, "numero di giornate non valido"

    if categoria == "chilometrico":
        km = richiesta.get("km")
        if not km or km <= 0:
            return False, "numero di chilometri non valido"

    if categoria == "alloggio":
        notti = richiesta.get("notti")
        if not notti or notti <= 0:
            return False, "numero di notti non valido"

    return True, ""


def _giorni_coperti(richiesta):
    """Insieme delle date coperte da una richiesta a giornate (trasferta o lavoro agile)."""
    data = date.fromisoformat(richiesta["data"])
    giorni = richiesta.get("giorni") or 1
    return {data + timedelta(days=i) for i in range(giorni)}


def controlla_incompatibilita(richiesta, richieste_esistenti):
    """Verifica incompatibilità lavoro agile / trasferta (Sezione 5, dal 01/01/2026).

    Restituisce (True, "") se compatibile, altrimenti (False, motivazione).
    Solo le richieste valide producono effetti di incompatibilità.
    """
    categoria = richiesta.get("categoria")
    try:
        data_richiesta = date.fromisoformat(richiesta.get("data") or "")
    except ValueError:
        return True, ""

    if data_richiesta < rules.DATA_DECORRENZA_2026:
        return True, ""

    TRASFERTE = {"trasferta_italia", "trasferta_estero"}

    if categoria == "lavoro_agile":
        giorni_nuovi = _giorni_coperti(richiesta)
        for r in richieste_esistenti:
            if r["stato"] != "valida":
                continue
            if r["dipendente"] != richiesta["dipendente"]:
                continue
            if r["categoria"] not in TRASFERTE:
                continue
            if giorni_nuovi & _giorni_coperti(r):
                return False, "incompatibilità lavoro agile / trasferta"

    elif categoria in TRASFERTE:
        giorni_nuovi = _giorni_coperti(richiesta)
        for r in richieste_esistenti:
            if r["stato"] != "valida":
                continue
            if r["dipendente"] != richiesta["dipendente"]:
                continue
            if r["categoria"] != "lavoro_agile":
                continue
            if giorni_nuovi & _giorni_coperti(r):
                return False, "incompatibilità lavoro agile / trasferta"

    return True, ""
