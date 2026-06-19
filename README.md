# Rimborsi Dipendenti

Strumento interno dell'ufficio HR per la gestione delle richieste di rimborso spese dei
dipendenti. Per ogni richiesta l'applicazione calcola la **quota esente** IRPEF e la
**quota imponibile** secondo i massimali della normativa vigente, applica le regole di
validazione e tiene traccia del plafond mensile di esenzione di ciascun dipendente.

> **Normativa di riferimento:** Circolare MEF n. 18/2026 — in vigore dal 01/01/2026.  
> Le spese con data di sostenimento fino al 31/12/2025 restano soggette alla Circolare n. 41/2024.

---

## Funzionalità

- **Nuova richiesta** — inserimento di una richiesta di rimborso con calcolo immediato di
  quota esente e imponibile; il form mostra in tempo reale il massimale applicabile in base
  a categoria, data e quantità inserita.
- **Richieste** — elenco di tutte le richieste, filtrabile per dipendente e mese, con stato
  (valida / respinta) e dettaglio del calcolo.
- **Riepilogo mensile** — totali esente/imponibile per dipendente e mese, con barra di
  utilizzo del plafond mensile (1.400 € dal 2026, 1.200 € fino al 2025).
- **Normativa vigente** — massimali correnti applicati dal sistema.

---

## Categorie di rimborso

| Categoria | Massimale 2026 | Massimale 2025 |
|---|---|---|
| Trasferta in Italia | 50,00 €/giorno | 46,48 €/giorno |
| Trasferta all'estero | 85,00 €/giorno (¹) | 77,47 €/giorno |
| Rimborso pasto | 10,00 €/giorno | 8,00 €/giorno |
| Rimborso chilometrico | 0,45 €/km | 0,42 €/km |
| Rimborso alloggio | 170,00 €/notte | 150,00 €/notte |
| Indennità lavoro agile | 3,50 €/giorno (max 12 gg/mese) | non prevista |
| **Plafond mensile** | **1.400,00 €** | **1.200,00 €** |

> (¹) Trasferta estera >5 giorni: riduzione del 10% dal 6° giorno, 20% dall'11° giorno.

---

## Regole principali

- La **quota esente** è il minore tra l'importo richiesto, il massimale teorico e la
  capienza residua del plafond mensile del dipendente.
- La **quota imponibile** è la parte eccedente la quota esente.
- Il regime applicabile (massimali e plafond) è determinato dalla **data di sostenimento**
  della spesa, non dalla data di presentazione della richiesta.
- **Incompatibilità lavoro agile / trasferta**: nella stessa giornata e per lo stesso
  dipendente non è possibile avere sia un'indennità di lavoro agile sia un'indennità di
  trasferta; la richiesta è respinta integralmente.
- Le richieste respinte non producono effetti sul plafond né sull'incompatibilità.

---

## Requisiti

- Python 3.10 o superiore
- Nessun database e nessun servizio esterno: i dati sono salvati in `data/richieste.json`

---

## Avvio

```bash
python -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app src/app.py run
```

L'applicazione è raggiungibile su <http://127.0.0.1:5000>.

---

## Test

```bash
pytest -v
```

La suite copre: calcolo quota esente/imponibile, massimali per categoria, plafond mensile,
validazione delle richieste, regole di incompatibilità e le principali route Flask.

La pipeline CI esegue i test automaticamente su Python 3.10, 3.11, 3.12 e 3.13 ad ogni
push o pull request sul branch `main`.

---

## Struttura del progetto

```
.github/
└── workflows/
    └── ci.yml          # pipeline GitHub Actions (test su 4 versioni Python)
src/
├── app.py              # route Flask e orchestrazione della logica
├── rules.py            # parametri normativi (massimali 2025/2026, plafond, categorie)
├── calculator.py       # calcolo quota esente/imponibile con regime transitorio
├── validator.py        # validazione richieste e controllo incompatibilità
├── storage.py          # persistenza su file JSON e query sui dati
├── templates/          # pagine HTML (Jinja2)
└── static/             # CSS e JavaScript
data/
└── richieste.json      # archivio delle richieste
tests/                  # test pytest (calcolo, validazione, route)
```
