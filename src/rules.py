"""Parametri normativi per il calcolo dei rimborsi spese.

Fonte: Circolare MEF n. 18/2026 (decorrenza 01/01/2026).
Regime previgente: Circolare n. 41/2024 (fino al 31/12/2025).
"""

from datetime import date

DATA_DECORRENZA_2026 = date(2026, 1, 1)

# Massimali vigenti dal 01/01/2026
MASSIMALI_GIORNALIERI = {
    "trasferta_italia": 50.00,
    "trasferta_estero": 85.00,
    "pasto": 10.00,
    "lavoro_agile": 3.50,
}

MASSIMALE_KM = 0.45
MASSIMALE_NOTTE = 170.00
PLAFOND_MENSILE = 1400.00
LAVORO_AGILE_MAX_GIORNI_MESE = 12

# Riduzione progressiva trasferta estera >5 giorni (Sezione 4, Circolare 18/2026)
ESTERO_TASSO_PIENO = 85.00        # giorni 1-5
ESTERO_TASSO_RIDOTTO_10 = 76.50   # giorni 6-10  (85 × 0.90)
ESTERO_TASSO_RIDOTTO_20 = 68.00   # giorni 11+   (85 × 0.80)

# Massimali previgenti fino al 31/12/2025 (Circolare n. 41/2024)
MASSIMALI_GIORNALIERI_2025 = {
    "trasferta_italia": 46.48,
    "trasferta_estero": 77.47,
    "pasto": 8.00,
}

MASSIMALE_KM_2025 = 0.42
MASSIMALE_NOTTE_2025 = 150.00
PLAFOND_MENSILE_2025 = 1200.00

CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
    "lavoro_agile": "Indennità lavoro agile",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto", "lavoro_agile")

RIFERIMENTO_NORMATIVO = "Circolare MEF n. 18/2026"
