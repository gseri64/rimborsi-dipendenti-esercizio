"""Calcolo della quota esente e della quota imponibile di una richiesta."""

from datetime import date

from src import rules


def _is_2026(richiesta):
    return date.fromisoformat(richiesta["data"]) >= rules.DATA_DECORRENZA_2026


def _massimale_estero_2026(giorni):
    """Massimale trasferta estera con riduzione progressiva (Sezione 4)."""
    g1 = min(giorni, 5)
    g2 = min(max(giorni - 5, 0), 5)
    g3 = max(giorni - 10, 0)
    return round(g1 * 85.00 + g2 * 76.50 + g3 * 68.00, 2)


def massimale_teorico(richiesta, giorni_agile_gia_usati=0):
    """Massimale di esenzione applicabile alla richiesta, in base alla categoria e alla data."""
    categoria = richiesta["categoria"]
    is_2026 = _is_2026(richiesta)

    if categoria == "trasferta_estero":
        if is_2026:
            return _massimale_estero_2026(richiesta["giorni"])
        return round(rules.MASSIMALI_GIORNALIERI_2025["trasferta_estero"] * richiesta["giorni"], 2)

    if categoria in ("trasferta_italia", "pasto"):
        massimali = rules.MASSIMALI_GIORNALIERI if is_2026 else rules.MASSIMALI_GIORNALIERI_2025
        return round(massimali[categoria] * richiesta["giorni"], 2)

    if categoria == "lavoro_agile":
        # Giorni ammessi = min(richiesti, capienza mensile residua)
        giorni_ammessi = min(
            richiesta["giorni"],
            max(rules.LAVORO_AGILE_MAX_GIORNI_MESE - giorni_agile_gia_usati, 0),
        )
        return round(rules.MASSIMALI_GIORNALIERI["lavoro_agile"] * giorni_ammessi, 2)

    if categoria == "chilometrico":
        tasso = rules.MASSIMALE_KM if is_2026 else rules.MASSIMALE_KM_2025
        return round(tasso * richiesta["km"], 2)

    if categoria == "alloggio":
        tasso = rules.MASSIMALE_NOTTE if is_2026 else rules.MASSIMALE_NOTTE_2025
        return round(tasso * richiesta["notti"], 2)

    raise ValueError(f"categoria non gestita: {categoria}")


def calcola(richiesta, esente_gia_riconosciuta, giorni_agile_gia_usati=0):
    """Restituisce (quota_esente, quota_imponibile, dettaglio).

    `esente_gia_riconosciuta` è la quota esente già riconosciuta al dipendente
    nel mese della richiesta, ai fini del plafond mensile.
    `giorni_agile_gia_usati` è il numero di giornate lavoro agile già rimborsate
    nel mese (rilevante solo per la categoria lavoro_agile).
    """
    plafond = rules.PLAFOND_MENSILE if _is_2026(richiesta) else rules.PLAFOND_MENSILE_2025
    importo = richiesta["importo"]
    teorico = massimale_teorico(richiesta, giorni_agile_gia_usati)
    esente_teorica = min(importo, teorico)
    capienza = max(plafond - esente_gia_riconosciuta, 0.0)
    esente = round(min(esente_teorica, capienza), 2)
    imponibile = round(importo - esente, 2)
    dettaglio = {
        "massimale_teorico": teorico,
        "esente_teorica": round(esente_teorica, 2),
        "capienza_plafond": round(capienza, 2),
    }
    return esente, imponibile, dettaglio
